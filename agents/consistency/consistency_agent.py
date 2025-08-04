"""
Consistency Agent for NovelWriter.

This agent maintains story consistency by tracking characters, world-building,
and plot threads across the narrative. It validates new content against
established story elements and provides consistency reports.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime

from agents.base.agent import BaseAgent, AgentResult
from agents.base.tool import ToolRegistry
from agents.consistency.consistency_tools import (
    ValidateCharacterConsistencyTool,
    TrackWorldBuildingTool, 
    TrackPlotThreadsTool,
    CharacterState,
    WorldElement,
    PlotThread
)
from core.generation.helper_fns import write_json, read_json


class ConsistencyAgent(BaseAgent):
    """
    Agent responsible for maintaining story consistency.
    
    This agent can:
    1. Track character development and validate consistency
    2. Monitor world-building elements and rules
    3. Manage plot threads and their progression
    4. Detect inconsistencies and provide recommendations
    5. Maintain persistent story state across sessions
    """
    
    def __init__(self, model: str = "gpt-4o", output_dir: str = "current_work", 
                 logger: Optional[logging.Logger] = None):
        super().__init__(name="ConsistencyAgent", model=model, logger=logger)
        
        self.output_dir = output_dir
        
        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self._register_tools()
        
        # Story state tracking
        self.characters: Dict[str, CharacterState] = {}
        self.world_elements: Dict[str, WorldElement] = {}
        self.plot_threads: Dict[str, PlotThread] = {}
        
        # State file paths
        self.state_files = {
            "characters": os.path.join(output_dir, "consistency_characters.json"),
            "world": os.path.join(output_dir, "consistency_world.json"),
            "plots": os.path.join(output_dir, "consistency_plots.json")
        }
        
        # Load existing state
        self._load_consistency_state()
        
        self.logger.info(f"Consistency Agent initialized with {len(self.characters)} characters, "
                        f"{len(self.world_elements)} world elements, {len(self.plot_threads)} plot threads")
    
    def _register_tools(self):
        """Register available tools for this agent."""
        self.tool_registry.register_tool(ValidateCharacterConsistencyTool(self.model))
        self.tool_registry.register_tool(TrackWorldBuildingTool(self.model))
        self.tool_registry.register_tool(TrackPlotThreadsTool(self.model))
        
        self.available_tools = [tool.name for tool in self.tool_registry.get_available_tools()]
        self.logger.debug(f"Registered tools: {self.available_tools}")
    
    def get_available_tools(self) -> List[str]:
        """Return list of tools this agent can use."""
        return self.available_tools
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for consistency tasks."""
        return ["content", "task_type"]
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process a consistency task.
        
        Args:
            task_data: Dictionary containing:
                - content: The content to analyze
                - task_type: Type of consistency check ("validate", "track", "report")
                - chapter_number: Optional chapter number
                - characters: Optional list of characters to focus on
                - context: Optional additional context
                
        Returns:
            AgentResult with consistency analysis and updates
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
        focus_characters = task_data.get("characters", [])
        context = task_data.get("context", {})
        
        try:
            if task_type == "validate":
                return self._validate_consistency(content, chapter_number, focus_characters, context)
            elif task_type == "track":
                return self._track_story_elements(content, chapter_number, context)
            elif task_type == "report":
                return self._generate_consistency_report(content, context)
            else:
                return self.handle_error(
                    ValueError(f"Unknown task type: {task_type}"),
                    "process_task"
                )
                
        except Exception as e:
            return self.handle_error(e, "process_task")
    
    def _validate_consistency(self, content: str, chapter_num: int, 
                            focus_characters: List[str], context: Dict) -> AgentResult:
        """Validate content consistency against established story elements."""
        
        self.logger.info(f"Validating consistency for chapter {chapter_num}")
        
        validation_results = {
            "character_validations": {},
            "world_validations": {},
            "plot_validations": {},
            "overall_consistency_score": 0.0
        }
        
        # Determine which characters to validate
        characters_to_check = focus_characters if focus_characters else self._detect_characters_in_content(content)
        
        # Validate character consistency
        character_scores = []
        for char_name in characters_to_check:
            if char_name in self.characters:
                char_result = self._validate_character(char_name, content, context)
                validation_results["character_validations"][char_name] = char_result
                if char_result.get("consistency_score"):
                    character_scores.append(char_result["consistency_score"])
        
        # Validate world-building consistency
        world_result = self._validate_world_building(content, context)
        validation_results["world_validations"] = world_result
        
        # Validate plot thread consistency
        plot_result = self._validate_plot_threads(content, chapter_num)
        validation_results["plot_validations"] = plot_result
        
        # Calculate overall consistency score
        scores = character_scores + [world_result.get("consistency_score", 0.8)]
        validation_results["overall_consistency_score"] = sum(scores) / len(scores) if scores else 0.8
        
        # Generate recommendations
        recommendations = self._generate_consistency_recommendations(validation_results)
        
        return AgentResult(
            success=True,
            data={
                "validation_results": validation_results,
                "recommendations": recommendations,
                "characters_checked": characters_to_check
            },
            messages=[f"Validated consistency for {len(characters_to_check)} characters"],
            metrics={
                "overall_consistency_score": validation_results["overall_consistency_score"],
                "characters_validated": len(characters_to_check)
            }
        )
    
    def _validate_character(self, char_name: str, content: str, context: Dict) -> Dict[str, Any]:
        """Validate a specific character's consistency."""
        
        char_tool = self.tool_registry.get_tool("validate_character_consistency")
        if not char_tool:
            return {"error": "Character validation tool not available"}
        
        # Prepare character history
        char_state = self.characters.get(char_name)
        char_history = {}
        if char_state:
            char_history = {
                "traits": char_state.traits,
                "relationships": char_state.relationships,
                "development_arc": char_state.development_arc,
                "current_status": char_state.current_status
            }
        
        # Execute validation
        result = char_tool.execute(
            character_name=char_name,
            new_content=content,
            character_history=char_history,
            context_chapters=context.get("previous_chapters", [])
        )
        
        if result.success:
            # Update character state with new information
            self._update_character_state(char_name, result.data, content)
            return result.data
        else:
            return {"error": result.error_message}
    
    def _validate_world_building(self, content: str, context: Dict) -> Dict[str, Any]:
        """Validate world-building consistency."""
        
        world_tool = self.tool_registry.get_tool("track_world_building")
        if not world_tool:
            return {"error": "World-building tool not available"}
        
        # Prepare established world elements
        established_world = {}
        for name, element in self.world_elements.items():
            established_world[name] = {
                "type": element.type,
                "description": element.description,
                "rules": element.rules
            }
        
        # Execute validation
        result = world_tool.execute(
            content=content,
            established_world=established_world,
            genre=context.get("genre", "general")
        )
        
        if result.success:
            # Update world elements with new information
            self._update_world_elements(result.data)
            return result.data
        else:
            return {"error": result.error_message}
    
    def _validate_plot_threads(self, content: str, chapter_num: int) -> Dict[str, Any]:
        """Validate plot thread progression."""
        
        plot_tool = self.tool_registry.get_tool("track_plot_threads")
        if not plot_tool:
            return {"error": "Plot tracking tool not available"}
        
        # Prepare active threads
        active_threads = []
        for name, thread in self.plot_threads.items():
            if thread.status == "active":
                active_threads.append({
                    "name": name,
                    "description": thread.description,
                    "characters_involved": thread.related_characters,
                    "key_events": thread.key_events
                })
        
        # Execute validation
        result = plot_tool.execute(
            content=content,
            active_threads=active_threads,
            chapter_number=chapter_num
        )
        
        if result.success:
            # Update plot threads
            self._update_plot_threads(result.data, chapter_num)
            return result.data
        else:
            return {"error": result.error_message}
    
    def _track_story_elements(self, content: str, chapter_num: int, context: Dict) -> AgentResult:
        """Track and update story elements from new content."""
        
        self.logger.info(f"Tracking story elements in chapter {chapter_num}")
        
        tracking_results = {
            "new_characters": [],
            "character_updates": {},
            "new_world_elements": [],
            "plot_thread_updates": []
        }
        
        # Detect and track new characters
        detected_characters = self._detect_characters_in_content(content)
        for char_name in detected_characters:
            if char_name not in self.characters:
                # New character detected
                self._add_new_character(char_name, content, chapter_num)
                tracking_results["new_characters"].append(char_name)
            else:
                # Update existing character
                updates = self._update_character_from_content(char_name, content, chapter_num)
                if updates:
                    tracking_results["character_updates"][char_name] = updates
        
        # Track world-building elements
        world_result = self._validate_world_building(content, context)
        if "new_elements" in world_result:
            tracking_results["new_world_elements"] = world_result["new_elements"]
        
        # Track plot threads
        plot_result = self._validate_plot_threads(content, chapter_num)
        if "thread_updates" in plot_result:
            tracking_results["plot_thread_updates"] = plot_result["thread_updates"]
        
        # Save updated state
        self._save_consistency_state()
        
        return AgentResult(
            success=True,
            data=tracking_results,
            messages=[f"Tracked story elements in chapter {chapter_num}"],
            metrics={
                "new_characters": len(tracking_results["new_characters"]),
                "character_updates": len(tracking_results["character_updates"]),
                "new_world_elements": len(tracking_results["new_world_elements"])
            }
        )
    
    def _generate_consistency_report(self, content: str, context: Dict) -> AgentResult:
        """Generate a comprehensive consistency report."""
        
        report = {
            "summary": {
                "total_characters": len(self.characters),
                "total_world_elements": len(self.world_elements),
                "active_plot_threads": len([t for t in self.plot_threads.values() if t.status == "active"]),
                "resolved_plot_threads": len([t for t in self.plot_threads.values() if t.status == "resolved"])
            },
            "character_status": {},
            "world_consistency": {},
            "plot_thread_status": {},
            "potential_issues": []
        }
        
        # Character status
        for name, char in self.characters.items():
            report["character_status"][name] = {
                "status": char.current_status,
                "last_seen": char.last_seen_chapter,
                "development_points": len(char.development_arc),
                "inconsistencies": len(char.inconsistencies)
            }
        
        # World element status
        for name, element in self.world_elements.items():
            report["world_consistency"][name] = {
                "type": element.type,
                "established_chapter": element.established_in_chapter,
                "modifications": len(element.modifications)
            }
        
        # Plot thread status
        for name, thread in self.plot_threads.items():
            report["plot_thread_status"][name] = {
                "status": thread.status,
                "introduced_chapter": thread.introduced_chapter,
                "resolution_chapter": thread.resolution_chapter,
                "key_events": len(thread.key_events)
            }
        
        # Identify potential issues
        report["potential_issues"] = self._identify_potential_issues()
        
        return AgentResult(
            success=True,
            data=report,
            messages=["Generated consistency report"],
            metrics=report["summary"]
        )
    
    def _detect_characters_in_content(self, content: str) -> List[str]:
        """Detect character names in content."""
        # Simple detection - could be enhanced with NLP
        detected = []
        
        # Look for existing characters
        for char_name in self.characters.keys():
            if char_name.lower() in content.lower():
                detected.append(char_name)
        
        # Look for new character patterns (capitalized names in dialogue/description)
        import re
        name_patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', content)
        
        # Filter out common words and add potential new characters
        common_words = {'The', 'This', 'That', 'Chapter', 'Scene', 'Meanwhile', 'However', 'Captain', 'Doctor'}
        for name in name_patterns:
            if name not in common_words and name not in detected and len(name.split()) <= 2:
                # Heuristic: if it appears multiple times, likely a character
                if content.count(name) >= 2:
                    detected.append(name)
        
        return list(set(detected))
    
    def _add_new_character(self, name: str, content: str, chapter_num: int):
        """Add a new character to tracking."""
        char_state = CharacterState(
            name=name,
            traits=[],
            relationships={},
            development_arc=[f"Introduced in chapter {chapter_num}"],
            current_status="active",
            last_seen_chapter=chapter_num
        )
        
        self.characters[name] = char_state
        self.logger.info(f"Added new character: {name}")
    
    def _update_character_state(self, name: str, validation_data: Dict, content: str):
        """Update character state based on validation results."""
        if name not in self.characters:
            return
        
        char = self.characters[name]
        
        # Add new insights
        if "character_insights" in validation_data:
            char.development_arc.extend(validation_data["character_insights"])
        
        # Record violations as inconsistencies
        if "violations" in validation_data:
            for violation in validation_data["violations"]:
                char.inconsistencies.append(f"{violation['type']}: {violation['description']}")
        
        # Update character updates
        if "character_updates" in validation_data:
            updates = validation_data["character_updates"]
            if "recent_dialogue" in updates:
                # Could store recent dialogue patterns
                pass
    
    def _update_character_from_content(self, name: str, content: str, chapter_num: int) -> Dict[str, Any]:
        """Update character information from content analysis."""
        if name not in self.characters:
            return {}
        
        char = self.characters[name]
        char.last_seen_chapter = chapter_num
        
        # Simple content analysis for updates
        updates = {}
        
        # Check for status changes
        status_indicators = {
            "died": "dead",
            "killed": "dead", 
            "disappeared": "missing",
            "vanished": "missing"
        }
        
        for indicator, status in status_indicators.items():
            if indicator in content.lower() and name.lower() in content.lower():
                if char.current_status != status:
                    char.current_status = status
                    updates["status_change"] = status
        
        return updates
    
    def _update_world_elements(self, world_data: Dict):
        """Update world elements from analysis."""
        if "new_elements" in world_data:
            for element_data in world_data["new_elements"]:
                name = element_data["name"]
                if name not in self.world_elements:
                    element = WorldElement(
                        name=name,
                        type=element_data["type"],
                        description=element_data["description"],
                        rules=element_data.get("rules", [])
                    )
                    self.world_elements[name] = element
                    self.logger.info(f"Added new world element: {name}")
    
    def _update_plot_threads(self, plot_data: Dict, chapter_num: int):
        """Update plot threads from analysis."""
        # Add new threads
        if "new_threads" in plot_data:
            for thread_data in plot_data["new_threads"]:
                name = thread_data["name"]
                if name not in self.plot_threads:
                    thread = PlotThread(
                        name=name,
                        description=thread_data["description"],
                        status="active",
                        introduced_chapter=chapter_num,
                        key_events=[],
                        related_characters=thread_data.get("characters_involved", [])
                    )
                    self.plot_threads[name] = thread
                    self.logger.info(f"Added new plot thread: {name}")
        
        # Update existing threads
        if "thread_updates" in plot_data:
            for update in plot_data["thread_updates"]:
                thread_name = update["thread_name"]
                if thread_name in self.plot_threads:
                    thread = self.plot_threads[thread_name]
                    thread.key_events.append({
                        "chapter": chapter_num,
                        "advancement": update["advancement"]
                    })
                    thread.status = update["status"]
                    
                    if update["status"] == "resolved":
                        thread.resolution_chapter = chapter_num
    
    def _generate_consistency_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Character consistency recommendations
        for char_name, char_result in validation_results["character_validations"].items():
            if "recommendations" in char_result:
                for rec in char_result["recommendations"]:
                    recommendations.append(f"Character {char_name}: {rec}")
        
        # World-building recommendations
        world_result = validation_results["world_validations"]
        if "world_expansion_opportunities" in world_result:
            recommendations.extend(world_result["world_expansion_opportunities"])
        
        # Plot thread recommendations
        plot_result = validation_results["plot_validations"]
        if "potential_issues" in plot_result:
            for issue in plot_result["potential_issues"]:
                recommendations.append(f"Plot concern: {issue}")
        
        return recommendations
    
    def _identify_potential_issues(self) -> List[str]:
        """Identify potential consistency issues."""
        issues = []
        
        # Characters with inconsistencies
        for name, char in self.characters.items():
            if char.inconsistencies:
                issues.append(f"Character {name} has {len(char.inconsistencies)} consistency issues")
        
        # Long-inactive characters
        max_chapter = max((char.last_seen_chapter or 0 for char in self.characters.values()), default=0)
        for name, char in self.characters.items():
            if char.current_status == "active" and char.last_seen_chapter and max_chapter - char.last_seen_chapter > 3:
                issues.append(f"Character {name} hasn't appeared since chapter {char.last_seen_chapter}")
        
        # Unresolved plot threads
        old_threads = [name for name, thread in self.plot_threads.items() 
                      if thread.status == "active" and max_chapter - thread.introduced_chapter > 5]
        if old_threads:
            issues.append(f"Long-running unresolved threads: {', '.join(old_threads)}")
        
        return issues
    
    def _load_consistency_state(self):
        """Load consistency state from files."""
        try:
            # Load characters
            if os.path.exists(self.state_files["characters"]):
                char_data = read_json(self.state_files["characters"])
                for name, data in char_data.items():
                    self.characters[name] = CharacterState(**data)
            
            # Load world elements
            if os.path.exists(self.state_files["world"]):
                world_data = read_json(self.state_files["world"])
                for name, data in world_data.items():
                    self.world_elements[name] = WorldElement(**data)
            
            # Load plot threads
            if os.path.exists(self.state_files["plots"]):
                plot_data = read_json(self.state_files["plots"])
                for name, data in plot_data.items():
                    self.plot_threads[name] = PlotThread(**data)
                    
        except Exception as e:
            self.logger.warning(f"Failed to load consistency state: {e}")
    
    def _save_consistency_state(self):
        """Save consistency state to files."""
        try:
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Save characters
            char_data = {name: asdict(char) for name, char in self.characters.items()}
            write_json(self.state_files["characters"], char_data)
            
            # Save world elements
            world_data = {name: asdict(element) for name, element in self.world_elements.items()}
            write_json(self.state_files["world"], world_data)
            
            # Save plot threads
            plot_data = {name: asdict(thread) for name, thread in self.plot_threads.items()}
            write_json(self.state_files["plots"], plot_data)
            
            self.logger.debug("Consistency state saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save consistency state: {e}")
