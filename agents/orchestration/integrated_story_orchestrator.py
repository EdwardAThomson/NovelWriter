"""
Integrated Story Generation Orchestrator for NovelWriter.

This orchestrator properly integrates with your existing GUI components and
generation functions, calling the actual methods in lore.py, story_structure.py,
scene_plan.py, and chapter_writing.py that use the Generators folder.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import os
import json
from dataclasses import dataclass
from datetime import datetime

from agents.base.agent import BaseAgent, AgentResult, AgentMessage
from agents.quality.quality_agent import QualityControlAgent
from agents.consistency.consistency_agent import ConsistencyAgent

# Import your existing GUI components
from core.gui.lore import Lore
from core.gui.story_structure import StoryStructure
from core.gui.scene_plan import ScenePlanning
from core.gui.chapter_writing import ChapterWriting
from core.gui.parameters import Parameters


@dataclass
class IntegratedWorkflowResult:
    """Result from integrated workflow execution."""
    success: bool
    completed_steps: List[str]
    generated_files: Dict[str, str]  # step -> filepath
    quality_scores: Dict[str, float]
    consistency_reports: List[Dict]
    recommendations: List[str]
    execution_summary: str


class IntegratedStoryOrchestrator(BaseAgent):
    """
    Orchestrator that integrates with your existing NovelWriter components.
    
    This orchestrator:
    1. Uses your actual GUI component generation methods
    2. Calls functions that use the Generators folder
    3. Creates files in your current_work directory
    4. Follows your established workflow process
    5. Adds agentic validation and quality control
    """
    
    def __init__(self, app_instance, model: str = "gpt-4o", 
                 logger: Optional[logging.Logger] = None):
        super().__init__(name="IntegratedStoryOrchestrator", model=model, logger=logger)
        
        self.app = app_instance  # Your main NovelWriter app instance
        self.output_dir = self.app.get_output_dir()
        
        # Initialize validation agents
        self.quality_agent = QualityControlAgent(model=model, logger=logger)
        self.consistency_agent = ConsistencyAgent(model=model, output_dir=self.output_dir, logger=logger)
        
        # Get references to your existing GUI components
        self.lore_component = None
        self.structure_component = None
        self.scene_component = None
        self.chapter_component = None
        self.parameters_component = None
        
        self._initialize_components()
        
        # Workflow configuration
        self.workflow_steps = ["parameters", "lore", "structure", "scenes", "chapters"]
        self.step_dependencies = {
            "lore": ["parameters"],
            "structure": ["parameters", "lore"],
            "scenes": ["parameters", "lore", "structure"], 
            "chapters": ["parameters", "lore", "structure", "scenes"]
        }
        
        self.logger.info("Integrated Story Orchestrator initialized with existing GUI components")
    
    def _initialize_components(self):
        """Initialize references to your existing GUI components."""
        try:
            # Get existing components from the app
            if hasattr(self.app, 'lore_tab'):
                self.lore_component = self.app.lore_tab
                self.logger.info("Connected to existing lore component")
            
            if hasattr(self.app, 'story_structure_tab'):
                self.structure_component = self.app.story_structure_tab
                self.logger.info("Connected to existing story structure component")
            
            if hasattr(self.app, 'scene_plan_tab'):
                self.scene_component = self.app.scene_plan_tab
                self.logger.info("Connected to existing scene plan component")
            
            if hasattr(self.app, 'chapter_writing_tab'):
                self.chapter_component = self.app.chapter_writing_tab
                self.logger.info("Connected to existing chapter writing component")
            
            if hasattr(self.app, 'param_ui'):
                self.parameters_component = self.app.param_ui
                self.logger.info("Connected to existing parameters component")
                
        except Exception as e:
            self.logger.warning(f"Could not connect to all GUI components: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Return integrated workflow capabilities."""
        return [
            "execute_integrated_workflow",
            "generate_parameters",
            "generate_lore_with_existing_functions",
            "generate_structure_with_existing_functions",
            "generate_scenes_with_existing_functions",
            "generate_chapters_with_existing_functions"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for integrated workflow."""
        return ["workflow_mode", "story_parameters"]
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process an integrated workflow task using your existing functions.
        
        Args:
            task_data: Dictionary containing:
                - workflow_mode: "complete", "step_by_step", "single_step"
                - story_parameters: Story parameters for generation
                - target_steps: Optional list of steps to execute
                - use_validation: Whether to use agentic validation
                - quality_standards: Optional quality requirements
                
        Returns:
            AgentResult with integrated workflow results
        """
        if not self.validate_input(task_data):
            return AgentResult(
                success=False,
                data={},
                messages=["Invalid input data for integrated workflow"],
                metrics={}
            )
        
        workflow_mode = task_data["workflow_mode"]
        story_params = task_data["story_parameters"]
        target_steps = task_data.get("target_steps", self.workflow_steps)
        use_validation = task_data.get("use_validation", True)
        quality_standards = task_data.get("quality_standards", {})
        
        try:
            if workflow_mode == "complete":
                return self._execute_complete_integrated_workflow(
                    story_params, use_validation, quality_standards
                )
            elif workflow_mode == "step_by_step":
                return self._execute_step_by_step_workflow(
                    story_params, target_steps, use_validation, quality_standards
                )
            elif workflow_mode == "single_step":
                step = target_steps[0] if target_steps else "lore"
                return self._execute_single_step(step, story_params, use_validation)
            else:
                return self.handle_error(
                    ValueError(f"Unknown workflow mode: {workflow_mode}"),
                    "process_task"
                )
                
        except Exception as e:
            return self.handle_error(e, "process_task")
    
    def _execute_complete_integrated_workflow(self, story_params: Dict, 
                                            use_validation: bool, quality_standards: Dict) -> AgentResult:
        """Execute the complete workflow using your existing functions."""
        
        self.logger.info("Starting complete integrated workflow using existing GUI functions")
        
        completed_steps = []
        generated_files = {}
        quality_scores = {}
        consistency_reports = []
        all_recommendations = []
        
        # Execute each step in order
        for step in self.workflow_steps:
            self.logger.info(f"Executing integrated workflow step: {step}")
            
            # Check dependencies
            if not self._check_step_dependencies(step, completed_steps):
                error_msg = f"Dependencies not met for step {step}. Completed: {completed_steps}"
                self.logger.error(error_msg)
                return AgentResult(
                    success=False,
                    data={"error": error_msg},
                    messages=[error_msg],
                    metrics={}
                )
            
            # Execute the step using your existing functions
            step_result = self._execute_integrated_step(step, story_params)
            
            if not step_result["success"]:
                error_msg = f"Step {step} failed: {step_result.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return AgentResult(
                    success=False,
                    data={"error": error_msg, "completed_steps": completed_steps},
                    messages=[error_msg],
                    metrics={"steps_completed": len(completed_steps)}
                )
            
            # Record successful completion
            completed_steps.append(step)
            if step_result.get("generated_files"):
                generated_files.update(step_result["generated_files"])
            
            self.logger.info(f"Successfully completed step: {step}")
            
            # Validate with agents if enabled
            if use_validation and step != "parameters":
                validation_result = self._validate_step_output(step, step_result, quality_standards)
                
                if validation_result.get("quality_score"):
                    quality_scores[step] = validation_result["quality_score"]
                
                if validation_result.get("consistency_report"):
                    consistency_reports.append({
                        "step": step,
                        "report": validation_result["consistency_report"]
                    })
                
                if validation_result.get("recommendations"):
                    all_recommendations.extend(validation_result["recommendations"])
        
        # Generate execution summary
        summary = f"Completed integrated workflow: {' → '.join(completed_steps)}. "
        summary += f"Generated {len(generated_files)} files in {self.output_dir}. "
        if quality_scores:
            avg_quality = sum(quality_scores.values()) / len(quality_scores)
            summary += f"Average quality score: {avg_quality:.2f}."
        
        result = IntegratedWorkflowResult(
            success=True,
            completed_steps=completed_steps,
            generated_files=generated_files,
            quality_scores=quality_scores,
            consistency_reports=consistency_reports,
            recommendations=list(set(all_recommendations)),
            execution_summary=summary
        )
        
        return AgentResult(
            success=True,
            data={"workflow_result": result},
            messages=[summary],
            metrics={
                "steps_completed": len(completed_steps),
                "files_generated": len(generated_files),
                "average_quality": sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0
            }
        )
    
    def _execute_integrated_step(self, step: str, story_params: Dict) -> Dict[str, Any]:
        """Execute a single workflow step using your existing functions."""
        
        try:
            if step == "parameters":
                return self._generate_parameters(story_params)
            elif step == "lore":
                return self._generate_lore_integrated(story_params)
            elif step == "structure":
                return self._generate_structure_integrated(story_params)
            elif step == "scenes":
                return self._generate_scenes_integrated(story_params)
            elif step == "chapters":
                return self._generate_chapters_integrated(story_params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown workflow step: {step}"
                }
                
        except Exception as e:
            self.logger.error(f"Error executing integrated step {step}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_parameters(self, story_params: Dict) -> Dict[str, Any]:
        """Generate and save parameters using your existing system."""
        
        self.logger.info("Generating parameters using existing parameter system")
        
        try:
            # Set parameters in your existing parameter component
            if self.parameters_component:
                # Set the parameters in the GUI component
                if hasattr(self.parameters_component, 'genre_var'):
                    self.parameters_component.genre_var.set(story_params.get("genre", "Fantasy"))
                if hasattr(self.parameters_component, 'subgenre_var'):
                    self.parameters_component.subgenre_var.set(story_params.get("subgenre", ""))
                
                # Save parameters using existing method
                if hasattr(self.parameters_component, 'save_parameters'):
                    self.parameters_component.save_parameters()
                    self.logger.info("Parameters saved using existing save_parameters method")
            
            # Also create parameters.txt file directly
            params_file = os.path.join(self.output_dir, "parameters.txt")
            with open(params_file, 'w', encoding='utf-8') as f:
                for key, value in story_params.items():
                    f.write(f"{key}: {value}\\n")
            
            self.logger.info(f"Parameters saved to {params_file}")
            
            return {
                "success": True,
                "generated_files": {"parameters": params_file},
                "step": "parameters"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate parameters: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_lore_integrated(self, story_params: Dict) -> Dict[str, Any]:
        """Generate lore using your existing lore.py functions."""
        
        self.logger.info("Generating lore using existing lore.py functions")
        
        if not self.lore_component:
            return {
                "success": False,
                "error": "Lore component not available"
            }
        
        try:
            generated_files = {}
            
            # Set parameters for lore generation
            if hasattr(self.lore_component, 'num_chars_var'):
                self.lore_component.num_chars_var.set(story_params.get("num_characters", 5))
            if hasattr(self.lore_component, 'num_factions_var'):
                self.lore_component.num_factions_var.set(story_params.get("num_factions", 3))
            
            # Generate factions using your existing function
            self.logger.info("Calling existing generate_factions() function")
            self.lore_component.generate_factions()
            
            factions_file = os.path.join(self.output_dir, "factions.json")
            if os.path.exists(factions_file):
                generated_files["factions"] = factions_file
                self.logger.info(f"Factions generated and saved to {factions_file}")
            
            # Generate characters using your existing function
            self.logger.info("Calling existing generate_characters() function")
            self.lore_component.generate_characters()
            
            characters_file = os.path.join(self.output_dir, "characters.json")
            if os.path.exists(characters_file):
                generated_files["characters"] = characters_file
                self.logger.info(f"Characters generated and saved to {characters_file}")
            
            # Generate main lore using your existing function
            self.logger.info("Calling existing generate_lore() function")
            self.lore_component.generate_lore()
            
            lore_file = os.path.join(self.output_dir, "lore.txt")
            if os.path.exists(lore_file):
                generated_files["lore"] = lore_file
                self.logger.info(f"Lore generated and saved to {lore_file}")
            
            return {
                "success": True,
                "generated_files": generated_files,
                "step": "lore"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate lore using existing functions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_structure_integrated(self, story_params: Dict) -> Dict[str, Any]:
        """Generate story structure using your existing story_structure.py functions."""
        
        self.logger.info("Generating story structure using existing story_structure.py functions")
        
        if not self.structure_component:
            return {
                "success": False,
                "error": "Story structure component not available"
            }
        
        try:
            generated_files = {}
            
            # Call your existing story structure generation methods
            # Check what methods are available
            if hasattr(self.structure_component, 'generate_structure'):
                self.logger.info("Calling existing generate_structure() function")
                self.structure_component.generate_structure()
                
                structure_file = os.path.join(self.output_dir, "story_structure.txt")
                if os.path.exists(structure_file):
                    generated_files["structure"] = structure_file
                    self.logger.info(f"Story structure generated and saved to {structure_file}")
            
            # Check for other structure-related files
            for filename in ["plot_outline.txt", "character_arcs.txt", "story_beats.txt"]:
                filepath = os.path.join(self.output_dir, filename)
                if os.path.exists(filepath):
                    generated_files[filename.replace('.txt', '')] = filepath
                    self.logger.info(f"Found generated file: {filepath}")
            
            return {
                "success": True,
                "generated_files": generated_files,
                "step": "structure"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate structure using existing functions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_scenes_integrated(self, story_params: Dict) -> Dict[str, Any]:
        """Generate scenes using your existing scene_plan.py functions."""
        
        self.logger.info("Generating scenes using existing scene_plan.py functions")
        
        if not self.scene_component:
            return {
                "success": False,
                "error": "Scene plan component not available"
            }
        
        try:
            generated_files = {}
            
            # Call your existing scene generation methods
            if hasattr(self.scene_component, 'generate_scenes'):
                self.logger.info("Calling existing generate_scenes() function")
                self.scene_component.generate_scenes()
                
                scenes_file = os.path.join(self.output_dir, "scene_plan.txt")
                if os.path.exists(scenes_file):
                    generated_files["scenes"] = scenes_file
                    self.logger.info(f"Scenes generated and saved to {scenes_file}")
            
            # Check for other scene-related files
            for filename in ["scene_outlines.txt", "scene_summaries.json"]:
                filepath = os.path.join(self.output_dir, filename)
                if os.path.exists(filepath):
                    generated_files[filename.replace('.txt', '').replace('.json', '')] = filepath
                    self.logger.info(f"Found generated file: {filepath}")
            
            return {
                "success": True,
                "generated_files": generated_files,
                "step": "scenes"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate scenes using existing functions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_chapters_integrated(self, story_params: Dict) -> Dict[str, Any]:
        """Generate chapters using your existing chapter_writing.py functions."""
        
        self.logger.info("Generating chapters using existing chapter_writing.py functions")
        
        if not self.chapter_component:
            return {
                "success": False,
                "error": "Chapter writing component not available"
            }
        
        try:
            generated_files = {}
            
            # Generate multiple chapters
            num_chapters = story_params.get("num_chapters", 3)
            
            for chapter_num in range(1, num_chapters + 1):
                if hasattr(self.chapter_component, 'generate_chapter'):
                    self.logger.info(f"Calling existing generate_chapter() function for chapter {chapter_num}")
                    
                    # Set chapter number if the component supports it
                    if hasattr(self.chapter_component, 'chapter_number_var'):
                        self.chapter_component.chapter_number_var.set(chapter_num)
                    
                    self.chapter_component.generate_chapter()
                    
                    chapter_file = os.path.join(self.output_dir, f"chapter_{chapter_num}.txt")
                    if os.path.exists(chapter_file):
                        generated_files[f"chapter_{chapter_num}"] = chapter_file
                        self.logger.info(f"Chapter {chapter_num} generated and saved to {chapter_file}")
            
            return {
                "success": True,
                "generated_files": generated_files,
                "step": "chapters"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate chapters using existing functions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_step_output(self, step: str, step_result: Dict, quality_standards: Dict) -> Dict[str, Any]:
        """Validate step output using agentic agents."""
        
        validation_result = {
            "quality_score": None,
            "consistency_report": None,
            "recommendations": []
        }
        
        try:
            # Get content from generated files for validation
            generated_files = step_result.get("generated_files", {})
            content_for_validation = ""
            
            for file_type, filepath in generated_files.items():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        content_for_validation += f"\\n\\n=== {file_type.upper()} ===\\n{file_content}"
                except Exception as e:
                    self.logger.warning(f"Could not read {filepath} for validation: {e}")
            
            if not content_for_validation:
                return validation_result
            
            # Quality validation
            quality_result = self.quality_agent.process_task({
                "content": content_for_validation,
                "task_type": "evaluate",
                "context": {"workflow_step": step}
            })
            
            if quality_result.success:
                validation_result["quality_score"] = quality_result.metrics.get("overall_quality_score", 0)
                if "recommendations" in quality_result.data:
                    validation_result["recommendations"].extend(quality_result.data["recommendations"])
            
            # Consistency validation for narrative content
            if step in ["lore", "structure", "scenes", "chapters"]:
                consistency_result = self.consistency_agent.process_task({
                    "content": content_for_validation,
                    "task_type": "validate",
                    "context": {"workflow_step": step}
                })
                
                if consistency_result.success:
                    validation_result["consistency_report"] = consistency_result.data
                    if "recommendations" in consistency_result.data:
                        validation_result["recommendations"].extend(consistency_result.data["recommendations"])
        
        except Exception as e:
            self.logger.warning(f"Validation failed for step {step}: {e}")
        
        return validation_result
    
    def _check_step_dependencies(self, step: str, completed_steps: List[str]) -> bool:
        """Check if dependencies for a workflow step are satisfied."""
        dependencies = self.step_dependencies.get(step, [])
        return all(dep in completed_steps for dep in dependencies)
    
    def _execute_step_by_step_workflow(self, story_params: Dict, target_steps: List[str],
                                     use_validation: bool, quality_standards: Dict) -> AgentResult:
        """Execute specific workflow steps."""
        
        # Filter to valid steps only
        valid_steps = [step for step in target_steps if step in self.workflow_steps]
        
        completed_steps = []
        generated_files = {}
        
        for step in valid_steps:
            if not self._check_step_dependencies(step, completed_steps):
                return AgentResult(
                    success=False,
                    data={"error": f"Dependencies not met for {step}"},
                    messages=[f"Cannot execute {step} without dependencies: {self.step_dependencies.get(step, [])}"],
                    metrics={"steps_completed": len(completed_steps)}
                )
            
            step_result = self._execute_integrated_step(step, story_params)
            
            if step_result["success"]:
                completed_steps.append(step)
                if step_result.get("generated_files"):
                    generated_files.update(step_result["generated_files"])
            else:
                return AgentResult(
                    success=False,
                    data={"error": step_result.get("error")},
                    messages=[f"Step {step} failed"],
                    metrics={"steps_completed": len(completed_steps)}
                )
        
        return AgentResult(
            success=True,
            data={"completed_steps": completed_steps, "generated_files": generated_files},
            messages=[f"Completed steps: {', '.join(completed_steps)}"],
            metrics={"steps_completed": len(completed_steps)}
        )
    
    def _execute_single_step(self, step: str, story_params: Dict, use_validation: bool) -> AgentResult:
        """Execute a single workflow step."""
        
        step_result = self._execute_integrated_step(step, story_params)
        
        if step_result["success"]:
            return AgentResult(
                success=True,
                data=step_result,
                messages=[f"Successfully executed step: {step}"],
                metrics={"steps_completed": 1}
            )
        else:
            return AgentResult(
                success=False,
                data=step_result,
                messages=[f"Failed to execute step: {step}"],
                metrics={"steps_completed": 0}
            )
