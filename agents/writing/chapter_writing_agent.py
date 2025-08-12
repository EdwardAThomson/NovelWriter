#!/usr/bin/env python3
"""
Automated Chapter Writing Agent for NovelWriter.

This agent provides intelligent automation for chapter writing:
- Detects which chapters need to be written
- Writes chapters sequentially or in batches
- Integrates with existing chapter writing workflow
- Provides progress tracking and quality validation
"""

import os
import re
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from agents.base.agent import BaseAgent, AgentResult
from core.generation.helper_fns import open_file, write_file, read_json
from core.config.directory_config import get_directory_manager
from core.gui.parameters import STRUCTURE_SECTIONS_MAP

# Import review system (with fallback if not available)
try:
    from agents.review.review_agent import ReviewAndRetryAgent, ContentReview
    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False
    ContentReview = None


@dataclass
class SceneReview:
    """Review data for a single scene."""
    scene_number: int
    chapter_number: int
    quality_score: float
    word_count: int
    issues: List[str]
    strengths: List[str]
    suggestions: List[str]
    timestamp: str
    confidence: float


@dataclass
class ChapterReview:
    """Review data for a complete chapter."""
    chapter_number: int
    section_name: str
    overall_quality: float
    scene_reviews: List[SceneReview]
    coherence_score: float
    pacing_score: float
    character_development_score: float
    total_word_count: int
    issues: List[str]
    strengths: List[str]
    suggestions: List[str]
    timestamp: str
    confidence: float


@dataclass
class BatchReview:
    """Review data for a batch of chapters."""
    batch_number: int
    chapter_numbers: List[int]
    chapter_reviews: List[ChapterReview]
    consistency_score: float
    progression_score: float
    style_consistency_score: float
    total_word_count: int
    average_quality: float
    issues: List[str]
    strengths: List[str]
    suggestions: List[str]
    timestamp: str
    confidence: float


@dataclass
class QualityThresholds:
    """User-configurable quality thresholds for review system."""
    minimum_scene_quality: float = 0.6
    minimum_chapter_quality: float = 0.65
    minimum_batch_quality: float = 0.7
    coherence_threshold: float = 0.6
    pacing_threshold: float = 0.6
    character_development_threshold: float = 0.6
    consistency_threshold: float = 0.7
    progression_threshold: float = 0.6
    style_consistency_threshold: float = 0.65
    retry_below_threshold: bool = True
    max_retries: int = 2


@dataclass
class QualityTrend:
    """Quality trend data for analytics."""
    timestamp: str
    chapter_number: int
    scene_number: Optional[int] = None
    quality_score: float = 0.0
    review_type: str = "scene"  # "scene", "chapter", "batch"
    improvement_from_previous: Optional[float] = None
    issues_resolved: int = 0
    new_issues_found: int = 0
    retry_attempt: int = 0


@dataclass
class ChapterWritingPlan:
    """Plan for automated chapter writing."""
    total_chapters: int
    chapters_to_write: List[int]  # Chapter numbers to write
    chapters_completed: List[int]  # Already written chapters
    current_chapter: Optional[int] = None
    batch_size: int = 1  # How many chapters to write in one session
    quality_check: bool = True
    enable_reviews: bool = True  # Enable multi-level review system
    quality_thresholds: Optional[QualityThresholds] = None  # Phase 3: Configurable thresholds


@dataclass
class ChapterInfo:
    """Information about a specific chapter."""
    chapter_number: int
    section_name: str
    scene_plan_file: str
    output_file: str
    exists: bool = False


