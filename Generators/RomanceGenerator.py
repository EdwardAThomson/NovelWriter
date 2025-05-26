import json
import random
import os
from datetime import datetime

# --- Romance Name Generation System ---

# Family names - elegant and diverse
FAMILY_SURNAMES = [
    "Ashworth", "Blackwood", "Carrington", "Delacroix", "Fairfax", "Grayson", "Hamilton", 
    "Kensington", "Lancaster", "Montgomery", "Pemberton", "Ravencroft", "Sinclair", "Thornfield",
    "Vanderbilt", "Wellington", "Beaumont", "Chandler", "Devereaux", "Fitzgerald", "Harrington",
    "Livingston", "Northcott", "Prescott", "Whitmore", "Aldridge", "Bancroft",
    "Covington", "Donovan", "Ellsworth", "Forrester", "Huntington", "Jameson"
]

# Business/Organization names
BUSINESS_PREFIXES = [
    "Elite", "Premier", "Luxury", "Exclusive", "Prestige", "Royal", "Golden", "Diamond",
    "Platinum", "Sterling", "Crystal", "Emerald", "Sapphire", "Pearl", "Ivory", "Silk",
    "Velvet", "Enchanted", "Romantic", "Dreamy", "Blissful", "Heavenly", "Divine", "Perfect"
]

BUSINESS_TYPES = [
    "Wedding Planning", "Event Design", "Matchmaking", "Dating Service", "Bridal Boutique",
    "Floral Design", "Photography Studio", "Catering Company", "Venue Management", "Travel Agency",
    "Jewelry Design", "Fashion House", "Beauty Salon", "Spa & Wellness", "Dance Studio",
    "Music Academy", "Art Gallery", "Publishing House", "Restaurant Group", "Hotel Chain"
]

# Location names for social settings
LOCATION_ADJECTIVES = [
    "Charming", "Elegant", "Romantic", "Cozy", "Intimate", "Sophisticated", "Enchanting",
    "Dreamy", "Serene", "Peaceful", "Vibrant", "Lively", "Exclusive", "Hidden", "Secret",
    "Magical", "Whimsical", "Vintage", "Modern", "Classic", "Timeless", "Boutique", "Grand"
]

LOCATION_TYPES = [
    "Café", "Bistro", "Restaurant", "Bar", "Lounge", "Garden", "Park", "Gallery", "Studio",
    "Library", "Bookstore", "Theater", "Club", "Resort", "Hotel", "Spa", "Beach", "Vineyard",
    "Manor", "Estate", "Cottage", "Cabin", "Penthouse", "Rooftop", "Terrace", "Conservatory"
]

