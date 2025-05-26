import json
import random
import os
from datetime import datetime

# --- Western Name Generation System ---

# Western character names (period-appropriate)
WESTERN_FIRST_NAMES = {
    "male": [
        "Wyatt", "Jesse", "Cole", "Jake", "Luke", "Sam", "Ben", "Tom", "Jack", "Will",
        "Hank", "Frank", "Joe", "Jim", "Bill", "Doc", "Clay", "Wade", "Colt", "Jed",
        "Buck", "Tex", "Red", "Slim", "Dutch", "Ace", "Bart", "Cal", "Dean", "Earl",
        "Gus", "Ike", "Kit", "Levi", "Mack", "Nate", "Otto", "Pete", "Roy", "Zeke",
        "Abraham", "Bartholomew", "Cornelius", "Ezekiel", "Jeremiah", "Nathaniel", "Obadiah", "Thaddeus"
    ],
    "female": [
        "Annie", "Belle", "Clara", "Daisy", "Emma", "Faith", "Grace", "Hope", "Ivy", "Jane",
        "Kate", "Lily", "Mary", "Nancy", "Opal", "Pearl", "Rose", "Sarah", "Tess", "Vera",
        "Abigail", "Beatrice", "Catherine", "Dorothy", "Eleanor", "Florence", "Georgia", "Hannah",
        "Isabel", "Josephine", "Katherine", "Lucille", "Margaret", "Ophelia", "Prudence", "Rebecca",
        "Susannah", "Victoria", "Wilhelmina", "Ximena", "Yvonne", "Zelda"
    ]
}

WESTERN_SURNAMES = [
    "Anderson", "Baker", "Carter", "Davis", "Evans", "Foster", "Garcia", "Harris", "Jackson", "Johnson",
    "Kelly", "Lewis", "Miller", "Nelson", "O'Brien", "Parker", "Quinn", "Roberts", "Smith", "Taylor",
    "Walker", "Wilson", "Young", "Brown", "Clark", "Cooper", "Fisher", "Green", "Hill", "King",
    "Martinez", "Morgan", "Murphy", "Phillips", "Reed", "Rodriguez", "Thompson", "Turner", "White", "Williams",
    # Western-specific surnames
    "Blackwood", "Colt", "Deadwood", "Eastwood", "Gunner", "Hawkins", "Ironwood", "Lawson", "Outlaw", "Ranger",
    "Rider", "Sheriff", "Steele", "Stone", "Tracker", "Wrangler", "McCoy", "O'Malley", "Cassidy", "Holliday"
]

# Western town name components
WESTERN_TOWN_PREFIXES = [
    "Dead", "Dry", "Dust", "Gold", "Iron", "Red", "Silver", "Black", "White", "Blue",
    "Broken", "Lost", "New", "Old", "Wild", "Lone", "Twin", "Three", "Devil's", "Angel's",
    "Copper", "Lead", "Tin", "Salt", "Sand", "Rock", "Stone", "Creek", "River", "Mesa"
]

WESTERN_TOWN_SUFFIXES = [
    "Creek", "Gulch", "Ridge", "Valley", "Springs", "Falls", "Rock", "Mesa", "Butte", "Canyon",
    "Flats", "Wells", "Crossing", "Junction", "Station", "Post", "Fort", "Camp", "City", "Town",
    "Hollow", "Gap", "Pass", "Trail", "Run", "Bend", "Point", "Peak", "Bluff", "Draw"
]

