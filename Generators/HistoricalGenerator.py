import random
import json
from datetime import datetime

# Historical faction types with detailed characteristics
HISTORICAL_FACTION_TYPES = {
    "Royal Court": {
        "description_templates": [
            "The {adjective} court of {ruler_title} {ruler_name}, ruling from the magnificent {palace_name}",
            "A {adjective} royal dynasty led by {ruler_title} {ruler_name}, controlling vast territories from {palace_name}",
            "The ancient {adjective} monarchy of {ruler_title} {ruler_name}, whose court at {palace_name} sets the political tone"
        ],
        "goals": [
            "Maintain absolute royal authority",
            "Expand territorial holdings",
            "Secure dynastic succession",
            "Suppress noble rebellions",
            "Form strategic marriage alliances",
            "Control trade routes",
            "Defend against foreign invasion",
            "Centralize governmental power"
        ],
        "resources": [
            "Royal treasury and crown jewels",
            "Standing army and royal guard",
            "Extensive spy network",
            "Noble vassals and allies",
            "Control of major cities",
            "Royal monopolies on trade",
            "Church support and blessing",
            "Diplomatic connections"
        ],
        "territories": [
            "Royal palaces and residences",
            "Crown lands and forests",
            "Major cities and ports",
            "Strategic fortresses",
            "Royal hunting grounds",
            "Administrative centers",
            "Court towns and capitals"
        ],
        "allies": [
            "Loyal noble houses",
            "Church hierarchy",
            "Royal military orders",
            "Wealthy merchant families",
            "Foreign royal courts",
            "Court scholars and advisors"
        ],
        "enemies": [
            "Rebellious noble houses",
            "Foreign kingdoms",
            "Religious dissidents",
            "Republican movements",
            "Ambitious generals",
            "Rival claimants to throne"
        ]
    },
    "Noble House": {
        "description_templates": [
            "The ancient and {adjective} House of {house_name}, whose ancestral seat at {castle_name} has stood for centuries",
            "A {adjective} noble family, the House of {house_name}, ruling their domain from the fortress of {castle_name}",
            "The {adjective} House of {house_name}, whose power emanates from their stronghold at {castle_name}"
        ],
        "goals": [
            "Preserve family honor and legacy",
            "Expand territorial holdings",
            "Gain influence at court",
            "Secure advantageous marriages",
            "Protect ancestral lands",
            "Increase family wealth",
            "Eliminate rival houses",
            "Achieve higher noble rank"
        ],
        "resources": [
            "Ancestral lands and estates",
            "Loyal household retainers",
            "Family treasury and heirlooms",
            "Military levies from vassals",
            "Marriage alliances",
            "Ancient legal privileges",
            "Skilled household staff",
            "Regional political influence"
        ],
        "territories": [
            "Ancestral castle and grounds",
            "Hereditary estates",
            "Vassal holdings",
            "Family burial grounds",
            "Hunting preserves",
            "Village holdings",
            "Strategic border lands"
        ],
        "allies": [
            "Allied noble houses",
            "Loyal vassal families",
            "Marriage-connected families",
            "Regional clergy",
            "Household knights",
            "Trusted advisors"
        ],
        "enemies": [
            "Rival noble houses",
            "Ambitious courtiers",
            "Royal displeasure",
            "Neighboring enemies",
            "Rebellious vassals",
            "Foreign invaders"
        ]
    },
    "Religious Order": {
        "description_templates": [
            "The {adjective} {order_type} of {saint_name}, dedicated to {religious_mission} from their {monastery_type}",
            "A {adjective} religious brotherhood, the {order_type} of {saint_name}, serving {religious_mission}",
            "The ancient {adjective} {order_type} of {saint_name}, whose {monastery_type} serves as a beacon of faith"
        ],
        "goals": [
            "Spread religious doctrine",
            "Preserve sacred knowledge",
            "Protect pilgrims and faithful",
            "Combat heresy and sin",
            "Accumulate religious relics",
            "Establish new monasteries",
            "Provide charitable works",
            "Maintain moral authority"
        ],
        "resources": [
            "Extensive church lands",
            "Tithes and donations",
            "Religious authority",
            "Educated clergy",
            "Sacred relics and artifacts",
            "Monastery libraries",
            "Healing knowledge",
            "International connections"
        ],
        "territories": [
            "Monasteries and abbeys",
            "Church lands and farms",
            "Pilgrimage routes",
            "Sacred sites and shrines",
            "Religious schools",
            "Charitable institutions",
            "Cemetery grounds"
        ],
        "allies": [
            "Devout noble families",
            "Other religious orders",
            "Faithful common people",
            "Church hierarchy",
            "Pious merchants",
            "Religious scholars"
        ],
        "enemies": [
            "Heretical movements",
            "Secular authorities",
            "Competing religions",
            "Corrupt clergy",
            "Anti-clerical nobles",
            "Foreign infidels"
        ]
    },
    "Merchant Guild": {
        "description_templates": [
            "The prosperous {adjective} Guild of {trade_type}, controlling {trade_focus} from their headquarters in {guild_hall}",
            "A {adjective} merchant organization, the Guild of {trade_type}, dominating commerce in {trade_focus}",
            "The influential {adjective} Guild of {trade_type}, whose wealth from {trade_focus} grants them significant power"
        ],
        "goals": [
            "Control regional trade routes",
            "Eliminate commercial competition",
            "Gain political influence",
            "Establish trade monopolies",
            "Protect merchant interests",
            "Expand to new markets",
            "Secure favorable laws",
            "Accumulate collective wealth"
        ],
        "resources": [
            "Vast commercial networks",
            "Accumulated guild treasury",
            "Skilled craftsmen and traders",
            "Trade route knowledge",
            "Commercial vessels and caravans",
            "Guild halls and warehouses",
            "Political connections",
            "International contacts"
        ],
        "territories": [
            "Guild halls and offices",
            "Market districts",
            "Warehouse complexes",
            "Trade route stations",
            "Craft workshops",
            "Commercial ports",
            "Guild-controlled towns"
        ],
        "allies": [
            "Other merchant guilds",
            "Wealthy noble patrons",
            "Foreign trading partners",
            "Skilled artisan guilds",
            "Sympathetic officials",
            "Banking houses"
        ],
        "enemies": [
            "Competing merchant groups",
            "Restrictive noble lords",
            "Bandit organizations",
            "Foreign trade rivals",
            "Anti-commerce clergy",
            "Corrupt tax collectors"
        ]
    },
    "Military Order": {
        "description_templates": [
            "The elite {adjective} Order of {military_name}, warrior-monks dedicated to {military_mission}",
            "A {adjective} brotherhood of knights, the Order of {military_name}, sworn to {military_mission}",
            "The legendary {adjective} Order of {military_name}, whose fortress-monasteries guard against all threats"
        ],
        "goals": [
            "Defend the realm from enemies",
            "Protect religious pilgrims",
            "Maintain military excellence",
            "Uphold chivalric ideals",
            "Serve the crown faithfully",
            "Combat foreign invaders",
            "Preserve martial traditions",
            "Train elite warriors"
        ],
        "resources": [
            "Elite trained knights",
            "Fortress-monasteries",
            "Military equipment and weapons",
            "War horses and mounts",
            "Strategic intelligence",
            "Military engineering knowledge",
            "Veteran commanders",
            "Royal military grants"
        ],
        "territories": [
            "Fortress-monasteries",
            "Strategic border posts",
            "Military training grounds",
            "Weapon forges and armories",
            "Cavalry breeding grounds",
            "Defensive outposts",
            "Military supply depots"
        ],
        "allies": [
            "Royal military forces",
            "Other knightly orders",
            "Church hierarchy",
            "Loyal noble houses",
            "Veteran soldiers",
            "Military engineers"
        ],
        "enemies": [
            "Foreign invading armies",
            "Bandit organizations",
            "Rebellious nobles",
            "Enemy military orders",
            "Corrupt officials",
            "Anti-military factions"
        ]
    },
    "Scholarly Academy": {
        "description_templates": [
            "The renowned {adjective} Academy of {academic_focus}, where scholars pursue {scholarly_mission}",
            "A {adjective} center of learning, the Academy of {academic_focus}, dedicated to advancing {scholarly_mission}",
            "The prestigious {adjective} Academy of {academic_focus}, whose libraries contain vast knowledge of {scholarly_mission}"
        ],
        "goals": [
            "Advance human knowledge",
            "Preserve ancient wisdom",
            "Train future scholars",
            "Conduct scientific research",
            "Translate ancient texts",
            "Develop new technologies",
            "Provide education to nobility",
            "Maintain academic independence"
        ],
        "resources": [
            "Vast libraries and archives",
            "Learned scholars and teachers",
            "Scientific instruments",
            "Ancient manuscripts",
            "Academic endowments",
            "International correspondence",
            "Research laboratories",
            "Scholarly publications"
        ],
        "territories": [
            "Academy buildings and halls",
            "Library complexes",
            "Research laboratories",
            "Student dormitories",
            "Observatory towers",
            "Botanical gardens",
            "Academic workshops"
        ],
        "allies": [
            "Other academic institutions",
            "Scholarly patrons",
            "Educated nobility",
            "International academics",
            "Progressive clergy",
            "Enlightened rulers"
        ],
        "enemies": [
            "Anti-intellectual movements",
            "Religious fundamentalists",
            "Superstitious populations",
            "Competing academies",
            "Authoritarian rulers",
            "Book burners and censors"
        ]
    }
}