class ChapterWritingAgent(BaseAgent):
    """
    Automated agent for writing novel chapters.
    
    This agent can:
    - Analyze story structure to determine total chapters
    - Detect which chapters are already written
    - Write chapters automatically in sequence
    - Provide progress tracking and validation
    """
    
    def __init__(self, output_dir: str, app_instance=None, use_new_structure: bool = False, 
                 quality_thresholds: Optional[QualityThresholds] = None):
        super().__init__(name="ChapterWritingAgent")
        self.output_dir = output_dir
        self.app = app_instance
        self.use_new_structure = use_new_structure
        self.dir_manager = get_directory_manager(output_dir, use_new_structure)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Phase 3: Configurable quality thresholds
        self.quality_thresholds = quality_thresholds or QualityThresholds()
        
        # Phase 3: Performance optimization - cache frequently accessed data
        self._quality_trends_cache = []
        self._last_cache_update = None
        self._cache_ttl_seconds = 300  # 5 minutes
        
        # Initialize review agent if available
        self.review_agent = None
        if REVIEW_AVAILABLE:
            try:
                self.review_agent = ReviewAndRetryAgent()
                self.logger.info("Review system initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize review system: {e}")
                self.review_agent = None
    
    def get_available_tools(self) -> List[str]:
        """Return list of available tools/capabilities for this agent."""
        return [
            "analyze_chapter_structure",
            "create_writing_plan", 
            "write_chapters_batch",
            "write_single_chapter",
            "get_progress_report",
            "quality_review_system",
            "batch_processing"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return list of required fields for task processing."""
        return [
            "task_type",  # "analyze_structure", "write_chapters", "write_single_chapter"
            "output_dir",
            "chapter_info_list"  # Optional, can be generated if not provided
        ]
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """Process different types of chapter writing tasks."""
        try:
            task_type = task_data.get("task_type")
            
            if task_type == "analyze_structure":
                chapter_info_list, story_params = self.analyze_chapter_structure()
                return AgentResult(
                    success=True,
                    data={
                        "chapter_info_list": [asdict(info) for info in chapter_info_list],
                        "story_parameters": story_params,
                        "total_chapters": len(chapter_info_list)
                    },
                    message=f"Analyzed structure: {len(chapter_info_list)} chapters found"
                )
                
            elif task_type == "write_chapters":
                chapter_info_list = task_data.get("chapter_info_list", [])
                if not chapter_info_list:
                    # Generate chapter info if not provided
                    chapter_info_list, _ = self.analyze_chapter_structure()
                
                batch_size = task_data.get("batch_size", 1)
                plan = self.create_writing_plan(chapter_info_list, batch_size)
                
                return self.write_chapters_batch(chapter_info_list, plan)
                
            elif task_type == "write_single_chapter":
                chapter_number = task_data.get("chapter_number")
                chapter_info_list = task_data.get("chapter_info_list", [])
                
                if not chapter_info_list:
                    chapter_info_list, _ = self.analyze_chapter_structure()
                
                # Find the specific chapter
                target_chapter = None
                for chapter_info in chapter_info_list:
                    if chapter_info.chapter_number == chapter_number:
                        target_chapter = chapter_info
                        break
                
                if not target_chapter:
                    return AgentResult(
                        success=False,
                        data=None,
                        message=f"Chapter {chapter_number} not found in structure"
                    )
                
                return self._write_single_chapter(target_chapter)
                
            else:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            return AgentResult(
                success=False,
                data=None,
                message=f"Task processing failed: {str(e)}"
            )
        
    def analyze_chapter_structure(self) -> Tuple[List[ChapterInfo], Dict[str, Any]]:
        """
        Analyze the story structure to determine all chapters/stories that need to be written.
        Handles both novels (multiple chapters) and short stories (single story).
        
        Returns:
            Tuple of (chapter_info_list, story_parameters)
        """
        self.logger.info("Analyzing story structure...")
        
        # 1. Load story parameters
        parameters_file = os.path.join(self.output_dir, "parameters.txt")
        story_params = self._load_story_parameters(parameters_file)
        
        structure_name = story_params.get("Story Structure", "6-Act Structure")
        story_length = story_params.get("Story Length", "Novel (Standard)")
        
        # 2. Handle short stories differently
        if story_length == "Short Story":
            return self._analyze_short_story_structure(structure_name, story_params)
        
        # 3. Handle novels - get structure sections
        sections = STRUCTURE_SECTIONS_MAP.get(structure_name, [])
        if not sections:
            raise ValueError(f"Unknown story structure: {structure_name}")
            
        # 4. Analyze each section to find chapters
        chapter_info_list = []
        chapter_counter = 1
        
        for section_name in sections:
            section_chapters = self._analyze_section_chapters(
                structure_name, section_name, chapter_counter
            )
            chapter_info_list.extend(section_chapters)
            chapter_counter += len(section_chapters)
            
        self.logger.info(f"Found {len(chapter_info_list)} total chapters across {len(sections)} sections")
        return chapter_info_list, story_params
        
    def _load_story_parameters(self, parameters_file: str) -> Dict[str, str]:
        """Load story parameters from file."""
        params = {}
        try:
            if os.path.exists(parameters_file):
                with open(parameters_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            params[key.strip()] = value.strip()
        except Exception as e:
            self.logger.error(f"Error loading parameters: {e}")
            
        return params
        
    def _analyze_short_story_structure(self, structure_name: str, story_params: Dict[str, str]) -> Tuple[List[ChapterInfo], Dict[str, Any]]:
        """Analyze short story structure - returns single 'chapter' representing the whole story."""
        safe_struct = structure_name.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '').replace('!', '').replace(',', '')
        
        # For short stories, there's one scene plan file and one output file
        scene_plan_file = f"scenes_short_story_{safe_struct}.md"
        scene_plan_path = os.path.join(self.output_dir, scene_plan_file)
        
        # Output file uses the story title
        novel_title = story_params.get("Novel Title", "Untitled Short Story")
        safe_title = novel_title.lower().replace(' ', '_').replace(':', '').replace('/', '')
        output_file = f"prose_short_story_{safe_title}.md"
        output_path = os.path.join(self.output_dir, output_file)
        
        # Create a single "chapter" info representing the whole short story
        story_info = ChapterInfo(
            chapter_number=1,  # Short stories are treated as "chapter 1"
            section_name="Complete Short Story",
            scene_plan_file=scene_plan_file,
            output_file=output_file,
            exists=os.path.exists(output_path)
        )
        
        self.logger.info(f"Short story analysis: Scene plan = {scene_plan_file}, Output = {output_file}, Exists = {story_info.exists}")
        return [story_info], story_params
        
    def _analyze_section_chapters(self, structure_name: str, section_name: str, start_chapter: int) -> List[ChapterInfo]:
        """Analyze a specific section to find its chapters."""
        safe_struct = structure_name.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '').replace('!', '').replace(',', '')
        safe_section = section_name.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
        
        # Find the chapter outline file for this section
        outline_file = f"chapter_outlines_{safe_struct}_{safe_section}.md"
        outline_path = os.path.join(self.output_dir, outline_file)
        
        chapters = []
        try:
            if os.path.exists(outline_path):
                content = open_file(outline_path)
                # Find all chapter headings
                chapter_matches = re.findall(r"^(?:\*{2,}|#{2,})\s*Chapter\s*(\d+)(?:[:\s\S]*?)?$", content, re.MULTILINE | re.IGNORECASE)
                
                for i, match in enumerate(chapter_matches):
                    chapter_num = start_chapter + i
                    
                    # Determine scene plan file using directory manager
                    scene_plans_dir = self.dir_manager.get_scene_plans_dir()
                    scene_plan_file = f"{scene_plans_dir}/scenes_{safe_struct}_{safe_section}_ch{chapter_num}.md"
                    scene_plan_path = os.path.join(self.output_dir, scene_plan_file)
                    
                    # Determine output file using directory manager
                    chapters_dir = self.dir_manager.get_chapters_dir()
                    output_file = f"{chapters_dir}/chapter_{chapter_num}.md"
                    output_path = os.path.join(self.output_dir, output_file)
                    
                    chapter_info = ChapterInfo(
                        chapter_number=chapter_num,
                        section_name=section_name,
                        scene_plan_file=scene_plan_file,
                        output_file=output_file,
                        exists=os.path.exists(output_path)
                    )
                    chapters.append(chapter_info)
                    
        except Exception as e:
            self.logger.error(f"Error analyzing section {section_name}: {e}")
            
        return chapters
        
    def create_writing_plan(self, chapter_info_list: List[ChapterInfo], batch_size: int = 1,
                          quality_thresholds: Optional[QualityThresholds] = None) -> ChapterWritingPlan:
        """Create a plan for writing chapters."""
        chapters_to_write = [info.chapter_number for info in chapter_info_list if not info.exists]
        chapters_completed = [info.chapter_number for info in chapter_info_list if info.exists]
        
        return ChapterWritingPlan(
            total_chapters=len(chapter_info_list),
            chapters_to_write=chapters_to_write,
            chapters_completed=chapters_completed,
            batch_size=batch_size,
            quality_check=True,
            enable_reviews=True,
            quality_thresholds=quality_thresholds or self.quality_thresholds
        )
        
    def write_chapters_batch(self, chapter_info_list: List[ChapterInfo], plan: ChapterWritingPlan) -> AgentResult:
        """Write a batch of chapters automatically."""
        if not plan.chapters_to_write:
            return AgentResult(
                success=True,
                data={"completed_chapters": plan.chapters_completed},
                messages=["All chapters are already written"],
                metrics={}
            )
            
        # Write chapters in batches with review collection
        chapters_written = []
        errors = []
        all_chapter_reviews = []  # Collect chapter reviews for batch analysis
        batch_number = 1
        
        for i in range(0, len(plan.chapters_to_write), plan.batch_size):
            batch = plan.chapters_to_write[i:i + plan.batch_size]
            batch_chapter_reviews = []  # Reviews for this specific batch
            
            self.logger.info(f"Starting batch {batch_number} with {len(batch)} chapters")
            
            for chapter_num in batch:
                try:
                    chapter_info = next(ch for ch in chapter_info_list if ch.chapter_number == chapter_num)
                    result = self._write_single_chapter(chapter_info)
                    
                    if result.success:
                        chapters_written.append(chapter_num)
                        self.logger.info(f"Successfully wrote Chapter {chapter_num}")
                        
                        # Extract chapter review if available
                        if "chapter_review" in result.data and result.data["chapter_review"]:
                            # Load the full chapter review from file for batch analysis
                            chapter_review = self._load_chapter_review(chapter_num)
                            if chapter_review:
                                batch_chapter_reviews.append(chapter_review)
                                all_chapter_reviews.append(chapter_review)
                    else:
                        error_msg = result.messages[0] if result.messages else "Unknown error"
                        errors.append(f"Chapter {chapter_num}: {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Chapter {chapter_num}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(f"Error writing Chapter {chapter_num}: {e}")
            
            # Perform batch-level review if we have chapter reviews
            if batch_chapter_reviews and self.review_agent and plan.enable_reviews:
                batch_review = self._review_batch(batch_chapter_reviews, batch_number)
                if batch_review:
                    self.logger.info(f"Batch {batch_number} review completed: "
                                   f"Quality {batch_review.average_quality:.2f}, "
                                   f"Consistency {batch_review.consistency_score:.2f}")
            
            batch_number += 1
                    
        # Prepare result with review metrics
        success = len(chapters_written) > 0
        message = f"Wrote {len(chapters_written)} chapters"
        if errors:
            message += f", {len(errors)} errors"
        
        # Add review summary to message
        if all_chapter_reviews:
            avg_quality = sum(review.overall_quality for review in all_chapter_reviews) / len(all_chapter_reviews)
            message += f" (Avg Quality: {avg_quality:.2f})"
            
        # Prepare result data with review metrics
        result_data = {
            "chapters_written": chapters_written,
            "errors": errors,
            "total_completed": len(plan.chapters_completed) + len(chapters_written),
            "reviews_generated": len(all_chapter_reviews)
        }
        
        # Add review summary if available
        if all_chapter_reviews:
            result_data["review_summary"] = {
                "total_reviews": len(all_chapter_reviews),
                "average_quality": sum(review.overall_quality for review in all_chapter_reviews) / len(all_chapter_reviews),
                "average_coherence": sum(review.coherence_score for review in all_chapter_reviews) / len(all_chapter_reviews),
                "average_pacing": sum(review.pacing_score for review in all_chapter_reviews) / len(all_chapter_reviews),
                "total_issues": sum(len(review.issues) for review in all_chapter_reviews),
                "total_suggestions": sum(len(review.suggestions) for review in all_chapter_reviews)
            }
            
        return AgentResult(
            success=success,
            data=result_data,
            messages=[message],
            metrics={
                "chapters_written": len(chapters_written), 
                "errors": len(errors),
                "reviews_generated": len(all_chapter_reviews)
            }
        )
        
    def _write_single_chapter(self, chapter_info: ChapterInfo) -> AgentResult:
        """Write a single chapter or short story using the existing writing logic."""
        try:
            # Check if scene plan exists
            scene_plan_path = os.path.join(self.output_dir, chapter_info.scene_plan_file)
            if not os.path.exists(scene_plan_path):
                return AgentResult(
                    success=False,
                    data={},
                    messages=[f"Scene plan not found: {chapter_info.scene_plan_file}"],
                    metrics={}
                )
                
            # Load required context
            context = self._load_writing_context()
            
            # Determine if this is a short story
            is_short_story = chapter_info.section_name == "Complete Short Story"
            
            # Load scene plan
            scenes_content = open_file(scene_plan_path)
            if not scenes_content.strip():
                return AgentResult(
                    success=False,
                    data={},
                    messages=[f"Scene plan is empty: {chapter_info.scene_plan_file}"],
                    metrics={}
                )
                
            # Parse scenes
            scenes = self._parse_scenes(scenes_content)
            if not scenes:
                return AgentResult(
                    success=False,
                    data={},
                    messages=[f"No scenes found in plan: {chapter_info.scene_plan_file}"],
                    metrics={}
                )
                
            # Generate prose for each scene with reviews
            generated_scenes = []
            scene_reviews = []
            
            for i, scene in enumerate(scenes, 1):
                if is_short_story:
                    self.logger.info(f"Writing scene {i}/{len(scenes)} for short story")
                else:
                    self.logger.info(f"Writing scene {i}/{len(scenes)} for Chapter {chapter_info.chapter_number}")
                
                prose = self._generate_scene_prose(
                    chapter_info.chapter_number,
                    i,
                    scene,
                    context,
                    is_short_story=is_short_story
                )
                generated_scenes.append(prose)
                
                # Perform scene-level review if enabled
                if self.review_agent:
                    scene_review = self._review_scene(prose, i, chapter_info.chapter_number)
                    if scene_review:
                        scene_reviews.append(scene_review)
                
            # Combine scenes into final content
            final_content = "\n\n---\n\n".join(generated_scenes)
            
            # Save to appropriate location
            output_path = os.path.join(self.output_dir, chapter_info.output_file)
            
            # For chapters, create subdirectory; for short stories, save directly
            if not is_short_story:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            write_file(output_path, final_content)
            
            # Perform chapter-level review if enabled
            chapter_review = None
            if self.review_agent and not is_short_story:  # Skip chapter review for short stories
                chapter_review = self._review_chapter(final_content, chapter_info, scene_reviews)
            
            # Prepare result data
            result_data = {
                "output_file": chapter_info.output_file, 
                "scenes_count": len(scenes), 
                "is_short_story": is_short_story,
                "scene_reviews_count": len(scene_reviews)
            }
            
            # Add review data if available
            if chapter_review:
                result_data["chapter_review"] = {
                    "quality_score": chapter_review.overall_quality,
                    "coherence_score": chapter_review.coherence_score,
                    "pacing_score": chapter_review.pacing_score,
                    "issues_count": len(chapter_review.issues),
                    "suggestions_count": len(chapter_review.suggestions)
                }
            
            # Return appropriate success message
            if is_short_story:
                success_msg = "Short story written successfully"
            else:
                success_msg = f"Chapter {chapter_info.chapter_number} written successfully"
                if chapter_review:
                    success_msg += f" (Quality: {chapter_review.overall_quality:.2f})"
            
            return AgentResult(
                success=True,
                data=result_data,
                messages=[success_msg],
                metrics={"scenes_count": len(scenes), "scene_reviews": len(scene_reviews)}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                messages=[f"Error writing chapter: {str(e)}"],
                metrics={}
            )
            
    def _load_writing_context(self) -> Dict[str, Any]:
        """Load context needed for chapter writing."""
        context = {}
        
        try:
            # Load story parameters
            params_file = os.path.join(self.output_dir, "parameters.txt")
            context["parameters"] = self._load_story_parameters(params_file)
            
            # Load lore
            lore_file = os.path.join(self.output_dir, "generated_lore.md")
            if os.path.exists(lore_file):
                context["lore"] = open_file(lore_file)
            else:
                context["lore"] = "Lore not available."
                
            # Load character roster
            context["characters"] = self._load_character_roster()
            
            # Load faction summary
            context["factions"] = self._load_faction_summary()
            
        except Exception as e:
            self.logger.error(f"Error loading writing context: {e}")
            
        return context
        
    def _load_character_roster(self) -> str:
        """Load character roster summary."""
        try:
            characters_file = os.path.join(self.output_dir, "characters.json")
            if os.path.exists(characters_file):
                characters_data = read_json(characters_file)
                if characters_data and "characters" in characters_data:
                    summaries = []
                    for char in characters_data["characters"]:
                        details = [
                            f"\n\nName: {char.get('name', 'N/A')}",
                            f"Role: {char.get('role', 'N/A')}",
                            f"Gender: {char.get('gender', 'N/A')}",
                            f"Age: {char.get('age', 'N/A')}",
                            f"Appearance: {char.get('appearance_summary', 'N/A')}"
                        ]
                        
                        goals = char.get('goals', [])
                        if goals:
                            details.append(f"Primary Goal: {goals[0]}")
                            
                        strengths = char.get('strengths', [])
                        if strengths:
                            details.append(f"Key Strength: {strengths[0]}")
                            
                        flaws = char.get('flaws', [])
                        if flaws:
                            details.append(f"Key Flaw: {flaws[0]}")
                            
                        backstory = char.get('backstory_summary', '')
                        if backstory:
                            details.append(f"Backstory: {backstory}")
                            
                        summaries.append("\n".join(details))
                        
                    return "Key Characters:\n" + "\n".join(summaries)
        except Exception as e:
            self.logger.error(f"Error loading character roster: {e}")
            
        return "Character roster not available."
        
    def _load_faction_summary(self) -> str:
        """Load faction summary."""
        try:
            factions_file = os.path.join(self.output_dir, "factions.json")
            if os.path.exists(factions_file):
                factions_data = read_json(factions_file)
                if factions_data:
                    summaries = []
                    for faction in factions_data[:5]:  # Top 5 factions
                        details = [
                            f"\n\nFaction: {faction.get('faction_name', 'N/A')}",
                            f"Profile: {faction.get('faction_profile', 'N/A')}"
                        ]
                        
                        traits = faction.get('primary_traits', [])
                        if traits:
                            details.append(f"Primary Traits: {', '.join(traits)}")
                            
                        summaries.append("\n".join(details))
                        
                    return "Key Factions:\n" + "\n".join(summaries)
        except Exception as e:
            self.logger.error(f"Error loading faction summary: {e}")
            
        return "Faction information not available."
        
    def _parse_scenes(self, scenes_content: str) -> List[str]:
        """Parse individual scenes from scene plan content."""
        scene_pattern = r'^## Scene \d+:.*$'
        scenes = []
        
        matches = []
        for match in re.finditer(scene_pattern, scenes_content, flags=re.MULTILINE):
            matches.append((match.start(), match.end(), match.group(0).strip()))
            
        for i in range(len(matches)):
            start_pos = matches[i][0]
            end_pos = len(scenes_content)
            if i + 1 < len(matches):
                end_pos = matches[i + 1][0]
                
            scene_text = scenes_content[start_pos:end_pos].strip()
            if scene_text:
                scenes.append(scene_text)
                
        return scenes
        
    def _generate_scene_prose(self, chapter_num: int, scene_num: int, scene_plan: str, context: Dict[str, Any], is_short_story: bool = False) -> str:
        """Generate prose for a single scene using genuine NovelWriter AI functions."""
        
        story_params = context.get("parameters", {})
        structure = story_params.get("Story Structure", "Unknown")
        length = story_params.get("Story Length", "Unknown")
        
        # Build prompt using the same format as the existing writing system
        if is_short_story:
            prompt_lines = [
                f"You are an AI assistant helping to write a science fiction {length.lower()}.",
                f"This story follows the '{structure}' framework.",
                f"I will provide you with the detailed plan for a single scene within this short story. Please write the full prose for THIS SCENE ONLY.",
                "Do not try to write other scenes or summarize the story.",
                f"\n## Current Scene Description (Scene {scene_num}):",
                scene_plan,
                "\n## Overall Story Context (for your reference):",
                f"Full Universe Lore: {context.get('lore', 'Not available')}",
                f"\n{context.get('characters', 'Characters not available')}",
                f"\n{context.get('factions', 'Factions not available')}",
                "\n## Instructions for Writing This Scene:",
                "- Write engaging and descriptive prose for this scene.",
                "- Include character actions, dialogue (if appropriate), thoughts, and emotions.",
                "- Ensure the setting is clear.",
                "- The scene should flow logically and advance the plot or character development.",
                "- Adhere strictly to the provided lore for all world-building details.",
                "- Provide ONLY the prose for this scene. Do NOT add extra commentary or titles.",
                "- Do NOT use backticks."
            ]
        else:
            prompt_lines = [
                f"You are an AI assistant helping to write Chapter {chapter_num} of a science fiction {length.lower()}.",
                f"This story follows the '{structure}' framework.",
                f"I will provide you with the detailed plan for a single scene within Chapter {chapter_num}. Please write the full prose for THIS SCENE ONLY.",
                "Do not try to write other scenes or summarize the chapter.",
                f"\n## Current Scene Description (Scene {scene_num} of Chapter {chapter_num}):",
                scene_plan,
                "\n## Overall Story Context (for your reference):",
                f"Full Universe Lore: {context.get('lore', 'Not available')}",
                f"\n{context.get('characters', 'Characters not available')}",
                f"\n{context.get('factions', 'Factions not available')}",
                "\n## Instructions for Writing This Scene:",
                "- Write engaging and descriptive prose for this scene.",
                "- Include character actions, dialogue (if appropriate), thoughts, and emotions.",
                "- Ensure the setting is clear.",
                "- The scene should flow logically and advance the plot or character development.",
                "- Adhere strictly to the provided lore for all world-building details.",
                "- Provide ONLY the prose for this scene. Do NOT add extra commentary or titles.",
                "- Do NOT use backticks."
            ]
        
        prompt = "\n".join(prompt_lines)
        
        # Use genuine NovelWriter AI helper functions
        try:
            from core.generation.ai_helper import send_prompt
            from core.generation.helper_fns import save_prompt_to_file
            
            # Get model from app instance or use default
            if self.app and hasattr(self.app, 'get_selected_model'):
                model = self.app.get_selected_model()
            else:
                model = "gpt-4"  # Default model
                
            # Save prompt to file (following existing pattern)
            if is_short_story:
                prompt_filename = f"short_story_scene_{scene_num}_prompt"
            else:
                prompt_filename = f"write_chapter_{chapter_num}_scene_{scene_num}_prompt"
                
            try:
                save_prompt_to_file(self.output_dir, prompt_filename, prompt)
            except Exception as e:
                self.logger.warning(f"Could not save prompt to file: {e}")
            
            # Call the genuine NovelWriter AI helper
            if is_short_story:
                self.logger.info(f"Generating prose for Scene {scene_num} of short story using model {model}")
            else:
                self.logger.info(f"Generating prose for Chapter {chapter_num}, Scene {scene_num} using model {model}")
                
            response = send_prompt(prompt, model=model)
            
            if not response or not response.strip():
                if is_short_story:
                    self.logger.warning(f"LLM returned empty response for Scene {scene_num} of short story")
                    return f"[[[LLM CAME BACK BLANK FOR SCENE {scene_num}]]]"
                else:
                    self.logger.warning(f"LLM returned empty response for Chapter {chapter_num}, Scene {scene_num}")
                    return f"[[[LLM CAME BACK BLANK FOR CHAPTER {chapter_num}, SCENE {scene_num}]]]"
            
            if is_short_story:
                self.logger.info(f"Generated prose for Scene {scene_num} of short story. Length: {len(response)} chars")
            else:
                self.logger.info(f"Generated prose for Chapter {chapter_num}, Scene {scene_num}. Length: {len(response)} chars")
                
            return response
            
        except ImportError as e:
            error_msg = f"Could not import NovelWriter AI functions: {e}"
            self.logger.error(error_msg)
            return f"[Error: {error_msg}]"
        except Exception as e:
            error_msg = f"Error calling LLM for scene generation: {e}"
            self.logger.error(error_msg)
            if is_short_story:
                return f"[[[ERROR GENERATING SCENE {scene_num}: {e}]]]"
            else:
                return f"[[[ERROR GENERATING CHAPTER {chapter_num}, SCENE {scene_num}: {e}]]]"
            
    def get_progress_report(self, chapter_info_list: List[ChapterInfo]) -> Dict[str, Any]:
        """Get a progress report on chapter writing status."""
        total = len(chapter_info_list)
        completed = sum(1 for ch in chapter_info_list if ch.exists)
        remaining = total - completed
        
        # Group by section
        section_progress = {}
        for chapter in chapter_info_list:
            section = chapter.section_name
            if section not in section_progress:
                section_progress[section] = {"total": 0, "completed": 0}
            section_progress[section]["total"] += 1
            if chapter.exists:
                section_progress[section]["completed"] += 1
                
        return {
            "total_chapters": total,
            "completed_chapters": completed,
            "remaining_chapters": remaining,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "section_progress": section_progress,
            "next_chapter": min([ch.chapter_number for ch in chapter_info_list if not ch.exists]) if remaining > 0 else None
        }
    
    # ========== REVIEW SYSTEM METHODS ==========
    
    def _review_scene(self, scene_content: str, scene_number: int, chapter_number: int, retry_attempt: int = 0) -> SceneReview:
        """Perform scene-level review using local analysis."""
        try:
            # Default values
            quality_score = 0.7  # Default quality score
            word_count = len(scene_content.split())
            issues = []
            strengths = []
            suggestions = []
            confidence = 0.8
            
            # Use review agent if available
            if self.review_agent:
                try:
                    review_result = self.review_agent.analyze_content(scene_content)
                    if review_result:
                        quality_score = review_result.quality_score
                        issues = review_result.issues
                        strengths = review_result.strengths
                        suggestions = review_result.suggestions
                        confidence = review_result.confidence
                except Exception as e:
                    self.logger.warning(f"Error using review agent: {e}")
            
            # Fallback to basic analysis if no review agent or it failed
            if not issues and not strengths:
                # Basic analysis - word count based quality
                if word_count < 300:
                    issues.append("Scene is too short")
                    quality_score = 0.5
                elif word_count > 2000:
                    issues.append("Scene may be too long")
                    quality_score = 0.6
                    
                # Add generic strengths/suggestions
                strengths.append("Scene completed successfully")
                suggestions.append("Consider reviewing for pacing and character development")
            
            # Phase 3: Record quality trend data
            self.record_quality_trend(
                chapter_number=chapter_number,
                scene_number=scene_number,
                quality_score=quality_score,
                review_type="scene",
                retry_attempt=retry_attempt
            )
            
            # Phase 3: Check if retry is recommended based on thresholds
            should_retry = self.should_retry_based_on_thresholds(
                quality_score=quality_score,
                review_type="scene",
                retry_attempt=retry_attempt
            )
            
            if should_retry:
                suggestions.insert(0, f"Quality score {quality_score:.2f} below threshold "
                                  f"{self.quality_thresholds.minimum_scene_quality:.2f}. Retry recommended.")
            
            # Create scene review
            scene_review = SceneReview(
                scene_number=scene_number,
                chapter_number=chapter_number,
                quality_score=quality_score,
                word_count=word_count,
                issues=issues,
                strengths=strengths,
                suggestions=suggestions,
                timestamp=datetime.now().isoformat(),
                confidence=confidence
            )
            
            return scene_review
            
        except Exception as e:
            self.logger.error(f"Error reviewing scene: {e}")
            # Return default review on error
            return SceneReview(
                scene_number=scene_number,
                chapter_number=chapter_number,
                quality_score=0.5,
                word_count=len(scene_content.split()),
                issues=[f"Error during review: {str(e)}"],
                strengths=[],
                suggestions=["Retry scene review"],
                timestamp=datetime.now().isoformat(),
                confidence=0.3
            )
    
    def _review_chapter(self, chapter_content: str, scene_reviews: List[SceneReview], 
                      chapter_number: int, section_name: str, retry_attempt: int = 0) -> ChapterReview:
        """Perform chapter-level review using local analysis."""
        try:
            # Calculate overall quality from scene reviews
            scene_quality_scores = [scene.quality_score for scene in scene_reviews]
            overall_quality = sum(scene_quality_scores) / len(scene_quality_scores) if scene_quality_scores else 0.7
            
            # Calculate total word count
            total_word_count = sum(scene.word_count for scene in scene_reviews)
            
            # Analyze chapter coherence
            coherence_score = self._analyze_chapter_coherence(scene_reviews)
            
            # Analyze chapter pacing
            pacing_score = self._analyze_chapter_pacing(scene_reviews)
            
            # Analyze character development
            character_development_score = self._analyze_character_development(scene_reviews)
            
            # Aggregate issues and suggestions
            all_issues = []
            all_strengths = []
            all_suggestions = []
            
            # Add scene-level issues/strengths/suggestions
            for scene in scene_reviews:
                for issue in scene.issues:
                    if issue not in all_issues:
                        all_issues.append(issue)
                        
                for strength in scene.strengths:
                    if strength not in all_strengths:
                        all_strengths.append(strength)
                        
                for suggestion in scene.suggestions:
                    if suggestion not in all_suggestions:
                        all_suggestions.append(suggestion)
            
            # Add chapter-level issues
            if coherence_score < self.quality_thresholds.coherence_threshold:
                all_issues.append("Low scene-to-scene coherence")
                all_suggestions.append("Improve transitions between scenes")
                
            if pacing_score < self.quality_thresholds.pacing_threshold:
                all_issues.append("Uneven pacing across scenes")
                all_suggestions.append("Balance scene lengths and tension")
                
            if character_development_score < self.quality_thresholds.character_development_threshold:
                all_issues.append("Limited character development")
                all_suggestions.append("Add more character moments and growth")
            
            # Calculate confidence
            confidence = min(0.9, sum(scene.confidence for scene in scene_reviews) / len(scene_reviews))
            
            # Phase 3: Record quality trend data
            self.record_quality_trend(
                chapter_number=chapter_number,
                scene_number=None,
                quality_score=overall_quality,
                review_type="chapter",
                retry_attempt=retry_attempt
            )
            
            # Phase 3: Check if retry is recommended based on thresholds
            should_retry = self.should_retry_based_on_thresholds(
                quality_score=overall_quality,
                review_type="chapter",
                retry_attempt=retry_attempt
            )
            
            if should_retry:
                all_suggestions.insert(0, f"Chapter quality score {overall_quality:.2f} below threshold "
                                     f"{self.quality_thresholds.minimum_chapter_quality:.2f}. Retry recommended.")
            
            # Create chapter review
            chapter_review = ChapterReview(
                chapter_number=chapter_number,
                section_name=section_name,
                overall_quality=overall_quality,
                scene_reviews=scene_reviews,
                coherence_score=coherence_score,
                pacing_score=pacing_score,
                character_development_score=character_development_score,
                total_word_count=total_word_count,
                issues=all_issues,
                strengths=all_strengths,
                suggestions=all_suggestions,
                timestamp=datetime.now().isoformat(),
                confidence=confidence
            )
            
            return chapter_review
            
        except Exception as e:
            self.logger.error(f"Error reviewing chapter: {e}")
            # Return default review on error
            return ChapterReview(
                chapter_number=chapter_number,
                section_name=section_name,
                overall_quality=0.5,
                scene_reviews=scene_reviews,
                coherence_score=0.5,
                pacing_score=0.5,
                character_development_score=0.5,
                total_word_count=sum(scene.word_count for scene in scene_reviews),
                issues=[f"Error during chapter review: {str(e)}"],
                strengths=[],
                suggestions=["Retry chapter review"],
                timestamp=datetime.now().isoformat(),
                confidence=0.3
            )
            
    def _review_batch(self, chapter_reviews: List[ChapterReview], batch_number: int, retry_attempt: int = 0) -> BatchReview:
        """Perform batch-level review across multiple chapters."""
        try:
            # Extract chapter numbers
            chapter_numbers = [review.chapter_number for review in chapter_reviews]
            
            # Calculate average quality
            chapter_quality_scores = [review.overall_quality for review in chapter_reviews]
            average_quality = sum(chapter_quality_scores) / len(chapter_quality_scores) if chapter_quality_scores else 0.7
            
            # Calculate total word count
            total_word_count = sum(review.total_word_count for review in chapter_reviews)
            
            # Analyze batch consistency
            consistency_score = self._analyze_batch_consistency(chapter_reviews)
            
            # Analyze story progression
            progression_score = self._analyze_story_progression(chapter_reviews)
            
            # Analyze style consistency
            style_consistency_score = self._analyze_style_consistency(chapter_reviews)
            
            # Aggregate issues and suggestions
            all_issues = []
            all_strengths = []
            all_suggestions = []
            
            # Add chapter-level issues/strengths/suggestions
            for review in chapter_reviews:
                for issue in review.issues:
                    if issue not in all_issues:
                        all_issues.append(issue)
                        
                for strength in review.strengths:
                    if strength not in all_strengths:
                        all_strengths.append(strength)
                        
                for suggestion in review.suggestions:
                    if suggestion not in all_suggestions:
                        all_suggestions.append(suggestion)
            
            # Add batch-level issues
            if consistency_score < self.quality_thresholds.consistency_threshold:
                all_issues.append("Inconsistent quality across chapters")
                all_suggestions.append("Standardize chapter quality and structure")
                
            if progression_score < self.quality_thresholds.progression_threshold:
                all_issues.append("Limited story progression across chapters")
                all_suggestions.append("Strengthen narrative arc across chapters")
                
            if style_consistency_score < self.quality_thresholds.style_consistency_threshold:
                all_issues.append("Inconsistent writing style")
                all_suggestions.append("Harmonize tone and style across chapters")
            
            # Calculate confidence
            confidence = min(0.9, sum(review.confidence for review in chapter_reviews) / len(chapter_reviews))
            
            # Phase 3: Record quality trend data
            # Use first chapter number as reference for the batch
            reference_chapter = chapter_numbers[0] if chapter_numbers else 0
            self.record_quality_trend(
                chapter_number=reference_chapter,
                scene_number=None,
                quality_score=average_quality,
                review_type="batch",
                retry_attempt=retry_attempt
            )
            
            # Phase 3: Check if retry is recommended based on thresholds
            should_retry = self.should_retry_based_on_thresholds(
                quality_score=average_quality,
                review_type="batch",
                retry_attempt=retry_attempt
            )
            
            if should_retry:
                all_suggestions.insert(0, f"Batch quality score {average_quality:.2f} below threshold "
                                     f"{self.quality_thresholds.minimum_batch_quality:.2f}. Retry recommended.")
            
            # Create batch review
            batch_review = BatchReview(
                batch_number=batch_number,
                chapter_numbers=chapter_numbers,
                chapter_reviews=chapter_reviews,
                consistency_score=consistency_score,
                progression_score=progression_score,
                style_consistency_score=style_consistency_score,
                total_word_count=total_word_count,
                average_quality=average_quality,
                issues=all_issues,
                strengths=all_strengths,
                suggestions=all_suggestions,
                timestamp=datetime.now().isoformat(),
                confidence=confidence
            )
            
            return batch_review
            
        except Exception as e:
            self.logger.error(f"Error reviewing batch: {e}")
            # Return default review on error
            return BatchReview(
                batch_number=batch_number,
                chapter_numbers=chapter_numbers,
                chapter_reviews=chapter_reviews,
                consistency_score=0.5,
                progression_score=0.5,
                style_consistency_score=0.5,
                total_word_count=sum(review.total_word_count for review in chapter_reviews),
                average_quality=0.5,
                issues=[f"Error during batch review: {str(e)}"],
                strengths=[],
                suggestions=["Retry batch review"],
                timestamp=datetime.now().isoformat(),
                confidence=0.3
            )
    
    def _analyze_chapter_coherence(self, scene_reviews: List[SceneReview]) -> float:
        """Analyze chapter coherence based on scene transitions and flow."""
        try:
            # Basic coherence analysis
            scenes_count = len(scene_reviews)
            if scenes_count == 0:
                return 0.5
            
            # Check for scene length variance (high variance = lower coherence)
            scene_lengths = [scene.word_count for scene in scene_reviews]
            if not scene_lengths:
                return 0.5
                
            avg_length = sum(scene_lengths) / len(scene_lengths)
            variance = sum((length - avg_length) ** 2 for length in scene_lengths) / len(scene_lengths)
            normalized_variance = min(1.0, variance / (avg_length * 0.5))
            
            # Higher variance = lower coherence
            coherence_base = 0.8 - (normalized_variance * 0.3)
            
            # Penalize for very few scenes (less than 3)
            if scenes_count < 3:
                coherence_base -= 0.1
                
            # Penalize for very short scenes
            if any(length < 200 for length in scene_lengths):
                coherence_base -= 0.1
                
            return max(0.1, min(0.9, coherence_base))
            
            # Average scene quality as coherence indicator
            avg_scene_quality = sum(review.quality_score for review in scene_reviews) / scenes_count
            
            # Adjust based on scene count (more scenes = potentially more complex)
            coherence_bonus = min(0.1, scenes_count * 0.02)
            
            return min(1.0, avg_scene_quality + coherence_bonus)
            
        except Exception as e:
            self.logger.error(f"Error analyzing chapter coherence: {e}")
            return 0.5
    
    def _analyze_chapter_pacing(self, chapter_content: str, scene_reviews: List[SceneReview]) -> float:
        """Analyze chapter pacing based on scene lengths and variety."""
        try:
            if not scene_reviews:
                return 0.5
            
            # Calculate scene length variance (good pacing has variety)
            scene_lengths = [review.word_count for review in scene_reviews]
            if len(scene_lengths) < 2:
                return 0.6  # Single scene, decent pacing
            
            avg_length = sum(scene_lengths) / len(scene_lengths)
            variance = sum((length - avg_length) ** 2 for length in scene_lengths) / len(scene_lengths)
            
            # Normalize variance to 0-1 scale (some variance is good)
            normalized_variance = min(1.0, variance / (avg_length ** 2))
            
            # Good pacing has moderate variance (not too uniform, not too chaotic)
            if 0.1 <= normalized_variance <= 0.4:
                pacing_score = 0.8
            elif normalized_variance < 0.1:
                pacing_score = 0.6  # Too uniform
            else:
                pacing_score = 0.5  # Too chaotic
            
            return pacing_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing chapter pacing: {e}")
            return 0.5
    
    def _analyze_character_development(self, chapter_content: str) -> float:
        """Analyze character development indicators in the chapter."""
        try:
            # Simple heuristics for character development
            content_lower = chapter_content.lower()
            
            # Look for dialogue (character interaction)
            dialogue_count = content_lower.count('"') + content_lower.count("'")
            dialogue_score = min(0.3, dialogue_count * 0.01)
            
            # Look for emotional/internal words
            emotion_words = ['felt', 'thought', 'realized', 'wondered', 'hoped', 'feared', 'remembered']
            emotion_count = sum(content_lower.count(word) for word in emotion_words)
            emotion_score = min(0.3, emotion_count * 0.05)
            
            # Look for action/decision words
            action_words = ['decided', 'chose', 'determined', 'resolved', 'acted', 'moved']
            action_count = sum(content_lower.count(word) for word in action_words)
            action_score = min(0.2, action_count * 0.05)
            
            # Base score for having content
            base_score = 0.2
            
            total_score = base_score + dialogue_score + emotion_score + action_score
            return min(1.0, total_score)
            
        except Exception as e:
            self.logger.error(f"Error analyzing character development: {e}")
            return 0.5
    
    def _analyze_batch_consistency(self, chapter_reviews: List[ChapterReview]) -> float:
        """Analyze consistency across chapters in a batch."""
        try:
            if len(chapter_reviews) < 2:
                return 0.8  # Single chapter is consistent with itself
            
            # Check quality consistency
            qualities = [review.overall_quality for review in chapter_reviews]
            quality_variance = sum((q - sum(qualities)/len(qualities))**2 for q in qualities) / len(qualities)
            quality_consistency = max(0.0, 1.0 - quality_variance * 2)
            
            # Check word count consistency
            word_counts = [review.total_word_count for review in chapter_reviews]
            avg_words = sum(word_counts) / len(word_counts)
            word_variance = sum((w - avg_words)**2 for w in word_counts) / len(word_counts)
            word_consistency = max(0.0, 1.0 - (word_variance / (avg_words**2)))
            
            # Weighted average
            consistency = (quality_consistency * 0.7) + (word_consistency * 0.3)
            return min(1.0, consistency)
            
        except Exception as e:
            self.logger.error(f"Error analyzing batch consistency: {e}")
            return 0.5
    
    def _analyze_story_progression(self, chapter_reviews: List[ChapterReview]) -> float:
        """Analyze story progression across chapters."""
        try:
            if len(chapter_reviews) < 2:
                return 0.7  # Single chapter, assume decent progression
            
            # Check if chapters are in sequence
            chapter_numbers = [review.chapter_number for review in chapter_reviews]
            is_sequential = all(chapter_numbers[i] == chapter_numbers[i-1] + 1 
                              for i in range(1, len(chapter_numbers)))
            
            if is_sequential:
                progression_score = 0.8
            else:
                progression_score = 0.6  # Non-sequential, but still valid
            
            # Bonus for variety in sections
            sections = set(review.section_name for review in chapter_reviews)
            if len(sections) > 1:
                progression_score += 0.1
            
            return min(1.0, progression_score)
            
        except Exception as e:
            self.logger.error(f"Error analyzing story progression: {e}")
            return 0.5
    
    def _analyze_style_consistency(self, chapter_reviews: List[ChapterReview]) -> float:
        """Analyze style consistency across chapters."""
        try:
            if len(chapter_reviews) < 2:
                return 0.8  # Single chapter is consistent with itself
            
            # Use character development scores as style indicator
            char_dev_scores = [review.character_development_score for review in chapter_reviews]
            avg_char_dev = sum(char_dev_scores) / len(char_dev_scores)
            char_dev_variance = sum((s - avg_char_dev)**2 for s in char_dev_scores) / len(char_dev_scores)
            
            # Use pacing scores as another style indicator
            pacing_scores = [review.pacing_score for review in chapter_reviews]
            avg_pacing = sum(pacing_scores) / len(pacing_scores)
            pacing_variance = sum((s - avg_pacing)**2 for s in pacing_scores) / len(pacing_scores)
            
            # Lower variance = higher consistency
            char_consistency = max(0.0, 1.0 - char_dev_variance * 4)
            pacing_consistency = max(0.0, 1.0 - pacing_variance * 4)
            
            # Average the consistency measures
            style_consistency = (char_consistency + pacing_consistency) / 2
            return min(1.0, style_consistency)
            
        except Exception as e:
            self.logger.error(f"Error analyzing style consistency: {e}")
            return 0.5
    
    # ========== REVIEW DATA PERSISTENCE METHODS ==========
    
    def _save_scene_review(self, scene_review: SceneReview) -> None:
        """Save scene review data to the quality directory."""
        try:
            # Create quality/reviews directory if it doesn't exist
            reviews_dir = os.path.join(self.dir_manager.get_quality_dir(), "reviews")
            os.makedirs(reviews_dir, exist_ok=True)
            
            # Save scene review
            filename = f"scene_ch{scene_review.chapter_number}_sc{scene_review.scene_number}_review.json"
            filepath = os.path.join(reviews_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(scene_review), f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Saved scene review: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving scene review: {e}")
    
    def _save_chapter_review(self, chapter_review: ChapterReview) -> None:
        """Save chapter review data to the quality directory."""
        try:
            # Create quality/reviews directory if it doesn't exist
            reviews_dir = os.path.join(self.dir_manager.get_quality_dir(), "reviews")
            os.makedirs(reviews_dir, exist_ok=True)
            
            # Save chapter review
            filename = f"chapter_{chapter_review.chapter_number}_review.json"
            filepath = os.path.join(reviews_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(chapter_review), f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Saved chapter review: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving chapter review: {e}")
    
    def _save_batch_review(self, batch_review: BatchReview) -> None:
        """Save batch review data to the quality directory."""
        try:
            # Create quality/reviews directory if it doesn't exist
            reviews_dir = os.path.join(self.dir_manager.get_quality_dir(), "reviews")
            os.makedirs(reviews_dir, exist_ok=True)
            
            # Save batch review
            filename = f"batch_{batch_review.batch_number}_review.json"
            filepath = os.path.join(reviews_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(batch_review), f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Saved batch review: {filename}")
            
            # Also save summary metrics
            self._save_batch_metrics_summary(batch_review)
            
        except Exception as e:
            self.logger.error(f"Error saving batch review: {e}")
    
    def _save_batch_metrics_summary(self, batch_review: BatchReview) -> None:
        """Save batch metrics summary for dashboard/reporting."""
        try:
            # Create quality/metrics directory if it doesn't exist
            metrics_dir = os.path.join(self.dir_manager.get_quality_dir(), "metrics")
            os.makedirs(metrics_dir, exist_ok=True)
            
            # Create metrics summary
            metrics_summary = {
                "batch_number": batch_review.batch_number,
                "timestamp": batch_review.timestamp,
                "chapters_count": len(batch_review.chapter_numbers),
                "total_word_count": batch_review.total_word_count,
                "average_quality": batch_review.average_quality,
                "consistency_score": batch_review.consistency_score,
                "progression_score": batch_review.progression_score,
                "style_consistency_score": batch_review.style_consistency_score,
                "issues_count": len(batch_review.issues),
                "suggestions_count": len(batch_review.suggestions),
                "confidence": batch_review.confidence,
                "chapter_details": [
                    {
                        "chapter_number": ch.chapter_number,
                        "section_name": ch.section_name,
                        "quality_score": ch.overall_quality,
                        "word_count": ch.total_word_count,
                        "scene_count": len(ch.scene_reviews)
                    }
                    for ch in batch_review.chapter_reviews
                ]
            }
            
            # Save metrics summary
            filename = f"batch_{batch_review.batch_number}_metrics.json"
            filepath = os.path.join(metrics_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metrics_summary, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Saved batch metrics: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving batch metrics: {e}")
    
    def _load_chapter_review(self, chapter_number: int) -> Optional[ChapterReview]:
        """Load chapter review from file."""
        try:
            reviews_dir = os.path.join(self.dir_manager.get_quality_dir(), "reviews")
            filename = f"chapter_{chapter_number}_review.json"
            filepath = os.path.join(reviews_dir, filename)
            
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                review_data = json.load(f)
                
            # Convert scene reviews back to objects
            scene_reviews = []
            for scene_data in review_data.get('scene_reviews', []):
                scene_review = SceneReview(**scene_data)
                scene_reviews.append(scene_review)
            
            # Create chapter review object
            review_data['scene_reviews'] = scene_reviews
            chapter_review = ChapterReview(**review_data)
            
            return chapter_review
            
        except Exception as e:
            self.logger.error(f"Error loading chapter review for chapter {chapter_number}: {e}")
            return None
    
    # Phase 3: Advanced Analytics & Optimization Methods
    
    def record_quality_trend(self, chapter_number: int, scene_number: Optional[int], 
                           quality_score: float, review_type: str, retry_attempt: int = 0) -> None:
        """Record quality trend data for analytics."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Calculate improvement from previous attempt
            improvement = self._calculate_quality_improvement(
                chapter_number, scene_number, quality_score, review_type, retry_attempt
            )
            
            trend = QualityTrend(
                timestamp=timestamp,
                chapter_number=chapter_number,
                scene_number=scene_number,
                quality_score=quality_score,
                review_type=review_type,
                improvement_from_previous=improvement,
                retry_attempt=retry_attempt
            )
            
            # Save trend data
            self._save_quality_trend(trend)
            
            # Update cache
            self._quality_trends_cache.append(trend)
            self._last_cache_update = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error recording quality trend: {e}")
    
    def _calculate_quality_improvement(self, chapter_number: int, scene_number: Optional[int],
                                     current_score: float, review_type: str, retry_attempt: int) -> Optional[float]:
        """Calculate quality improvement from previous attempt or similar content."""
        try:
            # Load previous trends for comparison
            trends = self.get_quality_trends()
            
            # Find most recent similar review
            previous_score = None
            for trend in reversed(trends):
                if (trend.chapter_number == chapter_number and 
                    trend.scene_number == scene_number and
                    trend.review_type == review_type and
                    trend.retry_attempt == retry_attempt - 1):
                    previous_score = trend.quality_score
                    break
            
            if previous_score is not None:
                return current_score - previous_score
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating quality improvement: {e}")
            return None
    
    def _save_quality_trend(self, trend: QualityTrend) -> None:
        """Save quality trend data to file."""
        try:
            trends_dir = os.path.join(self.dir_manager.get_quality_dir(), "trends")
            os.makedirs(trends_dir, exist_ok=True)
            
            # Create filename based on trend type and identifiers
            if trend.scene_number is not None:
                filename = f"trend_ch{trend.chapter_number}_sc{trend.scene_number}_{trend.review_type}.json"
            else:
                filename = f"trend_ch{trend.chapter_number}_{trend.review_type}.json"
            
            filepath = os.path.join(trends_dir, filename)
            
            # Load existing trends or create new list
            trends_list = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    trends_list = json.load(f)
            
            # Add new trend
            trends_list.append(asdict(trend))
            
            # Save updated trends
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(trends_list, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving quality trend: {e}")
    
    def get_quality_trends(self, chapter_number: Optional[int] = None, 
                          review_type: Optional[str] = None) -> List[QualityTrend]:
        """Get quality trends with optional filtering."""
        try:
            # Check cache first (performance optimization)
            if (self._last_cache_update and 
                (datetime.now() - self._last_cache_update).total_seconds() < self._cache_ttl_seconds):
                trends = self._quality_trends_cache.copy()
            else:
                # Load from files
                trends = self._load_all_quality_trends()
                self._quality_trends_cache = trends.copy()
                self._last_cache_update = datetime.now()
            
            # Apply filters
            if chapter_number is not None:
                trends = [t for t in trends if t.chapter_number == chapter_number]
            
            if review_type is not None:
                trends = [t for t in trends if t.review_type == review_type]
            
            return sorted(trends, key=lambda t: t.timestamp)
            
        except Exception as e:
            self.logger.error(f"Error getting quality trends: {e}")
            return []
    
    def _load_all_quality_trends(self) -> List[QualityTrend]:
        """Load all quality trends from files."""
        trends = []
        try:
            trends_dir = os.path.join(self.dir_manager.get_quality_dir(), "trends")
            
            if not os.path.exists(trends_dir):
                return trends
            
            # Load all trend files
            for filename in os.listdir(trends_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(trends_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        trend_data_list = json.load(f)
                    
                    for trend_data in trend_data_list:
                        trend = QualityTrend(**trend_data)
                        trends.append(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error loading quality trends: {e}")
            return trends
    
    def analyze_quality_trends(self, chapter_number: Optional[int] = None) -> Dict[str, Any]:
        """Analyze quality trends and provide insights."""
        try:
            trends = self.get_quality_trends(chapter_number)
            
            if not trends:
                return {
                    "total_reviews": 0,
                    "average_quality": 0.0,
                    "quality_trend": "no_data",
                    "improvement_rate": 0.0,
                    "retry_rate": 0.0
                }
            
            # Calculate basic statistics
            total_reviews = len(trends)
            average_quality = sum(t.quality_score for t in trends) / total_reviews
            
            # Calculate improvement trend
            improvements = [t.improvement_from_previous for t in trends if t.improvement_from_previous is not None]
            improvement_rate = sum(improvements) / len(improvements) if improvements else 0.0
            
            # Calculate retry rate
            retries = [t for t in trends if t.retry_attempt > 0]
            retry_rate = len(retries) / total_reviews if total_reviews > 0 else 0.0
            
            # Determine overall trend
            if len(trends) >= 3:
                recent_scores = [t.quality_score for t in trends[-3:]]
                early_scores = [t.quality_score for t in trends[:3]]
                recent_avg = sum(recent_scores) / len(recent_scores)
                early_avg = sum(early_scores) / len(early_scores)
                
                if recent_avg > early_avg + 0.05:
                    quality_trend = "improving"
                elif recent_avg < early_avg - 0.05:
                    quality_trend = "declining"
                else:
                    quality_trend = "stable"
            else:
                quality_trend = "insufficient_data"
            
            return {
                "total_reviews": total_reviews,
                "average_quality": round(average_quality, 3),
                "quality_trend": quality_trend,
                "improvement_rate": round(improvement_rate, 3),
                "retry_rate": round(retry_rate, 3),
                "latest_quality": trends[-1].quality_score if trends else 0.0,
                "best_quality": max(t.quality_score for t in trends),
                "worst_quality": min(t.quality_score for t in trends)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing quality trends: {e}")
            return {"error": str(e)}
    
    def should_retry_based_on_thresholds(self, quality_score: float, review_type: str, 
                                       retry_attempt: int = 0) -> bool:
        """Determine if content should be retried based on configurable thresholds."""
        try:
            if not self.quality_thresholds.retry_below_threshold:
                return False
            
            if retry_attempt >= self.quality_thresholds.max_retries:
                return False
            
            # Check against appropriate threshold
            if review_type == "scene":
                return quality_score < self.quality_thresholds.minimum_scene_quality
            elif review_type == "chapter":
                return quality_score < self.quality_thresholds.minimum_chapter_quality
            elif review_type == "batch":
                return quality_score < self.quality_thresholds.minimum_batch_quality
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking retry thresholds: {e}")
            return False
    
    def generate_quality_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive quality dashboard data."""
        try:
            # Overall trends analysis
            overall_analysis = self.analyze_quality_trends()
            
            # Per-chapter analysis
            chapter_analyses = {}
            trends = self.get_quality_trends()
            chapter_numbers = list(set(t.chapter_number for t in trends))
            
            for chapter_num in sorted(chapter_numbers):
                chapter_analyses[f"chapter_{chapter_num}"] = self.analyze_quality_trends(chapter_num)
            
            # Review type breakdown
            review_type_stats = {}
            for review_type in ["scene", "chapter", "batch"]:
                type_trends = self.get_quality_trends(review_type=review_type)
                if type_trends:
                    review_type_stats[review_type] = {
                        "count": len(type_trends),
                        "average_quality": sum(t.quality_score for t in type_trends) / len(type_trends),
                        "latest_quality": type_trends[-1].quality_score
                    }
            
            # Threshold compliance
            threshold_compliance = {
                "scene_threshold": self.quality_thresholds.minimum_scene_quality,
                "chapter_threshold": self.quality_thresholds.minimum_chapter_quality,
                "batch_threshold": self.quality_thresholds.minimum_batch_quality,
                "retry_enabled": self.quality_thresholds.retry_below_threshold,
                "max_retries": self.quality_thresholds.max_retries
            }
            
            return {
                "generated_at": datetime.now().isoformat(),
                "overall_analysis": overall_analysis,
                "chapter_analyses": chapter_analyses,
                "review_type_stats": review_type_stats,
                "threshold_compliance": threshold_compliance,
                "cache_status": {
                    "last_update": self._last_cache_update.isoformat() if self._last_cache_update else None,
                    "cached_trends": len(self._quality_trends_cache),
                    "ttl_seconds": self._cache_ttl_seconds
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating quality dashboard: {e}")
            return {"error": str(e)}
    
    def save_quality_dashboard(self) -> str:
        """Save quality dashboard to file and return filepath."""
        try:
            dashboard_data = self.generate_quality_dashboard()
            
            # Save to quality/reports directory
            reports_dir = os.path.join(self.dir_manager.get_quality_dir(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_dashboard_{timestamp}.json"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            # Also save as latest dashboard
            latest_filepath = os.path.join(reports_dir, "quality_dashboard_latest.json")
            with open(latest_filepath, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Quality dashboard saved: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving quality dashboard: {e}")
            return ""


# Convenience functions for integration
def analyze_story_chapters(output_dir: str, app_instance=None) -> Tuple[List[ChapterInfo], ChapterWritingPlan]:
    """Analyze story structure and create writing plan."""
    agent = ChapterWritingAgent(output_dir, app_instance)
    chapter_info_list, _ = agent.analyze_chapter_structure()
    plan = agent.create_writing_plan(chapter_info_list)
    return chapter_info_list, plan


def write_next_chapters(output_dir: str, batch_size: int = 1, app_instance=None) -> AgentResult:
    """Write the next batch of chapters automatically."""
    agent = ChapterWritingAgent(output_dir, app_instance)
    chapter_info_list, _ = agent.analyze_chapter_structure()
    plan = agent.create_writing_plan(chapter_info_list, batch_size)
    return agent.write_chapters_batch(chapter_info_list, plan)


def get_chapter_progress(output_dir: str, app_instance=None) -> Dict[str, Any]:
    """Get progress report on chapter writing."""
    agent = ChapterWritingAgent(output_dir, app_instance)
    chapter_info_list, _ = agent.analyze_chapter_structure()
    return agent.get_progress_report(chapter_info_list)
