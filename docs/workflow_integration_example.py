#!/usr/bin/env python3
"""
Example integration of Story Generation Orchestrator with existing NovelWriter GUI.

This demonstrates how to integrate the agentic workflow orchestrator with your
existing GUI components to follow the proper story creation process.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional

# Import existing GUI components
from core.gui.app import NovelWriterApp
from core.gui.parameters import Parameters
from core.gui.lore import Lore
from core.gui.story_structure import StoryStructure
from core.gui.scene_plan import ScenePlan
from core.gui.chapter_writing import ChapterWriting

# Import agentic orchestrators
from agents.orchestration.story_generation_orchestrator import StoryGenerationOrchestrator
from agents.orchestration.orchestrator import MultiAgentOrchestrator


class AgenticNovelWriterApp(NovelWriterApp):
    """
    Enhanced NovelWriter app with agentic workflow orchestration.
    
    This class extends the existing app to include:
    1. Proper workflow orchestration (Lore → Structure → Scenes → Chapters)
    2. Agentic quality and consistency validation
    3. Iterative improvement capabilities
    4. Resume functionality for interrupted workflows
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize agentic components
        self.story_orchestrator = None
        self.analysis_orchestrator = None
        self.agentic_enabled = tk.BooleanVar(value=False)
        
        # Workflow state
        self.current_workflow_step = "parameters"
        self.workflow_completed_steps = []
        
        # Add agentic controls to the GUI
        self.create_agentic_controls()
        
        # Override existing generation methods
        self.setup_agentic_workflow()
    
    def create_agentic_controls(self):
        """Add agentic workflow controls to the GUI."""
        
        # Create agentic frame
        agentic_frame = tk.LabelFrame(self.root, text="🤖 Agentic Workflow", padx=10, pady=10)
        agentic_frame.pack(fill="x", padx=10, pady=5)
        
        # Enable/disable agentic mode
        agentic_check = tk.Checkbutton(
            agentic_frame,
            text="Enable Agentic Workflow Orchestration",
            variable=self.agentic_enabled,
            command=self.toggle_agentic_mode,
            font=("Arial", 11, "bold")
        )
        agentic_check.pack(anchor="w", pady=5)
        
        # Workflow progress
        progress_frame = tk.Frame(agentic_frame)
        progress_frame.pack(fill="x", pady=5)
        
        tk.Label(progress_frame, text="Workflow Progress:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.workflow_progress = ttk.Progressbar(
            progress_frame, 
            mode='determinate',
            maximum=4  # lore, structure, scenes, chapters
        )
        self.workflow_progress.pack(fill="x", pady=2)
        
        self.workflow_status = tk.Label(
            progress_frame,
            text="Ready to begin workflow",
            font=("Arial", 9),
            fg="blue"
        )
        self.workflow_status.pack(anchor="w")
        
        # Workflow controls
        controls_frame = tk.Frame(agentic_frame)
        controls_frame.pack(fill="x", pady=5)
        
        self.start_workflow_btn = tk.Button(
            controls_frame,
            text="🚀 Start Complete Workflow",
            command=self.start_complete_workflow,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.start_workflow_btn.pack(side="left", padx=5)
        
        self.resume_workflow_btn = tk.Button(
            controls_frame,
            text="▶️ Resume Workflow",
            command=self.resume_workflow,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.resume_workflow_btn.pack(side="left", padx=5)
        
        self.analyze_content_btn = tk.Button(
            controls_frame,
            text="🔍 Analyze Current Content",
            command=self.analyze_current_content,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.analyze_content_btn.pack(side="left", padx=5)
        
        # Quality settings
        quality_frame = tk.LabelFrame(agentic_frame, text="Quality Standards", padx=5, pady=5)
        quality_frame.pack(fill="x", pady=5)
        
        quality_controls = tk.Frame(quality_frame)
        quality_controls.pack(fill="x")
        
        tk.Label(quality_controls, text="Minimum Quality:").pack(side="left")
        self.quality_threshold = tk.DoubleVar(value=0.75)
        quality_scale = tk.Scale(
            quality_controls,
            from_=0.5, to=1.0, resolution=0.05,
            orient="horizontal",
            variable=self.quality_threshold,
            length=200
        )
        quality_scale.pack(side="left", padx=10)
        
        tk.Label(quality_controls, text="Consistency Threshold:").pack(side="left", padx=(20, 0))
        self.consistency_threshold = tk.DoubleVar(value=0.8)
        consistency_scale = tk.Scale(
            quality_controls,
            from_=0.5, to=1.0, resolution=0.05,
            orient="horizontal",
            variable=self.consistency_threshold,
            length=200
        )
        consistency_scale.pack(side="left", padx=10)
    
    def toggle_agentic_mode(self):
        """Toggle agentic workflow mode."""
        enabled = self.agentic_enabled.get()
        
        if enabled:
            try:
                self.init_agentic_orchestrators()
                self.workflow_status.config(text="Agentic mode enabled - Ready for workflow", fg="green")
                self.logger.info("Agentic workflow mode enabled")
            except Exception as e:
                self.logger.error(f"Failed to enable agentic mode: {e}")
                messagebox.showerror("Error", f"Failed to enable agentic mode: {e}")
                self.agentic_enabled.set(False)
        else:
            self.story_orchestrator = None
            self.analysis_orchestrator = None
            self.workflow_status.config(text="Agentic mode disabled", fg="gray")
            self.logger.info("Agentic workflow mode disabled")
    
    def init_agentic_orchestrators(self):
        """Initialize agentic orchestrators."""
        model = self.get_selected_model()
        output_dir = self.get_output_directory()
        
        self.story_orchestrator = StoryGenerationOrchestrator(
            model=model,
            output_dir=output_dir,
            logger=self.logger
        )
        
        self.analysis_orchestrator = MultiAgentOrchestrator(
            model=model,
            output_dir=output_dir,
            logger=self.logger
        )
        
        self.logger.info("Agentic orchestrators initialized successfully")
    
    def setup_agentic_workflow(self):
        """Override existing generation methods to use agentic workflow."""
        
        # Store original methods
        self.original_generate_lore = getattr(self.lore_tab, 'generate_lore', None)
        self.original_generate_structure = getattr(self.story_structure_tab, 'generate_structure', None)
        self.original_generate_scenes = getattr(self.scene_plan_tab, 'generate_scenes', None)
        self.original_generate_chapter = getattr(self.chapter_writing_tab, 'generate_chapter', None)
        
        # Note: In a real implementation, you would override these methods
        # to integrate with the agentic workflow
    
    def start_complete_workflow(self):
        """Start the complete agentic story generation workflow."""
        
        if not self.agentic_enabled.get():
            messagebox.showwarning("Warning", "Please enable agentic mode first")
            return
        
        if not self.story_orchestrator:
            messagebox.showerror("Error", "Agentic orchestrators not initialized")
            return
        
        try:
            # Gather story parameters from the GUI
            story_params = self.gather_story_parameters()
            
            if not story_params:
                messagebox.showwarning("Warning", "Please fill in story parameters first")
                return
            
            # Update UI
            self.workflow_status.config(text="Starting complete workflow...", fg="orange")
            self.workflow_progress.config(value=0)
            self.root.update()
            
            # Create workflow task
            workflow_task = {
                "story_parameters": story_params,
                "generation_mode": "complete",
                "quality_standards": {
                    "minimum_quality": self.quality_threshold.get(),
                    "minimum_consistency": self.consistency_threshold.get()
                },
                "use_validation": True
            }
            
            # Execute workflow
            self.logger.info("Starting complete agentic workflow")
            result = self.story_orchestrator.process_task(workflow_task)
            
            if result.success:
                generation_result = result.data.get("generation_result")
                self.handle_workflow_success(generation_result)
            else:
                self.handle_workflow_error(result.messages)
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            self.handle_workflow_error([str(e)])
    
    def resume_workflow(self):
        """Resume an interrupted workflow."""
        
        if not self.agentic_enabled.get() or not self.story_orchestrator:
            messagebox.showwarning("Warning", "Please enable agentic mode first")
            return
        
        try:
            # Check existing content
            existing_steps = self.story_orchestrator._check_existing_content()
            
            if not existing_steps:
                messagebox.showinfo("Info", "No existing workflow content found. Use 'Start Complete Workflow' instead.")
                return
            
            # Gather parameters
            story_params = self.gather_story_parameters()
            
            # Update UI
            self.workflow_status.config(text="Resuming workflow...", fg="orange")
            self.root.update()
            
            # Create resume task
            resume_task = {
                "story_parameters": story_params,
                "generation_mode": "resume",
                "target_steps": ["lore", "structure", "scenes", "chapters"],
                "quality_standards": {
                    "minimum_quality": self.quality_threshold.get(),
                    "minimum_consistency": self.consistency_threshold.get()
                },
                "use_validation": True
            }
            
            # Execute resume
            result = self.story_orchestrator.process_task(resume_task)
            
            if result.success:
                generation_result = result.data.get("generation_result")
                self.handle_workflow_success(generation_result, resumed=True)
            else:
                self.handle_workflow_error(result.messages)
                
        except Exception as e:
            self.logger.error(f"Resume workflow failed: {e}")
            self.handle_workflow_error([str(e)])
    
    def analyze_current_content(self):
        """Analyze current content with agentic agents."""
        
        if not self.agentic_enabled.get() or not self.analysis_orchestrator:
            messagebox.showwarning("Warning", "Please enable agentic mode first")
            return
        
        try:
            # Get current content from active tab
            current_content = self.get_current_content()
            
            if not current_content:
                messagebox.showwarning("Warning", "No content to analyze")
                return
            
            # Update UI
            self.workflow_status.config(text="Analyzing content...", fg="orange")
            self.root.update()
            
            # Create analysis task
            analysis_task = {
                "content": current_content,
                "task_type": "comprehensive",
                "context": {
                    "genre": self.get_selected_genre(),
                    "analysis_type": "current_content"
                },
                "quality_standards": {
                    "minimum_quality": self.quality_threshold.get(),
                    "minimum_consistency": self.consistency_threshold.get()
                }
            }
            
            # Execute analysis
            result = self.analysis_orchestrator.process_task(analysis_task)
            
            if result.success:
                self.show_analysis_results(result)
            else:
                self.handle_workflow_error(result.messages)
                
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            self.handle_workflow_error([str(e)])
    
    def gather_story_parameters(self) -> Optional[Dict[str, Any]]:
        """Gather story parameters from the GUI."""
        
        try:
            # Get parameters from the parameters tab
            # This would integrate with your existing parameter collection
            
            params = {
                "genre": self.get_selected_genre(),
                "theme": "adventure",  # Would get from GUI
                "setting": "Fantasy realm",  # Would get from GUI
                "main_plot": "Hero's journey",  # Would get from GUI
                "characters": [],  # Would get from GUI
                "chapter_count": 10,  # Would get from GUI
                "story_type": "three_act"
            }
            
            return params
            
        except Exception as e:
            self.logger.error(f"Failed to gather story parameters: {e}")
            return None
    
    def get_current_content(self) -> str:
        """Get content from the currently active tab."""
        
        # This would get content from whichever tab is currently active
        # For example, if on chapter writing tab, get the current chapter text
        
        return "Sample content for analysis..."  # Placeholder
    
    def handle_workflow_success(self, generation_result, resumed=False):
        """Handle successful workflow completion."""
        
        completed_steps = generation_result.workflow_completed
        self.workflow_progress.config(value=len(completed_steps))
        
        action = "Resumed" if resumed else "Completed"
        self.workflow_status.config(
            text=f"{action} workflow: {' → '.join(completed_steps)}",
            fg="green"
        )
        
        # Show results dialog
        self.show_workflow_results(generation_result, resumed)
        
        # Update workflow state
        self.workflow_completed_steps.extend(completed_steps)
        
        self.logger.info(f"Workflow {action.lower()}: {len(completed_steps)} steps")
    
    def handle_workflow_error(self, error_messages):
        """Handle workflow errors."""
        
        error_text = "\n".join(error_messages) if isinstance(error_messages, list) else str(error_messages)
        
        self.workflow_status.config(text="Workflow failed", fg="red")
        
        messagebox.showerror("Workflow Error", f"Workflow execution failed:\n\n{error_text}")
        
        self.logger.error(f"Workflow failed: {error_text}")
    
    def show_workflow_results(self, generation_result, resumed=False):
        """Show workflow results in a dialog."""
        
        results_window = tk.Toplevel(self.root)
        results_window.title("🎉 Workflow Results")
        results_window.geometry("800x600")
        results_window.transient(self.root)
        
        # Create scrollable text widget
        text_frame = tk.Frame(results_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 11))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Format results
        action = "Resumed" if resumed else "Completed"
        results_text = f"🎭 Workflow {action} Successfully!\n\n"
        
        results_text += f"📊 Steps Completed: {len(generation_result.workflow_completed)}\n"
        results_text += f"🔄 Workflow: {' → '.join(generation_result.workflow_completed)}\n\n"
        
        if generation_result.quality_scores:
            results_text += "📈 Quality Scores:\n"
            for step, score in generation_result.quality_scores.items():
                results_text += f"   {step}: {score:.2f}\n"
            results_text += "\n"
        
        if generation_result.recommendations:
            results_text += f"💡 Recommendations ({len(generation_result.recommendations)}):\n"
            for i, rec in enumerate(generation_result.recommendations[:10], 1):
                results_text += f"   {i}. {rec}\n"
            results_text += "\n"
        
        results_text += f"📋 Summary: {generation_result.execution_summary}\n\n"
        
        # Add generated content info
        results_text += "📁 Generated Content:\n"
        for step, content in generation_result.generated_content.items():
            if isinstance(content, dict):
                results_text += f"   {step.title()}: {len(content)} elements\n"
            else:
                results_text += f"   {step.title()}: Content generated\n"
        
        text_widget.insert(tk.END, results_text)
        text_widget.config(state="disabled")
        
        # Close button
        close_btn = tk.Button(
            results_window,
            text="Close",
            command=results_window.destroy,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold")
        )
        close_btn.pack(pady=10)
    
    def show_analysis_results(self, analysis_result):
        """Show content analysis results."""
        
        # Similar to show_workflow_results but for analysis
        orchestration_result = analysis_result.data.get("orchestration_result")
        
        if orchestration_result:
            messagebox.showinfo(
                "Analysis Complete",
                f"Content Analysis Complete!\n\n"
                f"Quality Score: {orchestration_result.overall_quality_score:.2f}\n"
                f"Recommendations: {len(orchestration_result.recommendations)}\n\n"
                f"Check the logs for detailed analysis."
            )
        
        self.workflow_status.config(text="Analysis complete", fg="green")
    
def main():
    """Run the enhanced NovelWriter app with agentic capabilities."""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the app
    app = AgenticNovelWriterApp()
    app.run()

if __name__ == "__main__":
    main()