# Western faction types with detailed characteristics
WESTERN_FACTION_TYPES = {
    "Law Enforcement": {
        "description_templates": [
            "The {adjective} {organization} of {territory_name}, dedicated to maintaining law and order across the frontier",
            "A {adjective} law enforcement organization, the {organization} of {territory_name}, bringing justice to the lawless lands",
            "The {adjective} {organization} of {territory_name}, whose badge represents the thin line between civilization and chaos"
        ],
        "organizations": ["Sheriff's Department", "Marshal Service", "Ranger Company", "Town Watch", "Territorial Guard"],
        "goals": [
            "Maintain law and order in frontier territories",
            "Protect settlers from outlaw gangs",
            "Establish justice in lawless towns",
            "Hunt down notorious criminals",
            "Secure trade routes from bandits",
            "Enforce territorial and federal laws",
            "Protect mining operations",
            "Maintain peace between rival factions"
        ],
        "resources": [
            "Federal backing and authority",
            "Network of deputies and marshals",
            "Access to wanted posters and intelligence",
            "Legal jurisdiction and court system",
            "Weapons and ammunition supplies",
            "Jail facilities and holding cells",
            "Telegraph communication network",
            "Cooperation with military forces"
        ],
        "territories": [
            "County courthouse and jail",
            "Sheriff's office and deputy stations",
            "Patrol routes and checkpoints",
            "Federal marshal headquarters",
            "Ranger outposts and camps",
            "Town watch stations",
            "Territorial prison facilities"
        ],
        "allies": [
            "Federal government officials",
            "Local town councils",
            "Honest merchants and traders",
            "Railroad companies",
            "Mining company security",
            "Territorial militias"
        ],
        "enemies": [
            "Outlaw gangs and bandits",
            "Corrupt politicians",
            "Cattle rustlers",
            "Train robbers",
            "Claim jumpers",
            "Vigilante groups"
        ]
    },
    "Outlaw Gang": {
        "description_templates": [
            "The {adjective} {gang_name} Gang, a notorious band of outlaws terrorizing {territory_name}",
            "A {adjective} criminal organization, the {gang_name} Gang, whose reputation strikes fear across {territory_name}",
            "The {adjective} {gang_name} Gang, whose hideout in {territory_name} serves as a base for their criminal enterprises"
        ],
        "gang_names": ["Black Hat", "Iron Horse", "Dead Shot", "Wild Card", "Blood Moon", "Dust Devil", "Copper Canyon", "Silver Dollar"],
        "goals": [
            "Rob banks and stagecoaches",
            "Control lucrative criminal territories",
            "Evade law enforcement capture",
            "Eliminate rival gangs",
            "Intimidate local populations",
            "Steal cattle and horses",
            "Raid mining operations",
            "Establish criminal empire"
        ],
        "resources": [
            "Hidden camps and hideouts",
            "Stolen weapons and ammunition",
            "Network of criminal contacts",
            "Intimidation and fear tactics",
            "Knowledge of remote territories",
            "Stolen horses and equipment",
            "Corrupt officials on payroll",
            "Underground information network"
        ],
        "territories": [
            "Hidden canyon hideouts",
            "Abandoned mine shafts",
            "Remote mountain camps",
            "Desert oasis bases",
            "Outlaw town strongholds",
            "Cave systems and caverns",
            "Ruined fort positions"
        ],
        "allies": [
            "Corrupt sheriffs and officials",
            "Fence operations and black markets",
            "Saloon owners and gamblers",
            "Other outlaw gangs",
            "Desperate settlers",
            "Crooked merchants"
        ],
        "enemies": [
            "Law enforcement agencies",
            "Rival outlaw gangs",
            "Bounty hunters",
            "Railroad security forces",
            "Mining company guards",
            "Vigilante committees"
        ]
    },
    "Railroad Company": {
        "description_templates": [
            "The {adjective} {railroad_name} Railroad, connecting the frontier with civilization through steel and steam",
            "A {adjective} transportation empire, the {railroad_name} Railroad, whose tracks span across {territory_name}",
            "The {adjective} {railroad_name} Railroad, whose locomotives bring progress and prosperity to {territory_name}"
        ],
        "railroad_names": ["Central Pacific", "Union Pacific", "Denver & Rio Grande", "Atchison Topeka", "Southern Pacific", "Great Northern"],
        "goals": [
            "Expand railroad networks across territories",
            "Protect trains from outlaw attacks",
            "Secure profitable freight contracts",
            "Establish new towns along routes",
            "Control transportation monopolies",
            "Develop mining and lumber operations",
            "Influence territorial politics",
            "Eliminate competition from rivals"
        ],
        "resources": [
            "Vast financial backing from investors",
            "Large workforce of laborers",
            "Advanced locomotive technology",
            "Private security forces",
            "Political influence and lobbying",
            "Land grants from government",
            "Telegraph communication systems",
            "Engineering and surveying teams"
        ],
        "territories": [
            "Railroad stations and depots",
            "Maintenance yards and shops",
            "Company towns and settlements",
            "Rail lines and right-of-ways",
            "Corporate headquarters",
            "Worker housing and facilities",
            "Freight warehouses and loading docks"
        ],
        "allies": [
            "Federal government officials",
            "Eastern financial investors",
            "Local business communities",
            "Territorial governors",
            "Mining and lumber companies",
            "Cattle ranchers and farmers"
        ],
        "enemies": [
            "Outlaw gangs and train robbers",
            "Competing railroad companies",
            "Native American tribes",
            "Anti-railroad political movements",
            "Labor union organizers",
            "Environmental protesters"
        ]
    },
    "Cattle Ranch": {
        "description_templates": [
            "The {adjective} {ranch_name} Ranch, where thousands of cattle roam the vast ranges of {territory_name}",
            "A {adjective} cattle operation, the {ranch_name} Ranch, whose brand is respected throughout {territory_name}",
            "The {adjective} {ranch_name} Ranch, whose cowboys and cattle drives are legendary across {territory_name}"
        ],
        "ranch_names": ["Circle K", "Lazy S", "Double Bar", "Flying W", "Rocking Chair", "Diamond D", "Broken Arrow", "Lone Star"],
        "goals": [
            "Expand grazing territories",
            "Protect cattle from rustlers",
            "Secure water rights and access",
            "Establish profitable cattle drives",
            "Control local beef markets",
            "Eliminate competing ranchers",
            "Influence local politics",
            "Develop breeding programs"
        ],
        "resources": [
            "Vast herds of cattle and horses",
            "Experienced cowboys and ranch hands",
            "Large land holdings and grazing rights",
            "Ranch headquarters and facilities",
            "Branding and identification systems",
            "Weapons for protection",
            "Knowledge of cattle markets",
            "Political connections and influence"
        ],
        "territories": [
            "Ranch headquarters and homestead",
            "Grazing lands and pastures",
            "Water sources and wells",
            "Cattle pens and corrals",
            "Bunkhouses and worker quarters",
            "Hay fields and feed storage",
            "Breeding facilities and barns"
        ],
        "allies": [
            "Other cattle ranchers",
            "Cowboys and ranch workers",
            "Local merchants and suppliers",
            "Railroad shipping companies",
            "Territorial cattlemen's associations",
            "Friendly Native American tribes"
        ],
        "enemies": [
            "Cattle rustlers and thieves",
            "Competing ranchers",
            "Sheep herders and farmers",
            "Land grabbers and claim jumpers",
            "Hostile Native American tribes",
            "Environmental conservationists"
        ]
    },
    "Mining Company": {
        "description_templates": [
            "The {adjective} {company_name} Mining Company, extracting precious metals from the mountains of {territory_name}",
            "A {adjective} mining operation, the {company_name} Mining Company, whose claims span the richest veins in {territory_name}",
            "The {adjective} {company_name} Mining Company, whose mines and mills bring wealth from the earth of {territory_name}"
        ],
        "company_names": ["Consolidated Gold", "Silver Mountain", "Copper Creek", "Iron Horse", "Black Diamond", "Golden Eagle", "Silver Dollar", "Bonanza"],
        "goals": [
            "Extract maximum mineral wealth",
            "Secure and expand mining claims",
            "Protect operations from claim jumpers",
            "Control local mining markets",
            "Develop new extraction technologies",
            "Establish company towns",
            "Influence territorial mining laws",
            "Eliminate mining competition"
        ],
        "resources": [
            "Rich mineral claims and deposits",
            "Advanced mining equipment",
            "Large workforce of miners",
            "Company security forces",
            "Financial backing from investors",
            "Processing mills and refineries",
            "Transportation and shipping networks",
            "Technical expertise and engineers"
        ],
        "territories": [
            "Active mines and shafts",
            "Processing mills and refineries",
            "Company towns and worker housing",
            "Mining claims and territories",
            "Equipment storage and workshops",
            "Administrative offices",
            "Security outposts and guard stations"
        ],
        "allies": [
            "Eastern financial investors",
            "Railroad transportation companies",
            "Local business communities",
            "Territorial government officials",
            "Mining equipment suppliers",
            "Private security contractors"
        ],
        "enemies": [
            "Claim jumpers and thieves",
            "Competing mining companies",
            "Labor union organizers",
            "Environmental protesters",
            "Outlaw gangs targeting payrolls",
            "Native American tribes on traditional lands"
        ]
    },
    "Native American Tribe": {
        "description_templates": [
            "The {adjective} {tribe_name} Tribe, defending their ancestral lands in {territory_name} against encroaching settlers",
            "A {adjective} Native American nation, the {tribe_name} Tribe, whose warriors protect the sacred territories of {territory_name}",
            "The {adjective} {tribe_name} Tribe, whose ancient ways clash with the changing world of {territory_name}"
        ],
        "tribe_names": ["Apache", "Comanche", "Sioux", "Cheyenne", "Crow", "Blackfoot", "Shoshone", "Navajo"],
        "goals": [
            "Protect ancestral tribal lands",
            "Preserve traditional ways of life",
            "Resist settler encroachment",
            "Maintain tribal sovereignty",
            "Secure hunting and fishing rights",
            "Protect sacred sites and burial grounds",
            "Negotiate fair treaties",
            "Defend against military aggression"
        ],
        "resources": [
            "Knowledge of local terrain",
            "Skilled warriors and hunters",
            "Traditional weapons and tactics",
            "Spiritual and cultural unity",
            "Alliance networks with other tribes",
            "Mobility and guerrilla warfare",
            "Understanding of seasonal patterns",
            "Sacred sites and ceremonial grounds"
        ],
        "territories": [
            "Tribal villages and settlements",
            "Sacred sites and burial grounds",
            "Traditional hunting territories",
            "Seasonal camping grounds",
            "Water sources and fishing areas",
            "Defensive positions and strongholds",
            "Trading posts and meeting places"
        ],
        "allies": [
            "Other Native American tribes",
            "Sympathetic traders and trappers",
            "Some military officers",
            "Missionary groups",
            "Environmental conservationists",
            "Anti-expansion political movements"
        ],
        "enemies": [
            "Territorial military forces",
            "Settler communities",
            "Railroad companies",
            "Mining operations",
            "Cattle ranchers",
            "Land speculators and developers"
        ]
    }
}

