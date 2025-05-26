import json
import random
import os
from datetime import datetime

# --- Thriller Name Generation System ---

# Modern character names (contemporary thriller setting)
THRILLER_FIRST_NAMES = {
    "male": [
        "Alexander", "Benjamin", "Christopher", "Daniel", "Edward", "Frank", "Gabriel", "Henry", "Isaac", "James",
        "Kevin", "Lucas", "Michael", "Nathan", "Oliver", "Patrick", "Quinn", "Robert", "Samuel", "Thomas",
        "Victor", "William", "Xavier", "Zachary", "Adrian", "Blake", "Carter", "Derek", "Ethan", "Felix",
        "Grant", "Hunter", "Ivan", "Jason", "Kyle", "Logan", "Marcus", "Nicholas", "Owen", "Preston",
        "Ryan", "Sebastian", "Tyler", "Vincent", "Wesley", "Alex", "Brad", "Cole", "Dean", "Eric"
    ],
    "female": [
        "Alexandra", "Bethany", "Catherine", "Diana", "Elizabeth", "Fiona", "Grace", "Hannah", "Isabella", "Jessica",
        "Katherine", "Lauren", "Michelle", "Natalie", "Olivia", "Patricia", "Rachel", "Samantha", "Taylor", "Victoria",
        "Wendy", "Ximena", "Yvonne", "Zoe", "Amanda", "Brooke", "Chloe", "Danielle", "Emma", "Faith",
        "Gabrielle", "Haley", "Iris", "Julia", "Kimberly", "Lily", "Megan", "Nicole", "Paige", "Rebecca",
        "Sophia", "Tiffany", "Vanessa", "Whitney", "Abigail", "Claire", "Elena", "Jennifer", "Madison", "Sarah"
    ]
}

THRILLER_SURNAMES = [
    "Anderson", "Baker", "Carter", "Davis", "Evans", "Foster", "Garcia", "Harris", "Jackson", "Johnson",
    "Kelly", "Lewis", "Miller", "Nelson", "O'Brien", "Parker", "Quinn", "Roberts", "Smith", "Taylor",
    "Walker", "Wilson", "Young", "Brown", "Clark", "Cooper", "Fisher", "Green", "Hill", "King",
    "Martinez", "Morgan", "Murphy", "Phillips", "Reed", "Rodriguez", "Thompson", "Turner", "White", "Williams",
    # Thriller-specific surnames
    "Cross", "Stone", "Steel", "Sharp", "Black", "Grey", "Hunter", "Knight", "Wolf", "Fox",
    "Raven", "Storm", "Winter", "Frost", "Burns", "Kane", "Drake", "Pierce", "Steele", "Chase"
]

# Organization name components
THRILLER_ORG_PREFIXES = [
    "Global", "International", "United", "Allied", "Central", "Federal", "National", "Strategic", "Advanced", "Elite",
    "Covert", "Special", "Joint", "Integrated", "Consolidated", "Unified", "Classified", "Shadow", "Black", "Red"
]

THRILLER_ORG_SUFFIXES = [
    "Agency", "Division", "Bureau", "Department", "Service", "Command", "Operations", "Intelligence", "Security", "Force",
    "Group", "Unit", "Task Force", "Consortium", "Corporation", "Syndicate", "Network", "Alliance", "Coalition", "Initiative"
]

# Location name components for bases/headquarters
THRILLER_LOCATION_PREFIXES = [
    "Fort", "Camp", "Base", "Station", "Facility", "Complex", "Center", "Institute", "Laboratory", "Compound",
    "Headquarters", "Office", "Building", "Tower", "Plaza", "Point", "Site", "Zone", "Sector", "District"
]

THRILLER_LOCATION_NAMES = [
    "Langley", "Quantico", "Pentagon", "Cheyenne", "Blackwater", "Raven Rock", "Site R", "Mount Weather",
    "Pine Gap", "Menwith Hill", "Echelon", "Tempest", "Carnivore", "Prism", "Vault", "Nexus",
    "Phoenix", "Cerberus", "Hydra", "Medusa", "Titan", "Atlas", "Prometheus", "Pandora"
]

