from .base_handler import BaseGenreHandler
from ..RomanceCharacterGenerator import generate_romance_main_characters, save_romance_characters_to_file
from ..RomanceGenerator import generate_romance_factions, save_romance_factions_to_file

class RomanceHandler(BaseGenreHandler):
    """Handler for Romance genre stories"""
    
    def get_genre_name(self):
        return "Romance"
    
    def get_description(self):
        return "Stories focused on love, relationships, and romantic connections between characters"
    
    def generate_factions(self, num_factions=3, **kwargs):
        """Generate factions for romance stories using the Romance generator"""
        return generate_romance_factions(num_factions=num_factions, **kwargs)
    
    def generate_locations(self, num_locations=5):
        """Generate locations for romance stories"""
        romance_locations = [
            {
                "name": "Charming Café",
                "type": "Restaurant",
                "description": "A cozy neighborhood café where people meet for coffee dates and intimate conversations",
                "atmosphere": "Warm, intimate, welcoming",
                "key_features": ["Comfortable seating", "Soft lighting", "Quiet corners", "Outdoor patio"],
                "romantic_potential": ["First dates", "Morning coffee meetings", "Proposal spots"]
            },
            {
                "name": "Botanical Garden",
                "type": "Public Garden",
                "description": "Beautiful gardens with winding paths, perfect for romantic walks and quiet moments",
                "atmosphere": "Peaceful, beautiful, natural",
                "key_features": ["Flower gardens", "Walking paths", "Secluded benches", "Fountain"],
                "romantic_potential": ["Romantic walks", "Marriage proposals", "Wedding photos"]
            },
            {
                "name": "Luxury Hotel",
                "type": "Accommodation",
                "description": "An elegant hotel with romantic suites and beautiful views of the city",
                "atmosphere": "Luxurious, romantic, sophisticated",
                "key_features": ["Romantic suites", "Rooftop restaurant", "Spa services", "City views"],
                "romantic_potential": ["Romantic getaways", "Anniversary celebrations", "Honeymoon suites"]
            },
            {
                "name": "Beach Resort",
                "type": "Vacation Destination",
                "description": "A tropical paradise perfect for romantic escapes and destination weddings",
                "atmosphere": "Relaxing, tropical, dreamy",
                "key_features": ["Private beaches", "Sunset views", "Couples' activities", "Wedding venues"],
                "romantic_potential": ["Romantic vacations", "Beach weddings", "Honeymoons"]
            },
            {
                "name": "Art Gallery",
                "type": "Cultural Venue",
                "description": "A sophisticated gallery space where art lovers meet and connections are made",
                "atmosphere": "Cultured, inspiring, elegant",
                "key_features": ["Art exhibitions", "Wine tastings", "Opening events", "Quiet galleries"],
                "romantic_potential": ["Cultural dates", "Artistic inspiration", "Sophisticated meetings"]
            },
            {
                "name": "Mountain Cabin",
                "type": "Retreat Location",
                "description": "A secluded cabin in the mountains, perfect for romantic getaways and intimate moments",
                "atmosphere": "Cozy, private, rustic",
                "key_features": ["Fireplace", "Mountain views", "Hot tub", "Hiking trails"],
                "romantic_potential": ["Weekend retreats", "Intimate conversations", "Proposal settings"]
            },
            {
                "name": "Wedding Venue",
                "type": "Event Space",
                "description": "An elegant venue where dreams come true and love stories reach their happy endings",
                "atmosphere": "Celebratory, elegant, joyful",
                "key_features": ["Beautiful architecture", "Garden settings", "Reception halls", "Bridal suites"],
                "romantic_potential": ["Wedding ceremonies", "Receptions", "Anniversary parties"]
            }
        ]
        
        return romance_locations[:num_locations]
    
    def generate_characters(self, num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
        """Generate characters for romance stories"""
        return generate_romance_main_characters(
            num_characters=num_characters,
            female_percentage=female_percentage,
            male_percentage=male_percentage
        )
    
    def save_characters(self, characters, filename="romance_characters.json"):
        """Save romance characters using the genre-specific save function"""
        return save_romance_characters_to_file(characters, filename)
    
    def save_factions(self, factions, filename):
        """Save romance factions using the Romance generator save function"""
        return save_romance_factions_to_file(factions, filename)
    
    def get_faction_capitals_info(self, factions):
        """Extract location information for romance factions"""
        faction_section = "\n## Faction Locations:\n"
        for faction in factions:
            faction_name = faction.get("name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            faction_section += f"- {faction_name}: {territory}\n"
            faction_section += f"  - Type: {faction.get('type', 'Unknown')}\n"
            faction_section += f"  - Description: {faction.get('description', 'No description')}\n"
        return faction_section
    
    def get_character_attributes(self):
        """Get character attributes relevant to romance settings"""
        return ['gender', 'age', 'role', 'profession', 'background', 'social_group', 'group_role', 
                'venue', 'group_type', 'goals', 'motivations', 'flaws', 'strengths', 'arc']
    
    def get_world_type_mapping(self):
        """Get subgenre to world type mapping for romance"""
        return {
            "Contemporary Romance": "modern",
            "Historical Romance": "historical",
            "Paranormal Romance": "supernatural",
            "Romantic Suspense": "thriller",
            "Small Town Romance": "rural",
        }
    
    def uses_factions(self):
        """Romance stories use social groups, families, and organizations."""
        return True
    
    def get_organization_type(self):
        """Romance stories organize around social circles and families."""
        return "social groups"

    def get_location_info_from_factions(self, factions):
        """Extract location information from romance factions."""
        locations = []
        for faction in factions:
            faction_name = faction.get("name", "Unknown Faction")
            territory = faction.get("territory", "Unknown Location")
            locations.append({
                'name': territory,
                'controlled_by': faction_name,
                'type': 'Location',
                'description': f"{territory} (associated with {faction_name})"
            })
        return locations

    def get_location_type_name(self):
        """Return the location type name for romance."""
        return "Locations" 