# Western-specific titles and roles
WESTERN_LEADER_TITLES = [
    "Sheriff", "Marshal", "Captain", "Colonel", "Chief", "Boss", "Foreman", "Superintendent",
    "President", "Chairman", "Director", "Manager", "Overseer", "Warden"
]

WESTERN_MILITARY_TITLES = [
    "Sheriff", "Deputy Sheriff", "Marshal", "Deputy Marshal", "Captain", "Lieutenant", "Sergeant",
    "Corporal", "Ranger", "Scout", "Tracker", "Gunfighter", "Enforcer"
]

WESTERN_ADMINISTRATIVE_TITLES = [
    "Town Mayor", "County Clerk", "Territorial Judge", "Land Commissioner", "Tax Collector",
    "Postmaster", "Telegraph Operator", "Station Agent", "Bookkeeper", "Secretary"
]

WESTERN_SPECIALIZED_TITLES = [
    "Doctor", "Preacher", "Schoolteacher", "Lawyer", "Engineer", "Surveyor", "Assayer",
    "Blacksmith", "Gunsmith", "Veterinarian", "Banker", "Merchant"
]

WESTERN_OPERATIONAL_TITLES = [
    "Cowboy", "Ranch Hand", "Miner", "Prospector", "Teamster", "Stagecoach Driver",
    "Train Conductor", "Telegraph Operator", "Saloon Keeper", "Store Clerk", "Stable Hand"
]

