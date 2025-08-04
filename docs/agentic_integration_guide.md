# NovelWriter Agentic Integration Guide

This guide explains how to integrate and use the agentic AI capabilities in NovelWriter.

## Overview

The NovelWriter agentic system consists of three main components:

1. **Quality Control Agent** - Evaluates story quality using specialized analysis tools
2. **Consistency Agent** - Maintains story consistency and tracks narrative elements
3. **Multi-Agent Orchestrator** - Coordinates multiple agents for comprehensive analysis

## Quick Start

### Basic Usage

```python
from agents.quality.quality_agent import QualityControlAgent
from agents.consistency.consistency_agent import ConsistencyAgent
from agents.orchestration.orchestrator import MultiAgentOrchestrator

# Initialize individual agents
quality_agent = QualityControlAgent(model="gpt-4o")
consistency_agent = ConsistencyAgent(model="gpt-4o", output_dir="current_work")

# Or use the orchestrator for comprehensive analysis
orchestrator = MultiAgentOrchestrator(model="gpt-4o", output_dir="current_work")
```

### Quality Analysis

```python
# Evaluate chapter quality
result = quality_agent.process_task({
    "content": chapter_text,
    "task_type": "evaluate",
    "context": {"genre": "fantasy"},
    "quality_standards": {"minimum_quality": 0.8}
})

if result.success:
    quality_data = result.data["quality_analysis"]
    print(f"Overall assessment: {quality_data['overall_assessment']}")
    print(f"Strengths: {quality_data['key_strengths']}")
    print(f"Areas for improvement: {quality_data['key_weaknesses']}")
```

### Consistency Tracking

```python
# Track story elements in a new chapter
result = consistency_agent.process_task({
    "content": chapter_text,
    "task_type": "track",
    "chapter_number": 3,
    "context": {"genre": "mystery"}
})

# Validate consistency against previous chapters
result = consistency_agent.process_task({
    "content": chapter_text,
    "task_type": "validate",
    "chapter_number": 3,
    "characters": ["Sarah", "Mike"],
    "context": {"genre": "mystery"}
})

# Generate consistency report
result = consistency_agent.process_task({
    "content": chapter_text,
    "task_type": "report",
    "context": {"genre": "mystery"}
})
```

### Comprehensive Orchestration

```python
# Use orchestrator for full analysis
result = orchestrator.process_task({
    "content": chapter_text,
    "task_type": "comprehensive",
    "chapter_number": 3,
    "context": {
        "genre": "science_fiction",
        "story_type": "space_opera"
    },
    "quality_standards": {
        "minimum_quality": 0.75,
        "minimum_consistency": 0.8
    },
    "orchestration_mode": "iterative"  # or "single_pass"
})

if result.success:
    orch_result = result.data["orchestration_result"]
    print(f"Quality score: {orch_result.overall_quality_score:.2f}")
    print(f"Iterations: {orch_result.iterations_performed}")
    print(f"Recommendations: {len(orch_result.recommendations)}")
```

## Integration with Existing GUI

### Adding Agentic Features to Chapter Writing

```python
# In chapter_writing.py, add agentic analysis
def analyze_chapter_with_agents(self, chapter_content):
    """Analyze chapter using agentic capabilities."""
    
    # Get current chapter number and context
    chapter_num = self.get_current_chapter_number()
    context = {
        "genre": self.get_selected_genre(),
        "story_type": self.get_story_type()
    }
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(
        model=self.get_selected_model(),
        output_dir=self.get_output_directory()
    )
    
    # Run comprehensive analysis
    result = orchestrator.process_task({
        "content": chapter_content,
        "task_type": "comprehensive",
        "chapter_number": chapter_num,
        "context": context,
        "orchestration_mode": "iterative"
    })
    
    if result.success:
        # Display results in GUI
        self.display_analysis_results(result)
    else:
        self.show_error(f"Analysis failed: {result.messages}")

def display_analysis_results(self, result):
    """Display agentic analysis results in the GUI."""
    
    orch_result = result.data.get("orchestration_result")
    if not orch_result:
        return
    
    # Create results window
    results_window = tk.Toplevel(self.root)
    results_window.title("Agentic Analysis Results")
    results_window.geometry("800x600")
    
    # Quality score
    quality_frame = tk.Frame(results_window)
    quality_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(quality_frame, text=f"Quality Score: {orch_result.overall_quality_score:.2f}", 
             font=("Arial", 14, "bold")).pack(anchor="w")
    
    # Recommendations
    rec_frame = tk.Frame(results_window)
    rec_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    tk.Label(rec_frame, text="Recommendations:", font=("Arial", 12, "bold")).pack(anchor="w")
    
    rec_text = tk.Text(rec_frame, wrap="word", height=10)
    rec_text.pack(fill="both", expand=True)
    
    for i, rec in enumerate(orch_result.recommendations, 1):
        rec_text.insert(tk.END, f"{i}. {rec}\n\n")
    
    rec_text.config(state="disabled")
```

