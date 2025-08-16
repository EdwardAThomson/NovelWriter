"""
Checkpoint State Management System for NovelWriter Agentic Workflow.

This module handles persistent checkpoint state tracking, allowing the GUI
to know exactly where we are in the workflow and what files have been generated.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class CheckpointStatus(Enum):
    """Status of a checkpoint step."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CheckpointStep:
    """Information about a single checkpoint step."""
    name: str
    status: CheckpointStatus = CheckpointStatus.NOT_STARTED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    quality_score: Optional[float] = None
    output_files: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    retry_count: int = 0
    user_approved: bool = False


@dataclass
class WorkflowState:
    """Complete workflow state information."""
    workflow_id: str
    current_step: Optional[str] = None
    steps: Dict[str, CheckpointStep] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    parameters_snapshot: Dict[str, Any] = field(default_factory=dict)
    total_steps: int = 4  # lore, structure, scenes, chapters


class CheckpointStateManager:
    """Manages persistent checkpoint state for the workflow."""
    
    def __init__(self, output_dir: str = "current_work", logger: Optional[logging.Logger] = None):
        self.output_dir = output_dir
        self.logger = logger or logging.getLogger(__name__)
        self.state_file = os.path.join(output_dir, "system", "checkpoint_state.json")
        self.workflow_steps = ["lore", "structure", "scenes", "chapters"]
        
        # Expected output files for each step (based on actual file ownership)
        self.expected_files = {
            "lore": [
                "story/lore/characters.json",
                "story/lore/factions.json", 
                "story/lore/generated_lore.md",
                "story/lore/background_*.md"  # Character backstories
            ],
            "structure": [
                "story/structure/6-act_structure_*.md",  # Story section files
                "story/structure/character_arcs.md",
                "story/structure/faction_arcs.md", 
                "story/structure/reconciled_arcs.md",
                "story/planning/reconciled_locations_arcs.md",  # Final arcs with locations
                "story/planning/suggested_titles.md"  # Title suggestions
            ],
            "scenes": [
                "story/planning/detailed_scene_plans/scenes_*.md",  # Detailed scene plans (long-form)
                "story/planning/scenes_short_story_*.md",  # Short story scene plans
                "story/planning/chapter_outlines_*.md"  # Chapter outlines
            ],
            "chapters": [
                "story/content/chapters/chapter_*.md",  # Individual chapters
                "story/content/chapters/re_chapter_*.md",  # Rewritten chapters
                "story/content/prose_short_story_*.md"  # Short story files
            ]
        }
    
    def initialize_workflow(self, workflow_id: str, parameters: Dict[str, Any]) -> WorkflowState:
        """Initialize a new workflow state."""
        steps = {}
        for step_name in self.workflow_steps:
            steps[step_name] = CheckpointStep(name=step_name)
        
        state = WorkflowState(
            workflow_id=workflow_id,
            current_step=self.workflow_steps[0],  # Start with first step
            steps=steps,
            parameters_snapshot=parameters.copy()
        )
        
        self.save_state(state)
        self.logger.info(f"🚀 Initialized new workflow: {workflow_id}")
        return state
    
    def load_state(self) -> Optional[WorkflowState]:
        """Load workflow state from file."""
        if not os.path.exists(self.state_file):
            self.logger.info("No checkpoint state file found")
            return None
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert steps back to CheckpointStep objects
            steps = {}
            for step_name, step_data in data.get('steps', {}).items():
                step_data['status'] = CheckpointStatus(step_data['status'])
                steps[step_name] = CheckpointStep(**step_data)
            
            state = WorkflowState(
                workflow_id=data['workflow_id'],
                current_step=data.get('current_step'),
                steps=steps,
                created_at=data.get('created_at', ''),
                updated_at=data.get('updated_at', ''),
                parameters_snapshot=data.get('parameters_snapshot', {}),
                total_steps=data.get('total_steps', 4)
            )
            
            self.logger.info(f"📂 Loaded checkpoint state: {state.workflow_id}")
            return state
            
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint state: {e}")
            return None
    
    def save_state(self, state: WorkflowState):
        """Save workflow state to file."""
        try:
            # Ensure system directory exists
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            # Update timestamp
            state.updated_at = datetime.now().isoformat()
            
            # Convert to dict for JSON serialization
            state_dict = asdict(state)
            
            # Convert enum values to strings
            for step_name, step_data in state_dict['steps'].items():
                step_data['status'] = step_data['status'].value
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"💾 Saved checkpoint state: {state.workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint state: {e}")
    
    def update_step_status(self, state: WorkflowState, step_name: str, 
                          status: CheckpointStatus, **kwargs):
        """Update the status of a specific step."""
        if step_name not in state.steps:
            self.logger.error(f"Unknown step: {step_name}")
            return
        
        step = state.steps[step_name]
        old_status = step.status
        step.status = status
        
        # Update timestamps
        if status == CheckpointStatus.IN_PROGRESS and not step.started_at:
            step.started_at = datetime.now().isoformat()
        elif status == CheckpointStatus.COMPLETED:
            step.completed_at = datetime.now().isoformat()
        
        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(step, key):
                setattr(step, key, value)
        
        # Update current step
        if status == CheckpointStatus.IN_PROGRESS:
            state.current_step = step_name
        elif status == CheckpointStatus.COMPLETED:
            # Move to next step if available
            try:
                current_index = self.workflow_steps.index(step_name)
                if current_index < len(self.workflow_steps) - 1:
                    state.current_step = self.workflow_steps[current_index + 1]
                else:
                    state.current_step = None  # Workflow complete
            except ValueError:
                pass
        
        self.save_state(state)
        self.logger.info(f"📊 Step {step_name}: {old_status.value} → {status.value}")
    
    def scan_output_files(self, state: WorkflowState):
        """Scan the output directory and update file lists for each step."""
        import glob
        
        for step_name in self.workflow_steps:
            step = state.steps[step_name]
            step.output_files = []
            
            expected_patterns = self.expected_files.get(step_name, [])
            self.logger.debug(f"🔍 Scanning {step_name} step with patterns: {expected_patterns}")
            
            for pattern in expected_patterns:
                if '*' in pattern:
                    # Handle glob patterns
                    full_pattern = os.path.join(self.output_dir, pattern)
                    self.logger.debug(f"🔍 Checking glob pattern: {full_pattern}")
                    matches = glob.glob(full_pattern)
                    self.logger.debug(f"🔍 Glob matches: {matches}")
                    # Convert back to relative paths
                    relative_matches = [os.path.relpath(m, self.output_dir) for m in matches]
                    step.output_files.extend(relative_matches)
                else:
                    # Handle exact file paths
                    full_path = os.path.join(self.output_dir, pattern)
                    self.logger.debug(f"🔍 Checking exact file: {full_path}")
                    if os.path.exists(full_path):
                        self.logger.debug(f"✅ Found file: {pattern}")
                        step.output_files.append(pattern)
                    else:
                        self.logger.debug(f"❌ File not found: {pattern}")
            
            self.logger.info(f"📁 {step_name} step: found {len(step.output_files)} files: {step.output_files}")
        
        self.save_state(state)
        self.logger.debug("🔍 Scanned output files for all steps")
    
    def get_expected_file_patterns(self) -> Dict[str, List[str]]:
        """Get the expected file patterns for each step."""
        return self.expected_files.copy()
    
    def get_progress_summary(self, state: WorkflowState) -> Dict[str, Any]:
        """Get a summary of workflow progress."""
        completed_steps = [name for name, step in state.steps.items() 
                          if step.status == CheckpointStatus.COMPLETED]
        
        total_files = sum(len(step.output_files) for step in state.steps.values())
        
        return {
            "workflow_id": state.workflow_id,
            "current_step": state.current_step,
            "completed_steps": completed_steps,
            "total_steps": len(self.workflow_steps),
            "completion_percentage": len(completed_steps) / len(self.workflow_steps) * 100,
            "total_output_files": total_files,
            "created_at": state.created_at,
            "updated_at": state.updated_at
        }
    
    def reset_workflow(self, state: WorkflowState):
        """Reset workflow to initial state."""
        for step in state.steps.values():
            step.status = CheckpointStatus.NOT_STARTED
            step.started_at = None
            step.completed_at = None
            step.quality_score = None
            step.error_message = None
            step.retry_count = 0
            step.user_approved = False
        
        state.current_step = self.workflow_steps[0]
        self.save_state(state)
        self.logger.info("🔄 Workflow reset to initial state")
    
    def create_from_existing_work(self, workflow_id: str = None, parameters: Dict[str, Any] = None) -> WorkflowState:
        """Create a checkpoint state by scanning existing work in the output directory."""
        if workflow_id is None:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if parameters is None:
            parameters = {}
        
        # Create new workflow state
        state = self.initialize_workflow(workflow_id, parameters)
        
        # Scan for existing files and update step statuses
        self.scan_output_files(state)
        
        # Analyze which steps appear to be completed based on files
        for step_name, step in state.steps.items():
            if step.output_files:
                # If files exist, mark as completed
                step.status = CheckpointStatus.COMPLETED
                step.completed_at = datetime.now().isoformat()
                
                # Estimate quality score based on file count and expected files
                expected_count = len(self.expected_files.get(step_name, []))
                actual_count = len(step.output_files)
                if expected_count > 0:
                    step.quality_score = min(1.0, actual_count / expected_count * 0.8 + 0.2)
                else:
                    step.quality_score = 0.8  # Default reasonable score
                
                step.user_approved = True  # Assume existing work is approved
                self.logger.info(f"📁 Found {actual_count} files for {step_name} step")
        
        # Determine current step (first incomplete step)
        for step_name in self.workflow_steps:
            if state.steps[step_name].status != CheckpointStatus.COMPLETED:
                state.current_step = step_name
                break
        else:
            # All steps completed
            state.current_step = None
        
        self.save_state(state)
        self.logger.info(f"🎆 Created checkpoint state from existing work: {workflow_id}")
        return state
    
    def reset_step(self, state: WorkflowState, step_name: str):
        """Reset a specific step to not started."""
        if step_name in state.steps:
            step = state.steps[step_name]
            step.status = CheckpointStatus.NOT_STARTED
            step.started_at = None
            step.completed_at = None
            step.quality_score = None
            step.error_message = None
            step.user_approved = False
            step.retry_count += 1
            
            # Reset current step to this step
            state.current_step = step_name
            
            self.save_state(state)
            self.logger.info(f"🔄 Reset step: {step_name}")
