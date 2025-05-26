"""
Sci-Fi Genre Handler

Handles faction generation, lore processing, and character attributes for Science Fiction.
"""

from .base_handler import BaseGenreHandler
from ..SciFiGenerator import generate_universe, save_factions_to_file
from ..SciFiCharacterGenerator import generate_main_characters, save_characters_to_file

class SciFiHandler(BaseGenreHandler):
    """Handler for Science Fiction genre."""
    
    def generate_factions(self, num_factions, female_percentage=50, male_percentage=50, subgenre="", **kwargs):
        """Generate sci-fi factions using the SciFiGenerator."""
        return generate_universe(
            num_factions=num_factions, 
            female_percentage=female_percentage, 
            male_percentage=male_percentage
        )
    
    def save_factions(self, factions, filename):
        """Save sci-fi factions using the SciFi save function."""
        save_factions_to_file(factions=factions, filename=filename)
    
    def get_faction_capitals_info(self, factions):
        """Extract capital system and planet information for sci-fi factions."""
        faction_section = "\n## Faction Capitals:\n"
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            # Find the capital system and planet
            capital_system = next((sys for sys in faction.get("systems", []) if sys.get("is_capital_system", False)), None)
            if capital_system:
                capital_planet = next((planet for planet in capital_system.get("habitable_planets", []) 
                                    if planet.get("is_capital", False)), None)
                if capital_planet:
                    faction_section += f"- {faction_name}: {capital_planet.get('name', 'N/A')} in {capital_system.get('name', 'N/A')}\n"
                    stats = capital_planet.get("stats", {})
                    faction_section += f"  - Population: {stats.get('population', 'Unknown')}\n"
                    faction_section += f"  - Climate: {stats.get('climate', 'Unknown')}\n"
                    faction_section += f"  - Infrastructure: {stats.get('infrastructure', {}).get('description', 'Unknown')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to sci-fi settings."""
        return ['gender', 'age', 'title', 'occupation', 'faction', 'faction_role', 
                'homeworld', 'home_system', 'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for sci-fi."""
        # Sci-fi doesn't currently use world types, but we can add them later
        return {
            "Space Opera": "galactic",
            "Cyberpunk": "urban",
            "Military Sci-Fi": "conflict",
            "Hard Science Fiction": "scientific",
            # Add more mappings as needed
        }
    
    def generate_characters(self, num_characters, female_percentage=50, male_percentage=50, **kwargs):
        """Generate sci-fi characters using the SciFiCharacterGenerator."""
        return generate_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_characters(self, characters, filename):
        """Save sci-fi characters using the SciFi save function."""
        save_characters_to_file(characters, filename=filename)
    
    def get_genre_name(self):
        """Return the genre name."""
        return "Sci-Fi"

    def get_location_info_from_factions(self, factions):
        """Extract planet location information from sci-fi factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            systems = faction.get("systems", [])
            for system in systems:
                habitable_planets = system.get("habitable_planets", [])
                if habitable_planets:
                    # Take the first habitable planet as the key location for this faction
                    key_planet = habitable_planets[0]
                    locations.append({
                        'name': key_planet.get("name", "Unknown Planet"),
                        'controlled_by': faction_name,
                        'type': 'Planet',
                        'system': system.get("name", "Unknown System"),
                        'description': f"{key_planet.get('name', 'Unknown Planet')} in {system.get('name', 'Unknown System')}"
                    })
                    break  # Only take one key planet per faction
        return locations

    def get_location_type_name(self):
        """Return the location type name for sci-fi."""
        return "Planets" 