# Name generation components
RULER_TITLES = [
    "King", "Queen", "Emperor", "Empress", "Duke", "Duchess", "Prince", "Princess",
    "Archduke", "Grand Duke", "Margrave", "Count", "Earl", "Baron", "Lord", "Lady"
]

PALACE_NAMES = [
    "Versailles", "Windsor", "Buckingham", "Schönbrunn", "Neuschwanstein", "Fontainebleau",
    "Hampton Court", "Whitehall", "Louvre", "Escorial", "Peterhof", "Drottningholm",
    "Charlottenburg", "Sanssouci", "Caserta", "Aranjuez", "Queluz", "Christiansborg"
]

HOUSE_NAMES = [
    "Lancaster", "York", "Tudor", "Stuart", "Plantagenet", "Habsburg", "Bourbon", "Valois",
    "Medici", "Borgia", "Sforza", "Este", "Gonzaga", "Visconti", "Anjou", "Normandy",
    "Burgundy", "Savoy", "Orange", "Nassau", "Wittelsbach", "Hohenzollern", "Romanov", "Rurik"
]

CASTLE_NAMES = [
    "Camelot", "Warwick", "Edinburgh", "Stirling", "Conwy", "Caerphilly", "Bodiam", "Harlech",
    "Carcassonne", "Chambord", "Chenonceau", "Vincennes", "Hohensalzburg", "Neuschwanstein",
    "Malbork", "Krak des Chevaliers", "Alcázar", "Alhambra", "Segovia", "Belmonte"
]

