"""
Fantasy Genre Handler

Handles faction generation, lore processing, and character attributes for Fantasy.
"""

from .base_handler import BaseGenreHandler
from ..FantasyGenerator import generate_fantasy_world, save_factions_to_file
from ..FantasyCharacterGenerator import generate_fantasy_main_characters, save_fantasy_characters_to_file

class FantasyHandler(BaseGenreHandler):
    """Handler for Fantasy genre."""
    
    def generate_factions(self, num_factions, female_percentage=50, male_percentage=50, subgenre="", **kwargs):
        """Generate fantasy factions using the FantasyGenerator."""
        # Determine world type based on subgenre
        world_type = self._get_world_type_for_subgenre(subgenre)
        
        return generate_fantasy_world(
            num_factions=num_factions, 
            include_races=True,  # Enable fantasy races
            female_percentage=female_percentage, 
            male_percentage=male_percentage,
            world_type=world_type
        )
    
    def save_factions(self, factions, filename):
        """Save fantasy factions using the Fantasy save function."""
        save_factions_to_file(factions=factions, filename=filename)
    
    def get_faction_capitals_info(self, factions):
        """Extract capital region and city information for fantasy factions."""
        faction_section = "\n## Faction Capitals:\n"
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            # Find the capital region and city
            capital_region = next((region for region in faction.get("regions", []) if region.get("is_capital_region", False)), None)
            if capital_region:
                capital_city = next((city for city in capital_region.get("cities", []) 
                                  if city.get("is_capital", False)), None)
                if capital_city:
                    faction_section += f"- {faction_name}: {capital_city.get('name', 'N/A')} in {capital_region.get('name', 'N/A')}\n"
                    stats = capital_city.get("stats", {})
                    faction_section += f"  - Population: {stats.get('population', 'Unknown')}\n"
                    faction_section += f"  - Climate: {stats.get('climate', 'Unknown')}\n"
                    faction_section += f"  - Infrastructure: {stats.get('infrastructure', {}).get('description', 'Unknown')}\n"
                    faction_section += f"  - Terrain: {capital_region.get('terrain_type', 'Unknown')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to fantasy settings."""
        return ['gender', 'age', 'title', 'occupation', 'faction', 'faction_role', 
                'homeland', 'home_region', 'race', 'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for fantasy."""
        return {
            "High Fantasy": "political",
            "Mythic Fantasy": "political", 
            "Urban Fantasy": "city_states",
            "Sword and Sorcery": "city_states",
            "Dark Fantasy": "magical",
            "Fairy Tale": "balanced",
        }
    
    def generate_characters(self, num_characters, female_percentage=50, male_percentage=50, **kwargs):
        """Generate fantasy characters using the FantasyCharacterGenerator."""
        include_races = kwargs.get('include_races', True)  # Default to including races for fantasy
        return generate_fantasy_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage,
            include_races=include_races
        )
    
    def save_characters(self, characters, filename):
        """Save fantasy characters using the Fantasy save function."""
        save_fantasy_characters_to_file(characters, filename=filename)
    
    def get_genre_name(self):
        """Return the genre name."""
        return "Fantasy"
    
    def get_location_info_from_factions(self, factions):
        """Extract city location information from fantasy factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            regions = faction.get("regions", [])
            # Find the capital region and city
            capital_region = next((region for region in regions if region.get("is_capital_region", False)), None)
            if capital_region:
                capital_city = next((city for city in capital_region.get("cities", []) 
                                  if city.get("is_capital", False)), None)
                if capital_city:
                    locations.append({
                        'name': capital_city.get('name', 'Unknown City'),
                        'controlled_by': faction_name,
                        'type': 'City',
                        'region': capital_region.get('name', 'Unknown Region'),
                        'description': f"{capital_city.get('name', 'Unknown City')} in {capital_region.get('name', 'Unknown Region')}"
                    })
        return locations

    def get_location_type_name(self):
        """Return the location type name for fantasy."""
        return "Cities"
    
    def _get_world_type_for_subgenre(self, subgenre):
        """Helper method to get world type for a given subgenre."""
        mapping = self.get_world_type_mapping()
        return mapping.get(subgenre, "balanced")  # Default to balanced 