# Thriller faction types with detailed characteristics
THRILLER_FACTION_TYPES = {
    "Intelligence Agency": {
        "description_templates": [
            "The {adjective} {agency_name}, a {classification} intelligence organization operating from {headquarters}",
            "A {adjective} intelligence service, the {agency_name}, whose {classification} operations span the globe from {headquarters}",
            "The {adjective} {agency_name}, whose {classification} agents gather intelligence and conduct operations worldwide from {headquarters}"
        ],
        "agency_types": ["Intelligence Agency", "Security Service", "Special Operations Division", "Counterintelligence Bureau"],
        "classifications": ["classified", "top-secret", "black ops", "covert", "clandestine", "compartmentalized"],
        "goals": [
            "Gather foreign intelligence on threats",
            "Conduct covert operations abroad",
            "Protect national security interests",
            "Infiltrate terrorist organizations",
            "Monitor international communications",
            "Eliminate high-value targets",
            "Prevent weapons of mass destruction proliferation",
            "Maintain global intelligence networks"
        ],
        "resources": [
            "Vast surveillance networks",
            "Advanced technology and equipment",
            "Highly trained operatives",
            "International safe houses",
            "Unlimited black budget funding",
            "Government backing and authority",
            "Satellite and drone capabilities",
            "Cryptographic and cyber warfare tools"
        ],
        "territories": [
            "Classified headquarters facilities",
            "Regional field offices",
            "Safe houses and dead drops",
            "Training facilities and camps",
            "Communication relay stations",
            "Surveillance outposts",
            "Black sites and detention centers"
        ],
        "allies": [
            "Allied intelligence services",
            "Military special forces",
            "Government officials",
            "Friendly foreign agencies",
            "Private military contractors",
            "Technology corporations"
        ],
        "enemies": [
            "Hostile foreign intelligence",
            "Terrorist organizations",
            "Criminal syndicates",
            "Rogue states",
            "Cyber warfare groups",
            "Whistleblowers and leaks"
        ]
    },
    "Criminal Syndicate": {
        "description_templates": [
            "The {adjective} {syndicate_name}, a {criminal_type} criminal organization operating from {headquarters}",
            "A {adjective} criminal empire, the {syndicate_name}, whose {criminal_type} operations span multiple continents from {headquarters}",
            "The {adjective} {syndicate_name}, whose {criminal_type} network controls vast illegal enterprises from {headquarters}"
        ],
        "syndicate_names": ["Crimson Serpent", "Black Diamond", "Silver Wolf", "Iron Fist", "Golden Dragon", "Shadow Viper", "Blood Moon", "Steel Talon"],
        "criminal_types": ["international", "transnational", "organized", "sophisticated", "ruthless", "powerful"],
        "goals": [
            "Control international drug trafficking",
            "Expand money laundering operations",
            "Eliminate rival criminal organizations",
            "Corrupt government officials",
            "Establish criminal monopolies",
            "Conduct high-stakes heists",
            "Traffic weapons and contraband",
            "Build global criminal empire"
        ],
        "resources": [
            "Vast criminal networks",
            "Corrupt officials and judges",
            "Advanced weapons and equipment",
            "Money laundering operations",
            "International smuggling routes",
            "Private armies and enforcers",
            "Sophisticated communication systems",
            "Legitimate business fronts"
        ],
        "territories": [
            "Criminal headquarters and compounds",
            "Safe houses and hideouts",
            "Money laundering fronts",
            "Drug processing facilities",
            "Weapons storage depots",
            "Smuggling route checkpoints",
            "Corrupt territory control zones"
        ],
        "allies": [
            "Corrupt government officials",
            "Other criminal organizations",
            "Mercenary groups",
            "Dirty cops and judges",
            "Money laundering banks",
            "Arms dealers and suppliers"
        ],
        "enemies": [
            "Law enforcement agencies",
            "Rival criminal syndicates",
            "Intelligence services",
            "Anti-corruption task forces",
            "International police organizations",
            "Undercover agents"
        ]
    },
    "Terrorist Organization": {
        "description_templates": [
            "The {adjective} {terrorist_name}, a {ideology} terrorist organization operating from {headquarters}",
            "A {adjective} extremist group, the {terrorist_name}, whose {ideology} agenda drives their operations from {headquarters}",
            "The {adjective} {terrorist_name}, whose {ideology} ideology fuels their terrorist activities across the globe from {headquarters}"
        ],
        "terrorist_names": ["Red Dawn", "Black Flag", "Iron Crescent", "Shadow Brigade", "Blood Covenant", "Storm Front", "Fire Phoenix", "Dark Legion"],
        "ideologies": ["radical", "extremist", "fundamentalist", "revolutionary", "separatist", "anarchist"],
        "goals": [
            "Conduct high-profile terrorist attacks",
            "Destabilize target governments",
            "Spread fear and terror",
            "Recruit new members globally",
            "Acquire weapons of mass destruction",
            "Establish terrorist state",
            "Eliminate ideological enemies",
            "Inspire copycat attacks"
        ],
        "resources": [
            "Fanatical followers and recruits",
            "Underground funding networks",
            "Improvised explosive devices",
            "Stolen military equipment",
            "Safe houses and training camps",
            "Propaganda and recruitment tools",
            "Suicide bombers and martyrs",
            "International support networks"
        ],
        "territories": [
            "Hidden training camps",
            "Underground safe houses",
            "Recruitment centers",
            "Weapons caches and depots",
            "Communication relay points",
            "Propaganda production facilities",
            "Escape routes and tunnels"
        ],
        "allies": [
            "Sympathetic extremist groups",
            "Rogue state sponsors",
            "Criminal organizations",
            "Corrupt officials",
            "Radical religious leaders",
            "Anti-government militias"
        ],
        "enemies": [
            "Counter-terrorism forces",
            "Intelligence agencies",
            "Military special operations",
            "International coalitions",
            "Moderate religious leaders",
            "Rival terrorist groups"
        ]
    },
    "Mega Corporation": {
        "description_templates": [
            "The {adjective} {corporation_name}, a {corporate_type} mega-corporation with headquarters in {headquarters}",
            "A {adjective} multinational conglomerate, {corporation_name}, whose {corporate_type} operations span the globe from {headquarters}",
            "The {adjective} {corporation_name}, whose {corporate_type} influence reaches into every aspect of modern life from {headquarters}"
        ],
        "corporation_names": ["Nexus Industries", "Titan Corporation", "Phoenix Dynamics", "Atlas Global", "Cerberus Systems", "Hydra Enterprises", "Prometheus Tech", "Pandora Group"],
        "corporate_types": ["multinational", "diversified", "technology-focused", "defense-oriented", "pharmaceutical", "energy"],
        "goals": [
            "Maximize shareholder profits",
            "Eliminate business competition",
            "Influence government policy",
            "Control market monopolies",
            "Develop cutting-edge technology",
            "Expand global operations",
            "Suppress negative publicity",
            "Maintain corporate secrecy"
        ],
        "resources": [
            "Unlimited financial resources",
            "Advanced research facilities",
            "Private security forces",
            "Government contracts and influence",
            "Global supply chains",
            "Cutting-edge technology",
            "Legal teams and lobbying power",
            "International business networks"
        ],
        "territories": [
            "Corporate headquarters towers",
            "Research and development facilities",
            "Manufacturing plants",
            "Regional offices worldwide",
            "Private security compounds",
            "Executive retreat centers",
            "Data centers and server farms"
        ],
        "allies": [
            "Government officials and regulators",
            "Other mega-corporations",
            "Private military contractors",
            "Lobbying organizations",
            "Financial institutions",
            "Technology partners"
        ],
        "enemies": [
            "Regulatory agencies",
            "Competing corporations",
            "Environmental activists",
            "Investigative journalists",
            "Whistleblowers",
            "Consumer advocacy groups"
        ]
    },
    "Military Contractor": {
        "description_templates": [
            "The {adjective} {contractor_name}, a {contractor_type} military contractor operating from {headquarters}",
            "A {adjective} private military company, {contractor_name}, whose {contractor_type} services are available to the highest bidder from {headquarters}",
            "The {adjective} {contractor_name}, whose {contractor_type} operatives conduct missions too sensitive for regular military from {headquarters}"
        ],
        "contractor_names": ["Blackwater Security", "Aegis Defense", "Titan Military", "Phoenix Tactical", "Cerberus Operations", "Atlas Security", "Vanguard Forces", "Sentinel Group"],
        "contractor_types": ["elite", "specialized", "covert", "tactical", "strategic", "international"],
        "goals": [
            "Secure lucrative military contracts",
            "Provide deniable operations",
            "Train foreign military forces",
            "Protect corporate interests",
            "Conduct covert missions",
            "Eliminate high-value targets",
            "Provide security services",
            "Maintain operational secrecy"
        ],
        "resources": [
            "Elite military veterans",
            "Advanced weapons and equipment",
            "Military vehicles and aircraft",
            "Training facilities and ranges",
            "Intelligence gathering capabilities",
            "International operational licenses",
            "Government and corporate contracts",
            "Secure communication networks"
        ],
        "territories": [
            "Private military bases",
            "Training facilities and ranges",
            "Weapons storage depots",
            "Operational headquarters",
            "Safe houses and staging areas",
            "Equipment maintenance facilities",
            "Recruitment and vetting centers"
        ],
        "allies": [
            "Government defense departments",
            "Intelligence agencies",
            "Mega-corporations",
            "Foreign military forces",
            "Other military contractors",
            "Arms manufacturers"
        ],
        "enemies": [
            "Rival military contractors",
            "Anti-war activists",
            "International law organizations",
            "Investigative journalists",
            "Government oversight committees",
            "Human rights groups"
        ]
    },
    "Cyber Warfare Group": {
        "description_templates": [
            "The {adjective} {hacker_name}, a {hacker_type} cyber warfare organization operating from {headquarters}",
            "A {adjective} hacking collective, {hacker_name}, whose {hacker_type} cyber operations target critical infrastructure from {headquarters}",
            "The {adjective} {hacker_name}, whose {hacker_type} digital warfare capabilities threaten global security from {headquarters}"
        ],
        "hacker_names": ["Ghost Protocol", "Digital Storm", "Cyber Phantom", "Binary Shadow", "Code Red", "Dark Web", "Quantum Breach", "Neural Network"],
        "hacker_types": ["sophisticated", "state-sponsored", "anarchist", "criminal", "activist", "mercenary"],
        "goals": [
            "Conduct cyber espionage operations",
            "Disrupt critical infrastructure",
            "Steal classified information",
            "Launch ransomware attacks",
            "Manipulate financial markets",
            "Influence political elections",
            "Expose government secrets",
            "Develop advanced malware"
        ],
        "resources": [
            "Elite hacking skills and tools",
            "Advanced computer systems",
            "Encrypted communication networks",
            "Zero-day exploits and malware",
            "Cryptocurrency funding",
            "Anonymous proxy networks",
            "Insider access and contacts",
            "Artificial intelligence systems"
        ],
        "territories": [
            "Hidden server farms",
            "Encrypted communication hubs",
            "Underground hacker dens",
            "Virtual private networks",
            "Cryptocurrency mining operations",
            "Dark web marketplaces",
            "Secure data centers"
        ],
        "allies": [
            "Other hacker collectives",
            "Rogue state sponsors",
            "Criminal organizations",
            "Whistleblower networks",
            "Anonymous activists",
            "Corrupt insiders"
        ],
        "enemies": [
            "Cyber security agencies",
            "Law enforcement cyber units",
            "Corporate security teams",
            "Government cyber commands",
            "International cyber coalitions",
            "Rival hacker groups"
        ]
    }
}