# Western adjectives for descriptions
WESTERN_ADJECTIVES = [
    "legendary", "notorious", "respected", "feared", "powerful", "influential", "ruthless",
    "honorable", "corrupt", "ambitious", "determined", "cunning", "brave", "dangerous"
]

def generate_western_name(gender=None):
    """Generate a Western character name."""
    if gender is None:
        gender = random.choice(["male", "female"])
    
    first_name = random.choice(WESTERN_FIRST_NAMES[gender.lower()])
    last_name = random.choice(WESTERN_SURNAMES)
    
    return first_name, last_name

def generate_town_name():
    """Generate a Western town name."""
    prefix = random.choice(WESTERN_TOWN_PREFIXES)
    suffix = random.choice(WESTERN_TOWN_SUFFIXES)
    return f"{prefix} {suffix}"

def generate_territory_name():
    """Generate a territory name for Western factions."""
    territory_types = [
        "County", "Territory", "District", "Region", "Valley", "Basin", "Range", "Frontier"
    ]
    
    base_name = random.choice(WESTERN_TOWN_PREFIXES + ["Carson", "Lincoln", "Grant", "Sherman", "Custer"])
    territory_type = random.choice(territory_types)
    
    return f"{base_name} {territory_type}"

def generate_faction_name(faction_type):
    """Generate a name for a Western faction based on its type."""
    faction_template = WESTERN_FACTION_TYPES[faction_type]
    territory_name = generate_territory_name()
    
    if faction_type == "Law Enforcement":
        organization = random.choice(faction_template["organizations"])
        return f"{territory_name} {organization}", {
            "organization": organization,
            "territory_name": territory_name
        }
    
    elif faction_type == "Outlaw Gang":
        gang_name = random.choice(faction_template["gang_names"])
        return f"{gang_name} Gang", {
            "gang_name": gang_name,
            "territory_name": territory_name
        }
    
    elif faction_type == "Railroad Company":
        railroad_name = random.choice(faction_template["railroad_names"])
        return f"{railroad_name} Railroad", {
            "railroad_name": railroad_name,
            "territory_name": territory_name
        }
    
    elif faction_type == "Cattle Ranch":
        ranch_name = random.choice(faction_template["ranch_names"])
        return f"{ranch_name} Ranch", {
            "ranch_name": ranch_name,
            "territory_name": territory_name
        }
    
    elif faction_type == "Mining Company":
        company_name = random.choice(faction_template["company_names"])
        return f"{company_name} Mining Company", {
            "company_name": company_name,
            "territory_name": territory_name
        }
    
    elif faction_type == "Native American Tribe":
        tribe_name = random.choice(faction_template["tribe_names"])
        return f"{tribe_name} Tribe", {
            "tribe_name": tribe_name,
            "territory_name": territory_name
        }
    
    return f"Unknown {faction_type}", {"territory_name": territory_name}

