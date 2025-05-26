from .base_handler import BaseGenreHandler
from ..WesternCharacterGenerator import generate_western_main_characters, save_western_characters_to_file

class WesternHandler(BaseGenreHandler):
    """Handler for Western genre stories"""
    
    def get_genre_name(self):
        return "Western"
    
    def get_description(self):
        return "Stories set in the American frontier featuring cowboys, outlaws, and frontier justice"
    
    def generate_factions(self, num_factions=3, female_percentage=50, male_percentage=50, subgenre="", **kwargs):
        """Generate factions for western stories"""
        # Note: female_percentage, male_percentage, and subgenre are not used for western factions
        # as they are predefined organizations, but we accept them for interface compatibility
        western_factions = [
            {
                "faction_name": "The Law",
                "faction_type": "Law Enforcement",
                "description": "Sheriffs, marshals, and deputies working to bring order to the frontier",
                "goals": ["Maintain law and order", "Protect citizens", "Bring outlaws to justice"],
                "resources": ["Legal authority", "Weapons", "Jail facilities", "Federal backing"],
                "territory": "Towns and settlements",
                "allies": ["Honest citizens", "Federal marshals", "Military"],
                "enemies": ["Outlaw gangs", "Corrupt officials", "Vigilantes"]
            },
            {
                "faction_name": "The Outlaw Gang",
                "faction_type": "Criminal Organization",
                "description": "A notorious gang of bank robbers and cattle rustlers terrorizing the territory",
                "goals": ["Get rich quick", "Avoid capture", "Control territory"],
                "resources": ["Weapons", "Hideouts", "Stolen money", "Criminal contacts"],
                "territory": "Remote hideouts and badlands",
                "allies": ["Corrupt officials", "Sympathetic locals", "Other gangs"],
                "enemies": ["Law enforcement", "Bounty hunters", "Rival gangs"]
            },
            {
                "faction_name": "The Cattle Barons",
                "faction_type": "Business Empire",
                "description": "Wealthy ranchers who control vast territories and influence local politics",
                "goals": ["Expand territory", "Control water rights", "Eliminate competition"],
                "resources": ["Vast herds", "Land ownership", "Political influence", "Hired guns"],
                "territory": "Large ranches and grazing lands",
                "allies": ["Politicians", "Banks", "Railroad companies"],
                "enemies": ["Small ranchers", "Homesteaders", "Rustlers"]
            },
            {
                "faction_name": "The Railroad Company",
                "faction_type": "Corporate Interest",
                "description": "A powerful corporation building railways across the frontier",
                "goals": ["Complete railroad construction", "Acquire land rights", "Maximize profits"],
                "resources": ["Capital", "Political connections", "Security forces", "Technology"],
                "territory": "Railroad routes and stations",
                "allies": ["Government officials", "Investors", "Local businesses"],
                "enemies": ["Native tribes", "Land owners", "Competing railroads"]
            },
            {
                "faction_name": "The Native Tribe",
                "faction_type": "Indigenous Group",
                "description": "A proud tribe fighting to protect their ancestral lands from encroachment",
                "goals": ["Protect tribal lands", "Preserve way of life", "Defend against settlers"],
                "resources": ["Knowledge of land", "Warrior traditions", "Spiritual guidance"],
                "territory": "Ancestral tribal lands",
                "allies": ["Other tribes", "Sympathetic traders", "Some military officers"],
                "enemies": ["Settlers", "Military", "Land grabbers"]
            },
            {
                "faction_name": "The Vigilantes",
                "faction_type": "Citizen Militia",
                "description": "Citizens who take the law into their own hands when official law fails",
                "goals": ["Protect community", "Dispense frontier justice", "Fill law enforcement gaps"],
                "resources": ["Local support", "Weapons", "Knowledge of area"],
                "territory": "Local communities",
                "allies": ["Local citizens", "Business owners", "Frustrated lawmen"],
                "enemies": ["Outlaws", "Corrupt officials", "Federal authorities"]
            }
        ]
        
        return western_factions[:num_factions]
    
    def generate_locations(self, num_locations=5):
        """Generate locations for western stories"""
        western_locations = [
            {
                "name": "Frontier Town",
                "type": "Settlement",
                "description": "A dusty frontier town with a main street lined with saloons, shops, and the sheriff's office",
                "atmosphere": "Rough, lawless, bustling",
                "key_features": ["Main street", "Saloon", "Sheriff's office", "General store", "Bank"],
                "dangers": ["Gunfights", "Outlaws", "Corrupt officials", "Vigilante justice"]
            },
            {
                "name": "Cattle Ranch",
                "type": "Working Ranch",
                "description": "A sprawling ranch with vast grazing lands, cattle herds, and a fortified ranch house",
                "atmosphere": "Isolated, hardworking, territorial",
                "key_features": ["Ranch house", "Bunkhouse", "Corrals", "Grazing lands", "Water sources"],
                "dangers": ["Rustlers", "Range wars", "Natural disasters", "Hostile neighbors"]
            },
            {
                "name": "Outlaw Hideout",
                "type": "Criminal Base",
                "description": "A hidden canyon or cave system where outlaws plan their next heist and lay low",
                "atmosphere": "Secretive, dangerous, lawless",
                "key_features": ["Hidden entrances", "Natural defenses", "Weapon caches", "Escape routes"],
                "dangers": ["Rival gangs", "Law enforcement raids", "Internal conflicts", "Harsh conditions"]
            },
            {
                "name": "Mining Camp",
                "type": "Industrial Site",
                "description": "A rough mining settlement where prospectors seek their fortune in gold or silver",
                "atmosphere": "Chaotic, desperate, opportunistic",
                "key_features": ["Mine shafts", "Sluice boxes", "Tent city", "Company store", "Assay office"],
                "dangers": ["Cave-ins", "Claim jumpers", "Disease", "Violence over claims"]
            },
            {
                "name": "Railroad Station",
                "type": "Transportation Hub",
                "description": "A busy station where the railroad brings civilization and commerce to the frontier",
                "atmosphere": "Bustling, modern, transitional",
                "key_features": ["Train platform", "Depot building", "Telegraph office", "Freight yard"],
                "dangers": ["Train robberies", "Labor disputes", "Accidents", "Territorial conflicts"]
            },
            {
                "name": "Native American Village",
                "type": "Tribal Settlement",
                "description": "A traditional village where the tribe maintains their ancestral way of life",
                "atmosphere": "Spiritual, traditional, defensive",
                "key_features": ["Tribal dwellings", "Sacred sites", "Council areas", "Hunting grounds"],
                "dangers": ["Military raids", "Disease", "Encroachment", "Cultural conflicts"]
            },
            {
                "name": "Desert Badlands",
                "type": "Wilderness",
                "description": "Harsh, unforgiving terrain where only the toughest survive and outlaws hide",
                "atmosphere": "Desolate, dangerous, unforgiving",
                "key_features": ["Rock formations", "Hidden water sources", "Natural shelters", "Ancient ruins"],
                "dangers": ["Extreme weather", "Dangerous wildlife", "Getting lost", "Lack of water"]
            }
        ]
        
        return western_locations[:num_locations]
    
    def generate_characters(self, num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
        """Generate characters for western stories"""
        return generate_western_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_characters(self, characters, filename="western_characters.json"):
        """Save western characters using the genre-specific save function"""
        return save_western_characters_to_file(characters, filename)
    
    def save_factions(self, factions, filename):
        """Save western factions to a file"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(factions, f, indent=4, ensure_ascii=False)
    
    def get_faction_capitals_info(self, factions):
        """Extract territory information for western factions"""
        faction_section = "\n## Faction Territories:\n"
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            faction_section += f"- {faction_name}: {territory}\n"
            faction_section += f"  - Type: {faction.get('faction_type', 'Unknown')}\n"
            faction_section += f"  - Description: {faction.get('description', 'No description')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to western settings"""
        return ['gender', 'age', 'role', 'profession', 'background', 'faction', 'faction_role', 
                'territory', 'faction_type', 'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for western"""
        return {
            "Classic Western": "frontier",
            "Spaghetti Western": "lawless",
            "Weird Western": "supernatural",
            "Space Western": "sci_fi_frontier",
            "Modern Western": "contemporary_west",
        }
    
    def uses_factions(self):
        """Western stories use factions like law enforcement, outlaw gangs, and cattle barons."""
        return True
    
    def get_organization_type(self):
        """Western stories organize around traditional factions and groups."""
        return "factions"

    def get_location_info_from_factions(self, factions):
        """Extract territory information from western factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("faction_name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Territory")
            locations.append({
                'name': territory,
                'controlled_by': faction_name,
                'type': 'Territory',
                'description': f"{territory} (controlled by {faction_name})"
            })
        return locations

    def get_location_type_name(self):
        """Return the location type name for western."""
        return "Territories" 