# Thriller-specific titles and roles
THRILLER_LEADER_TITLES = [
    "Director", "Chief", "Commander", "General", "Admiral", "Secretary", "Chairman", "President",
    "CEO", "Executive", "Supervisor", "Administrator", "Coordinator", "Manager"
]

THRILLER_MILITARY_TITLES = [
    "Colonel", "Major", "Captain", "Lieutenant", "Sergeant", "Operative", "Agent", "Specialist",
    "Commander", "Officer", "Enforcer", "Assassin", "Sniper", "Demolitions Expert"
]

THRILLER_ADMINISTRATIVE_TITLES = [
    "Deputy Director", "Assistant Director", "Chief of Staff", "Operations Manager", "Intelligence Analyst",
    "Communications Officer", "Logistics Coordinator", "Security Chief", "Legal Counsel", "Financial Officer"
]

THRILLER_SPECIALIZED_TITLES = [
    "Cyber Warfare Specialist", "Psychological Operations Expert", "Weapons Specialist", "Surveillance Expert",
    "Interrogation Specialist", "Explosives Expert", "Communications Specialist", "Medical Officer", "Pilot", "Driver"
]

THRILLER_OPERATIONAL_TITLES = [
    "Field Agent", "Operative", "Contractor", "Mercenary", "Hacker", "Analyst", "Technician", "Guard",
    "Courier", "Handler", "Asset", "Informant", "Surveillance Operator", "Communications Operator"
]