RELIGIOUS_ORDERS = [
    "Benedictines", "Franciscans", "Dominicans", "Jesuits", "Templars", "Hospitallers",
    "Cistercians", "Augustinians", "Carmelites", "Carthusians", "Premonstratensians", "Cluniacs"
]

SAINT_NAMES = [
    "Benedict", "Francis", "Dominic", "Augustine", "Thomas", "Bernard", "Anthony", "Jerome",
    "Ambrose", "Gregory", "Martin", "Nicholas", "Christopher", "Michael", "Gabriel", "Raphael"
]

MONASTERY_TYPES = [
    "Abbey", "Monastery", "Priory", "Convent", "Hermitage", "Charterhouse", "Friary", "Cloister"
]

RELIGIOUS_MISSIONS = [
    "divine contemplation", "charitable works", "scholarly pursuits", "missionary activities",
    "healing the sick", "educating the young", "preserving knowledge", "serving the poor"
]

TRADE_TYPES = [
    "Silk Merchants", "Spice Traders", "Wool Merchants", "Wine Traders", "Goldsmiths",
    "Cloth Merchants", "Fur Traders", "Salt Merchants", "Grain Dealers", "Jewelers"
]

TRADE_FOCUS = [
    "luxury goods", "essential commodities", "exotic spices", "precious metals",
    "fine textiles", "rare books", "medicinal herbs", "artistic works"
]

