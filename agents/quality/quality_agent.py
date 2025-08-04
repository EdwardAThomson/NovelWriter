"""
Quality Control Agent for NovelWriter.

This agent is responsible for evaluating and improving the quality of generated content.
It follows the agentic principle of having a specific job: ensuring story quality meets standards.
"""

from typing import Dict, List, Any, Optional
import json
import logging

from agents.base.agent import BaseAgent, AgentResult
from agents.base.tool import ToolRegistry
from agents.quality.quality_tools import (
    AnalyzeCoherenceTool, 
    AnalyzePacingTool, 
    EvaluateProseQualityTool,
    QualityMetrics
)
from core.generation.ai_helper import send_prompt


class QualityControlAgent(BaseAgent):
    """
    Agent responsible for quality control of story content.
    
    This agent can:
    1. Evaluate chapter quality across multiple dimensions
    2. Provide specific improvement suggestions
    3. Decide which quality tools to use based on content type
    4. Generate revision recommendations
    """
    
    def __init__(self, model: str = "gpt-4o", logger: Optional[logging.Logger] = None):
        super().__init__(name="QualityControlAgent", model=model, logger=logger)
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self._register_tools()
        
        # Quality thresholds
        self.quality_thresholds = {
            "minimum_overall": 0.7,
            "minimum_coherence": 0.6,
            "minimum_pacing": 0.6,
            "minimum_prose": 0.6
        }
        
        self.logger.info("Quality Control Agent initialized with quality thresholds")
    
    def _register_tools(self):
        """Register available tools for this agent."""
        self.tool_registry.register_tool(AnalyzeCoherenceTool(self.model))
        self.tool_registry.register_tool(AnalyzePacingTool(self.model))
        self.tool_registry.register_tool(EvaluateProseQualityTool(self.model))
        
        self.available_tools = [tool.name for tool in self.tool_registry.get_available_tools()]
        self.logger.debug(f"Registered tools: {self.available_tools}")
    
    def get_available_tools(self) -> List[str]:
        """Return list of tools this agent can use."""
        return self.available_tools
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for quality control tasks."""
        return ["content", "task_type"]
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process a quality control task.
        
        Args:
            task_data: Dictionary containing:
                - content: The content to analyze
                - task_type: Type of quality check ("evaluate", "improve", "validate")
                - context: Optional context information
                - quality_standards: Optional quality requirements
                
        Returns:
            AgentResult with quality analysis and recommendations
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
        context = task_data.get("context", {})
        quality_standards = task_data.get("quality_standards", {})
        
        try:
            if task_type == "evaluate":
                return self._evaluate_content(content, context, quality_standards)
            elif task_type == "improve":
                return self._improve_content(content, context, quality_standards)
            elif task_type == "validate":
                return self._validate_content(content, context, quality_standards)
            else:
                return self.handle_error(
                    ValueError(f"Unknown task type: {task_type}"),
                    "process_task"
                )
                
        except Exception as e:
            return self.handle_error(e, "process_task")
    
    def _evaluate_content(self, content: str, context: Dict, standards: Dict) -> AgentResult:
        """
        Evaluate content quality using available tools.
        
        This method demonstrates agentic decision-making: the agent decides
        which tools to use based on the content and context.
        """
        self.logger.info("Starting content evaluation")
        
        # Agent decides which tools to use
        tools_to_use = self._select_evaluation_tools(content, context)
        
        evaluation_results = {}
        
        # Execute selected tools
        for tool_name in tools_to_use:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                self.logger.debug(f"Using tool: {tool_name}")
                
                # Prepare tool parameters
                tool_params = self._prepare_tool_params(tool_name, content, context, standards)
                
                # Execute tool
                result = tool.execute(**tool_params)
                evaluation_results[tool_name] = result
                
                if not result.success:
                    self.logger.warning(f"Tool {tool_name} failed: {result.error_message}")
        
        # Synthesize results
        quality_analysis = self._synthesize_evaluation_results(evaluation_results)
        
        # Calculate metrics
        metrics = self._calculate_quality_metrics(evaluation_results)
        
        return AgentResult(
            success=True,
            data={
                "quality_analysis": quality_analysis,
                "tool_results": evaluation_results,
                "meets_standards": self._check_quality_standards(metrics),
                "recommendations": self._generate_recommendations(quality_analysis)
            },
            messages=[f"Evaluated content using {len(tools_to_use)} tools"],
            metrics=metrics
        )
    
    def _select_evaluation_tools(self, content: str, context: Dict) -> List[str]:
        """
        Agent decision-making: select which tools to use based on content analysis.
        
        This is a key agentic behavior - the agent analyzes the situation
        and decides which tools are most appropriate.
        """
        tools_to_use = []
        
        # Always check coherence
        tools_to_use.append("analyze_coherence")
        
        # Check prose quality for all content
        tools_to_use.append("evaluate_prose_quality")
        
        # Decide on pacing analysis based on content length and type
        word_count = len(content.split())
        if word_count > 100:  # Only analyze pacing for substantial content
            tools_to_use.append("analyze_pacing")
        
        # Could add more sophisticated decision logic here
        # For example, analyze content type, genre, etc.
        
        self.logger.info(f"Agent selected tools: {tools_to_use}")
        return tools_to_use
    
    def _prepare_tool_params(self, tool_name: str, content: str, context: Dict, standards: Dict) -> Dict[str, Any]:
        """Prepare parameters for each tool based on available context."""
        base_params = {"content": content}
        
        if tool_name == "analyze_coherence":
            base_params.update({
                "context": context,
                "genre": context.get("genre", "general")
            })
        elif tool_name == "analyze_pacing":
            base_params.update({
                "target_pacing": standards.get("target_pacing", "medium"),
                "scene_type": context.get("scene_type", "general")
            })
        elif tool_name == "evaluate_prose_quality":
            base_params.update({
                "style_target": standards.get("style_target", "commercial"),
                "genre_standards": standards.get("genre_standards", {})
            })
        
        return base_params
    
    def _synthesize_evaluation_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple tools into coherent analysis."""
        synthesis = {
            "overall_assessment": "",
            "key_strengths": [],
            "key_weaknesses": [],
            "priority_improvements": []
        }
        
        # Collect insights from each tool
        all_strengths = []
        all_weaknesses = []
        all_suggestions = []
        
        for tool_name, result in results.items():
            if result.success and result.data:
                data = result.data
                
                # Extract common fields
                if "strengths" in data:
                    all_strengths.extend(data["strengths"])
                if "weaknesses" in data:
                    all_weaknesses.extend(data["weaknesses"])
                if "suggestions" in data:
                    all_suggestions.extend(data["suggestions"])
                if "specific_suggestions" in data:
                    all_suggestions.extend(data["specific_suggestions"])
        
        # Deduplicate and prioritize
        synthesis["key_strengths"] = list(set(all_strengths))[:5]
        synthesis["key_weaknesses"] = list(set(all_weaknesses))[:5]
        synthesis["priority_improvements"] = list(set(all_suggestions))[:7]
        
        # Generate overall assessment
        synthesis["overall_assessment"] = self._generate_overall_assessment(results)
        
        return synthesis
    
    def _generate_overall_assessment(self, results: Dict[str, Any]) -> str:
        """Generate an overall assessment based on tool results."""
        assessments = []
        
        for tool_name, result in results.items():
            if result.success and result.data:
                score = result.data.get("coherence_score") or result.data.get("pacing_score") or result.data.get("prose_score")
                if score:
                    if score >= 0.8:
                        assessments.append(f"{tool_name}: Excellent")
                    elif score >= 0.7:
                        assessments.append(f"{tool_name}: Good")
                    elif score >= 0.6:
                        assessments.append(f"{tool_name}: Acceptable")
                    else:
                        assessments.append(f"{tool_name}: Needs improvement")
        
        return "; ".join(assessments) if assessments else "Analysis completed"
    
    def _calculate_quality_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics from tool results."""
        metrics = {}
        
        for tool_name, result in results.items():
            if result.success and result.data:
                data = result.data
                
                # Extract scores
                if "coherence_score" in data:
                    metrics["coherence_score"] = data["coherence_score"]
                if "pacing_score" in data:
                    metrics["pacing_score"] = data["pacing_score"]
                if "prose_score" in data:
                    metrics["prose_score"] = data["prose_score"]
                
                # Add execution time if available
                if result.execution_time:
                    metrics[f"{tool_name}_execution_time"] = result.execution_time
        
        # Calculate overall score if we have component scores
        component_scores = [
            metrics.get("coherence_score"),
            metrics.get("pacing_score"),
            metrics.get("prose_score")
        ]
        component_scores = [s for s in component_scores if s is not None]
        
        if component_scores:
            metrics["overall_quality_score"] = sum(component_scores) / len(component_scores)
        
        return metrics
    
    def _check_quality_standards(self, metrics: Dict[str, float]) -> bool:
        """Check if content meets quality standards."""
        overall_score = metrics.get("overall_quality_score", 0)
        coherence_score = metrics.get("coherence_score", 0)
        pacing_score = metrics.get("pacing_score", 0)
        prose_score = metrics.get("prose_score", 0)
        
        return (
            overall_score >= self.quality_thresholds["minimum_overall"] and
            coherence_score >= self.quality_thresholds["minimum_coherence"] and
            pacing_score >= self.quality_thresholds["minimum_pacing"] and
            prose_score >= self.quality_thresholds["minimum_prose"]
        )
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Add priority improvements
        if analysis.get("priority_improvements"):
            recommendations.extend(analysis["priority_improvements"][:5])
        
        # Add general recommendations based on weaknesses
        if analysis.get("key_weaknesses"):
            for weakness in analysis["key_weaknesses"][:3]:
                recommendations.append(f"Address: {weakness}")
        
        return recommendations
    
    def _improve_content(self, content: str, context: Dict, standards: Dict) -> AgentResult:
        """Improve content based on quality analysis."""
        # First evaluate the content
        evaluation_result = self._evaluate_content(content, context, standards)
        
        if not evaluation_result.success:
            return evaluation_result
        
        # Generate improvement suggestions using LLM
        recommendations = evaluation_result.data.get("recommendations", [])
        
        improvement_prompt = self._create_improvement_prompt(content, recommendations, context)
        
        try:
            improved_content = send_prompt(improvement_prompt, model=self.model)
            
            return AgentResult(
                success=True,
                data={
                    "original_content": content,
                    "improved_content": improved_content,
                    "improvements_made": recommendations,
                    "original_analysis": evaluation_result.data
                },
                messages=["Content improved based on quality analysis"],
                metrics=evaluation_result.metrics
            )
            
        except Exception as e:
            return self.handle_error(e, "_improve_content")
    
    def _create_improvement_prompt(self, content: str, recommendations: List[str], context: Dict) -> str:
        """Create prompt for content improvement."""
        return f"""
Please improve the following content based on these specific recommendations:

RECOMMENDATIONS:
{chr(10).join(f"- {rec}" for rec in recommendations)}

ORIGINAL CONTENT:
{content}

CONTEXT:
Genre: {context.get('genre', 'general')}
Scene type: {context.get('scene_type', 'general')}

Please provide the improved version that addresses the recommendations while maintaining the original intent and style.
"""
    
    def _validate_content(self, content: str, context: Dict, standards: Dict) -> AgentResult:
        """Validate content against quality standards."""
        evaluation_result = self._evaluate_content(content, context, standards)
        
        if not evaluation_result.success:
            return evaluation_result
        
        meets_standards = evaluation_result.data.get("meets_standards", False)
        
        return AgentResult(
            success=True,
            data={
                "validation_passed": meets_standards,
                "quality_analysis": evaluation_result.data["quality_analysis"],
                "required_improvements": evaluation_result.data["recommendations"] if not meets_standards else []
            },
            messages=[f"Content validation: {'PASSED' if meets_standards else 'FAILED'}"],
            metrics=evaluation_result.metrics
        )
