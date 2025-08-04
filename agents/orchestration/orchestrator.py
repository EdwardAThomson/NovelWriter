"""
Multi-Agent Orchestrator for NovelWriter.

This orchestrator coordinates multiple agents to provide comprehensive
story generation and quality assurance. It demonstrates advanced agentic
behavior by deciding which agents to use and in what order.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime

from agents.base.agent import BaseAgent, AgentResult, AgentMessage
from agents.quality.quality_agent import QualityControlAgent
from agents.consistency.consistency_agent import ConsistencyAgent


@dataclass
class OrchestrationPlan:
    """Plan for orchestrating multiple agents."""
    agents_to_use: List[str]
    execution_order: List[Tuple[str, Dict[str, Any]]]  # (agent_name, task_data)
    coordination_strategy: str  # "sequential", "parallel", "conditional"
    quality_thresholds: Dict[str, float]
    max_iterations: int = 3


@dataclass
class OrchestrationResult:
    """Result from multi-agent orchestration."""
    success: bool
    final_content: str
    agent_results: Dict[str, AgentResult]
    iterations_performed: int
    overall_quality_score: float
    recommendations: List[str]
    execution_summary: str


class MultiAgentOrchestrator(BaseAgent):
    """
    Orchestrator that coordinates multiple agents for comprehensive story processing.
    
    This agent demonstrates advanced agentic behavior by:
    1. Analyzing content to determine which agents are needed
    2. Creating execution plans based on content type and requirements
    3. Coordinating agent execution with feedback loops
    4. Making decisions about iteration and improvement
    5. Synthesizing results from multiple agents
    """
    
    def __init__(self, model: str = "gpt-4o", output_dir: str = "current_work",
                 logger: Optional[logging.Logger] = None):
        super().__init__(name="MultiAgentOrchestrator", model=model, logger=logger)
        
        self.output_dir = output_dir
        
        # Initialize managed agents
        self.agents = {
            "quality": QualityControlAgent(model=model, logger=logger),
            "consistency": ConsistencyAgent(model=model, output_dir=output_dir, logger=logger)
        }
        
        # Default orchestration settings
        self.default_thresholds = {
            "minimum_quality": 0.7,
            "minimum_consistency": 0.8,
            "improvement_threshold": 0.1  # Minimum improvement to continue iterating
        }
        
        self.logger.info(f"Multi-Agent Orchestrator initialized with {len(self.agents)} agents")
    
    def get_available_tools(self) -> List[str]:
        """Return orchestration capabilities."""
        return [
            "orchestrate_content_processing",
            "create_orchestration_plan", 
            "execute_agent_workflow",
            "synthesize_agent_results"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for orchestration tasks."""
        return ["content", "task_type"]
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process a multi-agent orchestration task.
        
        Args:
            task_data: Dictionary containing:
                - content: The content to process
                - task_type: Type of orchestration ("comprehensive", "quality_focused", "consistency_focused")
                - chapter_number: Optional chapter number
                - context: Optional context information
                - quality_standards: Optional quality requirements
                - orchestration_mode: Optional mode ("iterative", "single_pass")
                
        Returns:
            AgentResult with orchestrated processing results
        """
        if not self.validate_input(task_data):
            return AgentResult(
                success=False,
                data={},
                messages=["Invalid input data"],
                metrics={}
            )
        
        content = task_data["content"]
        task_type = task_data["task_type"]
        chapter_number = task_data.get("chapter_number", 1)
        context = task_data.get("context", {})
        quality_standards = task_data.get("quality_standards", {})
        orchestration_mode = task_data.get("orchestration_mode", "iterative")
        
        try:
            if task_type == "comprehensive":
                return self._orchestrate_comprehensive_processing(
                    content, chapter_number, context, quality_standards, orchestration_mode
                )
            elif task_type == "quality_focused":
                return self._orchestrate_quality_focused(content, context, quality_standards)
            elif task_type == "consistency_focused":
                return self._orchestrate_consistency_focused(content, chapter_number, context)
            else:
                return self.handle_error(
                    ValueError(f"Unknown orchestration task type: {task_type}"),
                    "process_task"
                )
                
        except Exception as e:
            return self.handle_error(e, "process_task")
    
    def _orchestrate_comprehensive_processing(self, content: str, chapter_num: int,
                                            context: Dict, standards: Dict, mode: str) -> AgentResult:
        """
        Orchestrate comprehensive content processing with multiple agents.
        
        This method demonstrates advanced agentic orchestration by:
        1. Creating a dynamic execution plan
        2. Coordinating multiple agents with feedback loops
        3. Making decisions about iteration and improvement
        """
        self.logger.info(f"Starting comprehensive orchestration for chapter {chapter_num}")
        
        # Step 1: Create orchestration plan
        plan = self._create_orchestration_plan(content, context, standards, mode)
        
        # Step 2: Execute orchestration
        orchestration_result = self._execute_orchestration_plan(plan, content, chapter_num, context)
        
        # Step 3: Synthesize final results
        final_result = self._synthesize_orchestration_results(orchestration_result, content)
        
        return AgentResult(
            success=orchestration_result.success,
            data={
                "orchestration_result": orchestration_result,
                "final_analysis": final_result,
                "execution_plan": plan
            },
            messages=[orchestration_result.execution_summary],
            metrics={
                "overall_quality_score": orchestration_result.overall_quality_score,
                "iterations_performed": orchestration_result.iterations_performed,
                "agents_used": len(orchestration_result.agent_results)
            }
        )
    
    def _create_orchestration_plan(self, content: str, context: Dict, 
                                 standards: Dict, mode: str) -> OrchestrationPlan:
        """
        Create an orchestration plan based on content analysis.
        
        This demonstrates agentic decision-making: the orchestrator analyzes
        the content and context to decide which agents to use and how.
        """
        # Analyze content to determine agent needs
        content_analysis = self._analyze_content_requirements(content, context)
        
        # Determine which agents to use
        agents_to_use = []
        execution_order = []
        
        # Always use consistency agent first for tracking
        if "consistency" in self.agents:
            agents_to_use.append("consistency")
            execution_order.append(("consistency", {
                "content": content,
                "task_type": "track",
                "chapter_number": context.get("chapter_number", 1),
                "context": context
            }))
        
        # Use quality agent for evaluation
        if "quality" in self.agents:
            agents_to_use.append("quality")
            execution_order.append(("quality", {
                "content": content,
                "task_type": "evaluate",
                "context": context,
                "quality_standards": standards
            }))
        
        # Add consistency validation after quality check
        if "consistency" in self.agents:
            execution_order.append(("consistency", {
                "content": content,
                "task_type": "validate",
                "chapter_number": context.get("chapter_number", 1),
                "context": context
            }))
        
        # Determine coordination strategy
        strategy = "sequential"  # Default to sequential for reliability
        if mode == "single_pass":
            strategy = "sequential"
        elif content_analysis.get("complexity", "medium") == "high":
            strategy = "conditional"  # Use conditional for complex content
        
        # Set quality thresholds
        thresholds = {**self.default_thresholds, **standards}
        
        # Determine max iterations based on mode
        max_iterations = 1 if mode == "single_pass" else 3
        
        plan = OrchestrationPlan(
            agents_to_use=agents_to_use,
            execution_order=execution_order,
            coordination_strategy=strategy,
            quality_thresholds=thresholds,
            max_iterations=max_iterations
        )
        
        self.logger.info(f"Created orchestration plan: {len(agents_to_use)} agents, "
                        f"{strategy} strategy, max {max_iterations} iterations")
        
        return plan
    
    def _analyze_content_requirements(self, content: str, context: Dict) -> Dict[str, Any]:
        """Analyze content to determine orchestration requirements."""
        analysis = {
            "word_count": len(content.split()),
            "complexity": "medium",
            "character_count": 0,
            "dialogue_present": '"' in content,
            "action_indicators": any(word in content.lower() for word in ["ran", "jumped", "fought", "crashed"]),
            "description_heavy": content.count('.') > content.count('"')
        }
        
        # Estimate complexity
        if analysis["word_count"] > 1000:
            analysis["complexity"] = "high"
        elif analysis["word_count"] < 300:
            analysis["complexity"] = "low"
        
        # Estimate character count (simple heuristic)
        import re
        potential_names = re.findall(r'\b[A-Z][a-z]+\b', content)
        analysis["character_count"] = len(set(potential_names))
        
        return analysis
    
    def _execute_orchestration_plan(self, plan: OrchestrationPlan, content: str,
                                  chapter_num: int, context: Dict) -> OrchestrationResult:
        """Execute the orchestration plan with the specified agents."""
        
        agent_results = {}
        current_content = content
        iterations = 0
        overall_scores = []
        
        for iteration in range(plan.max_iterations):
            iterations += 1
            self.logger.info(f"Orchestration iteration {iteration + 1}")
            
            iteration_results = {}
            iteration_scores = []
            
            # Execute agents in planned order
            for agent_name, task_data in plan.execution_order:
                if agent_name not in self.agents:
                    self.logger.warning(f"Agent {agent_name} not available")
                    continue
                
                # Update task data with current content
                updated_task_data = {**task_data, "content": current_content}
                
                # Execute agent task
                agent = self.agents[agent_name]
                result = agent.process_task(updated_task_data)
                
                iteration_results[f"{agent_name}_{iteration}"] = result
                
                if result.success:
                    # Extract quality scores
                    if "overall_quality_score" in result.metrics:
                        iteration_scores.append(result.metrics["overall_quality_score"])
                    elif "overall_consistency_score" in result.data.get("validation_results", {}):
                        iteration_scores.append(result.data["validation_results"]["overall_consistency_score"])
                    
                    self.logger.debug(f"Agent {agent_name} completed successfully")
                else:
                    self.logger.warning(f"Agent {agent_name} failed: {result.messages}")
            
            # Store results for this iteration
            agent_results.update(iteration_results)
            
            # Calculate iteration score
            if iteration_scores:
                iteration_score = sum(iteration_scores) / len(iteration_scores)
                overall_scores.append(iteration_score)
                
                # Check if we should continue iterating
                if iteration_score >= plan.quality_thresholds.get("minimum_quality", 0.7):
                    self.logger.info(f"Quality threshold met after {iterations} iterations")
                    break
                
                # Check for improvement
                if len(overall_scores) > 1:
                    improvement = iteration_score - overall_scores[-2]
                    if improvement < plan.quality_thresholds.get("improvement_threshold", 0.1):
                        self.logger.info(f"Minimal improvement detected, stopping iterations")
                        break
        
        # Calculate final metrics
        final_score = overall_scores[-1] if overall_scores else 0.7
        
        # Generate execution summary
        summary = f"Executed {len(plan.agents_to_use)} agents over {iterations} iterations. "
        summary += f"Final quality score: {final_score:.2f}"
        
        # Collect recommendations from all agents
        all_recommendations = []
        for result in agent_results.values():
            if result.success and "recommendations" in result.data:
                all_recommendations.extend(result.data["recommendations"])
        
        return OrchestrationResult(
            success=True,
            final_content=current_content,
            agent_results=agent_results,
            iterations_performed=iterations,
            overall_quality_score=final_score,
            recommendations=list(set(all_recommendations)),  # Remove duplicates
            execution_summary=summary
        )
    
    def _synthesize_orchestration_results(self, orchestration_result: OrchestrationResult,
                                        original_content: str) -> Dict[str, Any]:
        """Synthesize results from multiple agents into a coherent analysis."""
        
        synthesis = {
            "overall_assessment": "",
            "quality_summary": {},
            "consistency_summary": {},
            "key_recommendations": [],
            "improvement_areas": [],
            "strengths": []
        }
        
        # Analyze quality results
        quality_results = [r for name, r in orchestration_result.agent_results.items() 
                          if "quality" in name and r.success]
        
        if quality_results:
            latest_quality = quality_results[-1]  # Get most recent quality result
            if "quality_analysis" in latest_quality.data:
                qa = latest_quality.data["quality_analysis"]
                synthesis["quality_summary"] = {
                    "overall_assessment": qa.get("overall_assessment", ""),
                    "strengths": qa.get("key_strengths", []),
                    "weaknesses": qa.get("key_weaknesses", [])
                }
        
        # Analyze consistency results
        consistency_results = [r for name, r in orchestration_result.agent_results.items() 
                             if "consistency" in name and r.success]
        
        if consistency_results:
            latest_consistency = consistency_results[-1]  # Get most recent consistency result
            if "validation_results" in latest_consistency.data:
                vr = latest_consistency.data["validation_results"]
                synthesis["consistency_summary"] = {
                    "overall_score": vr.get("overall_consistency_score", 0),
                    "character_issues": len([v for v in vr.get("character_validations", {}).values() 
                                           if v.get("violations", [])]),
                    "world_issues": len(vr.get("world_validations", {}).get("consistency_violations", []))
                }
        
        # Prioritize recommendations
        all_recs = orchestration_result.recommendations
        synthesis["key_recommendations"] = all_recs[:5]  # Top 5 recommendations
        
        # Generate overall assessment
        score = orchestration_result.overall_quality_score
        if score >= 0.9:
            assessment = "Excellent quality with strong consistency"
        elif score >= 0.8:
            assessment = "Good quality with minor areas for improvement"
        elif score >= 0.7:
            assessment = "Acceptable quality, some improvements recommended"
        else:
            assessment = "Significant improvements needed"
        
        synthesis["overall_assessment"] = f"{assessment}. Score: {score:.2f}"
        
        return synthesis
    
    def _orchestrate_quality_focused(self, content: str, context: Dict, standards: Dict) -> AgentResult:
        """Orchestrate quality-focused processing."""
        if "quality" not in self.agents:
            return self.handle_error(ValueError("Quality agent not available"), "_orchestrate_quality_focused")
        
        quality_agent = self.agents["quality"]
        result = quality_agent.process_task({
            "content": content,
            "task_type": "evaluate",
            "context": context,
            "quality_standards": standards
        })
        
        return AgentResult(
            success=result.success,
            data={"quality_focused_result": result.data},
            messages=[f"Quality-focused orchestration: {result.messages[0] if result.messages else 'completed'}"],
            metrics=result.metrics
        )
    
    def _orchestrate_consistency_focused(self, content: str, chapter_num: int, context: Dict) -> AgentResult:
        """Orchestrate consistency-focused processing."""
        if "consistency" not in self.agents:
            return self.handle_error(ValueError("Consistency agent not available"), "_orchestrate_consistency_focused")
        
        consistency_agent = self.agents["consistency"]
        result = consistency_agent.process_task({
            "content": content,
            "task_type": "validate",
            "chapter_number": chapter_num,
            "context": context
        })
        
        return AgentResult(
            success=result.success,
            data={"consistency_focused_result": result.data},
            messages=[f"Consistency-focused orchestration: {result.messages[0] if result.messages else 'completed'}"],
            metrics=result.metrics
        )