# Thriller adjectives for descriptions
THRILLER_ADJECTIVES = [
    "shadowy", "secretive", "ruthless", "elite", "covert", "dangerous", "powerful", "mysterious",
    "sophisticated", "deadly", "efficient", "relentless", "cunning", "notorious", "classified"
]

def generate_thriller_name(gender=None):
    """Generate a Thriller character name."""
    if gender is None:
        gender = random.choice(["male", "female"])
    
    first_name = random.choice(THRILLER_FIRST_NAMES[gender.lower()])
    last_name = random.choice(THRILLER_SURNAMES)
    
    return first_name, last_name

def generate_organization_name():
    """Generate a thriller organization name."""
    prefix = random.choice(THRILLER_ORG_PREFIXES)
    suffix = random.choice(THRILLER_ORG_SUFFIXES)
    return f"{prefix} {suffix}"

def generate_headquarters_name():
    """Generate a headquarters location name."""
    if random.choice([True, False]):
        # Use existing location
        return random.choice(THRILLER_LOCATION_NAMES)
    else:
        # Generate new location
        prefix = random.choice(THRILLER_LOCATION_PREFIXES)
        name = random.choice(THRILLER_LOCATION_NAMES)
        return f"{prefix} {name}"

def generate_faction_name(faction_type):
    """Generate a name for a Thriller faction based on its type."""
    faction_template = THRILLER_FACTION_TYPES[faction_type]
    headquarters = generate_headquarters_name()
    
    if faction_type == "Intelligence Agency":
        agency_name = generate_organization_name()
        classification = random.choice(faction_template["classifications"])
        return agency_name, {
            "agency_name": agency_name,
            "classification": classification,
            "headquarters": headquarters
        }
    
    elif faction_type == "Criminal Syndicate":
        syndicate_name = random.choice(faction_template["syndicate_names"])
        criminal_type = random.choice(faction_template["criminal_types"])
        return syndicate_name, {
            "syndicate_name": syndicate_name,
            "criminal_type": criminal_type,
            "headquarters": headquarters
        }
    
    elif faction_type == "Terrorist Organization":
        terrorist_name = random.choice(faction_template["terrorist_names"])
        ideology = random.choice(faction_template["ideologies"])
        return terrorist_name, {
            "terrorist_name": terrorist_name,
            "ideology": ideology,
            "headquarters": headquarters
        }
    
    elif faction_type == "Mega Corporation":
        corporation_name = random.choice(faction_template["corporation_names"])
        corporate_type = random.choice(faction_template["corporate_types"])
        return corporation_name, {
            "corporation_name": corporation_name,
            "corporate_type": corporate_type,
            "headquarters": headquarters
        }
    
    elif faction_type == "Military Contractor":
        contractor_name = random.choice(faction_template["contractor_names"])
        contractor_type = random.choice(faction_template["contractor_types"])
        return contractor_name, {
            "contractor_name": contractor_name,
            "contractor_type": contractor_type,
            "headquarters": headquarters
        }
    
    elif faction_type == "Cyber Warfare Group":
        hacker_name = random.choice(faction_template["hacker_names"])
        hacker_type = random.choice(faction_template["hacker_types"])
        return hacker_name, {
            "hacker_name": hacker_name,
            "hacker_type": hacker_type,
            "headquarters": headquarters
        }
    
    return f"Unknown {faction_type}", {"headquarters": headquarters}

