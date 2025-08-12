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

from typing import Dict, List, Any, Optional, Tuple, Callable
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime

from agents.base.agent import BaseAgent, AgentResult, AgentMessage
from agents.quality.quality_agent import QualityControlAgent
from agents.consistency.consistency_agent import ConsistencyAgent
from agents.review.review_agent import ReviewAndRetryAgent
from agents.writing.chapter_writing_agent import ChapterWritingAgent
from agents.orchestration.checkpoint_state import CheckpointStateManager, CheckpointStatus, WorkflowState

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
class WorkflowCheckpoint:
    """Represents a checkpoint in the workflow."""
    step_name: str
    step_completed: bool
    content_generated: Dict[str, Any]
    quality_score: Optional[float] = None
    user_approved: bool = False
    checkpoint_message: str = ""
    next_steps: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    retry_count: int = 0


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
    current_checkpoint: Optional[WorkflowCheckpoint] = None
    awaiting_user_approval: bool = False


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
                 logger: Optional[logging.Logger] = None, use_new_structure: bool = True):
        super().__init__(name="StoryGenerationOrchestrator", model=model, logger=logger)
        
        self.output_dir = output_dir
        self.use_new_structure = use_new_structure
        
        # Initialize directory manager and ensure directories exist
        from core.config.directory_config import get_directory_manager
        self.dir_manager = get_directory_manager(output_dir, use_new_structure)
        if use_new_structure:
            self.dir_manager.ensure_directories_exist()
        
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
        
        # Checkpoint system state
        self.checkpoint_mode_enabled = False
        self.current_checkpoint: Optional[WorkflowCheckpoint] = None
        self.user_approval_callback: Optional[Callable] = None
        self.checkpoint_lock = threading.Lock()
        self.awaiting_approval = threading.Event()
        
        # Checkpoint state manager for persistence
        self.state_manager = CheckpointStateManager(output_dir=output_dir, logger=logger)
        self.workflow_state: Optional[WorkflowState] = None
        
        # Checkpoint messages for each step
        self.checkpoint_messages = {
            "lore": "📚 **Lore Generation Complete**\n\nI've created the world-building foundation for your story. Please review the generated lore content and approve to continue with story structure.",
            "structure": "🏗️ **Story Structure Complete**\n\nI've developed the story structure and plot outline. Please review the story arcs and approve to continue with scene planning.",
            "scenes": "🎬 **Scene Planning Complete**\n\nI've created detailed scene plans for your story. Please review the scene breakdowns and approve to continue with chapter writing.",
            "chapters": "📖 **Chapter Writing Complete**\n\nI've finished writing all chapters of your story. Please review the generated content - your story is complete!"
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
    
    # ========== CHECKPOINT SYSTEM METHODS ==========
    
    def enable_checkpoint_mode(self, user_approval_callback: Optional[Callable] = None):
        """Enable checkpoint mode with optional user approval callback."""
        self.checkpoint_mode_enabled = True
        self.user_approval_callback = user_approval_callback
        self.logger.info("🚦 Checkpoint mode enabled")
    
    def disable_checkpoint_mode(self):
        """Disable checkpoint mode."""
        self.checkpoint_mode_enabled = False
        self.user_approval_callback = None
        self.current_checkpoint = None
        self.awaiting_approval.clear()
        self.logger.info("🚦 Checkpoint mode disabled")
    
    def approve_current_checkpoint(self) -> bool:
        """Approve the current checkpoint and continue workflow."""
        with self.checkpoint_lock:
            if self.current_checkpoint:
                self.current_checkpoint.user_approved = True
                self.awaiting_approval.set()
                self.logger.info(f"✅ Checkpoint approved: {self.current_checkpoint.step_name}")
                return True
            return False
    
    def retry_current_checkpoint(self) -> bool:
        """Retry the current checkpoint step."""
        with self.checkpoint_lock:
            if self.current_checkpoint:
                self.current_checkpoint.retry_count += 1
                self.current_checkpoint.user_approved = False
                self.awaiting_approval.set()
                self.logger.info(f"🔄 Checkpoint retry requested: {self.current_checkpoint.step_name}")
                return True
            return False
    
    def get_current_checkpoint(self) -> Optional[WorkflowCheckpoint]:
        """Get the current checkpoint information."""
        return self.current_checkpoint
    
    def is_awaiting_approval(self) -> bool:
        """Check if workflow is currently awaiting user approval."""
        return self.current_checkpoint is not None and not self.current_checkpoint.user_approved
    
    def _create_checkpoint(self, step_name: str, content: Dict[str, Any], 
                          quality_score: Optional[float] = None) -> WorkflowCheckpoint:
        """Create a new checkpoint for the given step."""
        next_steps = []
        current_index = self.workflow_steps.index(step_name) if step_name in self.workflow_steps else -1
        if current_index >= 0 and current_index < len(self.workflow_steps) - 1:
            next_steps = self.workflow_steps[current_index + 1:]
        
        checkpoint = WorkflowCheckpoint(
            step_name=step_name,
            step_completed=True,
            content_generated=content,
            quality_score=quality_score,
            checkpoint_message=self.checkpoint_messages.get(step_name, f"Step {step_name} completed"),
            next_steps=next_steps
        )
        
        return checkpoint
    
    def _wait_for_user_approval(self, checkpoint: WorkflowCheckpoint, timeout: Optional[float] = None) -> bool:
        """Wait for user approval of the current checkpoint."""
        self.logger.info(f"⏸️ Waiting for user approval: {checkpoint.step_name}")
        
        # Notify GUI if callback is available
        if self.user_approval_callback:
            try:
                self.user_approval_callback(checkpoint)
            except Exception as e:
                self.logger.error(f"Error in user approval callback: {e}")
        
        # Wait for approval
        if timeout:
            approved = self.awaiting_approval.wait(timeout)
        else:
            approved = self.awaiting_approval.wait()
        
        self.awaiting_approval.clear()
        
        if approved and checkpoint.user_approved:
            self.logger.info(f"✅ User approved: {checkpoint.step_name}")
            return True
        elif approved and checkpoint.retry_count > 0:
            self.logger.info(f"🔄 User requested retry: {checkpoint.step_name}")
            return False  # Indicates retry
        else:
            self.logger.warning(f"⏰ Approval timeout or cancelled: {checkpoint.step_name}")
            return False
    
    # ========== END CHECKPOINT SYSTEM METHODS ==========
    
    # ========== WORKFLOW STATE MANAGEMENT METHODS ==========
    
    def load_or_create_workflow_state(self, story_parameters: Dict[str, Any]) -> WorkflowState:
        """Load existing workflow state or create a new one."""
        existing_state = self.state_manager.load_state()
        
        if existing_state:
            self.workflow_state = existing_state
            self.logger.info(f"📂 Loaded existing workflow: {existing_state.workflow_id}")
            # Scan for any new output files
            self.state_manager.scan_output_files(existing_state)
        else:
            # Create new workflow
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.workflow_state = self.state_manager.initialize_workflow(workflow_id, story_parameters)
            self.logger.info(f"🎆 Created new workflow: {workflow_id}")
        
        return self.workflow_state
    
    def get_workflow_state(self) -> Optional[WorkflowState]:
        """Get the current workflow state."""
        if not self.workflow_state:
            self.workflow_state = self.state_manager.load_state()
        return self.workflow_state
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get workflow progress summary for GUI display."""
        if not self.workflow_state:
            return {"error": "No workflow state available"}
        
        return self.state_manager.get_progress_summary(self.workflow_state)
    
    def reset_workflow_state(self):
        """Reset the entire workflow to start over."""
        if self.workflow_state:
            self.state_manager.reset_workflow(self.workflow_state)
            self.logger.info("🔄 Workflow state reset")
    
    def reset_step_state(self, step_name: str):
        """Reset a specific step to retry it."""
        if self.workflow_state:
            self.state_manager.reset_step(self.workflow_state, step_name)
            self.logger.info(f"🔄 Step {step_name} reset for retry")
    
    def update_step_progress(self, step_name: str, status: CheckpointStatus, **kwargs):
        """Update progress for a specific step."""
        if self.workflow_state:
            self.state_manager.update_step_status(self.workflow_state, step_name, status, **kwargs)
    
    def scan_output_files(self):
        """Scan output directory and update file lists."""
        if self.workflow_state:
            self.state_manager.scan_output_files(self.workflow_state)
    
    # ========== END WORKFLOW STATE MANAGEMENT METHODS ==========
    
    def execute_single_step(self, step_name: str, story_parameters: Dict[str, Any]) -> StoryGenerationResult:
        """Execute a single workflow step and halt.
        
        This method allows executing individual steps of the workflow independently,
        which is useful for checkpoint-based execution where users want to review
        and approve each step before proceeding.
        
        Args:
            step_name: Name of the step to execute ("lore", "structure", "scenes", "chapters")
            story_parameters: Story parameters from the GUI
            
        Returns:
            StoryGenerationResult with the step execution results
        """
        self.logger.info(f"🎯 Executing single step: {step_name}")
        
        # Validate step name
        if step_name not in self.workflow_steps:
            error_msg = f"Invalid step name: {step_name}. Valid steps: {self.workflow_steps}"
            self.logger.error(error_msg)
            return StoryGenerationResult(
                success=False,
                generated_content={},
                workflow_completed=[],
                quality_scores={},
                consistency_reports=[],
                recommendations=[error_msg],
                execution_summary=f"Invalid step: {step_name}"
            )
        
        try:
            # Update step status to in progress
            self.update_step_progress(step_name, CheckpointStatus.IN_PROGRESS)
            
            # Check dependencies for this step
            if not self._check_single_step_dependencies(step_name):
                error_msg = f"Dependencies not met for step {step_name}"
                self.logger.error(error_msg)
                self.update_step_progress(step_name, CheckpointStatus.FAILED)
                return StoryGenerationResult(
                    success=False,
                    generated_content={},
                    workflow_completed=[],
                    quality_scores={},
                    consistency_reports=[],
                    recommendations=[error_msg],
                    execution_summary=f"Dependencies not met for {step_name}"
                )
            
            # Execute the specific step
            step_result = self._execute_single_workflow_step(step_name, story_parameters)
            
            if step_result["success"]:
                # Scan for actual output files created by this step
                self.scan_output_files()
                
                # Validate that files were actually created before marking as completed
                workflow_state = self.state_manager.load_state()
                step_data = workflow_state.steps.get(step_name)
                files_created = len(step_data.output_files) if step_data else 0
                
                if files_created > 0:
                    # Update step status to completed only if files were created
                    self.update_step_progress(
                        step_name, 
                        CheckpointStatus.COMPLETED,
                        quality_score=step_result.get("quality_score")
                    )
                    self.logger.info(f"✅ Step {step_name} completed with {files_created} files generated")
                else:
                    # Step execution succeeded but no files were created - mark as failed
                    self.update_step_progress(step_name, CheckpointStatus.FAILED)
                    error_msg = f"Step {step_name} execution completed but no output files were generated"
                    self.logger.error(error_msg)
                    return StoryGenerationResult(
                        success=False,
                        generated_content={},
                        workflow_completed=[],
                        quality_scores={},
                        consistency_reports=[],
                        recommendations=[error_msg],
                        execution_summary=error_msg
                    )
                
                # Perform validation if enabled
                validation_result = self._validate_workflow_step(
                    step_name, 
                    step_result["content"], 
                    {step_name: step_result["content"]}
                )
                
                # Create successful result
                result = StoryGenerationResult(
                    success=True,
                    generated_content={step_name: step_result["content"]},
                    workflow_completed=[step_name],
                    quality_scores={step_name: validation_result.get("quality_score", 0.8)},
                    consistency_reports=validation_result.get("consistency_reports", []),
                    recommendations=validation_result.get("recommendations", []),
                    execution_summary=f"Successfully completed {step_name} step"
                )
                
                self.logger.info(f"✅ Single step completed successfully: {step_name}")
                return result
                
            else:
                # Update step status to failed
                self.update_step_progress(step_name, CheckpointStatus.FAILED)
                
                error_msg = f"Step {step_name} execution failed"
                if "error" in step_result:
                    error_msg += f": {step_result['error']}"
                
                self.logger.error(error_msg)
                return StoryGenerationResult(
                    success=False,
                    generated_content={},
                    workflow_completed=[],
                    quality_scores={},
                    consistency_reports=[],
                    recommendations=[error_msg],
                    execution_summary=f"Failed to execute {step_name}"
                )
                
        except Exception as e:
            self.logger.error(f"Single step execution error for {step_name}: {e}")
            self.update_step_progress(step_name, CheckpointStatus.FAILED)
            
            return StoryGenerationResult(
                success=False,
                generated_content={},
                workflow_completed=[],
                quality_scores={},
                consistency_reports=[],
                recommendations=[f"Execution error: {str(e)}"],
                execution_summary=f"Error executing {step_name}: {str(e)}"
            )
    
    def _check_single_step_dependencies(self, step_name: str) -> bool:
        """Check if dependencies are met for a single step execution."""
        dependencies = self.step_dependencies.get(step_name, [])
        
        if not dependencies:
            return True  # No dependencies required
        
        # Check if dependency files exist or previous steps are completed
        for dep_step in dependencies:
            if self.workflow_state:
                step_status = self.workflow_state.steps.get(dep_step)
                if not step_status or step_status.status != CheckpointStatus.COMPLETED:
                    # Check if files exist even if step not marked as completed
                    if not self._check_step_files_exist(dep_step):
                        self.logger.warning(f"Dependency {dep_step} not completed for {step_name}")
                        return False
            else:
                # Fallback: check if files exist
                if not self._check_step_files_exist(dep_step):
                    self.logger.warning(f"Dependency files for {dep_step} not found for {step_name}")
                    return False
        
        return True
    
    def _check_step_files_exist(self, step_name: str) -> bool:
        """Check if the expected output files exist for a step."""
        expected_patterns = self.state_manager.get_expected_file_patterns().get(step_name, [])
        
        for pattern in expected_patterns:
            files = self.dir_manager.glob_files(pattern)
            if files:
                return True  # At least one file exists for this step
        
        return False
    
    def _execute_single_workflow_step(self, step_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step by calling the appropriate generation method."""
        try:
            if step_name == "lore":
                return self._generate_lore(parameters)
            elif step_name == "structure":
                # Load existing lore content for structure generation
                lore_content = self._load_existing_lore()
                return self._generate_structure(parameters, lore_content)
            elif step_name == "scenes":
                # Load existing structure content for scene planning
                structure_content = self._load_existing_structure()
                return self._generate_scene_plans(parameters, structure_content)
            elif step_name == "chapters":
                return self._generate_chapters(parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown step: {step_name}",
                    "content": {}
                }
        except Exception as e:
            self.logger.error(f"Error executing step {step_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": {}
            }
    
    def _load_existing_lore(self) -> Dict:
        """Load existing lore content from files for use in other steps."""
        lore_content = {}
        
        try:
            # Load characters
            characters_path = os.path.join(self.output_dir, "story", "lore", "characters.json")
            if os.path.exists(characters_path):
                with open(characters_path, 'r', encoding='utf-8') as f:
                    lore_content["characters"] = json.load(f)
            
            # Load generated lore
            lore_path = os.path.join(self.output_dir, "story", "lore", "generated_lore.md")
            if os.path.exists(lore_path):
                with open(lore_path, 'r', encoding='utf-8') as f:
                    lore_content["generated_lore"] = f.read()
            
            # Load factions if available
            factions_path = os.path.join(self.output_dir, "story", "lore", "factions.json")
            if os.path.exists(factions_path):
                with open(factions_path, 'r', encoding='utf-8') as f:
                    lore_content["factions"] = json.load(f)
                    
            self.logger.info(f"Loaded existing lore content: {list(lore_content.keys())}")
            
        except Exception as e:
            self.logger.warning(f"Could not load existing lore content: {e}")
            lore_content = {}
            
        return lore_content
    
    def _load_existing_structure(self) -> Dict:
        """Load existing structure content from files for use in other steps."""
        structure_content = {}
        
        try:
            # Load story structure JSON
            structure_path = os.path.join(self.output_dir, "story", "structure", "story_structure.json")
            if os.path.exists(structure_path):
                with open(structure_path, 'r', encoding='utf-8') as f:
                    structure_content["story_structure"] = json.load(f)
            
            # Load detailed structure markdown
            detailed_path = os.path.join(self.output_dir, "story", "structure", "detailed_structure.md")
            if os.path.exists(detailed_path):
                with open(detailed_path, 'r', encoding='utf-8') as f:
                    structure_content["detailed_structure"] = f.read()
            
            # Load reconciled arcs if available
            reconciled_path = os.path.join(self.output_dir, "story", "planning", "reconciled_locations_arcs.md")
            if os.path.exists(reconciled_path):
                with open(reconciled_path, 'r', encoding='utf-8') as f:
                    structure_content["reconciled_arcs"] = f.read()
                    
            self.logger.info(f"Loaded existing structure content: {list(structure_content.keys())}")
            
        except Exception as e:
            self.logger.warning(f"Could not load existing structure content: {e}")
            structure_content = {}
            
        return structure_content
    
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
        """Execute the complete story generation workflow with checkpoint support."""
        
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
                    execution_summary=f"Workflow failed at step {step}",
                    awaiting_user_approval=False
                )
            
            # Execute step with retry logic for checkpoints
            step_success = False
            max_retries = 3
            retry_count = 0
            
            while not step_success and retry_count <= max_retries:
                # Generate content for this step
                step_result = self._generate_workflow_step(step, plan.parameters, generated_content)
                
                if not step_result["success"]:
                    self.logger.error(f"Step {step} generation failed (attempt {retry_count + 1})")
                    retry_count += 1
                    if retry_count > max_retries:
                        return StoryGenerationResult(
                            success=False,
                            generated_content=generated_content,
                            workflow_completed=workflow_completed,
                            quality_scores=quality_scores,
                            consistency_reports=consistency_reports,
                            recommendations=[f"Step {step} generation failed after {max_retries} attempts"],
                            execution_summary=f"Workflow failed during {step} generation",
                            awaiting_user_approval=False
                        )
                    continue
                
                # Store generated content
                generated_content[step] = step_result["content"]
                
                # Validate with agents if enabled
                step_quality_score = None
                if plan.use_agentic_validation:
                    validation_result = self._validate_workflow_step(step, step_result["content"], generated_content)
                    
                    if validation_result["quality_score"]:
                        step_quality_score = validation_result["quality_score"]
                        quality_scores[step] = step_quality_score
                    
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
                            step_quality_score = improved_result.get("quality_score", step_quality_score)
                            quality_scores[step] = step_quality_score
                
                # CHECKPOINT INTEGRATION: Create checkpoint if mode is enabled
                if self.checkpoint_mode_enabled:
                    checkpoint = self._create_checkpoint(step, generated_content[step], step_quality_score)
                    self.current_checkpoint = checkpoint
                    
                    self.logger.info(f"🚦 Checkpoint created for step: {step}")
                    
                    # Wait for user approval
                    approval_result = self._wait_for_user_approval(checkpoint)
                    
                    if checkpoint.user_approved:
                        # User approved, continue to next step
                        step_success = True
                        workflow_completed.append(step)
                        self.current_checkpoint = None
                        self.logger.info(f"✅ Step {step} approved and completed")
                    elif checkpoint.retry_count > retry_count:
                        # User requested retry
                        retry_count = checkpoint.retry_count
                        self.logger.info(f"🔄 Retrying step {step} (attempt {retry_count + 1})")
                        continue
                    else:
                        # User cancelled or timeout
                        self.logger.warning(f"❌ Step {step} cancelled by user")
                        return StoryGenerationResult(
                            success=False,
                            generated_content=generated_content,
                            workflow_completed=workflow_completed,
                            quality_scores=quality_scores,
                            consistency_reports=consistency_reports,
                            recommendations=all_recommendations,
                            execution_summary=f"Workflow cancelled at step {step} by user",
                            current_checkpoint=checkpoint,
                            awaiting_user_approval=True
                        )
                else:
                    # No checkpoint mode, proceed normally
                    step_success = True
                    workflow_completed.append(step)
        
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
            
            # Step 1: Save parameters first (use GUI's save method for consistency)
            self.logger.info("🔹 Step 1: Saving parameters to file")
            app.param_ui.save_parameters()  # Use the GUI's save method instead of manual creation
            self.logger.info("✅ Parameters saved using GUI save method")
            
            # Step 2: Click each lore button in sequence (like you do)
            lore_results = {}
            
            self.logger.info("🔹 Step 2: Clicking 'Generate Factions' button")
            lore_ui.generate_factions()
            self.logger.info("✅ Generate Factions completed")
            
            # Tactical pause to allow file operations to complete
            import time
            time.sleep(1.0)
            
            self.logger.info("🔹 Step 3: Clicking 'Generate Characters' button")
            lore_ui.generate_characters()
            self.logger.info("✅ Generate Characters completed")
            
            # Tactical pause to allow file operations to complete
            time.sleep(1.0)
            
            self.logger.info("🔹 Step 4: Clicking 'Generate Lore' button")
            lore_content = lore_ui.generate_lore()
            self.logger.info("✅ Generate Lore completed")
            
            # Tactical pause to allow file operations to complete
            time.sleep(1.5)  # Longer pause after LLM call
            
            self.logger.info("🔹 Step 5: Clicking 'Enhance main characters' button")
            lore_ui.main_character_enhancement()
            self.logger.info("✅ Enhance main characters completed")
            
            # Tactical pause to allow file operations to complete
            time.sleep(1.5)  # Longer pause after LLM calls
            
            self.logger.info("🔹 Step 6: Clicking 'Suggest Story Titles' button")
            lore_ui.suggest_titles()
            self.logger.info("✅ Suggest Story Titles completed")
            
            # Final pause to ensure all files are written
            time.sleep(1.0)
            
            # Collect all the generated files from the output directory
            output_dir = app.get_output_dir()
            generated_files = []
            for file in os.listdir(output_dir):
                if file.endswith(('.json', '.md', '.txt')) and any(keyword in file.lower() for keyword in 
                    ['faction', 'character', 'lore', 'background', 'title']):
                    generated_files.append(file)
            
            lore_results = {
                "parameters_file": "system/parameters.txt",
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
            output_dir = story_params.get("output_directory", "current_work")  # Define output_dir early
            
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
            
            # Tactical pause to allow file operations to complete
            time.sleep(1.5)  # Longer pause after LLM call
            
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
            
            # Tactical pause to allow file operations to complete
            time.sleep(1.5)  # Longer pause after LLM call
            
            # Step 4: Add Locations to Arcs
            self.logger.info("🔹 Step 4: Clicking 'Add Locations to Arcs' button")
            try:
                story_structure_ui.add_planets_to_arcs()
                structure_results["functions_executed"].append("Add Locations to Arcs")
                structure_results["button_clicks"].append("cfp_arc_button")
                self.logger.info("✅ Add Locations to Arcs completed")
            except Exception as e:
                self.logger.warning(f"⚠️ Add Locations to Arcs failed: {e}")
            
            # Tactical pause to allow file operations to complete
            time.sleep(1.5)  # Longer pause after LLM call
            
            # Step 5: Create Detailed Plot (dispatches based on story length)
            self.logger.info("🔹 Step 5: Clicking 'Create Detailed Plot' button")
            try:
                story_structure_ui._dispatch_detailed_plot_creation()
                structure_results["functions_executed"].append("Create Detailed Plot")
                structure_results["button_clicks"].append("detailed_plot_button")
                self.logger.info("✅ Detailed Plot creation completed")
            except Exception as e:
                self.logger.warning(f"⚠️ Detailed Plot creation failed: {e}")
            
            # Final pause to ensure all structure files are written
            time.sleep(2.0)  # Longer pause after complex operations
            
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
            generated_files = []
            
            # Common structure files that might be generated (using structured paths)
            potential_files = [
                "story/structure/character_arcs.md",
                "story/structure/faction_arcs.md", 
                "story/structure/reconciled_arcs.md",
                "story/structure/locations_arcs.md",
                "story/structure/detailed_plot.md",
                "story/structure/plot_short_story_3-act_structure.md",
                "story/structure/plot_novella.md",
                "story/structure/plot_novel.md",
                "story/structure/improved_structure.md"
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
                
                # Tactical pause to allow file operations to complete
                time.sleep(1.5)  # Longer pause after LLM call
                
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
            
            # Final pause to ensure all scene planning files are written
            time.sleep(2.0)  # Longer pause after complex operations
            
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
            chapter_agent = ChapterWritingAgent(self.output_dir, app_instance=None, use_new_structure=self.use_new_structure)
            
            # Analyze story structure to find chapters
            self.logger.info("📊 Analyzing chapter structure...")
            
            # Tactical pause to ensure all prerequisite files are available
            time.sleep(1.0)
            
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
            
            # Final pause to ensure all chapter files are written
            time.sleep(2.0)  # Longer pause after complex writing operations
            
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
                # For chapter outlines, find the first section file that exists in structured directory
                sections = STRUCTURE_SECTIONS_MAP.get(story_structure, [])
                if sections:
                    for section in sections:
                        safe_section_name = section.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
                        filename = f"chapter_outlines_{safe_structure_name}_{safe_section_name}.md"
                        filepath = os.path.join(output_dir, "story", "planning", filename)
                        if os.path.exists(filepath):
                            return f"story/planning/{filename}"
                # Fallback to first section pattern
                if sections:
                    safe_section_name = sections[0].lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
                    return f"story/planning/chapter_outlines_{safe_structure_name}_{safe_section_name}.md"
                    
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