GUILD_HALLS = [
    "Merchant's Hall", "Trade House", "Commerce Center", "Guild Palace", "Market Hall",
    "Exchange Building", "Trader's Lodge", "Commercial Court", "Business Quarter"
]

MILITARY_NAMES = [
    "the Golden Lion", "the Iron Cross", "the Sacred Sword", "the Silver Eagle",
    "the Crimson Banner", "the White Rose", "the Black Shield", "the Azure Dragon"
]

MILITARY_MISSIONS = [
    "defending the realm", "protecting pilgrims", "guarding sacred sites", "maintaining peace",
    "serving the crown", "upholding justice", "fighting heresy", "preserving order"
]

ACADEMIC_FOCUS = [
    "Natural Philosophy", "Theological Studies", "Classical Learning", "Mathematical Arts",
    "Medical Sciences", "Astronomical Studies", "Historical Research", "Linguistic Studies"
]

SCHOLARLY_MISSIONS = [
    "natural philosophy", "theological inquiry", "historical research", "mathematical studies",
    "medical knowledge", "astronomical observation", "linguistic analysis", "artistic theory"
]

ADJECTIVES = [
    "ancient", "noble", "powerful", "prestigious", "influential", "wealthy", "respected",
    "feared", "legendary", "renowned", "mighty", "illustrious", "distinguished", "eminent"
]

def generate_faction_name(faction_type):
    """Generate a name for a historical faction based on its type"""
    if faction_type == "Royal Court":
        ruler_title = random.choice(RULER_TITLES)
        # Generate a royal name (simplified)
        royal_names = ["Henry", "Edward", "Richard", "William", "Charles", "Louis", "Frederick", "Alexander"]
        ruler_name = f"{random.choice(royal_names)} {random.choice(['I', 'II', 'III', 'IV', 'V'])}"
        palace_name = random.choice(PALACE_NAMES)
        return f"Court of {ruler_title} {ruler_name}", {
            "ruler_title": ruler_title,
            "ruler_name": ruler_name,
            "palace_name": palace_name
        }
    
    elif faction_type == "Noble House":
        house_name = random.choice(HOUSE_NAMES)
        castle_name = random.choice(CASTLE_NAMES)
        return f"House of {house_name}", {
            "house_name": house_name,
            "castle_name": castle_name
        }
    
    elif faction_type == "Religious Order":
        order_type = random.choice(RELIGIOUS_ORDERS)
        saint_name = random.choice(SAINT_NAMES)
        monastery_type = random.choice(MONASTERY_TYPES)
        religious_mission = random.choice(RELIGIOUS_MISSIONS)
        return f"Order of {order_type}", {
            "order_type": order_type,
            "saint_name": saint_name,
            "monastery_type": monastery_type,
            "religious_mission": religious_mission
        }
    
    elif faction_type == "Merchant Guild":
        trade_type = random.choice(TRADE_TYPES)
        trade_focus = random.choice(TRADE_FOCUS)
        guild_hall = random.choice(GUILD_HALLS)
        return f"Guild of {trade_type}", {
            "trade_type": trade_type,
            "trade_focus": trade_focus,
            "guild_hall": guild_hall
        }
    
    elif faction_type == "Military Order":
        military_name = random.choice(MILITARY_NAMES)
        military_mission = random.choice(MILITARY_MISSIONS)
        return f"Order of {military_name}", {
            "military_name": military_name,
            "military_mission": military_mission
        }
    
    elif faction_type == "Scholarly Academy":
        academic_focus = random.choice(ACADEMIC_FOCUS)
        scholarly_mission = random.choice(SCHOLARLY_MISSIONS)
        return f"Academy of {academic_focus}", {
            "academic_focus": academic_focus,
            "scholarly_mission": scholarly_mission
        }
    
    return f"Unknown {faction_type}", {}