def _generate_named_character(title_list, role, specific_title=None, female_percentage=50, male_percentage=50):
    """Generate a Western character with name, title, and role, using gender bias."""
    # Validate and calculate gender weights
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"WESTERN_GEN/_generate_named_character: Invalid gender percentages (F:{female_percentage}%, M:{male_percentage}%). Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0

    gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
    
    first_name, last_name = generate_western_name(gender)
    title = specific_title if specific_title else random.choice(title_list)
    
    full_name = f"{first_name} {last_name}"
    display_name = f"{title} {full_name}".strip() if title else full_name

    return {
        "title": title,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "display_name": display_name,
        "role": role,
        "gender": gender
    }

def generate_western_territories(faction_type, num_territories=3):
    """Generate territories for a Western faction."""
    territories = []
    
    for _ in range(num_territories):
        if faction_type == "Railroad Company":
            territory_name = f"{generate_town_name()} Station"
            territory_type = "Railroad Station"
        elif faction_type == "Cattle Ranch":
            territory_name = f"{generate_town_name()} Grazing Lands"
            territory_type = "Grazing Territory"
        elif faction_type == "Mining Company":
            territory_name = f"{generate_town_name()} Mine"
            territory_type = "Mining Claim"
        elif faction_type == "Native American Tribe":
            territory_name = f"{generate_town_name()} Tribal Lands"
            territory_type = "Tribal Territory"
        else:
            territory_name = generate_town_name()
            territory_type = "Settlement"
        
        # Generate basic territory stats
        population = random.randint(50, 2000)
        prosperity = random.choice(["Booming", "Prosperous", "Stable", "Struggling", "Declining"])
        law_level = random.choice(["Lawless", "Minimal", "Basic", "Well-Regulated", "Strict"])
        
        territory = {
            "name": territory_name,
            "type": territory_type,
            "population": population,
            "prosperity": prosperity,
            "law_level": law_level,
            "resources": random.choice([
                "Rich mineral deposits", "Fertile grazing land", "Strategic location",
                "Water access", "Railroad connection", "Trading post", "Military fort"
            ])
        }
        
        territories.append(territory)
    
    return territories