### Adding Agentic Mode Toggle

```python
# In app.py, add agentic mode toggle
def create_agentic_controls(self):
    """Create controls for agentic features."""
    
    agentic_frame = tk.LabelFrame(self.root, text="Agentic AI Features", padx=5, pady=5)
    agentic_frame.pack(fill="x", padx=10, pady=5)
    
    # Enable/disable toggle
    self.agentic_enabled = tk.BooleanVar(value=False)
    agentic_check = tk.Checkbutton(
        agentic_frame, 
        text="Enable Agentic Analysis",
        variable=self.agentic_enabled,
        command=self.toggle_agentic_mode
    )
    agentic_check.pack(anchor="w")
    
    # Quality threshold
    quality_frame = tk.Frame(agentic_frame)
    quality_frame.pack(fill="x", pady=2)
    
    tk.Label(quality_frame, text="Quality Threshold:").pack(side="left")
    self.quality_threshold = tk.DoubleVar(value=0.75)
    quality_scale = tk.Scale(
        quality_frame, 
        from_=0.5, to=1.0, resolution=0.05,
        orient="horizontal",
        variable=self.quality_threshold
    )
    quality_scale.pack(side="right", fill="x", expand=True)
    
    # Analysis mode
    mode_frame = tk.Frame(agentic_frame)
    mode_frame.pack(fill="x", pady=2)
    
    tk.Label(mode_frame, text="Analysis Mode:").pack(side="left")
    self.analysis_mode = tk.StringVar(value="comprehensive")
    mode_combo = ttk.Combobox(
        mode_frame,
        textvariable=self.analysis_mode,
        values=["comprehensive", "quality_focused", "consistency_focused"],
        state="readonly"
    )
    mode_combo.pack(side="right")

def toggle_agentic_mode(self):
    """Toggle agentic features on/off."""
    enabled = self.agentic_enabled.get()
    
    if enabled:
        self.status_label.config(text="Agentic mode enabled")
        # Initialize agents
        self.init_agentic_agents()
    else:
        self.status_label.config(text="Agentic mode disabled")
        self.agentic_agents = None

def init_agentic_agents(self):
    """Initialize agentic agents."""
    try:
        model = self.get_selected_model()
        output_dir = self.get_output_directory()
        
        self.agentic_agents = {
            "orchestrator": MultiAgentOrchestrator(model=model, output_dir=output_dir),
            "quality": QualityControlAgent(model=model),
            "consistency": ConsistencyAgent(model=model, output_dir=output_dir)
        }
        
        self.logger.info("Agentic agents initialized successfully")
        
    except Exception as e:
        self.logger.error(f"Failed to initialize agentic agents: {e}")
        self.agentic_enabled.set(False)
        self.show_error(f"Failed to initialize agentic features: {e}")
```

## Advanced Usage

### Custom Quality Standards

```python
# Define custom quality standards for different genres
quality_standards = {
    "fantasy": {
        "minimum_quality": 0.8,
        "world_building_weight": 0.3,
        "character_development_weight": 0.25,
        "prose_quality_weight": 0.25,
        "pacing_weight": 0.2
    },
    "mystery": {
        "minimum_quality": 0.75,
        "plot_coherence_weight": 0.4,
        "character_development_weight": 0.2,
        "prose_quality_weight": 0.2,
        "pacing_weight": 0.2
    }
}

# Use with orchestrator
result = orchestrator.process_task({
    "content": chapter_text,
    "task_type": "comprehensive",
    "quality_standards": quality_standards.get(genre, {}),
    # ... other parameters
})
```

