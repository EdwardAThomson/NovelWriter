"""
Genre Handler System for NovelWriter

This module provides a factory pattern for getting genre-specific handlers
that know how to generate factions, process lore data, and handle character attributes.
"""

from .scifi_handler import SciFiHandler
from .fantasy_handler import FantasyHandler
from .horror_handler import HorrorHandler
from .mystery_handler import MysteryHandler
from .romance_handler import RomanceHandler
from .thriller_handler import ThrillerHandler
from .western_handler import WesternHandler
from .historical_handler import HistoricalHandler

# Registry of available genre handlers
GENRE_HANDLERS = {
    "Sci-Fi": SciFiHandler,
    "Fantasy": FantasyHandler,
    "Horror": HorrorHandler,
    "Mystery": MysteryHandler,
    "Romance": RomanceHandler,
    "Thriller": ThrillerHandler,
    "Western": WesternHandler,
    "Historical Fiction": HistoricalHandler,
}

def get_genre_handler(genre_name):
    """
    Factory function to get the appropriate genre handler.
    
    Args:
        genre_name (str): The genre name (e.g., "Sci-Fi", "Fantasy")
    
    Returns:
        GenreHandler: An instance of the appropriate genre handler
    
    Raises:
        ValueError: If the genre is not supported
    """
    if genre_name not in GENRE_HANDLERS:
        available_genres = ", ".join(GENRE_HANDLERS.keys())
        raise ValueError(f"Unsupported genre: {genre_name}. Available genres: {available_genres}")
    
    handler_class = GENRE_HANDLERS[genre_name]
    return handler_class()

def get_supported_genres():
    """
    Get a list of all supported genres.
    
    Returns:
        list: List of supported genre names
    """
    return list(GENRE_HANDLERS.keys()) 