def generate_western_factions(num_factions=6):
    """Generate a set of Western factions with detailed information."""
    faction_types = list(WESTERN_FACTION_TYPES.keys())
    
    # Ensure we have enough faction types
    if num_factions > len(faction_types):
        faction_types = faction_types * ((num_factions // len(faction_types)) + 1)
    
    # Randomly select faction types
    selected_types = random.sample(faction_types, num_factions)
    
    factions = []
    
    for faction_type in selected_types:
        faction_name, name_components = generate_faction_name(faction_type)
        faction_template = WESTERN_FACTION_TYPES[faction_type]
        
        # Generate description
        description_template = random.choice(faction_template["description_templates"])
        adjective = random.choice(WESTERN_ADJECTIVES)
        
        # Fill in the template with generated components
        description = description_template.format(
            adjective=adjective,
            **name_components
        )
        
        # Generate territories
        territories = generate_western_territories(faction_type, random.randint(2, 4))
        
        # Generate faction personnel
        personnel = []
        
        # Leader
        personnel.append(_generate_named_character(
            WESTERN_LEADER_TITLES, 
            "Faction Leader"
        ))
        
        # Military/Enforcement leader
        personnel.append(_generate_named_character(
            WESTERN_MILITARY_TITLES, 
            "Military Leader"
        ))
        
        # Administrative staff
        for _ in range(random.randint(1, 3)):
            personnel.append(_generate_named_character(
                WESTERN_ADMINISTRATIVE_TITLES, 
                "Administrative Staff"
            ))
        
        # Specialized personnel
        for _ in range(random.randint(1, 2)):
            personnel.append(_generate_named_character(
                WESTERN_SPECIALIZED_TITLES, 
                "Specialist"
            ))
        
        # Operational personnel
        for _ in range(random.randint(3, 6)):
            personnel.append(_generate_named_character(
                WESTERN_OPERATIONAL_TITLES, 
                "Operational Staff"
            ))
        
        faction = {
            "faction_name": faction_name,
            "faction_type": faction_type,
            "description": description,
            "goals": random.sample(faction_template["goals"], min(4, len(faction_template["goals"]))),
            "resources": random.sample(faction_template["resources"], min(5, len(faction_template["resources"]))),
            "territories": territories,
            "allies": random.sample(faction_template["allies"], min(3, len(faction_template["allies"]))),
            "enemies": random.sample(faction_template["enemies"], min(3, len(faction_template["enemies"]))),
            "power_level": random.randint(3, 8),
            "influence_radius": random.choice(["Local", "Regional", "Territorial", "Multi-Territorial"]),
            "characters": personnel,
            "era": random.choice([
                "Early Frontier (1840s-1860s)", "Civil War Era (1860s)", "Post-War Expansion (1870s)",
                "Railroad Boom (1880s)", "Late Frontier (1890s)", "Turn of Century (1900s)"
            ])
        }
        
        factions.append(faction)
    
    return factions

def generate_faction_relationships(factions):
    """Generate relationships between Western factions."""
    relationships = []
    
    relationship_types = [
        "Allied", "Hostile", "Neutral", "Trade Partners", "Rivals", "Uneasy Truce",
        "Suspicious", "Cooperative", "Competitive", "Territorial Dispute"
    ]
    
    for i, faction1 in enumerate(factions):
        for faction2 in factions[i+1:]:
            # Determine relationship based on faction types
            relationship_type = random.choice(relationship_types)
            
            # Adjust probability based on faction types
            if faction1["faction_type"] == "Law Enforcement" and faction2["faction_type"] == "Outlaw Gang":
                relationship_type = "Hostile"
            elif faction1["faction_type"] == "Railroad Company" and faction2["faction_type"] == "Native American Tribe":
                relationship_type = random.choice(["Hostile", "Territorial Dispute", "Uneasy Truce"])
            elif faction1["faction_type"] == "Cattle Ranch" and faction2["faction_type"] == "Railroad Company":
                relationship_type = random.choice(["Trade Partners", "Cooperative", "Allied"])
            elif faction1["faction_type"] == "Mining Company" and faction2["faction_type"] == "Outlaw Gang":
                relationship_type = random.choice(["Hostile", "Rivals", "Suspicious"])
            
            relationship = {
                "faction1": faction1["faction_name"],
                "faction2": faction2["faction_name"],
                "relationship_type": relationship_type,
                "description": f"The {faction1['faction_name']} and {faction2['faction_name']} maintain {relationship_type.lower()} relations."
            }
            
            relationships.append(relationship)
    
    return relationships

def save_western_factions_to_file(factions, filename=None, timestamp=False):
    """Save Western factions to a JSON file."""
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"western_factions_{timestamp_str}.json"
        else:
            filename = "western_factions.json"
    
    relationships = generate_faction_relationships(factions)
    
    data = {
        "factions": factions,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_factions": len(factions),
            "genre": "Western"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename

def load_western_factions_from_file(filename="western_factions.json"):
    """Load Western factions from a JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("factions", []), data.get("relationships", [])
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return [], []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filename}.")
        return [], []

def print_western_factions(factions):
    """Print detailed information about the generated Western factions."""
    for faction in factions:
        print(f"\n=== {faction['faction_name']} ===")
        print(f"Type: {faction['faction_type']}")
        print(f"Era: {faction['era']}")
        print(f"Description: {faction['description']}")
        print(f"Power Level: {faction['power_level']}/10")
        print(f"Influence: {faction['influence_radius']}")
        
        print(f"\nGoals: {', '.join(faction['goals'])}")
        print(f"Resources: {', '.join(faction['resources'])}")
        print(f"Allies: {', '.join(faction['allies'])}")
        print(f"Enemies: {', '.join(faction['enemies'])}")
        
        print("\nTerritories:")
        for territory in faction["territories"]:
            print(f"  - {territory['name']} ({territory['type']})")
            print(f"    Population: {territory['population']}, Prosperity: {territory['prosperity']}")
            print(f"    Law Level: {territory['law_level']}, Resources: {territory['resources']}")
        
        print("\nKey Personnel:")
        for character in faction["characters"]:
            print(f"  - {character['display_name']} ({character['role']})")

def test_western_faction_generation():
    """Test function to generate and display Western factions."""
    print("Generating Western Factions...")
    factions = generate_western_factions(6)
    
    print_western_factions(factions)
    
    # Save to file
    filename = save_western_factions_to_file(factions, timestamp=True)
    print(f"\nFactions saved to {filename}")

if __name__ == "__main__":
    test_western_faction_generation() 