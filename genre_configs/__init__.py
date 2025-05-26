# Import other genre config classes as they're added

import importlib
import json
from pathlib import Path

def load_user_configs(genre: str) -> dict:
    """Load user-defined configurations from JSON files"""
    config_path = Path(f"configs/user/{genre.lower()}_configs.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def get_genre_config(genre: str, subgenre: str) -> dict:
    """
    Get genre configurations from both built-in and user configs.
    
    Args:
        genre (str): The main genre (e.g., "Sci-Fi", "Fantasy")
        subgenre (str): The specific subgenre
    
    Returns:
        dict: Combined built-in and user configurations
    """
    # Convert genre name to module name format (e.g., "Sci-Fi" -> "scifi")
    module_name = genre.lower().replace("-", "").replace(" ", "")
    
    # Special mappings for genres with different module names
    module_name_map = {
        "historicalfiction": "historical"
    }
    module_name = module_name_map.get(module_name, module_name)
    
    # Get built-in configs
    built_in_configs = {}
    try:
        module = importlib.import_module(f"genre_configs.{module_name}")
        
        # Map genre names to their config class names
        class_name_map = {
            "scifi": "SciFiConfigs",
            "fantasy": "FantasyConfigs", 
            "western": "WesternConfigs",
            "mystery": "MysteryConfigs",
            "romance": "RomanceConfigs",
            "horror": "HorrorConfigs",
            "thriller": "ThrillerConfigs",
            "historical": "HistoricalConfigs",
            "historicalfiction": "HistoricalConfigs"
        }
        
        configs_class_name = class_name_map.get(module_name, f"{module_name.capitalize()}Configs")
        built_in_configs = getattr(module, configs_class_name).CONFIGS
    except (ImportError, AttributeError) as e:
        print(f"Warning: No built-in configuration found for genre: {genre} ({str(e)})")

    # Get user configs
    user_configs = load_user_configs(genre)
    
    # Combine configs, with user configs taking precedence
    combined_configs = {**built_in_configs, **user_configs}
    
    return combined_configs.get(subgenre, {}) 