### Batch Processing Multiple Chapters

```python
def analyze_multiple_chapters(chapters, orchestrator):
    """Analyze multiple chapters with consistency tracking."""
    
    results = []
    
    for i, chapter in enumerate(chapters, 1):
        # Track elements in each chapter
        track_result = orchestrator.process_task({
            "content": chapter,
            "task_type": "consistency_focused",
            "chapter_number": i,
            "context": {"genre": "fantasy"}
        })
        
        # Comprehensive analysis
        analysis_result = orchestrator.process_task({
            "content": chapter,
            "task_type": "comprehensive",
            "chapter_number": i,
            "context": {"genre": "fantasy"}
        })
        
        results.append({
            "chapter": i,
            "tracking": track_result,
            "analysis": analysis_result
        })
    
    return results
```

### Error Handling and Fallbacks

```python
def safe_agentic_analysis(content, orchestrator, fallback_agent=None):
    """Perform agentic analysis with error handling."""
    
    try:
        # Try comprehensive orchestration first
        result = orchestrator.process_task({
            "content": content,
            "task_type": "comprehensive",
            "orchestration_mode": "single_pass"  # Faster fallback
        })
        
        if result.success:
            return result
        
    except Exception as e:
        logging.warning(f"Orchestration failed: {e}")
    
    # Fallback to individual agent
    if fallback_agent:
        try:
            return fallback_agent.process_task({
                "content": content,
                "task_type": "evaluate"
            })
        except Exception as e:
            logging.error(f"Fallback agent failed: {e}")
    
    # Return empty result if all fails
    return AgentResult(
        success=False,
        data={},
        messages=["All agentic analysis methods failed"],
        metrics={}
    )
```

## Configuration

### Model Selection

Different agents can use different models for specialized tasks:

```python
# High-quality model for quality analysis
quality_agent = QualityControlAgent(model="gpt-4o")

# Faster model for consistency tracking
consistency_agent = ConsistencyAgent(model="gpt-3.5-turbo", output_dir="current_work")

# Mixed model orchestrator
orchestrator = MultiAgentOrchestrator(model="gpt-4o", output_dir="current_work")
```

### Output Directory Management

```python
# Ensure consistent output directory across agents
output_dir = "current_work"

# All agents should use the same directory for state persistence
consistency_agent = ConsistencyAgent(output_dir=output_dir)
orchestrator = MultiAgentOrchestrator(output_dir=output_dir)
```

## Testing and Validation

Use the provided test scripts to verify agentic functionality:

```bash
# Test individual agents
python test_quality_agent.py
python test_consistency_agent.py

# Test orchestration
python test_orchestrator.py

# Test GUI integration
python test_gui_startup.py
```

## Performance Considerations

1. **Model Selection**: Use faster models for frequent operations, higher-quality models for final analysis
2. **Caching**: Consistency agent maintains state files to avoid reprocessing
3. **Batch Processing**: Process multiple chapters together for efficiency
4. **Fallback Modes**: Implement fallbacks for when advanced features fail

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all agent modules are in the Python path
2. **Model Access**: Verify API keys and model availability
3. **File Permissions**: Check write permissions for output directory
4. **Memory Usage**: Monitor memory usage with large content analysis

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Agents will provide detailed execution logs
agent = QualityControlAgent(model="gpt-4o")
```

## Next Steps

1. **GUI Integration**: Add agentic controls to existing GUI components
2. **Custom Tools**: Develop genre-specific analysis tools
3. **Feedback Loops**: Implement user feedback for agent improvement
4. **Performance Optimization**: Profile and optimize agent execution
5. **Advanced Orchestration**: Develop adaptive planning capabilities

This integration guide provides the foundation for incorporating powerful agentic AI capabilities into your NovelWriter workflow.