def _generate_named_character(title_list, role, specific_title=None, female_percentage=50, male_percentage=50):
    """Generate a Thriller character with name, title, and role, using gender bias."""
    # Validate and calculate gender weights
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"THRILLER_GEN/_generate_named_character: Invalid gender percentages (F:{female_percentage}%, M:{male_percentage}%). Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0

    gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
    
    first_name, last_name = generate_thriller_name(gender)
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

def generate_thriller_assets(faction_type):
    """Generate assets for a Thriller faction."""
    assets = {}
    
    if faction_type == "Intelligence Agency":
        assets = {
            "personnel": {
                "field_agents": random.randint(50, 200),
                "analysts": random.randint(100, 500),
                "support_staff": random.randint(200, 1000),
                "contractors": random.randint(20, 100)
            },
            "technology": {
                "surveillance_systems": random.randint(10, 50),
                "communication_networks": random.randint(5, 20),
                "cyber_warfare_tools": random.randint(3, 15),
                "satellite_access": random.randint(1, 5)
            },
            "facilities": {
                "safe_houses": random.randint(10, 50),
                "training_facilities": random.randint(2, 8),
                "data_centers": random.randint(3, 12),
                "black_sites": random.randint(1, 5)
            }
        }
    
    elif faction_type == "Criminal Syndicate":
        assets = {
            "personnel": {
                "enforcers": random.randint(20, 100),
                "lieutenants": random.randint(5, 25),
                "associates": random.randint(50, 300),
                "corrupt_officials": random.randint(3, 20)
            },
            "operations": {
                "drug_labs": random.randint(2, 15),
                "money_laundering_fronts": random.randint(5, 30),
                "smuggling_routes": random.randint(3, 20),
                "weapons_caches": random.randint(5, 25)
            },
            "territory": {
                "controlled_areas": random.randint(2, 10),
                "safe_houses": random.randint(5, 30),
                "legitimate_businesses": random.randint(10, 50)
            }
        }
    
    elif faction_type == "Terrorist Organization":
        assets = {
            "personnel": {
                "active_members": random.randint(20, 200),
                "sleeper_agents": random.randint(5, 50),
                "sympathizers": random.randint(100, 1000),
                "suicide_bombers": random.randint(2, 20)
            },
            "weapons": {
                "explosive_devices": random.randint(10, 100),
                "small_arms": random.randint(50, 500),
                "heavy_weapons": random.randint(2, 20),
                "chemical_weapons": random.randint(0, 5)
            },
            "infrastructure": {
                "training_camps": random.randint(1, 8),
                "safe_houses": random.randint(5, 30),
                "weapons_caches": random.randint(3, 20),
                "communication_networks": random.randint(2, 10)
            }
        }
    
    elif faction_type == "Mega Corporation":
        assets = {
            "financial": {
                "annual_revenue_billions": random.randint(10, 500),
                "liquid_assets_billions": random.randint(1, 50),
                "market_cap_billions": random.randint(20, 1000),
                "r_and_d_budget_billions": random.randint(1, 20)
            },
            "personnel": {
                "employees_worldwide": random.randint(10000, 500000),
                "executives": random.randint(50, 500),
                "security_personnel": random.randint(100, 2000),
                "researchers": random.randint(500, 10000)
            },
            "facilities": {
                "headquarters": 1,
                "regional_offices": random.randint(10, 100),
                "manufacturing_plants": random.randint(5, 50),
                "research_facilities": random.randint(3, 20)
            }
        }
    
    elif faction_type == "Military Contractor":
        assets = {
            "personnel": {
                "operators": random.randint(100, 1000),
                "support_staff": random.randint(50, 500),
                "trainers": random.randint(20, 100),
                "pilots": random.randint(10, 50)
            },
            "equipment": {
                "small_arms": random.randint(500, 5000),
                "vehicles": random.randint(20, 200),
                "aircraft": random.randint(2, 20),
                "communication_systems": random.randint(10, 100)
            },
            "contracts": {
                "active_contracts": random.randint(5, 50),
                "government_clients": random.randint(2, 20),
                "corporate_clients": random.randint(3, 30),
                "annual_revenue_millions": random.randint(50, 2000)
            }
        }
    
    elif faction_type == "Cyber Warfare Group":
        assets = {
            "personnel": {
                "hackers": random.randint(10, 100),
                "analysts": random.randint(5, 50),
                "social_engineers": random.randint(3, 30),
                "insiders": random.randint(1, 20)
            },
            "technology": {
                "botnets": random.randint(5, 50),
                "zero_day_exploits": random.randint(2, 20),
                "malware_variants": random.randint(10, 100),
                "cryptocurrency_wallets": random.randint(3, 30)
            },
            "operations": {
                "active_campaigns": random.randint(2, 20),
                "compromised_systems": random.randint(100, 10000),
                "data_breaches": random.randint(5, 100),
                "ransomware_attacks": random.randint(3, 50)
            }
        }
    
    return assets

