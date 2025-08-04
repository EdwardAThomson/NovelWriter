"""
Directory Configuration for NovelWriter

This module provides centralized directory path management to support
the new structured directory hierarchy while maintaining backward compatibility.
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class DirectoryPaths:
    """Centralized directory path configuration."""
    
    # Root directories
    story_root: str = "story"
    quality_root: str = "quality" 
    system_root: str = "system"
    archive_root: str = "archive"
    
    # Story subdirectories
    lore_dir: str = "story/lore"
    structure_dir: str = "story/structure"
    planning_dir: str = "story/planning"
    content_dir: str = "story/content"
    
    # Planning subdirectories
    chapter_outlines_dir: str = "story/planning/chapter_outlines"
    scene_plans_dir: str = "story/planning/detailed_scene_plans"
    
    # Content subdirectories
    chapters_dir: str = "story/content/chapters"
    backgrounds_dir: str = "story/lore/backgrounds"
    structure_outlines_dir: str = "story/structure/structure_outlines"
    
    # Quality subdirectories
    reviews_dir: str = "quality/reviews"
    scene_reviews_dir: str = "quality/reviews/scene_reviews"
    chapter_reviews_dir: str = "quality/reviews/chapter_reviews"
    batch_reviews_dir: str = "quality/reviews/batch_reviews"
    metrics_dir: str = "quality/metrics"
    reports_dir: str = "quality/reports"
    
    # System subdirectories
    logs_dir: str = "system/logs"
    prompts_dir: str = "system/prompts"
    metadata_dir: str = "system/metadata"
    
    # Archive subdirectories
    previous_versions_dir: str = "archive/previous_versions"
    failed_generations_dir: str = "archive/failed_generations"


class DirectoryManager:
    """Manages directory paths and provides backward compatibility."""
    
    def __init__(self, output_dir: str, use_new_structure: bool = False):
        """
        Initialize directory manager.
        
        Args:
            output_dir: Base output directory (e.g., "current_work")
            use_new_structure: Whether to use new structured directories
        """
        self.output_dir = output_dir
        self.use_new_structure = use_new_structure
        self.paths = DirectoryPaths()
        
        # Legacy path mappings for backward compatibility
        self.legacy_paths = {
            "detailed_scene_plans": "detailed_scene_plans",
            "chapters": "chapters",
            "prompts": "prompts"
        }
    
    def get_path(self, path_type: str) -> str:
        """
        Get the appropriate path based on current configuration.
        
        Args:
            path_type: Type of path needed (e.g., 'scene_plans_dir', 'chapters_dir')
            
        Returns:
            Full path relative to output_dir
        """
        if self.use_new_structure:
            # Use new structured paths
            return getattr(self.paths, path_type, path_type)
        else:
            # Use legacy flat structure
            return self.legacy_paths.get(path_type, path_type)
    
    def get_full_path(self, path_type: str) -> str:
        """Get full absolute path."""
        relative_path = self.get_path(path_type)
        return os.path.join(self.output_dir, relative_path)
    
    def ensure_directories_exist(self) -> None:
        """Create all necessary directories."""
        if self.use_new_structure:
            # Create new structured directories
            dirs_to_create = [
                self.paths.story_root,
                self.paths.lore_dir,
                self.paths.structure_dir,
                self.paths.planning_dir,
                self.paths.content_dir,
                self.paths.chapter_outlines_dir,
                self.paths.scene_plans_dir,
                self.paths.chapters_dir,
                self.paths.backgrounds_dir,
                self.paths.structure_outlines_dir,
                self.paths.quality_root,
                self.paths.reviews_dir,
                self.paths.scene_reviews_dir,
                self.paths.chapter_reviews_dir,
                self.paths.batch_reviews_dir,
                self.paths.metrics_dir,
                self.paths.reports_dir,
                self.paths.system_root,
                self.paths.logs_dir,
                self.paths.prompts_dir,
                self.paths.metadata_dir,
                self.paths.archive_root,
                self.paths.previous_versions_dir,
                self.paths.failed_generations_dir
            ]
        else:
            # Create legacy directories
            dirs_to_create = [
                "detailed_scene_plans",
                "chapters",
                "prompts"
            ]
        
        for dir_path in dirs_to_create:
            full_path = os.path.join(self.output_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
    
    def migrate_to_new_structure(self) -> Dict[str, str]:
        """
        Migrate files from flat structure to new structured directories.
        
        Returns:
            Dictionary mapping old paths to new paths for migrated files
        """
        migration_log = {}
        
        if not os.path.exists(self.output_dir):
            return migration_log
        
        # Ensure new directories exist
        self.use_new_structure = True
        self.ensure_directories_exist()
        
        # Define migration mappings
        file_migrations = {
            # Story parameters
            "parameters.txt": "story/parameters.txt",
            "story_parameters.txt": "story/parameters.txt",
            
            # Lore files
            "generated_lore.md": "story/lore/generated_lore.md",
            "characters.json": "story/lore/characters.json",
            "factions.json": "story/lore/factions.json",
            
            # Character backgrounds
            "background_protagonist_*.md": "story/lore/backgrounds/",
            "background_deuteragonist_*.md": "story/lore/backgrounds/",
            "background_antagonist_*.md": "story/lore/backgrounds/",
            
            # Structure files
            "character_arcs.md": "story/structure/character_arcs.md",
            "faction_arcs.md": "story/structure/faction_arcs.md",
            "reconciled_arcs.md": "story/structure/reconciled_arcs.md",
            "reconciled_locations_arcs.md": "story/structure/reconciled_locations_arcs.md",
            
            # Structure outlines (pattern-based)
            "*_structure_*.md": "story/structure/structure_outlines/",
            
            # System files
            "application.log": "system/logs/application.log",
            "review_analysis.log": "system/logs/review_analysis.log",
            
            # Quality files
            "content_review_data.json": "quality/metrics/content_review_data.json",
            "detailed_content_reviews.txt": "quality/reports/detailed_content_reviews.txt",
            
            # Titles and metadata
            "suggested_titles.md": "story/suggested_titles.md"
        }
        
        # Directory migrations
        directory_migrations = {
            "detailed_scene_plans/": "story/planning/detailed_scene_plans/",
            "chapters/": "story/content/chapters/",
            "prompts/": "system/prompts/"
        }
        
        # Migrate individual files
        for pattern, new_path in file_migrations.items():
            if "*" in pattern:
                # Handle wildcard patterns
                self._migrate_pattern_files(pattern, new_path, migration_log)
            else:
                # Handle specific files
                old_path = os.path.join(self.output_dir, pattern)
                if os.path.exists(old_path):
                    new_full_path = os.path.join(self.output_dir, new_path)
                    os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                    os.rename(old_path, new_full_path)
                    migration_log[pattern] = new_path
        
        # Migrate directories
        for old_dir, new_dir in directory_migrations.items():
            old_full_path = os.path.join(self.output_dir, old_dir)
            if os.path.exists(old_full_path):
                new_full_path = os.path.join(self.output_dir, new_dir)
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                
                # Move all files from old directory to new directory
                for filename in os.listdir(old_full_path):
                    old_file = os.path.join(old_full_path, filename)
                    new_file = os.path.join(new_full_path, filename)
                    os.rename(old_file, new_file)
                    migration_log[f"{old_dir}{filename}"] = f"{new_dir}{filename}"
                
                # Remove empty old directory
                os.rmdir(old_full_path)
        
        return migration_log
    
    def _migrate_pattern_files(self, pattern: str, target_dir: str, migration_log: Dict[str, str]) -> None:
        """Migrate files matching a wildcard pattern."""
        import glob
        
        # Convert pattern to glob pattern
        glob_pattern = os.path.join(self.output_dir, pattern)
        matching_files = glob.glob(glob_pattern)
        
        for file_path in matching_files:
            filename = os.path.basename(file_path)
            new_path = os.path.join(target_dir, filename)
            new_full_path = os.path.join(self.output_dir, new_path)
            
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
            os.rename(file_path, new_full_path)
            migration_log[os.path.relpath(file_path, self.output_dir)] = new_path
    
    def get_scene_plans_dir(self) -> str:
        """Get scene plans directory path (backward compatibility method)."""
        if self.use_new_structure:
            return self.paths.scene_plans_dir
        else:
            return "detailed_scene_plans"
    
    def get_chapters_dir(self) -> str:
        """Get chapters directory path (backward compatibility method)."""
        if self.use_new_structure:
            return self.paths.chapters_dir
        else:
            return "chapters"
    
    def get_prompts_dir(self) -> str:
        """Get prompts directory path (backward compatibility method)."""
        if self.use_new_structure:
            return self.paths.prompts_dir
        else:
            return "prompts"
    
    def get_quality_dir(self) -> str:
        """Get quality directory path (for review system)."""
        if self.use_new_structure:
            return self.paths.quality_root
        else:
            # For legacy structure, create quality directory in root
            return "quality"


# Global configuration - can be set by user preferences
DEFAULT_USE_NEW_STRUCTURE = False


def get_directory_manager(output_dir: str, use_new_structure: Optional[bool] = None) -> DirectoryManager:
    """
    Get a directory manager instance.
    
    Args:
        output_dir: Base output directory
        use_new_structure: Whether to use new structure (defaults to global setting)
        
    Returns:
        DirectoryManager instance
    """
    if use_new_structure is None:
        use_new_structure = DEFAULT_USE_NEW_STRUCTURE
    
    return DirectoryManager(output_dir, use_new_structure)


def set_global_structure_preference(use_new_structure: bool) -> None:
    """Set global preference for directory structure."""
    global DEFAULT_USE_NEW_STRUCTURE
    DEFAULT_USE_NEW_STRUCTURE = use_new_structure
