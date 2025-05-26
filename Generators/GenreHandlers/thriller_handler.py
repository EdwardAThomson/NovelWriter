from .base_handler import BaseGenreHandler
from ..ThrillerCharacterGenerator import generate_thriller_main_characters, save_thriller_characters_to_file

class ThrillerHandler(BaseGenreHandler):
    """Handler for Thriller genre stories"""
    
    def get_genre_name(self):
        return "Thriller"
    
    def get_description(self):
        return "High-stakes stories filled with suspense, danger, and intense action"
    
    def generate_factions(self, num_factions=3, female_percentage=50, male_percentage=50, subgenre="", **kwargs):
        """Generate factions for thriller stories"""
        # Note: female_percentage, male_percentage, and subgenre are not used for thriller factions
        # as they are predefined organizations, but we accept them for interface compatibility
        thriller_factions = [
            {
                "faction_name": "The Agency",
                "faction_type": "Intelligence Organization",
                "description": "A secretive government intelligence agency with global reach and unlimited resources",
                "goals": ["Protect national security", "Gather intelligence", "Eliminate threats"],
                "resources": ["Advanced technology", "Global network", "Unlimited funding", "Elite operatives"],
                "territory": "Global operations",
                "allies": ["Government officials", "Military", "Allied intelligence services"],
                "enemies": ["Terrorist organizations", "Foreign spies", "Rogue agents"]
            },
            {
                "faction_name": "Shadow Syndicate",
                "faction_type": "Criminal Organization",
                "description": "A powerful international criminal network involved in arms dealing, terrorism, and espionage",
                "goals": ["Expand criminal empire", "Eliminate rivals", "Corrupt governments"],
                "resources": ["Weapons", "Money", "Criminal contacts", "Safe houses"],
                "territory": "International criminal underworld",
                "allies": ["Corrupt officials", "Mercenaries", "Other criminal groups"],
                "enemies": ["Law enforcement", "Intelligence agencies", "Rival syndicates"]
            },
            {
                "faction_name": "Corporate Security Division",
                "faction_type": "Private Military",
                "description": "Elite private security force protecting corporate interests and conducting covert operations",
                "goals": ["Protect corporate assets", "Eliminate competition", "Maintain secrecy"],
                "resources": ["Military equipment", "Corporate funding", "Private facilities"],
                "territory": "Corporate facilities worldwide",
                "allies": ["Corporate executives", "Government contractors"],
                "enemies": ["Whistleblowers", "Competitors", "Investigative journalists"]
            },
            {
                "faction_name": "Terrorist Cell",
                "faction_type": "Extremist Group",
                "description": "A radical organization planning devastating attacks to further their ideological agenda",
                "goals": ["Spread terror", "Overthrow governments", "Advance ideology"],
                "resources": ["Explosives", "Weapons", "Fanatical followers", "Hidden bases"],
                "territory": "Underground networks",
                "allies": ["Sympathizers", "Other extremist groups"],
                "enemies": ["Government forces", "Intelligence agencies", "Civilians"]
            },
            {
                "faction_name": "Special Forces Unit",
                "faction_type": "Military Elite",
                "description": "Highly trained military operatives specializing in counter-terrorism and special operations",
                "goals": ["Complete missions", "Protect civilians", "Eliminate threats"],
                "resources": ["Advanced weapons", "Military support", "Specialized training"],
                "territory": "Military bases and operations",
                "allies": ["Military command", "Intelligence agencies", "Allied forces"],
                "enemies": ["Terrorists", "Enemy combatants", "Rogue operatives"]
            },
            {
                "faction_name": "Underground Resistance",
                "faction_type": "Rebel Organization",
                "description": "A covert group fighting against oppressive regimes and corrupt organizations",
                "goals": ["Overthrow corruption", "Expose truth", "Protect innocents"],
                "resources": ["Hidden networks", "Loyal supporters", "Stolen intelligence"],
                "territory": "Underground hideouts",
                "allies": ["Sympathetic civilians", "Whistleblowers", "Reform movements"],
                "enemies": ["Corrupt governments", "Corporate interests", "Security forces"]
            }
        ]
        
        return thriller_factions[:num_factions]
    
    def generate_locations(self, num_locations=5):
        """Generate locations for thriller stories"""
        thriller_locations = [
            {
                "name": "Secret Government Facility",
                "type": "Military Installation",
                "description": "A heavily fortified underground complex housing classified operations and dangerous secrets",
                "atmosphere": "Sterile, secure, ominous",
                "key_features": ["Security checkpoints", "Underground levels", "High-tech equipment", "Restricted areas"],
                "dangers": ["Armed guards", "Security systems", "Classified experiments", "Lockdown protocols"]
            },
            {
                "name": "Abandoned Warehouse",
                "type": "Industrial Building",
                "description": "A derelict building perfect for clandestine meetings and dangerous confrontations",
                "atmosphere": "Dark, isolated, threatening",
                "key_features": ["Multiple entrances", "Hidden rooms", "Industrial equipment", "Poor lighting"],
                "dangers": ["Ambush points", "Structural hazards", "Criminal activity", "No witnesses"]
            },
            {
                "name": "High-Rise Office Building",
                "type": "Corporate Headquarters",
                "description": "A gleaming skyscraper that houses corporate secrets and serves as a fortress for the powerful",
                "atmosphere": "Modern, imposing, deceptive",
                "key_features": ["Executive floors", "Security systems", "Conference rooms", "Rooftop access"],
                "dangers": ["Corporate security", "Surveillance", "Long falls", "Powerful enemies"]
            },
            {
                "name": "International Airport",
                "type": "Transportation Hub",
                "description": "A busy terminal where identities can be changed and escapes can be made or prevented",
                "atmosphere": "Crowded, chaotic, urgent",
                "key_features": ["Multiple terminals", "Security checkpoints", "Private jets", "Cargo areas"],
                "dangers": ["Airport security", "Surveillance cameras", "Crowds", "International complications"]
            },
            {
                "name": "Remote Mountain Compound",
                "type": "Isolated Facility",
                "description": "A fortified compound in the mountains, perfect for training operatives or hiding secrets",
                "atmosphere": "Isolated, militaristic, harsh",
                "key_features": ["Training facilities", "Defensive positions", "Communication arrays", "Helicopter pads"],
                "dangers": ["Armed personnel", "Harsh terrain", "Limited escape routes", "Extreme weather"]
            },
            {
                "name": "Luxury Hotel",
                "type": "Hospitality Venue",
                "description": "An upscale hotel that serves as neutral ground for dangerous negotiations and secret meetings",
                "atmosphere": "Elegant, discreet, deceptive",
                "key_features": ["Private suites", "Conference rooms", "Multiple exits", "VIP areas"],
                "dangers": ["Hidden enemies", "Surveillance", "Assassins", "Diplomatic immunity"]
            },
            {
                "name": "Nuclear Power Plant",
                "type": "Critical Infrastructure",
                "description": "A heavily secured facility that could become a devastating weapon in the wrong hands",
                "atmosphere": "Industrial, dangerous, high-stakes",
                "key_features": ["Reactor core", "Control rooms", "Security systems", "Emergency protocols"],
                "dangers": ["Radiation", "Meltdown risk", "Terrorist targets", "Catastrophic consequences"]
            }
        ]
        
        return thriller_locations[:num_locations]
    
    def generate_characters(self, num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
        """Generate characters for thriller stories"""
        return generate_thriller_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_characters(self, characters, filename="thriller_characters.json"):
        """Save thriller characters using the genre-specific save function"""
        return save_thriller_characters_to_file(characters, filename)
    
    def save_factions(self, factions, filename):
        """Save thriller factions to a file"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(factions, f, indent=4, ensure_ascii=False)
    
    def get_faction_capitals_info(self, factions):
        """Extract headquarters information for thriller factions"""
        faction_section = "\n## Faction Headquarters:\n"
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            faction_section += f"- {faction_name}: {territory}\n"
            faction_section += f"  - Type: {faction.get('faction_type', 'Unknown')}\n"
            faction_section += f"  - Description: {faction.get('description', 'No description')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to thriller settings"""
        return ['gender', 'age', 'role', 'background', 'specialty', 'agency', 'agency_role', 
                'headquarters', 'agency_type', 'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for thriller"""
        return {
            "Espionage Thriller": "international",
            "Techno-Thriller": "high_tech",
            "Political Thriller": "political",
            "Action Thriller": "action",
            "Psychological Thriller": "psychological",
        }
    
    def uses_factions(self):
        """Thriller stories use factions like intelligence agencies and criminal organizations."""
        return True
    
    def get_organization_type(self):
        """Thriller stories organize around agencies and organizations."""
        return "agencies"

    def get_location_info_from_factions(self, factions):
        """Extract headquarters information from thriller factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            locations.append({
                'name': territory,
                'controlled_by': faction_name,
                'type': 'Headquarters',
                'description': f"{territory} (headquarters of {faction_name})"
            })
        return locations

    def get_location_type_name(self):
        """Return the location type name for thriller."""
        return "Headquarters" 