# Romance-specific faction types and their characteristics
ROMANCE_FACTION_TYPES = {
    "Wealthy Family": {
        "description_templates": [
            "An influential family with old money and social connections",
            "A prestigious family dynasty with business empire spanning generations",
            "An aristocratic family with deep roots in high society",
            "A powerful family known for their philanthropy and social influence"
        ],
        "goals": [
            "Maintain family honor and reputation",
            "Arrange advantageous marriages",
            "Expand business empire",
            "Preserve family traditions",
            "Protect family interests",
            "Secure the next generation's future"
        ],
        "resources": [
            "Vast wealth and investments",
            "Social connections and influence",
            "Family estates and properties",
            "Business networks",
            "Political connections",
            "Cultural patronage"
        ],
        "territories": [
            "High society circles",
            "Exclusive neighborhoods",
            "Private clubs and venues",
            "Family estates",
            "Business districts",
            "Cultural institutions"
        ]
    },
    "Corporate Empire": {
        "description_templates": [
            "A successful corporation where office romances and professional relationships flourish",
            "A competitive business environment that brings ambitious people together",
            "A modern company culture that values both success and personal connections",
            "An innovative corporation where collaboration leads to unexpected romance"
        ],
        "goals": [
            "Achieve market dominance",
            "Foster innovation and growth",
            "Build strong corporate culture",
            "Attract top talent",
            "Maintain work-life balance",
            "Create networking opportunities"
        ],
        "resources": [
            "Financial capital and investments",
            "Professional networks",
            "Modern office facilities",
            "Technology and innovation",
            "Training and development programs",
            "Corporate events and retreats"
        ],
        "territories": [
            "Business districts",
            "Corporate headquarters",
            "Conference centers",
            "Professional networks",
            "Industry events",
            "Executive clubs"
        ]
    },
    "Arts Community": {
        "description_templates": [
            "A vibrant creative community where artists find inspiration and love",
            "An artistic collective that celebrates creativity and passionate connections",
            "A bohemian community where art and romance intertwine naturally",
            "A supportive arts scene that nurtures both talent and relationships"
        ],
        "goals": [
            "Support artistic expression",
            "Foster creative collaboration",
            "Build community connections",
            "Promote cultural events",
            "Preserve artistic traditions",
            "Encourage emerging talent"
        ],
        "resources": [
            "Studios and creative spaces",
            "Art galleries and venues",
            "Cultural networks",
            "Patron support",
            "Educational programs",
            "Exhibition opportunities"
        ],
        "territories": [
            "Arts districts",
            "Gallery quarters",
            "Creative studios",
            "Cultural venues",
            "Bohemian neighborhoods",
            "Artist communities"
        ]
    },
    "Social Circle": {
        "description_templates": [
            "An exclusive social group that organizes elegant events and gatherings",
            "A close-knit community where friendships bloom into romance",
            "A sophisticated social network that brings like-minded people together",
            "An influential social circle that shapes trends and relationships"
        ],
        "goals": [
            "Organize memorable social events",
            "Maintain exclusive membership",
            "Foster meaningful connections",
            "Set social trends",
            "Support charitable causes",
            "Create networking opportunities"
        ],
        "resources": [
            "Social connections and influence",
            "Event planning expertise",
            "Exclusive venues and locations",
            "Cultural knowledge",
            "Fashion and style influence",
            "Charitable networks"
        ],
        "territories": [
            "Exclusive venues",
            "Private clubs",
            "Social events",
            "Cultural gatherings",
            "Charity functions",
            "Fashion scenes"
        ]
    },
    "Small Town Community": {
        "description_templates": [
            "A tight-knit small town where everyone knows everyone and love stories unfold publicly",
            "A charming community where traditional values and modern romance coexist",
            "A close community where family connections and local traditions matter",
            "A welcoming town where newcomers quickly become part of the extended family"
        ],
        "goals": [
            "Preserve community traditions",
            "Support local businesses",
            "Maintain close relationships",
            "Welcome newcomers",
            "Organize community events",
            "Protect local interests"
        ],
        "resources": [
            "Strong community bonds",
            "Local business networks",
            "Shared history and traditions",
            "Community facilities",
            "Local knowledge",
            "Volunteer networks"
        ],
        "territories": [
            "Town center",
            "Local businesses",
            "Community centers",
            "Churches and schools",
            "Parks and recreation areas",
            "Residential neighborhoods"
        ]
    },
    "Service Organization": {
        "description_templates": [
            "A professional service that specializes in bringing people together",
            "An organization dedicated to creating perfect romantic experiences",
            "A service company that understands the business of love and relationships",
            "A professional group that makes dreams come true through expert planning"
        ],
        "goals": [
            "Create perfect romantic experiences",
            "Build lasting client relationships",
            "Maintain professional excellence",
            "Expand service offerings",
            "Develop industry expertise",
            "Foster successful matches"
        ],
        "resources": [
            "Professional expertise",
            "Vendor networks",
            "Client databases",
            "Event planning capabilities",
            "Industry connections",
            "Specialized knowledge"
        ],
        "territories": [
            "Professional service areas",
            "Client networks",
            "Vendor partnerships",
            "Event venues",
            "Industry associations",
            "Service territories"
        ]
    }
}

def generate_family_name():
    """Generate a family surname."""
    return random.choice(FAMILY_SURNAMES)

def generate_business_name():
    """Generate a business or organization name."""
    prefix = random.choice(BUSINESS_PREFIXES)
    business_type = random.choice(BUSINESS_TYPES)
    
    # Sometimes add "& Associates", "Group", "Company", etc.
    suffixes = ["", " & Associates", " Group", " Company", " Services", " Enterprises", " International"]
    suffix = random.choice(suffixes)
    
    return f"{prefix} {business_type}{suffix}"

