from .base_handler import BaseGenreHandler
from ..MysteryCharacterGenerator import generate_mystery_main_characters, save_mystery_characters_to_file
from ..MysteryGenerator import generate_mystery_factions, save_mystery_factions_to_file

class MysteryHandler(BaseGenreHandler):
    """Handler for Mystery genre stories"""
    
    def get_genre_name(self):
        return "Mystery"
    
    def get_description(self):
        return "Stories featuring detectives, crimes, puzzles, and the pursuit of truth"
    
    def generate_factions(self, num_factions=3, **kwargs):
        """Generate factions for mystery stories using the Mystery generator"""
        return generate_mystery_factions(num_factions=num_factions, **kwargs)
    
    def generate_locations(self, num_locations=5):
        """Generate locations for mystery stories"""
        mystery_locations = [
            {
                "name": "Police Headquarters",
                "type": "Government Building",
                "description": "The main police station with detective units, forensic labs, and holding cells",
                "atmosphere": "Busy, professional, tense",
                "key_features": ["Detective bullpen", "Interrogation rooms", "Evidence locker", "Crime lab"],
                "dangers": ["Corrupt officers", "Information leaks", "Political pressure"]
            },
            {
                "name": "The Crime Scene",
                "type": "Investigation Site",
                "description": "The location where the crime occurred, now sealed off for investigation",
                "atmosphere": "Eerie, methodical, revealing",
                "key_features": ["Evidence markers", "Forensic equipment", "Witness statements"],
                "dangers": ["Contaminated evidence", "Missing clues", "Returning criminals"]
            },
            {
                "name": "Downtown Courthouse",
                "type": "Legal Building",
                "description": "Where justice is served and legal battles are fought",
                "atmosphere": "Formal, tense, decisive",
                "key_features": ["Courtrooms", "Judge's chambers", "Jury rooms", "Legal archives"],
                "dangers": ["Corrupt judges", "Intimidated witnesses", "Legal loopholes"]
            },
            {
                "name": "The Morgue",
                "type": "Medical Facility",
                "description": "Where autopsies are performed and the dead tell their stories",
                "atmosphere": "Cold, clinical, revealing",
                "key_features": ["Autopsy tables", "Medical equipment", "Body storage", "Forensic lab"],
                "dangers": ["Misidentified bodies", "Tampered evidence", "Health hazards"]
            },
            {
                "name": "Abandoned Warehouse District",
                "type": "Industrial Area",
                "description": "A maze of empty buildings perfect for hiding secrets and conducting illegal business",
                "atmosphere": "Dark, dangerous, secretive",
                "key_features": ["Empty warehouses", "Loading docks", "Hidden passages", "Surveillance blind spots"],
                "dangers": ["Criminal hideouts", "Ambush points", "Structural hazards"]
            },
            {
                "name": "Upscale Hotel",
                "type": "Commercial Building",
                "description": "A luxury hotel where the wealthy and powerful conduct their business",
                "atmosphere": "Elegant, discreet, suspicious",
                "key_features": ["Luxury suites", "Private dining", "Security cameras", "VIP areas"],
                "dangers": ["Hidden agendas", "Surveillance", "Powerful enemies"]
            },
            {
                "name": "Underground Parking Garage",
                "type": "Urban Infrastructure",
                "description": "A dimly lit space perfect for secret meetings and dangerous encounters",
                "atmosphere": "Dark, echoing, threatening",
                "key_features": ["Multiple levels", "Security cameras", "Emergency exits", "Hidden corners"],
                "dangers": ["Ambushes", "Poor visibility", "Limited escape routes"]
            }
        ]
        
        return mystery_locations[:num_locations]
    
    def generate_characters(self, num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
        """Generate characters for mystery stories"""
        return generate_mystery_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_characters(self, characters, filename="mystery_characters.json"):
        """Save mystery characters using the genre-specific save function"""
        return save_mystery_characters_to_file(characters, filename)
    
    def save_factions(self, factions, filename):
        """Save mystery factions using the Mystery generator save function"""
        return save_mystery_factions_to_file(factions, filename)
    
    def get_faction_capitals_info(self, factions):
        """Extract headquarters information for mystery factions"""
        faction_section = "\n## Faction Headquarters:\n"
        for faction in factions:
            faction_name = faction.get("name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            faction_section += f"- {faction_name}: {territory}\n"
            faction_section += f"  - Type: {faction.get('type', 'Unknown')}\n"
            faction_section += f"  - Description: {faction.get('description', 'No description')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to mystery settings"""
        return ['gender', 'age', 'role', 'profession', 'background', 'specialty', 'agency', 'agency_role', 
                'headquarters', 'agency_type', 'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for mystery"""
        return {
            "Cozy Mystery": "small_town",
            "Police Procedural": "urban",
            "Hard-boiled": "noir",
            "Amateur Detective": "contemporary",
            "Historical Mystery": "historical",
        }
    
    def uses_factions(self):
        """Mystery stories use organizations like police departments and agencies."""
        return True
    
    def get_organization_type(self):
        """Mystery stories organize around agencies and departments."""
        return "agencies"

    def get_location_info_from_factions(self, factions):
        """Extract headquarters information from mystery factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            locations.append({
                'name': territory,
                'controlled_by': faction_name,
                'type': 'Headquarters',
                'description': f"{territory} (headquarters of {faction_name})"
            })
        return locations

    def get_location_type_name(self):
        """Return the location type name for mystery."""
        return "Headquarters" 