def generate_historical_factions(num_factions=6):
    """Generate a set of historical factions with detailed information"""
    faction_types = list(HISTORICAL_FACTION_TYPES.keys())
    
    # Ensure we have enough faction types
    if num_factions > len(faction_types):
        # Repeat faction types if we need more factions
        faction_types = faction_types * ((num_factions // len(faction_types)) + 1)
    
    # Randomly select faction types
    selected_types = random.sample(faction_types, num_factions)
    
    factions = []
    
    for faction_type in selected_types:
        faction_name, name_components = generate_faction_name(faction_type)
        faction_template = HISTORICAL_FACTION_TYPES[faction_type]
        
        # Generate description
        description_template = random.choice(faction_template["description_templates"])
        adjective = random.choice(ADJECTIVES)
        
        # Fill in the template with generated components
        description = description_template.format(
            adjective=adjective,
            **name_components
        )
        
        faction = {
            "faction_name": faction_name,
            "faction_type": faction_type,
            "description": description,
            "goals": random.sample(faction_template["goals"], min(4, len(faction_template["goals"]))),
            "resources": random.sample(faction_template["resources"], min(5, len(faction_template["resources"]))),
            "territory": random.choice(faction_template["territories"]),
            "allies": random.sample(faction_template["allies"], min(3, len(faction_template["allies"]))),
            "enemies": random.sample(faction_template["enemies"], min(3, len(faction_template["enemies"]))),
            "power_level": random.randint(3, 8),
            "influence_radius": random.choice(["Local", "Regional", "National", "International"]),
            "historical_period": random.choice([
                "Medieval", "Renaissance", "Early Modern", "Classical Antiquity", 
                "Late Medieval", "High Medieval", "Byzantine", "Carolingian"
            ])
        }
        
        factions.append(faction)
    
    return factions

def generate_faction_relationships(factions):
    """Generate relationships between historical factions"""
    relationships = []
    
    relationship_types = [
        "Allied", "Hostile", "Neutral", "Trade Partners", "Rivals", "Vassals",
        "Suspicious", "Cooperative", "Competitive", "Dependent"
    ]
    
    for i, faction1 in enumerate(factions):
        for faction2 in factions[i+1:]:
            # Determine relationship based on faction types
            relationship_type = random.choice(relationship_types)
            
            # Adjust probability based on faction types
            if faction1["faction_type"] == "Royal Court" and faction2["faction_type"] == "Noble House":
                relationship_type = random.choice(["Allied", "Vassals", "Suspicious", "Neutral"])
            elif faction1["faction_type"] == "Religious Order" and faction2["faction_type"] == "Scholarly Academy":
                relationship_type = random.choice(["Cooperative", "Suspicious", "Allied", "Competitive"])
            elif faction1["faction_type"] == "Merchant Guild" and faction2["faction_type"] == "Noble House":
                relationship_type = random.choice(["Trade Partners", "Dependent", "Cooperative", "Rivals"])
            
            relationship = {
                "faction1": faction1["faction_name"],
                "faction2": faction2["faction_name"],
                "relationship_type": relationship_type,
                "description": f"The {faction1['faction_name']} and {faction2['faction_name']} maintain {relationship_type.lower()} relations."
            }
            
            relationships.append(relationship)
    
    return relationships

def save_historical_factions_to_file(factions, filename=None, timestamp=False):
    """Save historical factions to a JSON file"""
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historical_factions_{timestamp_str}.json"
        else:
            filename = "historical_factions.json"
    
    relationships = generate_faction_relationships(factions)
    
    data = {
        "factions": factions,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_factions": len(factions),
            "genre": "Historical Fiction"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename

def load_historical_factions_from_file(filename="historical_factions.json"):
    """Load historical factions from a JSON file"""
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

def test_historical_faction_generation():
    """Test function to generate and display historical factions"""
    print("Generating Historical Factions...")
    factions = generate_historical_factions(6)
    
    for faction in factions:
        print(f"\n=== {faction['faction_name']} ===")
        print(f"Type: {faction['faction_type']}")
        print(f"Description: {faction['description']}")
        print(f"Goals: {', '.join(faction['goals'])}")
        print(f"Territory: {faction['territory']}")
        print(f"Power Level: {faction['power_level']}/10")
        print(f"Historical Period: {faction['historical_period']}")
    
    # Save to file
    filename = save_historical_factions_to_file(factions, timestamp=True)
    print(f"\nFactions saved to {filename}")

if __name__ == "__main__":
    test_historical_faction_generation() 