def generate_location_name():
    """Generate a romantic location name."""
    adjective = random.choice(LOCATION_ADJECTIVES)
    location_type = random.choice(LOCATION_TYPES)
    
    # Sometimes add "The" at the beginning
    if random.random() < 0.6:
        return f"The {adjective} {location_type}"
    else:
        return f"{adjective} {location_type}"

def create_romance_faction(faction_type=None):
    """
    Create a single romance faction/social group.
    
    Args:
        faction_type: Specific type of faction to create, or None for random
    
    Returns:
        dict: Faction data structure
    """
    if faction_type is None:
        faction_type = random.choice(list(ROMANCE_FACTION_TYPES.keys()))
    
    faction_data = ROMANCE_FACTION_TYPES[faction_type]
    
    # Generate name based on faction type
    if faction_type == "Wealthy Family":
        name = f"The {generate_family_name()} Family"
    elif faction_type == "Corporate Empire":
        name = generate_business_name()
    elif faction_type == "Service Organization":
        name = generate_business_name()
    elif faction_type == "Arts Community":
        location = random.choice(["District", "Quarter", "Community", "Collective", "Circle"])
        adjective = random.choice(["Creative", "Artistic", "Bohemian", "Cultural", "Avant-garde"])
        name = f"The {adjective} {location}"
    elif faction_type == "Social Circle":
        adjective = random.choice(["Elite", "Exclusive", "Sophisticated", "Distinguished", "Prestigious"])
        group_type = random.choice(["Society", "Circle", "Club", "Group", "Network"])
        name = f"The {adjective} {group_type}"
    else:  # Small Town Community
        town_names = ["Willowbrook", "Rosewood", "Maplewood", "Oakville", "Riverside", "Hillcrest", 
                     "Fairview", "Greenfield", "Sunset Valley", "Cedar Falls", "Pine Ridge", "Harmony"]
        name = f"{random.choice(town_names)} Community"
    
    # Select random elements from the faction type data
    description = random.choice(faction_data["description_templates"])
    goals = random.sample(faction_data["goals"], min(3, len(faction_data["goals"])))
    resources = random.sample(faction_data["resources"], min(4, len(faction_data["resources"])))
    territory = random.choice(faction_data["territories"])
    
    # Generate allies and enemies based on faction type
    allies, enemies = generate_faction_relationships(faction_type)
    
    return {
        "name": name,
        "type": faction_type,
        "description": description,
        "goals": goals,
        "resources": resources,
        "territory": territory,
        "allies": allies,
        "enemies": enemies,
        "influence_level": random.choice(["Local", "Regional", "National", "International"]),
        "wealth_level": random.choice(["Modest", "Comfortable", "Wealthy", "Very Wealthy", "Extremely Wealthy"]),
        "social_standing": random.choice(["Emerging", "Established", "Prestigious", "Elite", "Legendary"])
    }

