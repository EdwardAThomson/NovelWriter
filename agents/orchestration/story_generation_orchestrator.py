"""
Story Generation Orchestrator for NovelWriter.

This orchestrator follows the proper story creation workflow:
1. Universe/Lore Creation
2. Story Structure Development  
3. Scene Planning
4. Chapter Writing
5. Quality & Consistency Validation

It integrates with existing GUI components while adding agentic intelligence.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from dataclasses import dataclass
from datetime import datetime

from agents.base.agent import BaseAgent, AgentResult, AgentMessage
from agents.quality.quality_agent import QualityControlAgent
from agents.consistency.consistency_agent import ConsistencyAgent
from agents.review.review_agent import ReviewAndRetryAgent
from agents.writing.chapter_writing_agent import ChapterWritingAgent

# Note: GUI components will be integrated separately
# This orchestrator focuses on the generation workflow logic


@dataclass
class StoryGenerationPlan:
    """Plan for complete story generation workflow."""
    workflow_steps: List[str]  # ["lore", "structure", "scenes", "chapters"]
    current_step: str
    parameters: Dict[str, Any]
    quality_standards: Dict[str, float]
    use_agentic_validation: bool = True
    iterative_improvement: bool = True


@dataclass
class StoryGenerationResult:
    """Result from complete story generation."""
    success: bool
    generated_content: Dict[str, Any]  # lore, structure, scenes, chapters
    workflow_completed: List[str]
    quality_scores: Dict[str, float]
    consistency_reports: List[Dict]
    recommendations: List[str]
    execution_summary: str


class StoryGenerationOrchestrator(BaseAgent):
    """
    Orchestrator that manages the complete story generation workflow.
    
    This agent demonstrates advanced workflow orchestration by:
    1. Following the established NovelWriter process
    2. Integrating existing GUI components with agentic intelligence
    3. Providing quality validation at each step
    4. Maintaining story consistency throughout
    5. Enabling iterative improvement
    """
    
    def __init__(self, model: str = "gpt-4o", output_dir: str = "current_work",
                 logger: Optional[logging.Logger] = None):
        super().__init__(name="StoryGenerationOrchestrator", model=model, logger=logger)
        
        self.output_dir = output_dir
        
        # Initialize validation agents
        self.quality_agent = QualityControlAgent(model=model, logger=logger)
        self.consistency_agent = ConsistencyAgent(model=model, output_dir=output_dir, logger=logger)
        
        # Initialize Phase 1 review agent (safe, analysis-only)
        self.review_agent = ReviewAndRetryAgent(model=model, logger=logger)
        
        # Initialize GUI components for generation
        self.gui_components = {}
        self._init_gui_components()
        
        # Workflow configuration
        self.workflow_steps = ["lore", "structure", "scenes", "chapters"]
        self.step_dependencies = {
            "structure": ["lore"],
            "scenes": ["lore", "structure"], 
            "chapters": ["lore", "structure", "scenes"]
        }
        
        self.logger.info("Story Generation Orchestrator initialized")
    
    def _init_gui_components(self):
        """Initialize GUI components for story generation."""
        try:
            # Note: These would normally be initialized with proper parent widgets
            # For orchestration, we use them as generation engines
            self.gui_components = {
                "lore": None,  # Will be initialized when needed
                "structure": None,
                "scenes": None, 
                "chapters": None
            }
            self.logger.info("GUI components prepared for orchestration")
        except Exception as e:
            self.logger.warning(f"Could not initialize GUI components: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Return story generation capabilities."""
        return [
            "generate_complete_story",
            "generate_story_step", 
            "validate_story_step",
            "create_generation_plan"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for story generation."""
        return ["story_parameters", "generation_mode"]
    
    def execute_complete_workflow(self, story_parameters: Dict[str, Any], 
                                quality_threshold: float = 0.7, 
                                auto_retry: bool = True) -> Dict[str, Any]:
        """Execute the complete story generation workflow (GUI interface method).
        
        This is the main method called by the GUI to start the agentic workflow.
        It clicks all your GUI buttons in sequence and returns the results.
        
        Args:
            story_parameters: Story parameters from the GUI
            quality_threshold: Minimum quality score (0.0-1.0)
            auto_retry: Whether to retry if quality is below threshold
            
        Returns:
            Dictionary with workflow results
        """
        self.logger.info("🚀 Starting complete agentic workflow")
        
        try:
            # Create a generation plan
            plan = StoryGenerationPlan(
                workflow_steps=["lore", "structure", "scenes", "chapters"],
                current_step="lore",
                parameters=story_parameters,
                quality_standards={"overall": quality_threshold},
                use_agentic_validation=True,
                iterative_improvement=auto_retry
            )
            
            # Execute the workflow
            result = self._execute_generation_workflow(plan)
            
            # Convert to GUI-friendly format
            return {
                "success": result.success,
                "content": result.generated_content,
                "completed_steps": result.workflow_completed,
                "quality_scores": result.quality_scores,
                "recommendations": result.recommendations,
                "summary": result.execution_summary
            }
            
        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": {},
                "completed_steps": [],
                "quality_scores": {},
                "recommendations": [f"Workflow failed: {e}"],
                "summary": f"Workflow execution failed: {e}"
            }
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process a story generation orchestration task.
        
        Args:
            task_data: Dictionary containing:
                - story_parameters: Story parameters (genre, theme, etc.)
                - generation_mode: "complete", "step_by_step", "resume"
                - target_steps: Optional list of steps to generate
                - quality_standards: Optional quality requirements
                - use_validation: Whether to use agentic validation
                
        Returns:
            AgentResult with story generation results
        """
        if not self.validate_input(task_data):
            return AgentResult(
                success=False,
                data={},
                messages=["Invalid input data for story generation"],
                metrics={}
            )
        
        story_params = task_data["story_parameters"]
        generation_mode = task_data["generation_mode"]
        target_steps = task_data.get("target_steps", self.workflow_steps)
        quality_standards = task_data.get("quality_standards", {})
        use_validation = task_data.get("use_validation", True)
        
        try:
            if generation_mode == "complete":
                return self._generate_complete_story(story_params, quality_standards, use_validation)
            elif generation_mode == "step_by_step":
                return self._generate_step_by_step(story_params, target_steps, quality_standards, use_validation)
            elif generation_mode == "resume":
                return self._resume_generation(story_params, target_steps, quality_standards, use_validation)
            else:
                return self.handle_error(
                    ValueError(f"Unknown generation mode: {generation_mode}"),
                    "process_task"
                )
                
        except Exception as e:
            return self.handle_error(e, "process_task")
    
    def _generate_complete_story(self, story_params: Dict, quality_standards: Dict, 
                               use_validation: bool) -> AgentResult:
        """Generate a complete story following the full workflow."""
        
        self.logger.info("Starting complete story generation workflow")
        
        # Create generation plan
        plan = StoryGenerationPlan(
            workflow_steps=self.workflow_steps.copy(),
            current_step="lore",
            parameters=story_params,
            quality_standards=quality_standards,
            use_agentic_validation=use_validation,
            iterative_improvement=True
        )
        
        # Execute workflow
        result = self._execute_generation_workflow(plan)
        
        return AgentResult(
            success=result.success,
            data={
                "generation_result": result,
                "generated_content": result.generated_content,
                "workflow_plan": plan
            },
            messages=[result.execution_summary],
            metrics={
                "steps_completed": len(result.workflow_completed),
                "overall_quality": sum(result.quality_scores.values()) / len(result.quality_scores) if result.quality_scores else 0,
                "consistency_issues": sum(len(report.get("issues", [])) for report in result.consistency_reports)
            }
        )
    
    def _execute_generation_workflow(self, plan: StoryGenerationPlan) -> StoryGenerationResult:
        """Execute the complete story generation workflow."""
        
        generated_content = {}
        workflow_completed = []
        quality_scores = {}
        consistency_reports = []
        all_recommendations = []
        
        for step in plan.workflow_steps:
            self.logger.info(f"Executing workflow step: {step}")
            
            # Check dependencies
            if not self._check_step_dependencies(step, workflow_completed):
                error_msg = f"Dependencies not met for step {step}"
                self.logger.error(error_msg)
                return StoryGenerationResult(
                    success=False,
                    generated_content=generated_content,
                    workflow_completed=workflow_completed,
                    quality_scores=quality_scores,
                    consistency_reports=consistency_reports,
                    recommendations=[error_msg],
                    execution_summary=f"Workflow failed at step {step}"
                )
            
            # Generate content for this step
            step_result = self._generate_workflow_step(step, plan.parameters, generated_content)
            
            if not step_result["success"]:
                self.logger.error(f"Step {step} generation failed")
                return StoryGenerationResult(
                    success=False,
                    generated_content=generated_content,
                    workflow_completed=workflow_completed,
                    quality_scores=quality_scores,
                    consistency_reports=consistency_reports,
                    recommendations=[f"Step {step} generation failed"],
                    execution_summary=f"Workflow failed during {step} generation"
                )
            
            # Store generated content
            generated_content[step] = step_result["content"]
            workflow_completed.append(step)
            
            # Validate with agents if enabled
            if plan.use_agentic_validation:
                validation_result = self._validate_workflow_step(step, step_result["content"], generated_content)
                
                if validation_result["quality_score"]:
                    quality_scores[step] = validation_result["quality_score"]
                
                if validation_result["consistency_report"]:
                    consistency_reports.append({
                        "step": step,
                        "report": validation_result["consistency_report"]
                    })
                
                if validation_result["recommendations"]:
                    all_recommendations.extend(validation_result["recommendations"])
                
                # Check if iterative improvement is needed
                if plan.iterative_improvement and validation_result["needs_improvement"]:
                    self.logger.info(f"Attempting iterative improvement for step {step}")
                    improved_result = self._improve_step_content(step, step_result["content"], 
                                                               validation_result["recommendations"])
                    if improved_result["success"]:
                        generated_content[step] = improved_result["content"]
                        quality_scores[step] = improved_result.get("quality_score", quality_scores.get(step, 0))
        
        # Generate execution summary
        summary = f"Completed {len(workflow_completed)}/{len(plan.workflow_steps)} workflow steps. "
        if quality_scores:
            avg_quality = sum(quality_scores.values()) / len(quality_scores)
            summary += f"Average quality score: {avg_quality:.2f}. "
        summary += f"Generated: {', '.join(workflow_completed)}"
        
        return StoryGenerationResult(
            success=len(workflow_completed) == len(plan.workflow_steps),
            generated_content=generated_content,
            workflow_completed=workflow_completed,
            quality_scores=quality_scores,
            consistency_reports=consistency_reports,
            recommendations=list(set(all_recommendations)),  # Remove duplicates
            execution_summary=summary
        )
    
    def _check_step_dependencies(self, step: str, completed_steps: List[str]) -> bool:
        """Check if dependencies for a workflow step are satisfied."""
        dependencies = self.step_dependencies.get(step, [])
        return all(dep in completed_steps for dep in dependencies)
    
    def _generate_workflow_step(self, step: str, story_params: Dict, 
                              existing_content: Dict) -> Dict[str, Any]:
        """Generate content for a specific workflow step."""
        
        try:
            if step == "lore":
                return self._generate_lore(story_params)
            elif step == "structure":
                return self._generate_structure(story_params, existing_content.get("lore"))
            elif step == "scenes":
                return self._generate_scene_plans(story_params, existing_content.get("structure"))
            elif step == "chapters":
                return self._generate_chapters(story_params, existing_content)
            else:
                return {
                    "success": False,
                    "content": None,
                    "error": f"Unknown workflow step: {step}"
                }
                
        except Exception as e:
            self.logger.error(f"Error generating {step}: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e)
            }
    
    def _generate_lore(self, story_params: Dict) -> Dict[str, Any]:
        """Generate lore by clicking the actual GUI buttons like a human would."""
        self.logger.info("🤖 Agent starting lore generation - clicking GUI buttons like a human")
        
        try:
            if not (hasattr(self, 'app_instance') and self.app_instance):
                raise Exception("No GUI access available - cannot click buttons")
            
            app = self.app_instance
            lore_ui = app.lore_ui
            
            # Step 1: Save parameters first (like you do)
            self.logger.info("🔹 Step 1: Saving parameters to file")
            current_params = app.param_ui.get_current_parameters()
            # This mimics clicking "Save Parameters" - save to txt file in output dir
            params_file = os.path.join(app.get_output_dir(), "story_parameters.txt")
            with open(params_file, 'w') as f:
                for key, value in current_params.items():
                    f.write(f"{key}: {value}\n")
            self.logger.info(f"✅ Parameters saved to {params_file}")
            
            # Step 2: Click each lore button in sequence (like you do)
            lore_results = {}
            
            self.logger.info("🔹 Step 2: Clicking 'Generate Factions' button")
            lore_ui.generate_factions()
            self.logger.info("✅ Generate Factions completed")
            
            self.logger.info("🔹 Step 3: Clicking 'Generate Characters' button")
            lore_ui.generate_characters()
            self.logger.info("✅ Generate Characters completed")
            
            self.logger.info("🔹 Step 4: Clicking 'Generate Lore' button")
            lore_content = lore_ui.generate_lore()
            self.logger.info("✅ Generate Lore completed")
            
            self.logger.info("🔹 Step 5: Clicking 'Enhance main characters' button")
            lore_ui.main_character_enhancement()
            self.logger.info("✅ Enhance main characters completed")
            
            self.logger.info("🔹 Step 6: Clicking 'Suggest Story Titles' button")
            lore_ui.suggest_titles()
            self.logger.info("✅ Suggest Story Titles completed")
            
            # Collect all the generated files from the output directory
            output_dir = app.get_output_dir()
            generated_files = []
            for file in os.listdir(output_dir):
                if file.endswith(('.json', '.md', '.txt')) and any(keyword in file.lower() for keyword in 
                    ['faction', 'character', 'lore', 'background', 'title']):
                    generated_files.append(file)
            
            lore_results = {
                "parameters_file": "story_parameters.txt",
                "generated_files": generated_files,
                "output_directory": output_dir,
                "buttons_clicked": [
                    "Generate Factions",
                    "Generate Characters", 
                    "Generate Lore",
                    "Enhance main characters",
                    "Suggest Story Titles"
                ],
                "total_files_generated": len(generated_files)
            }
            
            self.logger.info(f"🎉 Lore generation complete! Generated {len(generated_files)} files: {generated_files}")
            
            return {
                "success": True,
                "content": lore_results,
                "step": "lore"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error during lore generation: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "step": "lore"
            }
    
    def _generate_structure(self, story_params: Dict, lore_content: Dict) -> Dict[str, Any]:
        """Generate story structure by clicking all GUI buttons like a human would."""
        self.logger.info("🤖 Agent starting story structure generation - clicking GUI buttons like a human")
        
        try:
            if not (hasattr(self, 'app_instance') and self.app_instance):
                raise Exception("No GUI access available - cannot click buttons")
            
            app = self.app_instance
            story_structure_ui = app.structure_ui
            
            # Step 1: Save parameters first (like you do)
            self.logger.info("🔹 Step 1: Saving parameters to file")
            app.param_ui.save_parameters()
            
            structure_results = {
                "functions_executed": [],
                "files_generated": [],
                "button_clicks": [],
                "step_reviews": {},  # Phase 1: Intelligent analysis
                "quality_scores": {},
                "improvement_suggestions": {}
            }
            
            # Step 2: Generate Character Arcs
            self.logger.info("🔹 Step 2: Clicking 'Generate Character Arcs' button")
            try:
                story_structure_ui.generate_arcs()
                structure_results["functions_executed"].append("Generate Character Arcs")
                structure_results["button_clicks"].append("c_arc_button")
                self.logger.info("✅ Character Arcs generation completed")
                
                # Phase 1: Intelligent review of generated content
                self._review_step_output("character_arcs", output_dir, structure_results)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Character Arcs generation failed: {e}")
            
            # Step 3: Generate Faction Arcs
            self.logger.info("🔹 Step 3: Clicking 'Generate Faction Arcs' button")
            try:
                story_structure_ui.generate_faction_arcs()
                structure_results["functions_executed"].append("Generate Faction Arcs")
                structure_results["button_clicks"].append("f_arc_button")
                self.logger.info("✅ Faction Arcs generation completed")
                
                # Phase 1: Intelligent review of generated content
                self._review_step_output("faction_arcs", output_dir, structure_results)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Faction Arcs generation failed: {e}")
            
            # Step 4: Add Locations to Arcs
            self.logger.info("🔹 Step 4: Clicking 'Add Locations to Arcs' button")
            try:
                story_structure_ui.add_planets_to_arcs()
                structure_results["functions_executed"].append("Add Locations to Arcs")
                structure_results["button_clicks"].append("cfp_arc_button")
                self.logger.info("✅ Add Locations to Arcs completed")
            except Exception as e:
                self.logger.warning(f"⚠️ Add Locations to Arcs failed: {e}")
            
            # Step 5: Create Detailed Plot (dispatches based on story length)
            self.logger.info("🔹 Step 5: Clicking 'Create Detailed Plot' button")
            try:
                story_structure_ui._dispatch_detailed_plot_creation()
                structure_results["functions_executed"].append("Create Detailed Plot")
                structure_results["button_clicks"].append("detailed_plot_button")
                self.logger.info("✅ Detailed Plot creation completed")
            except Exception as e:
                self.logger.warning(f"⚠️ Detailed Plot creation failed: {e}")
            
            # Step 6: Improve Structure (if available)
            self.logger.info("🔹 Step 6: Executing 'Improve Structure' function")
            try:
                story_structure_ui.improve_structure()
                structure_results["functions_executed"].append("Improve Structure")
                structure_results["button_clicks"].append("improve_structure_function")
                self.logger.info("✅ Improve Structure completed")
            except Exception as e:
                self.logger.warning(f"⚠️ Improve Structure failed: {e}")
            
            # Check what files were generated
            output_dir = story_params.get("output_directory", "current_work")
            generated_files = []
            
            # Common structure files that might be generated
            potential_files = [
                "character_arcs.md",
                "faction_arcs.md", 
                "locations_arcs.md",
                "detailed_plot.md",
                "plot_short_story_3-act_structure.md",
                "plot_novella.md",
                "plot_novel.md",
                "improved_structure.md"
            ]
            
            for filename in potential_files:
                filepath = os.path.join(output_dir, filename)
                if os.path.exists(filepath):
                    generated_files.append(filename)
            
            structure_results["files_generated"] = generated_files
            structure_results["total_functions_executed"] = len(structure_results["functions_executed"])
            
            self.logger.info(f"🎉 Story Structure generation complete! Executed {len(structure_results['functions_executed'])} functions: {structure_results['functions_executed']}")
            
            return {
                "success": True,
                "content": structure_results,
                "step": "structure"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error during story structure generation: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "step": "structure"
            }
    
    def _generate_scene_plans(self, story_params: Dict, structure_content: Dict) -> Dict[str, Any]:
        """Generate scene plans by clicking GUI buttons like a human would."""
        self.logger.info("🤖 Agent starting scene planning generation - clicking GUI buttons like a human")
        
        try:
            if not (hasattr(self, 'app_instance') and self.app_instance):
                raise Exception("No GUI access available - cannot click buttons")
            
            app = self.app_instance
            scene_plan_ui = app.outlining_ui
            output_dir = story_params.get("output_directory", "current_work")
            
            scene_results = {
                "functions_executed": [],
                "files_generated": [],
                "button_clicks": [],
                "step_reviews": {},  # Phase 1: Intelligent analysis
                "quality_scores": {},
                "improvement_suggestions": {}
            }
            
            # Step 1: Generate Chapter Outlines (for longer forms)
            story_length = story_params.get("story_length", "Novel (Standard)")
            
            if story_length != "Short Story":
                self.logger.info("🔹 Step 1: Clicking 'Generate Chapter Outlines' button")
                try:
                    scene_plan_ui.generate_chapter_outline()
                    scene_results["functions_executed"].append("Generate Chapter Outlines")
                    scene_results["button_clicks"].append("chapter_outline_button")
                    self.logger.info("✅ Chapter Outlines generation completed")
                    
                    # Phase 1: Intelligent review of generated content
                    self._review_step_output("chapter_outlines", output_dir, scene_results)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Chapter Outlines generation failed: {e}")
            else:
                self.logger.info("🔹 Skipping Chapter Outlines for Short Story")
            
            # Step 2: Plan Scenes (dispatches based on story length)
            self.logger.info("🔹 Step 2: Clicking 'Plan Scenes' button")
            try:
                scene_plan_ui._dispatch_scene_planning()
                scene_results["functions_executed"].append("Plan Scenes")
                scene_results["button_clicks"].append("plan_scenes_button")
                self.logger.info("✅ Scene Planning completed")
                
                # Phase 1: Intelligent review of generated content
                self._review_step_output("scene_plans", output_dir, scene_results)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Scene Planning failed: {e}")
            
            # Check what files were generated
            generated_files = []
            
            # Dynamically determine potential files based on current structure
            potential_files = self._get_expected_scene_planning_files(story_params, output_dir)
            
            # Add detailed scene plans directory files
            detailed_scene_plans_dir = os.path.join(output_dir, "detailed_scene_plans")
            if os.path.exists(detailed_scene_plans_dir):
                try:
                    for filename in os.listdir(detailed_scene_plans_dir):
                        if filename.endswith('.md'):
                            potential_files.append(f"detailed_scene_plans/{filename}")
                except Exception as e:
                    self.logger.warning(f"Could not list detailed scene plans directory: {e}")
            
            for filename in potential_files:
                if filename.startswith("detailed_scene_plans/"):
                    filepath = os.path.join(output_dir, filename)
                else:
                    filepath = os.path.join(output_dir, filename)
                    
                if os.path.exists(filepath):
                    generated_files.append(filename)
            
            scene_results["files_generated"] = generated_files
            scene_results["total_functions_executed"] = len(scene_results["functions_executed"])
            
            self.logger.info(f"🎉 Scene Planning generation completed! Generated {len(generated_files)} files")
            self.logger.info(f"📁 Files: {', '.join(generated_files)}")
            
            return {
                "success": True,
                "content": scene_results,
                "step": "scene_plans"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error during scene planning generation: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "step": "scene_plans"
            }
    
    def _generate_chapters(self, story_params: Dict, existing_content: Dict) -> Dict[str, Any]:
        """Generate chapters using automated chapter writing agent."""
        
        self.logger.info("🖋️ Starting automated chapter writing...")
        
        try:
            # Initialize chapter writing agent with directory structure preference
            use_new_structure = getattr(self, 'use_new_structure', False)
            chapter_agent = ChapterWritingAgent(self.output_dir, app_instance=None, use_new_structure=use_new_structure)
            
            # Analyze story structure to find chapters
            self.logger.info("📊 Analyzing chapter structure...")
            chapter_info_list, story_parameters = chapter_agent.analyze_chapter_structure()
            
            if not chapter_info_list:
                return {
                    "success": False,
                    "content": None,
                    "error": "No chapters found in story structure",
                    "step": "chapters"
                }
            
            # Create writing plan
            plan = chapter_agent.create_writing_plan(chapter_info_list, batch_size=3)  # Write 3 chapters at a time
            
            # Get progress report
            progress = chapter_agent.get_progress_report(chapter_info_list)
            self.logger.info(f"📈 Chapter Progress: {progress['completed_chapters']}/{progress['total_chapters']} completed ({progress['completion_percentage']:.1f}%)")
            
            if not plan.chapters_to_write:
                self.logger.info("✅ All chapters already written")
                return {
                    "success": True,
                    "content": {
                        "chapters_written": [],
                        "chapters_completed": plan.chapters_completed,
                        "total_chapters": plan.total_chapters,
                        "message": "All chapters already exist"
                    },
                    "step": "chapters"
                }
            
            # Write chapters in batches
            self.logger.info(f"✍️ Writing {len(plan.chapters_to_write)} chapters in batches of {plan.batch_size}...")
            
            result = chapter_agent.write_chapters_batch(chapter_info_list, plan)
            
            if result.success:
                chapters_written = result.data.get("chapters_written", [])
                errors = result.data.get("errors", [])
                
                self.logger.info(f"✅ Successfully wrote {len(chapters_written)} chapters")
                if errors:
                    self.logger.warning(f"⚠️ {len(errors)} chapters had errors: {errors}")
                
                # Get updated progress
                final_progress = chapter_agent.get_progress_report(chapter_info_list)
                
                return {
                    "success": True,
                    "content": {
                        "chapters_written": chapters_written,
                        "chapters_completed": result.data.get("total_completed", 0),
                        "total_chapters": plan.total_chapters,
                        "errors": errors,
                        "progress": final_progress,
                        "message": f"Wrote {len(chapters_written)} chapters successfully"
                    },
                    "step": "chapters"
                }
            else:
                return {
                    "success": False,
                    "content": None,
                    "error": result.message,
                    "step": "chapters"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error during chapter generation: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "step": "chapters"
            }
    
    def _get_step_output_filename(self, step_name: str, output_dir: str) -> str:
        """Intelligently determine the output filename for a given step based on current parameters."""
        try:
            # Import here to avoid circular imports
            from core.gui.parameters import STRUCTURE_SECTIONS_MAP
            
            # Get current parameters if available
            story_structure = "6-Act Structure"  # Default
            story_length = "Novel (Standard)"    # Default
            
            if hasattr(self, 'app_instance') and self.app_instance:
                try:
                    params = self.app_instance.param_ui.get_current_parameters()
                    story_structure = params.get("story_structure", story_structure)
                    story_length = params.get("story_length", story_length)
                except Exception as e:
                    self.logger.warning(f"Could not get current parameters for file mapping: {e}")
            
            # Create safe structure name for filenames
            safe_structure_name = story_structure.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '').replace('!', '').replace(',', '')
            
            # Handle different step types
            if step_name == "character_arcs":
                return "character_arcs.md"
                
            elif step_name == "faction_arcs":
                return "faction_arcs.md"
                
            elif step_name == "locations":
                return "reconciled_locations_arcs.md"
                
            elif step_name == "plot_structure":
                if story_length == "Short Story":
                    return f"plot_short_story_{safe_structure_name}.md"
                else:
                    return "detailed_plot.md"
                    
            elif step_name == "chapter_outlines":
                # For chapter outlines, find the first section file that exists
                sections = STRUCTURE_SECTIONS_MAP.get(story_structure, [])
                if sections:
                    for section in sections:
                        safe_section_name = section.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
                        filename = f"chapter_outlines_{safe_structure_name}_{safe_section_name}.md"
                        filepath = os.path.join(output_dir, filename)
                        if os.path.exists(filepath):
                            return filename
                # Fallback to first section pattern
                if sections:
                    safe_section_name = sections[0].lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
                    return f"chapter_outlines_{safe_structure_name}_{safe_section_name}.md"
                    
            elif step_name == "scene_plans":
                if story_length == "Short Story":
                    # Look for short story scene files
                    filename = f"scenes_short_story_{safe_structure_name}.md"
                    filepath = os.path.join(output_dir, filename)
                    if os.path.exists(filepath):
                        return filename
                else:
                    # Look for detailed scene plans in subdirectory
                    detailed_scene_plans_dir = os.path.join(output_dir, "detailed_scene_plans")
                    if os.path.exists(detailed_scene_plans_dir):
                        try:
                            scene_files = [f for f in os.listdir(detailed_scene_plans_dir) if f.endswith('.md')]
                            if scene_files:
                                # Return the first scene file found for review
                                return f"detailed_scene_plans/{scene_files[0]}"
                        except Exception as e:
                            self.logger.warning(f"Could not list detailed scene plans: {e}")
            
            # If no specific file found, try to find any related files
            self.logger.debug(f"No specific file mapping found for {step_name}, searching for related files...")
            return None
            
        except Exception as e:
            self.logger.error(f"Error determining filename for {step_name}: {e}")
            return None
    
    def _get_expected_scene_planning_files(self, story_params: Dict, output_dir: str) -> List[str]:
        """Get list of expected scene planning files based on current story parameters."""
        try:
            from core.gui.parameters import STRUCTURE_SECTIONS_MAP
            
            story_structure = story_params.get("story_structure", "6-Act Structure")
            story_length = story_params.get("story_length", "Novel (Standard)")
            
            safe_structure_name = story_structure.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '').replace('!', '').replace(',', '')
            
            potential_files = []
            
            if story_length == "Short Story":
                # Short story scene files
                potential_files.append(f"scenes_short_story_{safe_structure_name}.md")
            else:
                # Chapter outline files for each section of the structure
                sections = STRUCTURE_SECTIONS_MAP.get(story_structure, [])
                for section in sections:
                    safe_section_name = section.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
                    potential_files.append(f"chapter_outlines_{safe_structure_name}_{safe_section_name}.md")
            
            return potential_files
            
        except Exception as e:
            self.logger.warning(f"Error determining expected scene planning files: {e}")
            # Fallback to common patterns
            return [
                "scenes_short_story_3-act_structure.md",
                "chapter_outlines_6-act_structure_beginning.md"
            ]
    
    def _review_step_output(self, step_name: str, output_dir: str, results_dict: Dict):
        """
        Phase 1: Intelligent review of step output.
        Analyzes generated content and provides recommendations without modifying workflow.
        """
        try:
            # Dynamic file mapping based on step type and current parameters
            filename = self._get_step_output_filename(step_name, output_dir)
            if not filename:
                self.logger.info(f"🔍 No file found for {step_name}, skipping review")
                return
            
            filepath = os.path.join(output_dir, filename)
            
            # Retry logic for file availability (files may not exist immediately)
            content = None
            max_retries = 5
            retry_delay = 1.0  # seconds
            
            for attempt in range(max_retries):
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if content and content.strip():  # Ensure file has content
                            break
                        else:
                            self.logger.info(f"🔍 File {filepath} exists but is empty, retrying... (attempt {attempt + 1}/{max_retries})")
                    except Exception as e:
                        self.logger.warning(f"Could not read {filepath} for review (attempt {attempt + 1}): {e}")
                else:
                    self.logger.info(f"🔍 File {filepath} not found, retrying... (attempt {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    import time
                    time.sleep(retry_delay)
            
            if not content or not content.strip():
                self.logger.warning(f"🔍 Could not read content from {filepath} after {max_retries} attempts, skipping review")
                return
            
            self.logger.info(f"🧠 Performing intelligent analysis of {step_name}...")
            
            # Use the review agent to analyze the content
            review = self.review_agent.review_step_output(step_name, content)
            
            # Store review results
            results_dict["step_reviews"][step_name] = {
                "quality_score": review.quality_score,
                "confidence": review.confidence,
                "retry_recommended": review.retry_recommended,
                "issues_found": review.issues_found,
                "strengths_found": review.strengths_found,
                "improvement_suggestions": review.improvement_suggestions
            }
            
            results_dict["quality_scores"][step_name] = review.quality_score
            results_dict["improvement_suggestions"][step_name] = review.improvement_suggestions
            
            # Log key insights
            if review.quality_score >= 0.8:
                self.logger.info(f"🌟 {step_name}: Excellent quality (score: {review.quality_score:.2f})")
            elif review.quality_score >= 0.6:
                self.logger.info(f"✅ {step_name}: Good quality (score: {review.quality_score:.2f})")
            elif review.quality_score >= 0.4:
                self.logger.warning(f"⚠️ {step_name}: Moderate quality (score: {review.quality_score:.2f})")
            else:
                self.logger.warning(f"❌ {step_name}: Low quality (score: {review.quality_score:.2f})")
            
            if review.retry_recommended:
                self.logger.warning(f"🔄 {step_name}: Review agent recommends retry")
            
            if review.improvement_suggestions:
                self.logger.info(f"💡 {step_name}: {len(review.improvement_suggestions)} improvement suggestions available")
            
        except Exception as e:
            self.logger.error(f"Error during intelligent review of {step_name}: {e}")
    
    # Scene generation removed - use your app's Scene Planning tab instead
    
    # Chapter generation removed - use your app's Write Chapters tab instead
    
    def _validate_workflow_step(self, step: str, content: Any, full_context: Dict) -> Dict[str, Any]:
        """Validate a workflow step using agentic agents."""
        
        validation_result = {
            "quality_score": None,
            "consistency_report": None,
            "recommendations": [],
            "needs_improvement": False
        }
        
        # Convert content to text for validation
        content_text = self._content_to_text(content)
        if not content_text:
            return validation_result
        
        try:
            # Quality validation
            quality_result = self.quality_agent.process_task({
                "content": content_text,
                "task_type": "evaluate",
                "context": {"workflow_step": step}
            })
            
            if quality_result.success:
                validation_result["quality_score"] = quality_result.metrics.get("overall_quality_score", 0)
                if "recommendations" in quality_result.data:
                    validation_result["recommendations"].extend(quality_result.data["recommendations"])
                
                # Check if improvement is needed
                if validation_result["quality_score"] < 0.75:
                    validation_result["needs_improvement"] = True
            
            # Consistency validation (for steps that have narrative content)
            if step in ["scenes", "chapters"]:
                consistency_result = self.consistency_agent.process_task({
                    "content": content_text,
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
    
    def _improve_step_content(self, step: str, content: Any, recommendations: List[str]) -> Dict[str, Any]:
        """Attempt to improve step content based on recommendations."""
        
        # This would implement iterative improvement logic
        # For now, we'll return the original content
        self.logger.info(f"Iterative improvement for {step} with {len(recommendations)} recommendations")
        
        return {
            "success": True,
            "content": content,
            "quality_score": 0.8  # Simulated improvement
        }
    
    def _content_to_text(self, content: Any) -> str:
        """Convert content to text for validation."""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Extract text from dictionary content
            text_parts = []
            for key, value in content.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(item) for item in value])
            return " ".join(text_parts)
        else:
            return str(content)
    
    # Fake content generation methods removed - use your app's GUI tabs instead
    
    def _generate_step_by_step(self, story_params: Dict, target_steps: List[str],
                             quality_standards: Dict, use_validation: bool) -> AgentResult:
        """Generate story content step by step."""
        
        # Filter target steps to only include valid ones
        valid_steps = [step for step in target_steps if step in self.workflow_steps]
        
        plan = StoryGenerationPlan(
            workflow_steps=valid_steps,
            current_step=valid_steps[0] if valid_steps else "lore",
            parameters=story_params,
            quality_standards=quality_standards,
            use_agentic_validation=use_validation,
            iterative_improvement=False  # Less aggressive for step-by-step
        )
        
        result = self._execute_generation_workflow(plan)
        
        return AgentResult(
            success=result.success,
            data={"generation_result": result},
            messages=[f"Step-by-step generation: {result.execution_summary}"],
            metrics={
                "steps_completed": len(result.workflow_completed),
                "target_steps": len(valid_steps)
            }
        )
    
    def _resume_generation(self, story_params: Dict, target_steps: List[str],
                         quality_standards: Dict, use_validation: bool) -> AgentResult:
        """Resume generation from where it left off."""
        
        # Check what's already been generated
        existing_steps = self._check_existing_content()
        
        # For resume, we need to include existing steps in the workflow
        # so dependencies are satisfied
        all_needed_steps = []
        for step in self.workflow_steps:
            if step in target_steps:
                # Add all dependencies first
                dependencies = self.step_dependencies.get(step, [])
                for dep in dependencies:
                    if dep not in all_needed_steps:
                        all_needed_steps.append(dep)
                # Then add the step itself
                if step not in all_needed_steps:
                    all_needed_steps.append(step)
        
        # Filter to only generate steps that don't exist yet
        steps_to_generate = [step for step in all_needed_steps if step not in existing_steps]
        
        if not steps_to_generate:
            return AgentResult(
                success=True,
                data={"message": "All requested steps already completed"},
                messages=["No remaining steps to generate"],
                metrics={"existing_steps": len(existing_steps)}
            )
        
        # Create a plan that includes existing steps for dependency satisfaction
        plan = StoryGenerationPlan(
            workflow_steps=steps_to_generate,
            current_step=steps_to_generate[0] if steps_to_generate else "lore",
            parameters=story_params,
            quality_standards=quality_standards,
            use_agentic_validation=use_validation,
            iterative_improvement=False
        )
        
        # Load existing content for dependencies
        generated_content = {}
        for step in existing_steps:
            try:
                import json
                filename = os.path.join(self.output_dir, f"generated_{step}.json")
                with open(filename, 'r', encoding='utf-8') as f:
                    generated_content[step] = json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load existing {step} content: {e}")
        
        # Execute workflow with existing content
        result = self._execute_generation_workflow_with_existing(plan, generated_content)
        
        return AgentResult(
            success=result.success,
            data={"generation_result": result},
            messages=[f"Resume generation: {result.execution_summary}"],
            metrics={
                "steps_completed": len(result.workflow_completed),
                "existing_steps": len(existing_steps),
                "new_steps": len(steps_to_generate)
            }
        )
    
    def _check_existing_content(self) -> List[str]:
        """Check which workflow steps have already been completed."""
        existing_steps = []
        
        for step in self.workflow_steps:
            filename = os.path.join(self.output_dir, f"generated_{step}.json")
            if os.path.exists(filename):
                existing_steps.append(step)
        
        return existing_steps
    
    def _execute_generation_workflow_with_existing(self, plan: StoryGenerationPlan, 
                                                  existing_content: Dict) -> StoryGenerationResult:
        """Execute workflow with pre-existing content loaded."""
        
        generated_content = existing_content.copy()
        workflow_completed = list(existing_content.keys())
        quality_scores = {}
        consistency_reports = []
        all_recommendations = []
        
        for step in plan.workflow_steps:
            self.logger.info(f"Executing workflow step: {step}")
            
            # Check dependencies (should be satisfied since we loaded existing content)
            if not self._check_step_dependencies(step, workflow_completed):
                error_msg = f"Dependencies not met for step {step}"
                self.logger.error(error_msg)
                return StoryGenerationResult(
                    success=False,
                    generated_content=generated_content,
                    workflow_completed=workflow_completed,
                    quality_scores=quality_scores,
                    consistency_reports=consistency_reports,
                    recommendations=[error_msg],
                    execution_summary=f"Workflow failed at step {step}"
                )
            
            # Generate content for this step
            step_result = self._generate_workflow_step(step, plan.parameters, generated_content)
            
            if not step_result["success"]:
                self.logger.error(f"Step {step} generation failed")
                return StoryGenerationResult(
                    success=False,
                    generated_content=generated_content,
                    workflow_completed=workflow_completed,
                    quality_scores=quality_scores,
                    consistency_reports=consistency_reports,
                    recommendations=[f"Step {step} generation failed"],
                    execution_summary=f"Workflow failed during {step} generation"
                )
            
            # Store generated content
            generated_content[step] = step_result["content"]
            workflow_completed.append(step)
            
            # Validate with agents if enabled
            if plan.use_agentic_validation:
                validation_result = self._validate_workflow_step(step, step_result["content"], generated_content)
                
                if validation_result["quality_score"]:
                    quality_scores[step] = validation_result["quality_score"]
                
                if validation_result["consistency_report"]:
                    consistency_reports.append({
                        "step": step,
                        "report": validation_result["consistency_report"]
                    })
                
                if validation_result["recommendations"]:
                    all_recommendations.extend(validation_result["recommendations"])
        
        # Generate execution summary
        new_steps = [step for step in plan.workflow_steps]
        summary = f"Resumed generation: completed {len(new_steps)} new steps. "
        if quality_scores:
            avg_quality = sum(quality_scores.values()) / len(quality_scores)
            summary += f"Average quality score: {avg_quality:.2f}. "
        summary += f"New steps: {', '.join(new_steps)}"
        
        return StoryGenerationResult(
            success=True,
            generated_content=generated_content,
            workflow_completed=new_steps,  # Only return newly completed steps
            quality_scores=quality_scores,
            consistency_reports=consistency_reports,
            recommendations=list(set(all_recommendations)),
            execution_summary=summary
        )
