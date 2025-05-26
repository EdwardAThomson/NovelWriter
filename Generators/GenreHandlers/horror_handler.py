"""
Horror Genre Handler

Handles faction generation, lore processing, and character attributes for Horror.
"""

from .base_handler import BaseGenreHandler
from ..HorrorGenerator import generate_horror_factions, save_horror_factions_to_file
from ..HorrorCharacterGenerator import generate_horror_main_characters, save_horror_characters_to_file

class HorrorHandler(BaseGenreHandler):
    """Handler for Horror genre."""
    
    def generate_factions(self, num_factions, female_percentage=50, male_percentage=50, subgenre="", **kwargs):
        """Generate horror factions using the HorrorGenerator."""
        return generate_horror_factions(
            num_factions=num_factions,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_factions(self, factions, filename):
        """Save horror factions using the Horror save function."""
        save_horror_factions_to_file(factions=factions, filename=filename)
    
    def get_faction_capitals_info(self, factions):
        """Extract stronghold information for horror factions."""
        faction_section = "\n## Horror Faction Strongholds:\n"
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            faction_type = faction.get("faction_type", "Unknown Type")
            # Horror factions don't have traditional capitals, but strongholds/territories
            territories = faction.get("territories", [])
            if territories:
                primary_territory = territories[0]  # Use first territory as primary stronghold
                faction_section += f"- {faction_name}: {primary_territory}\n"
                faction_section += f"  - Type: {faction_type}\n"
                faction_section += f"  - Threat Level: {faction.get('threat_level', 'Unknown')}\n"
                faction_section += f"  - Secrecy Level: {faction.get('secrecy_level', 'Unknown')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to horror settings."""
        return ['gender', 'age', 'title', 'occupation', 'faction', 'faction_role', 
                'stronghold', 'faction_type', 'sanity', 'fears', 'supernatural_encounters', 
                'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for horror."""
        return {
            "Gothic Horror": "isolated",
            "Cosmic Horror": "unknowable",
            "Psychological Horror": "urban",
            "Body Horror": "medical",
            "Slasher Horror": "suburban",
            "Supernatural Horror": "haunted",
        }
    
    def generate_characters(self, num_characters, female_percentage=50, male_percentage=50, **kwargs):
        """Generate horror characters using the HorrorCharacterGenerator."""
        return generate_horror_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_characters(self, characters, filename):
        """Save horror characters using the Horror save function."""
        save_horror_characters_to_file(characters, filename)
    
    def get_genre_name(self):
        """Return the genre name."""
        return "Horror"
    
    def uses_factions(self):
        """Horror stories may use cults, organizations, or groups."""
        return True
    
    def get_organization_type(self):
        """Horror stories organize around cults and groups."""
        return "cults"

    def get_location_info_from_factions(self, factions):
        """Extract stronghold information from horror factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Cult")
            territories = faction.get("territories", [])
            if territories:
                # Use the first territory as the primary stronghold
                primary_territory = territories[0]
                locations.append({
                    'name': primary_territory,
                    'controlled_by': faction_name,
                    'type': 'Stronghold',
                    'description': f"{primary_territory} (stronghold of {faction_name})"
                })
        return locations

    def get_location_type_name(self):
        """Return the location type name for horror."""
        return "Strongholds" 