def generate_faction_relationships(faction_type):
    """Generate allies and enemies for a faction based on its type."""
    
    relationship_map = {
        "Wealthy Family": {
            "allies": ["Other wealthy families", "Business partners", "Political connections", 
                      "Cultural institutions", "Charitable organizations", "Exclusive clubs"],
            "enemies": ["Social climbers", "Scandal-seeking media", "Business rivals", 
                       "Unsuitable suitors", "Family black sheep", "Competing families"]
        },
        "Corporate Empire": {
            "allies": ["Business partners", "Industry leaders", "Professional networks", 
                      "Successful executives", "Innovation hubs", "Trade associations"],
            "enemies": ["Competitors", "Hostile takeover attempts", "Regulatory bodies", 
                       "Disruptive startups", "Labor disputes", "Corporate scandals"]
        },
        "Arts Community": {
            "allies": ["Art patrons", "Cultural institutions", "Creative professionals", 
                      "Art lovers", "Educational institutions", "Media supporters"],
            "enemies": ["Commercial developers", "Art critics", "Funding cuts", 
                       "Gentrification", "Censorship advocates", "Philistines"]
        },
        "Social Circle": {
            "allies": ["Cultural institutions", "Charity organizations", "Fashion industry", 
                      "Event planners", "Influential families", "Media personalities"],
            "enemies": ["Social outsiders", "Scandal creators", "Competing circles", 
                       "Paparazzi", "Social media trolls", "Inappropriate behavior"]
        },
        "Small Town Community": {
            "allies": ["Local families", "Community leaders", "Local businesses", 
                      "Church groups", "School systems", "Volunteer organizations"],
            "enemies": ["Big city developers", "Chain stores", "Outside influences", 
                       "Urban sprawl", "Corporate takeovers", "Cultural changes"]
        },
        "Service Organization": {
            "allies": ["Vendor networks", "Happy clients", "Industry partners", 
                      "Professional associations", "Referral sources", "Success stories"],
            "enemies": ["Competing services", "Difficult clients", "Bad reviews", 
                       "Economic downturns", "Changing trends", "Service failures"]
        }
    }
    
    faction_relationships = relationship_map.get(faction_type, {
        "allies": ["Supportive community", "Like-minded individuals", "Professional networks"],
        "enemies": ["Opposition forces", "Competing interests", "Negative influences"]
    })
    
    # Select 2-4 allies and 2-3 enemies
    allies = random.sample(faction_relationships["allies"], 
                          min(random.randint(2, 4), len(faction_relationships["allies"])))
    enemies = random.sample(faction_relationships["enemies"], 
                           min(random.randint(2, 3), len(faction_relationships["enemies"])))
    
    return allies, enemies

def generate_romance_world(num_factions=5, **kwargs):
    """
    Generate a complete romance world with social groups and organizations.
    
    Args:
        num_factions: Number of factions/groups to generate
        **kwargs: Additional parameters (for compatibility)
    
    Returns:
        list: List of faction dictionaries
    """
    factions = []
    
    # Ensure we have a good mix of faction types
    faction_types = list(ROMANCE_FACTION_TYPES.keys())
    
    for i in range(num_factions):
        # For the first few factions, ensure variety
        if i < len(faction_types):
            faction_type = faction_types[i]
        else:
            # For additional factions, choose randomly
            faction_type = random.choice(faction_types)
        
        faction = create_romance_faction(faction_type)
        factions.append(faction)
    
    return factions

def save_romance_factions_to_file(factions, filename=None, timestamp=False):
    """
    Save romance factions to a JSON file.
    
    Args:
        factions: List of faction dictionaries
        filename: Output filename (optional)
        timestamp: Whether to add timestamp to filename
    
    Returns:
        str: Path to saved file
    """
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"romance_factions_{timestamp_str}.json"
        else:
            filename = "romance_factions.json"
    
    # Ensure the filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(factions, f, indent=4, ensure_ascii=False)
        print(f"Romance factions saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving romance factions: {e}")
        return None

def print_romance_factions(factions):
    """Print romance factions in a readable format."""
    print("\n" + "="*60)
    print("ROMANCE WORLD - SOCIAL GROUPS & ORGANIZATIONS")
    print("="*60)
    
    for i, faction in enumerate(factions, 1):
        print(f"\n{i}. {faction['name']} ({faction['type']})")
        print("-" * 50)
        print(f"Description: {faction['description']}")
        print(f"Territory: {faction['territory']}")
        print(f"Influence: {faction['influence_level']} | Wealth: {faction['wealth_level']} | Standing: {faction['social_standing']}")
        
        print(f"\nGoals:")
        for goal in faction['goals']:
            print(f"  • {goal}")
        
        print(f"\nResources:")
        for resource in faction['resources']:
            print(f"  • {resource}")
        
        print(f"\nAllies: {', '.join(faction['allies'])}")
        print(f"Enemies: {', '.join(faction['enemies'])}")

# Main generation function for compatibility with existing system
def generate_romance_factions(num_factions=5, **kwargs):
    """
    Main function to generate romance factions.
    Compatible with the existing faction generation system.
    """
    return generate_romance_world(num_factions=num_factions, **kwargs)

if __name__ == "__main__":
    # Test the generator
    print("Testing Romance Generator...")
    factions = generate_romance_factions(6)
    print_romance_factions(factions)
    
    # Save to file
    save_romance_factions_to_file(factions, "test_romance_factions.json") 