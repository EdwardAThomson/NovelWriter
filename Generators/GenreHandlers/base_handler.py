"""
Base Genre Handler

Defines the interface that all genre handlers must implement.
"""

from abc import ABC, abstractmethod

class BaseGenreHandler(ABC):
    """
    Abstract base class for genre handlers.
    
    Each genre handler must implement methods for:
    - Generating factions
    - Processing faction data for lore generation
    - Defining character attributes
    - Getting world type mappings
    """
    
    @abstractmethod
    def generate_factions(self, num_factions, female_percentage=50, male_percentage=50, subgenre="", **kwargs):
        """
        Generate factions for this genre.
        
        Args:
            num_factions (int): Number of factions to generate
            female_percentage (int): Percentage of female characters
            male_percentage (int): Percentage of male characters
            subgenre (str): Specific subgenre
            **kwargs: Additional genre-specific parameters
        
        Returns:
            list: List of faction dictionaries
        """
        pass
    
    @abstractmethod
    def save_factions(self, factions, filename):
        """
        Save factions using the appropriate save function for this genre.
        
        Args:
            factions (list): List of faction dictionaries
            filename (str): Output filename
        """
        pass
    
    @abstractmethod
    def get_faction_capitals_info(self, factions):
        """
        Extract capital information from factions for lore generation.
        
        Args:
            factions (list): List of faction dictionaries
        
        Returns:
            str: Formatted string with faction capital information
        """
        pass
    
    @abstractmethod
    def get_character_attributes(self):
        """
        Get the list of character attributes relevant to this genre.
        
        Returns:
            list: List of character attribute keys
        """
        pass
    
    @abstractmethod
    def get_world_type_mapping(self):
        """
        Get the mapping of subgenres to world types for this genre.
        
        Returns:
            dict: Mapping of subgenre names to world type parameters
        """
        pass
    
    @abstractmethod
    def generate_characters(self, num_characters, female_percentage=50, male_percentage=50, **kwargs):
        """
        Generate characters for this genre.
        
        Args:
            num_characters (int): Number of characters to generate
            female_percentage (int): Percentage of female characters
            male_percentage (int): Percentage of male characters
            **kwargs: Additional genre-specific parameters
        
        Returns:
            list: List of character objects
        """
        pass
    
    @abstractmethod
    def save_characters(self, characters, filename):
        """
        Save characters using the appropriate save function for this genre.
        
        Args:
            characters (list): List of character objects
            filename (str): Output filename
        """
        pass
    
    @abstractmethod
    def get_genre_name(self):
        """
        Get the name of this genre.
        
        Returns:
            str: Genre name
        """
        pass
    
    def uses_factions(self):
        """
        Determine if this genre uses traditional factions as organizational structures.
        
        Returns:
            bool: True if genre uses factions, False otherwise
        """
        return True  # Default to True for backward compatibility
    
    def get_organization_type(self):
        """
        Get the type of organizational structure this genre uses.
        
        Returns:
            str: Type of organization (e.g., "factions", "agencies", "families", "groups")
        """
        return "factions"  # Default organizational type 

    @abstractmethod
    def get_location_info_from_factions(self, factions):
        """
        Extract location information from factions for story arc integration.
        This is a generic version of get_faction_capitals_info that works for any genre.
        
        Args:
            factions (list): List of faction dictionaries
        
        Returns:
            list: List of location dictionaries with keys like 'name', 'controlled_by', 'type'
        """
        pass

    def get_location_type_name(self):
        """
        Get the name of the location type this genre uses (for UI display).
        
        Returns:
            str: Location type name (e.g., "Planets", "Cities", "Territories")
        """
        return "Locations"  # Default generic name 