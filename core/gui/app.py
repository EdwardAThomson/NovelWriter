import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Optional
from core.config.logger_config import setup_app_logger
from core.gui.parameters import Parameters
from core.config.genre_configs import get_genre_config
from core.gui.lore import Lore
from core.gui.story_structure import StoryStructure
from core.gui.scene_plan import ScenePlanning
from core.gui.chapter_writing import ChapterWriting
from core.generation.ai_helper import get_supported_models
from core.gui.notifications import init_notifications, show_success, show_info, show_warning, show_error

# Import agentic orchestrators
try:
    from agents.orchestration.story_generation_orchestrator import StoryGenerationOrchestrator
    from agents.orchestration.orchestrator import MultiAgentOrchestrator
    AGENTIC_AVAILABLE = True
except ImportError as e:
    AGENTIC_AVAILABLE = False
    print(f"Warning: Agentic features not available: {e}")

# NovelWriter: An AI-assisted novel writing tool
# Features:
# - GUI-based interface for novel development
# - Supports parameter collection, lore generation, and chapter writing
# - Saves work across multiple files
#
# Currently optimized for Science Fiction, with planned expansion to other genres

class NovelWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Writer")

        # --- Add Model Selection ---
        self.model_frame = ttk.Frame(root)
        self.model_frame.pack(pady=5, padx=10, fill='x')

        ttk.Label(self.model_frame, text="Select LLM Model:").pack(side="left", padx=5)

        # Get available models dynamically
        self.available_models = get_supported_models()
        if not self.available_models: # Fallback if list is empty
            self.available_models = ["gpt-4o"] # Provide a default fallback
            # Potential place for a log warning if logger was already set up
            # print("Warning: Could not retrieve models from ai_helper. Using default.")

        self.selected_model_var = tk.StringVar(value=self.available_models[0] if self.available_models else "") # Default to the first model or empty

        self.model_combobox = ttk.Combobox(
            self.model_frame,
            textvariable=self.selected_model_var,
            values=self.available_models, # Use the dynamic list
            state="readonly"
        )
        self.model_combobox.pack(side="left", fill='x', expand=True)
        # --- End Model Selection ---

        # Create notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Parameters UI
        self.param_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.param_frame, text="Novel Parameters")
        self.param_ui = Parameters(self.param_frame, app=self)
        
        # --- Initialize Logger HERE, after param_ui is available for get_output_dir() ---
        # self.get_output_dir() has a fallback, so it's safe to call even if params haven't been loaded by user yet.
        self.logger = setup_app_logger(output_dir=self.get_output_dir(), level=logging.DEBUG)
        self.logger.info("NovelWriterApp initialized and logger started.")
        if not self.available_models:
             self.logger.warning("Could not retrieve models from ai_helper. Using default: gpt-4o")
        # --- End Logger Initialization ---
        
        # Initialize notification system
        init_notifications(self.root)
        self.logger.info("Non-blocking notification system initialized")
        
        # Lore Generation UI
        self.lore_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lore_frame, text="Generate Lore")
        # self.lore_frame.parameters_ui = self.param_ui # Lore gets app, which has param_ui
        self.lore_ui = Lore(self.lore_frame, app=self) # Pass the app instance
        
        # Register Lore's update method as a callback in Parameters
        self.param_ui.add_callback(self.lore_ui.update_extra_parameter)

        # High-Level Story Structure UI
        self.structure_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.structure_frame, text="Story Structure")
        self.structure_ui = StoryStructure(self.structure_frame, app=self)

        # Scene Planning UI
        self.outlining_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.outlining_frame, text="Scene Planning")
        self.outlining_ui = ScenePlanning(self.outlining_frame, app=self)

        # Chapter Writing UI
        self.chapter_writing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chapter_writing_frame, text="Write Chapters")
        self.chapter_writing_ui = ChapterWriting(self.chapter_writing_frame, app=self)

        # Initialize agentic components if available
        if AGENTIC_AVAILABLE:
            self.story_orchestrator = None
            self.analysis_orchestrator = None
            self.agentic_enabled = tk.BooleanVar(value=False)
            
            # Workflow state
            self.current_workflow_step = "parameters"
            self.workflow_completed_steps = []
            
            # Add agentic controls to the GUI
            self.create_agentic_controls()
        else:
            self.agentic_enabled = None
            self.logger.warning("Agentic features disabled - orchestrators not available")

    def get_output_dir(self):
        """Returns the configured output directory path."""
        # Default to 'current_work' if param_ui isn't ready or var is empty
        
        try:
            path = self.param_ui.output_dir_var.get()
            # Log which path is being used if logger is available
            if hasattr(self, 'logger') and self.logger:
                returning_value = path if path else "current_work"
                self.logger.debug(f"get_output_dir called. Path from param_ui: '{path}'. Returning: '{returning_value}'")
            return path if path else "current_work"
        except AttributeError:
            # Logger might not be initialized yet if this is called before param_ui setup.
            # This case is less likely if logger setup is after param_ui init.
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning("get_output_dir called before param_ui fully initialized or output_dir_var missing. Falling back to 'current_work'.")
            return "current_work"

    def get_selected_model(self):
        """Returns the currently selected LLM model name."""
        model = self.selected_model_var.get()
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"get_selected_model called. Returning: {model}")
        return model

    def generate_story(self):
        """
        Coordinates story generation across all UI components using current parameters
        and genre configurations.
        """
        # Ensure this function also uses the selected model if it makes LLM calls
        selected_model = self.get_selected_model()
        # print(f"Using model: {selected_model} for story generation coordination")
        self.logger.info(f"generate_story called. Using model: {selected_model} for story generation coordination")

        # 1. Get base parameters
        current_params = self.param_ui.get_current_parameters()
        genre = current_params["genre"]
        subgenre = current_params["subgenre"]
        genre_config = get_genre_config(genre, subgenre)

        # 2. Generate world lore
        #lore_elements = self.lore_ui.generate_lore(
        #    parameters=current_params,
        #    genre_config=genre_config
        #)
        lore_elements = self.lore_ui.generate_lore()

        # 3. Create high-level story structure
        story_outline = self.structure_ui.generate_structure(
            parameters=current_params,
            genre_config=genre_config,
            lore=lore_elements
        )

        # 4. Plan scenes based on story structure
        scene_plan = self.outlining_ui.plan_scenes(
            parameters=current_params,
            genre_config=genre_config,
            story_structure=story_outline,
            lore=lore_elements
        )

        # 5. Initialize chapter writing interface
        self.chapter_writing_ui.initialize_chapters(
            parameters=current_params,
            genre_config=genre_config,
            scene_plan=scene_plan,
            lore=lore_elements
        )

        # 6. Switch to the chapter writing tab
        self.notebook.select(self.chapter_writing_frame)

        return {
            "parameters": current_params,
            "lore": lore_elements,
            "story_structure": story_outline,
            "scene_plan": scene_plan
        }
    
    # ==================== AGENTIC WORKFLOW METHODS ====================
    
    def create_agentic_controls(self):
        """Add agentic workflow controls to the GUI."""
        if not AGENTIC_AVAILABLE:
            return
            
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
            text="🔍 Analyze Content",
            command=self.analyze_current_content,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.analyze_content_btn.pack(side="left", padx=5)
        
        # Quality standards
        quality_frame = tk.LabelFrame(agentic_frame, text="Quality Standards", padx=5, pady=5)
        quality_frame.pack(fill="x", pady=5)
        
        # Quality threshold
        threshold_frame = tk.Frame(quality_frame)
        threshold_frame.pack(fill="x")
        
        tk.Label(threshold_frame, text="Quality Threshold:").pack(side="left")
        self.quality_threshold = tk.DoubleVar(value=0.7)
        threshold_scale = tk.Scale(
            threshold_frame,
            from_=0.1,
            to=1.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.quality_threshold
        )
        threshold_scale.pack(side="left", fill="x", expand=True)
        
        # Auto-retry option
        self.auto_retry = tk.BooleanVar(value=True)
        retry_check = tk.Checkbutton(
            quality_frame,
            text="Auto-retry on quality issues",
            variable=self.auto_retry
        )
        retry_check.pack(anchor="w")
    
    def toggle_agentic_mode(self):
        """Toggle agentic workflow mode."""
        if not AGENTIC_AVAILABLE:
            self.notifications.show_error("Error", "Agentic features are not available")
            self.agentic_enabled.set(False)
            return
            
        enabled = self.agentic_enabled.get()
        
        if enabled:
            try:
                self.init_agentic_orchestrators()
                self.workflow_status.config(text="Agentic mode enabled - Ready for workflow", fg="green")
                self.logger.info("Agentic workflow mode enabled")
            except Exception as e:
                self.logger.error(f"Failed to enable agentic mode: {e}")
                self.notifications.show_error("Error", f"Failed to enable agentic mode: {e}")
                self.agentic_enabled.set(False)
        else:
            self.story_orchestrator = None
            self.analysis_orchestrator = None
            self.workflow_status.config(text="Agentic mode disabled", fg="gray")
            self.logger.info("Agentic workflow mode disabled")
    
    def init_agentic_orchestrators(self):
        """Initialize agentic orchestrators."""
        try:
            # Initialize story generation orchestrator
            self.story_orchestrator = StoryGenerationOrchestrator(
                model=self.get_selected_model(),
                output_dir=self.get_output_dir(),
                logger=self.logger
            )
            # Give orchestrator access to app instance for real function calls
            self.story_orchestrator.app_instance = self
            
            # Initialize analysis orchestrator
            self.analysis_orchestrator = MultiAgentOrchestrator(
                model=self.get_selected_model(),
                output_dir=self.get_output_dir(),
                logger=self.logger
            )
            
            self.logger.info("Agentic orchestrators initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrators: {e}")
            raise
    
    def start_complete_workflow(self):
        """Start the complete agentic story generation workflow."""
        if not AGENTIC_AVAILABLE:
            self.notifications.show_warning("Warning", "Agentic features are not available")
            return
            
        if not self.agentic_enabled.get():
            self.notifications.show_warning("Warning", "Please enable agentic mode first")
            return
            
        if not self.story_orchestrator:
            self.notifications.show_error("Error", "Agentic orchestrators not initialized")
            return
        
        try:
            # Gather story parameters
            story_params = self.gather_story_parameters()
            
            if not story_params:
                self.notifications.show_warning("Warning", "Please fill in story parameters first")
                return
            
            # Update workflow status
            self.workflow_status.config(text="Starting complete workflow...", fg="orange")
            self.workflow_progress['value'] = 0
            self.root.update()
            
            self.logger.info("Starting complete agentic workflow")
            
            # Execute the workflow
            generation_result = self.story_orchestrator.execute_complete_workflow(
                story_parameters=story_params,
                quality_threshold=self.quality_threshold.get(),
                auto_retry=self.auto_retry.get()
            )
            
            if generation_result.success:
                self.handle_workflow_success(generation_result)
            else:
                self.handle_workflow_error(generation_result.messages)
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            self.handle_workflow_error([str(e)])
    
    def resume_workflow(self):
        """Resume an interrupted workflow."""
        if not AGENTIC_AVAILABLE or not self.agentic_enabled.get() or not self.story_orchestrator:
            show_warning("Warning", "Please enable agentic mode first")
            return
        
        try:
            # Check for existing workflow state
            current_content = self.get_current_content()
            
            if not current_content:
                show_info("Info", "No existing content found to resume from")
                return
            
            # Update status
            self.workflow_status.config(text="Resuming workflow...", fg="orange")
            self.root.update()
            
            # Resume the workflow
            generation_result = self.story_orchestrator.resume_workflow(
                existing_content=current_content,
                quality_threshold=self.quality_threshold.get()
            )
            
            if generation_result.success:
                self.handle_workflow_success(generation_result, resumed=True)
            else:
                self.handle_workflow_error(generation_result.messages)
                
        except Exception as e:
            self.logger.error(f"Workflow resume failed: {e}")
            self.handle_workflow_error([str(e)])
    
    def analyze_current_content(self):
        """Analyze current content with agentic agents."""
        if not AGENTIC_AVAILABLE or not self.agentic_enabled.get() or not self.analysis_orchestrator:
            show_warning("Warning", "Please enable agentic mode first")
            return
        
        try:
            # Get current content
            current_content = self.get_current_content()
            
            if not current_content:
                show_info("Info", "No content available to analyze")
                return
            
            # Update status
            self.workflow_status.config(text="Analyzing content...", fg="orange")
            self.root.update()
            
            # Perform analysis
            analysis_result = self.analysis_orchestrator.process_task({
                "type": "analyze_content",
                "parameters": {
                    "content": current_content,
                    "analysis_type": "comprehensive"
                }
            })
            
            if analysis_result.success:
                self.show_analysis_results(analysis_result)
            else:
                self.notifications.show_error("Analysis Error", "\n".join(analysis_result.messages))
                
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            self.notifications.show_error("Error", f"Analysis failed: {e}")
    
    def gather_story_parameters(self) -> Optional[Dict[str, Any]]:
        """Gather story parameters from the GUI."""
        try:
            return self.param_ui.get_current_parameters()
        except Exception as e:
            self.logger.error(f"Failed to gather parameters: {e}")
            return None
    
    def get_current_content(self) -> Dict[str, Any]:
        """Get content from the currently active tab."""
        # This would need to be implemented based on your specific UI structure
        # For now, return empty dict
        return {}
    
    def handle_workflow_success(self, generation_result, resumed=False):
        """Handle successful workflow completion."""
        # Update progress
        self.workflow_progress['value'] = self.workflow_progress['maximum']
        action = "resumed" if resumed else "completed"
        self.workflow_status.config(text=f"Workflow {action} successfully!", fg="green")
        
        # Show results
        self.show_workflow_results(generation_result, resumed)
        
        # Switch to appropriate tab
        self.notebook.select(self.chapter_writing_frame)
        
        self.logger.info(f"Workflow {action} successfully")
    
    def handle_workflow_error(self, error_messages):
        """Handle workflow errors."""
        error_text = "\n".join(error_messages) if isinstance(error_messages, list) else str(error_messages)
        
        self.workflow_status.config(text="Workflow failed", fg="red")
        
        self.notifications.show_error("Workflow Error", f"Workflow execution failed:\n\n{error_text}")
        
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
        
        # Add basic result information
        if hasattr(generation_result, 'data') and generation_result.data:
            results_text += f"📊 Generated Content: {len(generation_result.data)} sections\n"
        
        if hasattr(generation_result, 'messages') and generation_result.messages:
            results_text += f"📋 Messages: {len(generation_result.messages)}\n"
            for msg in generation_result.messages[:5]:  # Show first 5 messages
                results_text += f"   • {msg}\n"
        
        results_text += "\n🎉 Your story generation workflow has completed successfully!"
        
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
        if hasattr(analysis_result, 'data') and analysis_result.data:
            show_success(
                "Analysis Complete",
                f"Content Analysis Complete!\n\n"
                f"Analysis completed successfully.\n"
                f"Check the logs for detailed analysis."
            )
        else:
            show_success("Analysis Complete", "Content analysis completed.")
        
        self.workflow_status.config(text="Analysis complete", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()