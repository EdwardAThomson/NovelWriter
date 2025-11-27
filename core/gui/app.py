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
from core.generation.ai_helper import get_supported_models, set_backend, get_backend, check_cli_availability, get_available_backends
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

        # --- Add Backend and Model Selection ---
        self.model_frame = ttk.Frame(root)
        self.model_frame.pack(pady=5, padx=10, fill='x')

        # Backend selection
        ttk.Label(self.model_frame, text="Backend:").pack(side="left", padx=(5, 2))
        
        self.available_backends = self._get_available_backends_list()
        self.selected_backend_var = tk.StringVar(value="api")
        
        self.backend_combobox = ttk.Combobox(
            self.model_frame,
            textvariable=self.selected_backend_var,
            values=self.available_backends,
            state="readonly",
            width=12
        )
        self.backend_combobox.pack(side="left", padx=(0, 10))
        self.backend_combobox.bind("<<ComboboxSelected>>", self._on_backend_changed)

        # Model selection (for API backend)
        self.model_label = ttk.Label(self.model_frame, text="Model:")
        self.model_label.pack(side="left", padx=(5, 2))

        # Get available models dynamically
        self.available_models = get_supported_models()
        if not self.available_models:
            self.available_models = ["gpt-4o"]

        self.selected_model_var = tk.StringVar(value=self.available_models[0] if self.available_models else "")

        self.model_combobox = ttk.Combobox(
            self.model_frame,
            textvariable=self.selected_model_var,
            values=self.available_models,
            state="readonly"
        )
        self.model_combobox.pack(side="left", fill='x', expand=True)
        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_changed)
        
        # CLI availability indicator
        self.cli_status_label = ttk.Label(self.model_frame, text="", foreground="gray")
        self.cli_status_label.pack(side="right", padx=5)
        self._update_cli_status()
        # --- End Backend and Model Selection ---

        # Create main horizontal container
        self.main_container = tk.Frame(root)
        self.main_container.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Left side: Notebook with tabs
        self.left_panel = tk.Frame(self.main_container)
        self.left_panel.pack(side="left", expand=True, fill="both", padx=(0, 5))
        
        # Create notebook in left panel
        self.notebook = ttk.Notebook(self.left_panel)
        self.notebook.pack(expand=True, fill="both")
        
        # Right side: Persistent workflow progress panel
        self.right_panel = tk.Frame(self.main_container, width=400)
        self.right_panel.pack(side="right", fill="y", padx=(5, 0))
        self.right_panel.pack_propagate(False)  # Maintain fixed width

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
        
        # Workflow Tab (Agentic Automation)
        self.workflow_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.workflow_frame, text="🤖 Workflow")
        
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

        # Initialize workflow progress panel (always available)
        self.create_workflow_progress_panel()
        
        # Initialize agentic components if available
        if AGENTIC_AVAILABLE:
            self.story_orchestrator = None
            self.analysis_orchestrator = None
            self.agentic_enabled = tk.BooleanVar(value=False)
            
            # Workflow state
            self.current_workflow_step = "parameters"
            self.workflow_completed_steps = []
            
            # Add agentic controls to the workflow tab
            self.create_agentic_controls()
            
            # Load initial workflow state and refresh progress display
            self.load_initial_workflow_state()
        else:
            self.agentic_enabled = None
            self.logger.warning("Agentic features disabled - orchestrators not available")
            # Still show progress panel but with limited functionality
            self.load_initial_workflow_state()

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

    def get_selected_backend(self):
        """Returns the currently selected LLM backend."""
        return self.selected_backend_var.get()

    def _get_available_backends_list(self):
        """Get list of available backends for the dropdown."""
        try:
            backends = get_available_backends()
            return list(backends.keys())
        except Exception:
            return ["api"]  # Fallback to API only
    
    def _on_backend_changed(self, event=None):
        """Handle backend selection change."""
        backend = self.selected_backend_var.get()
        model = self.selected_model_var.get()
        
        # Update model selector visibility based on backend
        if backend == "api":
            self.model_label.pack(side="left", padx=(5, 2))
            self.model_combobox.pack(side="left", fill='x', expand=True)
        else:
            # Hide model selector for CLI backends
            self.model_label.pack_forget()
            self.model_combobox.pack_forget()
        
        # Set the backend in ai_helper
        try:
            set_backend(backend, model)
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"Backend changed to: {backend}" + (f" (model: {model})" if backend == "api" else ""))
            show_success("Backend Changed", f"{backend}" + (f" ({model})" if backend == "api" else ""))
        except RuntimeError as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Failed to set backend {backend}: {e}")
            show_error("Backend Error", f"Backend unavailable: {e}")
            # Revert to API
            self.selected_backend_var.set("api")
            self._on_backend_changed()
        
        self._update_cli_status()
    
    def _on_model_changed(self, event=None):
        """Handle model selection change."""
        backend = self.selected_backend_var.get()
        model = self.selected_model_var.get()
        
        if backend == "api":
            try:
                set_backend(backend, model)
                if hasattr(self, 'logger') and self.logger:
                    self.logger.info(f"Model changed to: {model}")
            except Exception as e:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.error(f"Failed to set model {model}: {e}")
    
    def _update_cli_status(self):
        """Update the CLI availability status indicator."""
        try:
            cli_status = check_cli_availability()
            available = [name for name, avail in cli_status.items() if avail]
            if available:
                self.cli_status_label.config(
                    text=f"CLI: {', '.join(available)}",
                    foreground="green"
                )
            else:
                self.cli_status_label.config(
                    text="No CLI tools detected",
                    foreground="gray"
                )
        except Exception:
            self.cli_status_label.config(text="", foreground="gray")

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
        """Add agentic workflow controls to the workflow tab only."""
        if not AGENTIC_AVAILABLE:
            return
            
        # Create workflow controls container (full width in workflow tab)
        workflow_container = tk.Frame(self.workflow_frame)
        workflow_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create agentic frame
        agentic_frame = tk.LabelFrame(workflow_container, text="🤖 Workflow Controls", padx=10, pady=10)
        agentic_frame.pack(fill="x", pady=(0, 5))
        
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
        
        # Individual Step Controls
        step_controls_frame = tk.LabelFrame(workflow_container, text="🎯 Individual Step Controls", padx=5, pady=5)
        step_controls_frame.pack(fill="x", pady=5)
        
        step_info = tk.Label(
            step_controls_frame,
            text="Execute specific workflow steps independently:",
            font=("Arial", 9),
            fg="darkblue"
        )
        step_info.pack(anchor="w", pady=(0, 5))
        
        # Row 1: Lore and Structure
        step_row1 = tk.Frame(step_controls_frame)
        step_row1.pack(fill="x", pady=2)
        
        self.lore_step_btn = tk.Button(
            step_row1,
            text="📚 Generate Lore",
            command=lambda: self.execute_single_step("lore"),
            bg="#9C27B0",
            fg="white",
            font=("Arial", 9, "bold"),
            width=15
        )
        self.lore_step_btn.pack(side="left", padx=2)
        
        self.structure_step_btn = tk.Button(
            step_row1,
            text="🏗️ Generate Structure",
            command=lambda: self.execute_single_step("structure"),
            bg="#673AB7",
            fg="white",
            font=("Arial", 9, "bold"),
            width=15
        )
        self.structure_step_btn.pack(side="left", padx=2)
        
        # Row 2: Scenes and Chapters
        step_row2 = tk.Frame(step_controls_frame)
        step_row2.pack(fill="x", pady=2)
        
        self.scenes_step_btn = tk.Button(
            step_row2,
            text="🎬 Plan Scenes",
            command=lambda: self.execute_single_step("scenes"),
            bg="#3F51B5",
            fg="white",
            font=("Arial", 9, "bold"),
            width=15
        )
        self.scenes_step_btn.pack(side="left", padx=2)
        
        self.chapters_step_btn = tk.Button(
            step_row2,
            text="📖 Write Chapters",
            command=lambda: self.execute_single_step("chapters"),
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            width=15
        )
        self.chapters_step_btn.pack(side="left", padx=2)
        
        # Checkpoint controls - COMMENTED OUT FOR NOW
        # checkpoint_frame = tk.LabelFrame(workflow_container, text="🚐 Checkpoint Controls", padx=5, pady=5)
        # checkpoint_frame.pack(fill="x", pady=5)
        
        # # Checkpoint mode toggle
        # self.checkpoint_mode = tk.BooleanVar(value=False)
        # checkpoint_check = tk.Checkbutton(
        #     checkpoint_frame,
        #     text="Enable Checkpoint Mode (Pause at each step for approval)",
        #     variable=self.checkpoint_mode,
        #     command=self.toggle_checkpoint_mode,
        #     font=("Arial", 10)
        # )
        # checkpoint_check.pack(anchor="w", pady=2)
        
        # # Checkpoint status
        # self.checkpoint_status = tk.Label(
        #     checkpoint_frame,
        #     text="Checkpoint mode disabled",
        #     font=("Arial", 9),
        #     fg="gray"
        # )
        # self.checkpoint_status.pack(anchor="w", pady=2)
        
        # # Checkpoint action buttons
        # checkpoint_actions = tk.Frame(checkpoint_frame)
        # checkpoint_actions.pack(fill="x", pady=2)
        
        # self.approve_btn = tk.Button(
        #     checkpoint_actions,
        #     text="✅ Approve & Continue",
        #     command=self.approve_checkpoint,
        #     bg="#4CAF50",
        #     fg="white",
        #     font=("Arial", 9, "bold"),
        #     state="disabled"
        # )
        # self.approve_btn.pack(side="left", padx=2)
        
        # self.retry_btn = tk.Button(
        #     checkpoint_actions,
        #     text="🔄 Retry Step",
        #     command=self.retry_checkpoint,
        #     bg="#FF9800",
        #     fg="white",
        #     font=("Arial", 9, "bold"),
        #     state="disabled"
        # )
        # self.retry_btn.pack(side="left", padx=2)
        
        # self.review_btn = tk.Button(
        #     checkpoint_actions,
        #     text="📋 Review Step",
        #     command=self.review_checkpoint,
        #     bg="#9C27B0",
        #     fg="white",
        #     font=("Arial", 9, "bold"),
        #     state="disabled"
        # )
        # self.review_btn.pack(side="left", padx=2)
        
        # Initialize checkpoint mode variable for compatibility
        self.checkpoint_mode = tk.BooleanVar(value=False)
        
        # Quality standards
        quality_frame = tk.LabelFrame(workflow_container, text="Quality Standards", padx=5, pady=5)
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
    
    def create_workflow_progress_panel(self):
        """Create persistent workflow progress panel in right panel."""
            
        # Progress Display Panel (persistent across all tabs)
        progress_display_frame = tk.LabelFrame(self.right_panel, text="📈 Workflow Progress", padx=5, pady=5)
        progress_display_frame.pack(fill="both", expand=True, pady=5)
        
        # Progress steps display with improved layout
        self.progress_steps_frame = tk.Frame(progress_display_frame)
        self.progress_steps_frame.pack(fill="both", expand=True, pady=2)
        
        # Create step indicators with better labels
        self.step_indicators = {}
        self.step_labels = {}
        self.file_counts = {}
        self.step_buttons = {}  # For clickable step details
        
        steps = [
            ("lore", "📚 Lore Generation", "World-building & Background"),
            ("structure", "🏗️ Story Structure", "Plot & Story Arcs"), 
            ("scenes", "🎬 Scene Planning", "Detailed Scene Outlines"),
            ("chapters", "📖 Chapter Writing", "Final Story Content")
        ]
        
        for i, (step_name, step_label, step_description) in enumerate(steps):
            # Create a detailed step frame (vertical layout for right panel)
            step_frame = tk.LabelFrame(self.progress_steps_frame, text=step_label, 
                                     font=("Arial", 10, "bold"), padx=5, pady=5)
            step_frame.pack(fill="x", padx=2, pady=3)
            
            # Status indicator with larger, clearer display
            status_frame = tk.Frame(step_frame)
            status_frame.pack(fill="x")
            
            indicator = tk.Label(status_frame, text="○", font=("Arial", 16), fg="gray")
            indicator.pack(side="left")
            self.step_indicators[step_name] = indicator
            
            # Status text
            status_text = tk.Label(status_frame, text="Not Started", 
                                 font=("Arial", 9), fg="gray")
            status_text.pack(side="left", padx=(8, 0))
            self.step_labels[step_name] = status_text
            
            # Description
            desc_label = tk.Label(step_frame, text=step_description, 
                                font=("Arial", 8), fg="darkblue", wraplength=300)
            desc_label.pack(fill="x", pady=(2, 0))
            
            # File count with better formatting
            file_count = tk.Label(step_frame, text="📁 0 files", 
                                font=("Arial", 8), fg="gray")
            file_count.pack(fill="x")
            self.file_counts[step_name] = file_count
            
            # Clickable button for file details
            details_btn = tk.Button(step_frame, text="📋 View Files", 
                                  command=lambda s=step_name: self.show_step_files(s),
                                  font=("Arial", 8), state="disabled")
            details_btn.pack(fill="x", pady=(2, 0))
            self.step_buttons[step_name] = details_btn
        
        # Progress summary
        self.progress_summary = tk.Label(
            progress_display_frame,
            text="No workflow loaded",
            font=("Arial", 10),
            fg="gray"
        )
        self.progress_summary.pack(pady=5)
        
        # Progress navigation buttons
        nav_frame = tk.Frame(progress_display_frame)
        nav_frame.pack(fill="x", pady=5)
        
        self.refresh_progress_btn = tk.Button(
            nav_frame,
            text="🔄 Refresh",
            command=self.refresh_progress_display,
            font=("Arial", 9),
            bg="#4CAF50",
            fg="white"
        )
        self.refresh_progress_btn.pack(fill="x", pady=2)
        
        self.reset_workflow_btn = tk.Button(
            nav_frame,
            text="🚫 Reset Workflow",
            command=self.reset_workflow_state,
            font=("Arial", 9),
            bg="#f44336",
            fg="white"
        )
        self.reset_workflow_btn.pack(fill="x", pady=2)
        
        self.scan_existing_btn = tk.Button(
            nav_frame,
            text="🔍 Scan Existing Work",
            command=self.create_from_existing_work,
            font=("Arial", 9),
            bg="#03A9F4",
            fg="white"
        )
        self.scan_existing_btn.pack(fill="x", pady=2)
    
    def load_initial_workflow_state(self):
        """Load and display initial workflow state on startup."""
        try:
            if AGENTIC_AVAILABLE:
                # Initialize checkpoint state manager to scan existing files
                from agents.orchestration.checkpoint_state import CheckpointStateManager
                
                checkpoint_manager = CheckpointStateManager(self.get_output_dir())
                workflow_state = checkpoint_manager.load_state()
                
                # If no state exists, create one from existing work
                if workflow_state is None:
                    # Get current parameters for state creation
                    current_params = self.param_ui.get_current_parameters() if hasattr(self, 'param_ui') else {}
                    workflow_state = checkpoint_manager.create_from_existing_work(current_params)
                
                # Scan for existing files to update progress display
                checkpoint_manager.scan_output_files(workflow_state)
                
                # Update progress display with current state
                self.update_progress_display_from_state(workflow_state)
                
                self.logger.info("Initial workflow state loaded and progress display updated")
            else:
                # Even without agentic features, scan for existing files
                self.scan_existing_files_basic()
                
        except Exception as e:
            self.logger.warning(f"Could not load initial workflow state: {e}")
            # Set default state
            self.progress_summary.config(text="No workflow data available")
    
    def scan_existing_files_basic(self):
        """Basic file scanning when agentic features are not available."""
        try:
            output_dir = self.get_output_dir()
            
            # Define expected files for each step
            expected_files = {
                "lore": ["story/lore/characters.json", "story/lore/generated_lore.md"],
                "structure": ["story/structure/story_structure.json", "story/structure/detailed_structure.md"],
                "scenes": ["story/planning/scene_plans.json", "story/planning/scene_outlines.md"],
                "chapters": ["story/content/chapter_*.md"]
            }
            
            # Check each step and update display
            for step_name, file_patterns in expected_files.items():
                file_count = 0
                for pattern in file_patterns:
                    if '*' in pattern:
                        import glob
                        full_pattern = os.path.join(output_dir, pattern)
                        matches = glob.glob(full_pattern)
                        file_count += len(matches)
                    else:
                        full_path = os.path.join(output_dir, pattern)
                        if os.path.exists(full_path):
                            file_count += 1
                
                # Update display
                if step_name in self.file_counts:
                    self.file_counts[step_name].config(text=f"📁 {file_count} files")
                    
                if step_name in self.step_indicators and file_count > 0:
                    self.step_indicators[step_name].config(text="✅", fg="green")
                    self.step_labels[step_name].config(text="Files Found", fg="green")
                    if step_name in self.step_buttons:
                        self.step_buttons[step_name].config(state="normal")
            
            # Update summary
            total_files = sum(int(label.cget("text").split()[1]) for label in self.file_counts.values() if label.cget("text").split()[1].isdigit())
            self.progress_summary.config(text=f"Found {total_files} existing files across workflow steps")
            
        except Exception as e:
            self.logger.warning(f"Error in basic file scanning: {e}")
    
    def update_progress_display_from_state(self, workflow_state):
        """Update progress display from loaded workflow state."""
        try:
            for step_name, step_data in workflow_state.steps.items():
                if step_name in self.step_indicators:
                    # Update status indicator
                    if step_data.status.value == "completed":
                        self.step_indicators[step_name].config(text="✅", fg="green")
                        self.step_labels[step_name].config(text="Completed", fg="green")
                    elif step_data.status.value == "in_progress":
                        self.step_indicators[step_name].config(text="🔄", fg="orange")
                        self.step_labels[step_name].config(text="In Progress", fg="orange")
                    elif step_data.status.value == "failed":
                        self.step_indicators[step_name].config(text="❌", fg="red")
                        self.step_labels[step_name].config(text="Failed", fg="red")
                    else:
                        self.step_indicators[step_name].config(text="○", fg="gray")
                        self.step_labels[step_name].config(text="Not Started", fg="gray")
                    
                    # Update file count
                    file_count = len(step_data.output_files)
                    if step_name in self.file_counts:
                        self.file_counts[step_name].config(text=f"📁 {file_count} files")
                    
                    # Enable/disable details button
                    if step_name in self.step_buttons:
                        if file_count > 0:
                            self.step_buttons[step_name].config(state="normal")
                        else:
                            self.step_buttons[step_name].config(state="disabled")
            
            # Update summary
            completed_steps = [name for name, step in workflow_state.steps.items() if step.status.value == "completed"]
            total_files = sum(len(step.output_files) for step in workflow_state.steps.values())
            
            if completed_steps:
                self.progress_summary.config(
                    text=f"Workflow: {len(completed_steps)}/4 steps completed, {total_files} files generated"
                )
            else:
                self.progress_summary.config(text=f"Workflow ready to start - {total_files} existing files found")
                
        except Exception as e:
            self.logger.warning(f"Error updating progress display from state: {e}")
    
    def toggle_agentic_mode(self):
        """Toggle agentic workflow mode."""
        if not AGENTIC_AVAILABLE:
            show_error("Error", "Agentic features are not available")
            self.agentic_enabled.set(False)
            return
            
        enabled = self.agentic_enabled.get()
        
        if enabled:
            try:
                self.init_agentic_orchestrators()
                self.workflow_status.config(text="Agentic mode enabled - Ready for workflow", fg="green")
                # Progress display is already loaded on startup, just refresh if needed
                if hasattr(self, 'story_orchestrator') and self.story_orchestrator:
                    self.refresh_progress_display()
                self.logger.info("Agentic workflow mode enabled")
            except Exception as e:
                self.logger.error(f"Failed to enable agentic mode: {e}")
                show_error("Error", f"Failed to enable agentic mode: {e}")
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
            show_warning("Warning", "Agentic features are not available")
            return
            
        if not self.agentic_enabled.get():
            show_warning("Warning", "Please enable agentic mode first")
            return
            
        if not self.story_orchestrator:
            show_error("Error", "Agentic orchestrators not initialized")
            return
        
        try:
            # Gather story parameters
            story_params = self.gather_story_parameters()
            
            if not story_params:
                show_warning("Warning", "Please fill in story parameters first")
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
            
            # Handle dictionary result format
            if generation_result["success"]:
                self.handle_workflow_success(generation_result)
            else:
                error_messages = generation_result.get("recommendations", [generation_result.get("error", "Unknown error")])
                self.handle_workflow_error(error_messages)
                
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
            
            # Resume the workflow using process_task method
            task_data = {
                "story_parameters": self.gather_story_parameters(),
                "generation_mode": "resume",
                "target_steps": ["lore", "structure", "scenes", "chapters"],
                "quality_standards": {"overall": self.quality_threshold.get()},
                "use_validation": True
            }
            
            generation_result = self.story_orchestrator.process_task(task_data)
            
            if generation_result.success:
                self.handle_workflow_success(generation_result, resumed=True)
            else:
                self.handle_workflow_error(generation_result.messages)
                
        except Exception as e:
            self.logger.error(f"Workflow resume failed: {e}")
            self.handle_workflow_error([str(e)])
    
    def analyze_current_content(self):
        """Analyze current content with agentic agents."""
        if not AGENTIC_AVAILABLE or not self.agentic_enabled.get():
            show_warning("Warning", "Agentic mode is not enabled")
            return
        
        if not self.analysis_orchestrator:
            show_warning("Warning", "Multi-agent orchestrator not initialized")
            return
        
        try:
            # Get current content for analysis
            current_content = self.get_current_content()
            
            if not current_content:
                show_info("Info", "No content found to analyze")
                return
            
            # Analyze with multi-agent orchestrator
            analysis_result = self.analysis_orchestrator.analyze_content(current_content)
            
            if analysis_result.success:
                self.show_analysis_results(analysis_result)
                show_success("Success", "Content analysis completed successfully")
            else:
                show_error("Error", f"Content analysis failed: {analysis_result.error_message}")
                
        except Exception as e:
            self.logger.error(f"Content analysis error: {e}")
            show_error("Error", f"Content analysis failed: {str(e)}")
    
    def execute_single_step(self, step_name: str):
        """Execute a single workflow step and halt."""
        if not AGENTIC_AVAILABLE or not self.agentic_enabled.get():
            show_warning("Warning", "Agentic mode is not enabled")
            return
        
        if not self.story_orchestrator:
            show_warning("Warning", "Story orchestrator not initialized")
            return
        
        try:
            self.logger.info(f"🎯 Starting single step execution: {step_name}")
            
            # Disable step buttons during execution
            self._disable_step_buttons()
            
            # Update UI to show step in progress
            self.workflow_status.config(text=f"Executing {step_name} step...", fg="orange")
            
            # Gather current parameters
            story_parameters = self.gather_story_parameters()
            
            # Load or create workflow state
            self.story_orchestrator.load_or_create_workflow_state(story_parameters)
            
            # Execute the specific step
            step_result = self.story_orchestrator.execute_single_step(step_name, story_parameters)
            
            if step_result.success:
                # Update progress display
                self.refresh_progress_display()
                
                # Show success message with step details
                step_emoji = {"lore": "📚", "structure": "🏗️", "scenes": "🎬", "chapters": "📖"}
                emoji = step_emoji.get(step_name, "✅")
                
                success_msg = f"{emoji} {step_name.title()} step completed successfully!"
                if step_result.quality_scores and step_name in step_result.quality_scores:
                    quality_score = step_result.quality_scores[step_name]
                    if quality_score is not None:
                        success_msg += f"\nQuality Score: {quality_score:.2f}"
                
                show_success("Step Completed", success_msg)
                
                self.workflow_status.config(text=f"{step_name.title()} step completed", fg="green")
                self.logger.info(f"✅ Single step execution completed: {step_name}")
                
            else:
                error_msg = f"Failed to execute {step_name} step"
                if hasattr(step_result, 'error_message') and step_result.error_message:
                    error_msg += f": {step_result.error_message}"
                
                show_error("Step Failed", error_msg)
                self.workflow_status.config(text=f"{step_name.title()} step failed", fg="red")
                self.logger.error(f"❌ Single step execution failed: {step_name}")
                
        except Exception as e:
            self.logger.error(f"Single step execution error for {step_name}: {e}")
            show_error("Error", f"Failed to execute {step_name} step: {str(e)}")
            self.workflow_status.config(text=f"{step_name.title()} step error", fg="red")
        
        finally:
            # Re-enable step buttons
            self._enable_step_buttons()
    
    def _disable_step_buttons(self):
        """Disable all individual step buttons during execution."""
        if hasattr(self, 'lore_step_btn'):
            self.lore_step_btn.config(state="disabled")
        if hasattr(self, 'structure_step_btn'):
            self.structure_step_btn.config(state="disabled")
        if hasattr(self, 'scenes_step_btn'):
            self.scenes_step_btn.config(state="disabled")
        if hasattr(self, 'chapters_step_btn'):
            self.chapters_step_btn.config(state="disabled")
    
    def _enable_step_buttons(self):
        """Enable all individual step buttons after execution."""
        if hasattr(self, 'lore_step_btn'):
            self.lore_step_btn.config(state="normal")
        if hasattr(self, 'structure_step_btn'):
            self.structure_step_btn.config(state="normal")
        if hasattr(self, 'scenes_step_btn'):
            self.scenes_step_btn.config(state="normal")
        if hasattr(self, 'chapters_step_btn'):
            self.chapters_step_btn.config(state="normal")

    def gather_story_parameters(self):
        """Gather story parameters from the GUI."""
        try:
            return self.param_ui.get_current_parameters()
        except Exception as e:
            self.logger.error(f"Failed to gather parameters: {e}")
            return {}
    
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
        
        show_error("Workflow Error", f"Workflow execution failed:\n\n{error_text}")
        
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
        
        # Add basic result information - handle both dict and object formats
        if isinstance(generation_result, dict):
            content = generation_result.get('content', {})
            if content:
                results_text += f"📊 Generated Content: {len(content)} sections\n"
            
            recommendations = generation_result.get('recommendations', [])
            if recommendations:
                results_text += f"📋 Recommendations: {len(recommendations)}\n"
                for msg in recommendations[:5]:  # Show first 5 recommendations
                    results_text += f"   • {msg}\n"
            
            quality_scores = generation_result.get('quality_scores', {})
            if quality_scores:
                results_text += f"⭐ Quality Scores:\n"
                for step, score in quality_scores.items():
                    results_text += f"   • {step}: {score:.2f}\n"
        else:
            # Legacy object format
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
    
    # ==================== CHECKPOINT CONTROL METHODS ====================
    
    def toggle_checkpoint_mode(self):
        """Toggle checkpoint mode on/off."""
        if not AGENTIC_AVAILABLE or not self.agentic_enabled.get():
            show_warning("Warning", "Please enable agentic mode first")
            self.checkpoint_mode.set(False)
            return
        
        enabled = self.checkpoint_mode.get()
        
        if enabled:
            # Enable checkpoint mode
            if self.story_orchestrator:
                self.story_orchestrator.enable_checkpoint_mode(self.on_checkpoint_reached)
                self.checkpoint_status.config(text="Checkpoint mode enabled - Will pause at each step", fg="green")
                self.logger.info("🚦 Checkpoint mode enabled")
            else:
                show_error("Error", "Orchestrator not initialized")
                self.checkpoint_mode.set(False)
        else:
            # Disable checkpoint mode
            if self.story_orchestrator:
                self.story_orchestrator.disable_checkpoint_mode()
            self.checkpoint_status.config(text="Checkpoint mode disabled", fg="gray")
            self._disable_checkpoint_buttons()
            self.logger.info("🚦 Checkpoint mode disabled")
    
    def on_checkpoint_reached(self, checkpoint):
        """Called when a workflow checkpoint is reached."""
        self.logger.info(f"🚦 Checkpoint reached: {checkpoint.step_name}")
        
        # Update UI on main thread
        self.root.after(0, self._update_checkpoint_ui, checkpoint)
    
    def _update_checkpoint_ui(self, checkpoint):
        """Update the UI when a checkpoint is reached (main thread)."""
        # Update status
        self.checkpoint_status.config(
            text=f"Waiting for approval: {checkpoint.step_name.title()} step completed",
            fg="orange"
        )
        
        # Update workflow status
        self.workflow_status.config(
            text=f"⏸️ Paused at {checkpoint.step_name} - Awaiting approval",
            fg="orange"
        )
        
        # Enable checkpoint buttons
        self._enable_checkpoint_buttons()
        
        # Show checkpoint notification
        show_info(
            f"Checkpoint: {checkpoint.step_name.title()}",
            checkpoint.checkpoint_message
        )
        
        # Update progress
        completed_steps = len([s for s in ["lore", "structure", "scenes", "chapters"] 
                              if s in checkpoint.content_generated])
        self.workflow_progress['value'] = completed_steps
    
    def approve_checkpoint(self):
        """Approve the current checkpoint and continue workflow."""
        if not self.story_orchestrator:
            show_error("Error", "Orchestrator not available")
            return
        
        if self.story_orchestrator.approve_current_checkpoint():
            self.checkpoint_status.config(text="Step approved - Continuing workflow...", fg="green")
            self._disable_checkpoint_buttons()
            self.logger.info("✅ Checkpoint approved by user")
        else:
            show_warning("Warning", "No checkpoint to approve")
    
    def retry_checkpoint(self):
        """Retry the current checkpoint step."""
        if not self.story_orchestrator:
            show_error("Error", "Orchestrator not available")
            return
        
        if self.story_orchestrator.retry_current_checkpoint():
            self.checkpoint_status.config(text="Retrying step...", fg="orange")
            self._disable_checkpoint_buttons()
            self.logger.info("🔄 Checkpoint retry requested by user")
        else:
            show_warning("Warning", "No checkpoint to retry")
    
    def review_checkpoint(self):
        """Show detailed review of the current checkpoint."""
        if not self.story_orchestrator:
            show_error("Error", "Orchestrator not available")
            return
        
        checkpoint = self.story_orchestrator.get_current_checkpoint()
        if not checkpoint:
            show_warning("Warning", "No checkpoint to review")
            return
        
        self._show_checkpoint_review(checkpoint)
    
    def _show_checkpoint_review(self, checkpoint):
        """Show detailed checkpoint review in a popup window."""
        review_window = tk.Toplevel(self.root)
        review_window.title(f"📋 Checkpoint Review: {checkpoint.step_name.title()}")
        review_window.geometry("700x500")
        review_window.transient(self.root)
        
        # Create scrollable text widget
        text_frame = tk.Frame(review_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10))
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add checkpoint information
        review_text = f"""CHECKPOINT REVIEW: {checkpoint.step_name.upper()}
{'=' * 50}

Step: {checkpoint.step_name.title()}
Completed: {'Yes' if checkpoint.step_completed else 'No'}
Timestamp: {checkpoint.timestamp}
Retry Count: {checkpoint.retry_count}

Quality Score: {checkpoint.quality_score if checkpoint.quality_score else 'Not available'}

Next Steps: {', '.join(checkpoint.next_steps) if checkpoint.next_steps else 'None'}

Message:
{checkpoint.checkpoint_message}

{'=' * 50}
CONTENT GENERATED:
{'=' * 50}

"""
        
        # Add content information
        if checkpoint.content_generated:
            for key, value in checkpoint.content_generated.items():
                review_text += f"\n{key.upper()}:\n{'-' * 20}\n"
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        review_text += f"{sub_key}: {str(sub_value)[:200]}...\n"
                else:
                    review_text += f"{str(value)[:500]}...\n"
        
        text_widget.insert("1.0", review_text)
        text_widget.config(state="disabled")
        
        # Close button
        close_btn = tk.Button(
            review_window,
            text="Close",
            command=review_window.destroy,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold")
        )
        close_btn.pack(pady=10)
    
    def _enable_checkpoint_buttons(self):
        """Enable checkpoint control buttons."""
        self.approve_btn.config(state="normal")
        self.retry_btn.config(state="normal")
        self.review_btn.config(state="normal")
    
    def _disable_checkpoint_buttons(self):
        """Disable checkpoint control buttons."""
        self.approve_btn.config(state="disabled")
        self.retry_btn.config(state="disabled")
        self.review_btn.config(state="disabled")
    
    # ==================== PROGRESS DISPLAY METHODS ====================
    
    def refresh_progress_display(self):
        """Refresh the workflow progress display."""
        if not AGENTIC_AVAILABLE or not self.story_orchestrator:
            return
        
        try:
            # Get workflow state from orchestrator
            workflow_state = self.story_orchestrator.get_workflow_state()
            if not workflow_state:
                self.progress_summary.config(text="No workflow state available", fg="gray")
                return
            
            # Update step indicators
            for step_name in ["lore", "structure", "scenes", "chapters"]:
                step = workflow_state.steps.get(step_name)
                if not step:
                    continue
                
                indicator = self.step_indicators[step_name]
                status_label = self.step_labels[step_name]
                file_count = self.file_counts[step_name]
                details_btn = self.step_buttons[step_name]
                
                # Update indicator and status text based on status
                if step.status.value == "completed":
                    indicator.config(text="✓", fg="green")  # Checkmark
                    status_label.config(text="Completed", fg="green")
                    details_btn.config(state="normal")  # Enable file viewing
                elif step.status.value == "in_progress":
                    indicator.config(text="●", fg="orange")  # Filled circle
                    status_label.config(text="In Progress", fg="orange")
                    details_btn.config(state="normal" if step.output_files else "disabled")
                elif step.status.value == "failed":
                    indicator.config(text="✗", fg="red")  # X mark
                    status_label.config(text="Failed", fg="red")
                    details_btn.config(state="normal" if step.output_files else "disabled")
                else:
                    indicator.config(text="○", fg="gray")  # Empty circle
                    status_label.config(text="Not Started", fg="gray")
                    details_btn.config(state="disabled")
                
                # Update file count with better formatting
                file_count_text = f"📁 {len(step.output_files)} files"
                if len(step.output_files) > 0:
                    file_count.config(text=file_count_text, fg="blue")
                else:
                    file_count.config(text=file_count_text, fg="gray")
            
            # Update progress summary
            progress_summary = self.story_orchestrator.get_progress_summary()
            workflow_id = str(progress_summary.get('workflow_id', 'Unknown'))
            summary_text = f"Workflow: {workflow_id[:12]}... | "
            summary_text += f"Progress: {progress_summary.get('completion_percentage', 0):.0f}% | "
            summary_text += f"Current: {progress_summary.get('current_step') or 'Complete'} | "
            summary_text += f"Files: {progress_summary.get('total_output_files', 0)}"
            
            self.progress_summary.config(text=summary_text, fg="blue")
            
            self.logger.debug("Progress display refreshed")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh progress display: {e}")
            self.progress_summary.config(text="Error loading progress", fg="red")
    
    def show_step_files(self, step_name):
        """Show detailed file information for a specific step."""
        if not AGENTIC_AVAILABLE or not self.story_orchestrator:
            show_warning("Warning", "Agentic mode not available")
            return
        
        try:
            # Get current workflow state
            state = self.story_orchestrator.state_manager.load_state()
            if not state or step_name not in state.steps:
                show_warning("Warning", f"No data available for {step_name} step")
                return
            
            step = state.steps[step_name]
            
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title(f"📁 {step_name.title()} Step Files")
            popup.geometry("600x400")
            popup.transient(self.root)
            popup.grab_set()
            
            # Main frame
            main_frame = tk.Frame(popup, padx=10, pady=10)
            main_frame.pack(fill="both", expand=True)
            
            # Step info header
            header_frame = tk.Frame(main_frame)
            header_frame.pack(fill="x", pady=(0, 10))
            
            # Step status and info
            status_color = "green" if step.status.value == "completed" else "orange" if step.status.value == "in_progress" else "red" if step.status.value == "failed" else "gray"
            status_text = step.status.value.replace("_", " ").title()
            
            tk.Label(header_frame, text=f"📊 Status: {status_text}", 
                    font=("Arial", 12, "bold"), fg=status_color).pack(anchor="w")
            
            if step.quality_score:
                tk.Label(header_frame, text=f"⭐ Quality Score: {step.quality_score:.2f}", 
                        font=("Arial", 10)).pack(anchor="w")
            
            if step.started_at:
                tk.Label(header_frame, text=f"🕐 Started: {step.started_at[:19].replace('T', ' ')}", 
                        font=("Arial", 9), fg="gray").pack(anchor="w")
            
            if step.completed_at:
                tk.Label(header_frame, text=f"✅ Completed: {step.completed_at[:19].replace('T', ' ')}", 
                        font=("Arial", 9), fg="gray").pack(anchor="w")
            
            # Files section
            files_frame = tk.LabelFrame(main_frame, text="📁 Output Files", 
                                      font=("Arial", 11, "bold"), padx=5, pady=5)
            files_frame.pack(fill="both", expand=True, pady=(10, 0))
            
            # Files listbox with scrollbar
            list_frame = tk.Frame(files_frame)
            list_frame.pack(fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side="right", fill="y")
            
            files_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                     font=("Courier", 9))
            files_listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=files_listbox.yview)
            
            # Populate files list
            if step.output_files:
                for file_path in sorted(step.output_files):
                    # Show relative path and file size if exists
                    import os
                    full_path = os.path.join(self.get_output_dir(), file_path)
                    if os.path.exists(full_path):
                        size = os.path.getsize(full_path)
                        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                        files_listbox.insert(tk.END, f"📄 {file_path} ({size_str})")
                    else:
                        files_listbox.insert(tk.END, f"❌ {file_path} (missing)")
            else:
                files_listbox.insert(tk.END, "No files generated yet")
            
            # Buttons frame
            buttons_frame = tk.Frame(main_frame)
            buttons_frame.pack(fill="x", pady=(10, 0))
            
            # Refresh files button
            refresh_btn = tk.Button(buttons_frame, text="🔄 Refresh Files", 
                                  command=lambda: self.refresh_step_files_popup(step_name, files_listbox),
                                  font=("Arial", 9))
            refresh_btn.pack(side="left", padx=(0, 5))
            
            # Open folder button
            open_folder_btn = tk.Button(buttons_frame, text="📂 Open Folder", 
                                      command=lambda: self.open_step_folder(step_name),
                                      font=("Arial", 9))
            open_folder_btn.pack(side="left", padx=5)
            
            # Close button
            close_btn = tk.Button(buttons_frame, text="❌ Close", 
                                command=popup.destroy, font=("Arial", 9))
            close_btn.pack(side="right")
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
            y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            
        except Exception as e:
            self.logger.error(f"Failed to show step files for {step_name}: {e}")
            show_error("Error", f"Failed to load file details: {e}")
    
    def refresh_step_files_popup(self, step_name, listbox):
        """Refresh the files list in the popup."""
        try:
            # Trigger a file scan
            state = self.story_orchestrator.state_manager.load_state()
            if state:
                self.story_orchestrator.state_manager.scan_output_files(state)
                self.story_orchestrator.state_manager.save_state(state)
            
            # Clear and repopulate listbox
            listbox.delete(0, tk.END)
            
            if state and step_name in state.steps:
                step = state.steps[step_name]
                if step.output_files:
                    for file_path in sorted(step.output_files):
                        import os
                        full_path = os.path.join(self.get_output_dir(), file_path)
                        if os.path.exists(full_path):
                            size = os.path.getsize(full_path)
                            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                            listbox.insert(tk.END, f"📄 {file_path} ({size_str})")
                        else:
                            listbox.insert(tk.END, f"❌ {file_path} (missing)")
                else:
                    listbox.insert(tk.END, "No files generated yet")
            
            # Refresh main progress display too
            self.refresh_progress_display()
            
        except Exception as e:
            self.logger.error(f"Failed to refresh step files: {e}")
    
    def open_step_folder(self, step_name):
        """Open the folder containing files for this step."""
        try:
            import subprocess
            import os
            
            output_dir = self.get_output_dir()
            
            # Determine the appropriate subfolder for this step
            step_folders = {
                "lore": "story/lore",
                "structure": "story/structure", 
                "scenes": "story/planning",
                "chapters": "story/content"
            }
            
            folder_path = os.path.join(output_dir, step_folders.get(step_name, ""))
            
            if os.path.exists(folder_path):
                # Open folder in file manager
                subprocess.run(["xdg-open", folder_path], check=True)
            else:
                # Open the main output directory
                subprocess.run(["xdg-open", output_dir], check=True)
                
        except Exception as e:
            self.logger.error(f"Failed to open folder for {step_name}: {e}")
            show_error("Error", f"Failed to open folder: {e}")
    
    def reset_workflow_state(self):
        """Reset the workflow state to start over."""
        if not AGENTIC_AVAILABLE or not self.story_orchestrator:
            show_warning("Warning", "Agentic mode not available")
            return
        
        # Confirm with user
        import tkinter.messagebox as msgbox
        result = msgbox.askyesno(
            "Reset Workflow",
            "Are you sure you want to reset the entire workflow?\n\n"
            "This will mark all steps as not started, but won't delete generated files."
        )
        
        if result:
            try:
                self.story_orchestrator.reset_workflow_state()
                self.refresh_progress_display()
                show_success("Success", "Workflow state reset successfully")
                self.logger.info("🔄 Workflow state reset by user")
            except Exception as e:
                self.logger.error(f"Failed to reset workflow state: {e}")
                show_error("Error", f"Failed to reset workflow: {e}")
    
    def create_from_existing_work(self):
        """Create checkpoint state by scanning existing work in the output directory."""
        if not AGENTIC_AVAILABLE or not self.story_orchestrator:
            show_warning("Warning", "Agentic mode not available")
            return
        
        try:
            # Get current parameters to include in the state
            current_params = self.param_ui.get_current_parameters()
            
            # Create checkpoint state from existing work
            state = self.story_orchestrator.state_manager.create_from_existing_work(
                parameters=current_params
            )
            
            # Refresh the display
            self.refresh_progress_display()
            
            # Show summary of what was found
            completed_steps = [name for name, step in state.steps.items() 
                             if step.status.value == "completed"]
            total_files = sum(len(step.output_files) for step in state.steps.values())
            
            if completed_steps:
                message = f"Found existing work:\n\n"
                message += f"✅ Completed steps: {', '.join(completed_steps)}\n"
                message += f"📁 Total files found: {total_files}\n\n"
                
                if state.current_step:
                    message += f"🎢 Next step: {state.current_step}"
                else:
                    message += f"🎆 All steps appear complete!"
                
                show_success("Existing Work Detected", message)
            else:
                show_info(
                    "No Existing Work", 
                    "No existing workflow files found.\n\nYou can start a new workflow or generate content in the individual tabs first."
                )
            
            self.logger.info(f"🔍 Scanned existing work: {len(completed_steps)} steps completed, {total_files} files")
            
        except Exception as e:
            self.logger.error(f"Failed to scan existing work: {e}")
            show_error("Error", f"Failed to scan existing work: {e}")
    
    def update_progress_on_step_completion(self, step_name: str):
        """Update progress display when a step completes."""
        # This method can be called by workflow callbacks
        self.root.after(0, self.refresh_progress_display)

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelWriterApp(root)
    root.mainloop()