def generate_thriller_factions(num_factions=6):
    """Generate a set of Thriller factions with detailed information."""
    faction_types = list(THRILLER_FACTION_TYPES.keys())
    
    # Ensure we have enough faction types
    if num_factions > len(faction_types):
        faction_types = faction_types * ((num_factions // len(faction_types)) + 1)
    
    # Randomly select faction types
    selected_types = random.sample(faction_types, num_factions)
    
    factions = []
    
    for faction_type in selected_types:
        faction_name, name_components = generate_faction_name(faction_type)
        faction_template = THRILLER_FACTION_TYPES[faction_type]
        
        # Generate description
        description_template = random.choice(faction_template["description_templates"])
        adjective = random.choice(THRILLER_ADJECTIVES)
        
        # Fill in the template with generated components
        description = description_template.format(
            adjective=adjective,
            **name_components
        )
        
        # Generate faction personnel
        personnel = []
        
        # Leader
        personnel.append(_generate_named_character(
            THRILLER_LEADER_TITLES, 
            "Faction Leader"
        ))
        
        # Military/Operations leader
        personnel.append(_generate_named_character(
            THRILLER_MILITARY_TITLES, 
            "Operations Leader"
        ))
        
        # Administrative staff
        for _ in range(random.randint(2, 4)):
            personnel.append(_generate_named_character(
                THRILLER_ADMINISTRATIVE_TITLES, 
                "Administrative Staff"
            ))
        
        # Specialized personnel
        for _ in range(random.randint(2, 4)):
            personnel.append(_generate_named_character(
                THRILLER_SPECIALIZED_TITLES, 
                "Specialist"
            ))
        
        # Operational personnel
        for _ in range(random.randint(4, 8)):
            personnel.append(_generate_named_character(
                THRILLER_OPERATIONAL_TITLES, 
                "Operational Staff"
            ))
        
        # Generate assets
        assets = generate_thriller_assets(faction_type)
        
        faction = {
            "faction_name": faction_name,
            "faction_type": faction_type,
            "description": description,
            "goals": random.sample(faction_template["goals"], min(4, len(faction_template["goals"]))),
            "resources": random.sample(faction_template["resources"], min(5, len(faction_template["resources"]))),
            "territories": random.sample(faction_template["territories"], min(4, len(faction_template["territories"]))),
            "allies": random.sample(faction_template["allies"], min(3, len(faction_template["allies"]))),
            "enemies": random.sample(faction_template["enemies"], min(3, len(faction_template["enemies"]))),
            "power_level": random.randint(4, 9),
            "influence_radius": random.choice(["Regional", "National", "International", "Global"]),
            "characters": personnel,
            "assets": assets,
            "threat_level": random.choice(["Low", "Medium", "High", "Critical", "Extreme"]),
            "classification": random.choice(["Unclassified", "Confidential", "Secret", "Top Secret", "Compartmentalized"])
        }
        
        factions.append(faction)
    
    return factions

def generate_faction_relationships(factions):
    """Generate relationships between Thriller factions."""
    relationships = []
    
    relationship_types = [
        "Allied", "Hostile", "Neutral", "Competing", "Rivals", "Suspicious",
        "Cooperative", "Adversarial", "Infiltrated", "Under Surveillance"
    ]
    
    for i, faction1 in enumerate(factions):
        for faction2 in factions[i+1:]:
            # Determine relationship based on faction types
            relationship_type = random.choice(relationship_types)
            
            # Adjust probability based on faction types
            if faction1["faction_type"] == "Intelligence Agency" and faction2["faction_type"] == "Terrorist Organization":
                relationship_type = random.choice(["Hostile", "Under Surveillance", "Adversarial"])
            elif faction1["faction_type"] == "Criminal Syndicate" and faction2["faction_type"] == "Intelligence Agency":
                relationship_type = random.choice(["Hostile", "Under Surveillance", "Infiltrated"])
            elif faction1["faction_type"] == "Mega Corporation" and faction2["faction_type"] == "Military Contractor":
                relationship_type = random.choice(["Allied", "Cooperative", "Competing"])
            elif faction1["faction_type"] == "Cyber Warfare Group" and faction2["faction_type"] == "Intelligence Agency":
                relationship_type = random.choice(["Hostile", "Adversarial", "Under Surveillance"])
            
            relationship = {
                "faction1": faction1["faction_name"],
                "faction2": faction2["faction_name"],
                "relationship_type": relationship_type,
                "description": f"The {faction1['faction_name']} and {faction2['faction_name']} maintain {relationship_type.lower()} relations."
            }
            
            relationships.append(relationship)
    
    return relationships

def save_thriller_factions_to_file(factions, filename=None, timestamp=False):
    """Save Thriller factions to a JSON file."""
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"thriller_factions_{timestamp_str}.json"
        else:
            filename = "thriller_factions.json"
    
    relationships = generate_faction_relationships(factions)
    
    data = {
        "factions": factions,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_factions": len(factions),
            "genre": "Thriller"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename

def load_thriller_factions_from_file(filename="thriller_factions.json"):
    """Load Thriller factions from a JSON file."""
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

def print_thriller_factions(factions):
    """Print detailed information about the generated Thriller factions."""
    for faction in factions:
        print(f"\n=== {faction['faction_name']} ===")
        print(f"Type: {faction['faction_type']}")
        print(f"Classification: {faction['classification']}")
        print(f"Threat Level: {faction['threat_level']}")
        print(f"Description: {faction['description']}")
        print(f"Power Level: {faction['power_level']}/10")
        print(f"Influence: {faction['influence_radius']}")
        
        print(f"\nGoals: {', '.join(faction['goals'])}")
        print(f"Resources: {', '.join(faction['resources'])}")
        print(f"Allies: {', '.join(faction['allies'])}")
        print(f"Enemies: {', '.join(faction['enemies'])}")
        
        print("\nAssets:")
        for category, assets in faction["assets"].items():
            print(f"  {category.title()}:")
            for asset_type, count in assets.items():
                if isinstance(count, int):
                    print(f"    {asset_type.replace('_', ' ').title()}: {count:,}")
                else:
                    print(f"    {asset_type.replace('_', ' ').title()}: {count}")
        
        print("\nKey Personnel:")
        for character in faction["characters"]:
            print(f"  - {character['display_name']} ({character['role']})")

def test_thriller_faction_generation():
    """Test function to generate and display Thriller factions."""
    print("Generating Thriller Factions...")
    factions = generate_thriller_factions(6)
    
    print_thriller_factions(factions)
    
    # Save to file
    filename = save_thriller_factions_to_file(factions, timestamp=True)
    print(f"\nFactions saved to {filename}")

if __name__ == "__main__":
    test_thriller_faction_generation() 