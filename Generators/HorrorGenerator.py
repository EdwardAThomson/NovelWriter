import json
import random
import os
from datetime import datetime

# --- Horror Name Generation System ---

# Horror character names (mix of classic and modern)
HORROR_FIRST_NAMES = {
    "male": [
        "Adrian", "Bartholomew", "Cornelius", "Damien", "Edgar", "Frederick", "Gabriel", "Horatio", "Ichabod", "Jasper",
        "Klaus", "Lucian", "Mortimer", "Nathaniel", "Obadiah", "Percival", "Quentin", "Roderick", "Sebastian", "Theodore",
        "Vincent", "Wilfred", "Xavier", "Yorick", "Zacharias", "Ambrose", "Benedict", "Cassius", "Dorian", "Edmund",
        "Felix", "Gideon", "Hector", "Ivan", "Julius", "Kieran", "Leopold", "Magnus", "Nigel", "Oswald",
        "Phineas", "Quincy", "Raphael", "Silas", "Tobias", "Ulysses", "Victor", "Winston", "Alexander", "Benjamin"
    ],
    "female": [
        "Agatha", "Beatrice", "Cordelia", "Delphine", "Evangeline", "Felicity", "Genevieve", "Helena", "Isadora", "Josephine",
        "Katherine", "Lillian", "Morgana", "Natasha", "Ophelia", "Penelope", "Quintessa", "Rosalind", "Seraphina", "Tabitha",
        "Ursula", "Vivienne", "Wilhelmina", "Ximena", "Yvette", "Zelda", "Anastasia", "Belladonna", "Cassandra", "Drusilla",
        "Esmeralda", "Francesca", "Gwendolyn", "Hermione", "Imogen", "Jacqueline", "Katarina", "Lucinda", "Miranda", "Nicolette",
        "Octavia", "Persephone", "Raven", "Sabrina", "Theodora", "Valentina", "Winifred", "Xara", "Yasmin", "Zara"
    ]
}

HORROR_SURNAMES = [
    "Blackwood", "Ravencroft", "Thornfield", "Grimm", "Darkmore", "Shadowmere", "Bloodworth", "Nightshade", "Ashford", "Bane",
    "Crowley", "Dracul", "Evernight", "Faust", "Graves", "Hollow", "Ironwood", "Jekyll", "Karnstein", "Lovecraft",
    "Moreau", "Nosferatu", "Orlok", "Poe", "Quatermass", "Renfield", "Stoker", "Thorne", "Usher", "Van Helsing",
    "Whitmore", "Xander", "York", "Zorn", "Addams", "Bathory", "Carmilla", "Dracula", "Frankenstein", "Gothic",
    "Hawthorne", "Irving", "Karloff", "Lugosi", "Murnau", "Nosferatu", "Price", "Rathbone", "Shelley", "Whale"
]

# Organization name components for horror cults and groups
HORROR_ORG_PREFIXES = [
    "Order of", "Cult of", "Brotherhood of", "Sisterhood of", "Circle of", "Covenant of", "Society of", "Temple of",
    "Church of", "Disciples of", "Children of", "Servants of", "Followers of", "Worshippers of", "Devotees of", "Acolytes of"
]

HORROR_ORG_SUFFIXES = [
    "the Crimson Moon", "the Black Sun", "the Void", "the Abyss", "Eternal Darkness", "the Damned", "the Forsaken",
    "the Ancient Ones", "the Old Gods", "the Nameless", "the Whispering Shadows", "the Blood Covenant", "the Dark Arts",
    "the Forbidden Knowledge", "the Unholy Trinity", "the Seven Seals", "the Thirteenth Hour", "the Final Revelation",
    "the Bleeding Crown", "the Shattered Mirror", "the Weeping Angels", "the Screaming Silence", "the Living Dead",
    "the Eternal Torment", "the Infinite Nightmare", "the Crawling Chaos", "the Devouring Dark", "the Consuming Fire"
]

# Location name components for horror strongholds
HORROR_LOCATION_PREFIXES = [
    "Asylum", "Monastery", "Mansion", "Manor", "Castle", "Cathedral", "Chapel", "Crypt", "Mausoleum", "Sanitarium",
    "Institute", "Academy", "Seminary", "Convent", "Abbey", "Priory", "Fortress", "Tower", "Keep", "Citadel"
]

HORROR_LOCATION_NAMES = [
    "Ravenshollow", "Blackmoor", "Grimhaven", "Shadowvale", "Thornwick", "Darkwood", "Nightfall", "Bloodmere",
    "Ashcroft", "Irongate", "Stoneheart", "Crowsrest", "Wolfsbane", "Mistmoor", "Gloomheath", "Dreadmoor",
    "Cursed Hollow", "Whispering Pines", "Silent Hill", "Devil's Backbone", "Witch's Hollow", "Phantom Ridge",
    "Spectral Valley", "Haunted Moor", "Forsaken Glen", "Damned Crossing", "Lost Souls", "Eternal Rest"
]

# Horror faction types with detailed characteristics
HORROR_FACTION_TYPES = {
    "Occult Cult": {
        "description_templates": [
            "The {adjective} {cult_name}, a {devotion_type} cult operating from {stronghold}",
            "A {adjective} occult organization, the {cult_name}, whose {devotion_type} rituals are conducted in {stronghold}",
            "The {adjective} {cult_name}, whose {devotion_type} worship centers around their stronghold at {stronghold}"
        ],
        "devotion_types": ["fanatical", "secretive", "ancient", "forbidden", "blasphemous", "unholy"],
        "goals": [
            "Summon ancient entities from beyond",
            "Perform dark rituals and sacrifices",
            "Spread their unholy influence",
            "Collect forbidden knowledge and artifacts",
            "Convert new followers to their cause",
            "Prepare for the coming apocalypse",
            "Commune with otherworldly beings",
            "Unlock the secrets of immortality"
        ],
        "resources": [
            "Ancient tomes and grimoires",
            "Ritual implements and artifacts",
            "Devoted followers and acolytes",
            "Hidden sanctuaries and temples",
            "Supernatural allies and entities",
            "Occult knowledge and secrets",
            "Ceremonial weapons and tools",
            "Blood and sacrifice offerings"
        ],
        "territories": [
            "Hidden underground temples",
            "Abandoned churches and cathedrals",
            "Remote forest clearings",
            "Ancient burial grounds",
            "Forgotten catacombs",
            "Isolated mansions and estates",
            "Sacred groves and stone circles"
        ],
        "allies": [
            "Other occult organizations",
            "Supernatural entities",
            "Corrupt scholars and academics",
            "Desperate individuals seeking power",
            "Ancient bloodline families",
            "Practitioners of dark arts"
        ],
        "enemies": [
            "Religious authorities",
            "Paranormal investigators",
            "Law enforcement agencies",
            "Rival occult groups",
            "Monster hunters",
            "Skeptical scientists"
        ]
    },
    "Secret Society": {
        "description_templates": [
            "The {adjective} {society_name}, a {secrecy_type} secret society operating from {stronghold}",
            "A {adjective} clandestine organization, the {society_name}, whose {secrecy_type} agenda is pursued from {stronghold}",
            "The {adjective} {society_name}, whose {secrecy_type} influence extends from their base at {stronghold}"
        ],
        "society_names": ["Illuminated Order", "Shadow Council", "Crimson Lodge", "Obsidian Circle", "Midnight Society", "Veiled Brotherhood"],
        "secrecy_types": ["ancient", "powerful", "mysterious", "influential", "shadowy", "elite"],
        "goals": [
            "Control world events from the shadows",
            "Preserve ancient and dangerous knowledge",
            "Manipulate governments and institutions",
            "Protect humanity from supernatural threats",
            "Maintain the balance between worlds",
            "Eliminate threats to their secrecy",
            "Recruit influential members",
            "Guard forbidden technologies"
        ],
        "resources": [
            "Vast financial resources",
            "Political and social connections",
            "Advanced surveillance networks",
            "Private security forces",
            "Ancient libraries and archives",
            "Cutting-edge technology",
            "Safe houses and meeting places",
            "Loyal agents and operatives"
        ],
        "territories": [
            "Exclusive private clubs",
            "Hidden meeting chambers",
            "Secure underground facilities",
            "Private estates and compounds",
            "Corporate headquarters",
            "University secret societies",
            "Government black sites"
        ],
        "allies": [
            "Government officials",
            "Corporate executives",
            "Academic institutions",
            "Military leaders",
            "Intelligence agencies",
            "Other secret societies"
        ],
        "enemies": [
            "Investigative journalists",
            "Conspiracy theorists",
            "Rival secret organizations",
            "Supernatural entities",
            "Whistleblowers",
            "Reform movements"
        ]
    },
    "Monster Hunters": {
        "description_templates": [
            "The {adjective} {hunter_name}, a {dedication_type} monster hunting organization based at {stronghold}",
            "A {adjective} group of hunters, the {hunter_name}, whose {dedication_type} mission operates from {stronghold}",
            "The {adjective} {hunter_name}, whose {dedication_type} crusade against darkness is coordinated from {stronghold}"
        ],
        "hunter_names": ["Van Helsing Institute", "Order of the Silver Cross", "Midnight Vigil", "Sacred Hunt", "Divine Retribution"],
        "dedication_types": ["relentless", "sacred", "ancient", "sworn", "righteous", "fearless"],
        "goals": [
            "Hunt and destroy supernatural monsters",
            "Protect innocent civilians",
            "Research monster weaknesses",
            "Train new generations of hunters",
            "Maintain ancient hunting traditions",
            "Prevent supernatural outbreaks",
            "Collect monster artifacts",
            "Preserve humanity's safety"
        ],
        "resources": [
            "Blessed and silver weapons",
            "Monster hunting equipment",
            "Trained combat specialists",
            "Research libraries and databases",
            "Safe houses and armories",
            "Religious backing and support",
            "Ancient hunting knowledge",
            "Protective charms and wards"
        ],
        "territories": [
            "Fortified hunting lodges",
            "Training compounds",
            "Weapon storage facilities",
            "Research laboratories",
            "Safe houses for civilians",
            "Monster containment sites",
            "Religious sanctuaries"
        ],
        "allies": [
            "Religious organizations",
            "Law enforcement contacts",
            "Paranormal researchers",
            "Other hunter groups",
            "Government black ops",
            "Supernatural allies"
        ],
        "enemies": [
            "Vampires and werewolves",
            "Demonic entities",
            "Occult cults",
            "Supernatural creatures",
            "Monster sympathizers",
            "Corrupt officials"
        ]
    }
}

# Adjectives for horror factions
HORROR_ADJECTIVES = [
    "ancient", "forbidden", "cursed", "damned", "unholy", "blasphemous", "sinister", "malevolent",
    "shadowy", "mysterious", "secretive", "hidden", "dark", "twisted", "corrupt", "evil",
    "supernatural", "otherworldly", "eldritch", "arcane", "occult", "mystical", "ethereal", "spectral"
]

# Horror faction leadership titles
HORROR_LEADER_TITLES = {
    "Occult Cult": [
        "High Priest", "High Priestess", "Dark Prophet", "Cult Leader", "Grand Hierophant",
        "Master of Ceremonies", "Supreme Acolyte", "Dark Oracle", "Unholy Shepherd", "Void Speaker"
    ],
    "Secret Society": [
        "Grand Master", "Shadow Director", "Council Chair", "Supreme Overseer", "Hidden Hand",
        "Master of Secrets", "Prime Conspirator", "Shadow Sovereign", "Veiled Leader", "Dark Chancellor"
    ],
    "Monster Hunters": [
        "Master Hunter", "Grand Inquisitor", "Order Leader", "Chief Slayer", "Supreme Guardian",
        "Elder Hunter", "Monster Bane", "Sacred Protector", "Divine Champion", "Beast Master"
    ]
}

HORROR_MILITARY_TITLES = {
    "Occult Cult": [
        "War Priest", "Battle Acolyte", "Dark Crusader", "Unholy Warrior", "Ritual Guardian",
        "Blood Champion", "Shadow Enforcer", "Cult Protector", "Dark Sentinel", "Void Soldier"
    ],
    "Secret Society": [
        "Operations Director", "Shadow Commander", "Security Chief", "Enforcement Leader", "Black Ops Director",
        "Covert Operations Head", "Silent Blade", "Hidden Fist", "Shadow Strike Leader", "Dark Operative"
    ],
    "Monster Hunters": [
        "Hunt Master", "Battle Leader", "Strike Commander", "Field Marshal", "Combat Veteran",
        "Slayer Captain", "Guardian Commander", "Holy Warrior", "Monster Slayer", "Sacred Soldier"
    ]
}

HORROR_ADMINISTRATIVE_TITLES = {
    "Occult Cult": [
        "Keeper of Secrets", "Ritual Coordinator", "Dark Scribe", "Unholy Archivist", "Cult Administrator",
        "Sacred Keeper", "Tome Guardian", "Knowledge Keeper", "Dark Librarian", "Void Chronicler"
    ],
    "Secret Society": [
        "Intelligence Coordinator", "Information Broker", "Network Administrator", "Resource Manager", "Strategic Planner",
        "Shadow Coordinator", "Hidden Assets Manager", "Covert Administrator", "Silent Coordinator", "Dark Facilitator"
    ],
    "Monster Hunters": [
        "Research Coordinator", "Lore Keeper", "Equipment Master", "Training Director", "Archive Guardian",
        "Knowledge Keeper", "Weapon Master", "Sacred Librarian", "Hunt Coordinator", "Order Administrator"
    ]
}

HORROR_SPECIALIZED_TITLES = {
    "Occult Cult": [
        "Summoner", "Blood Ritualist", "Dark Seer", "Necromancer", "Demon Binder",
        "Soul Harvester", "Curse Weaver", "Shadow Walker", "Void Touched", "Dark Medium"
    ],
    "Secret Society": [
        "Master Manipulator", "Information Specialist", "Infiltration Expert", "Psychological Operative", "Social Engineer",
        "Mind Controller", "Influence Peddler", "Shadow Agent", "Covert Specialist", "Hidden Influencer"
    ],
    "Monster Hunters": [
        "Monster Expert", "Supernatural Researcher", "Blessed Warrior", "Exorcist", "Divine Scholar",
        "Beast Tracker", "Holy Investigator", "Supernatural Detective", "Sacred Researcher", "Monster Lore Master"
    ]
}

def generate_horror_name(gender=None):
    """Generate a horror-appropriate character name."""
    if gender is None:
        gender = random.choice(["male", "female"])
    
    first_name = random.choice(HORROR_FIRST_NAMES[gender])
    surname = random.choice(HORROR_SURNAMES)
    
    return f"{first_name} {surname}", gender

def generate_cult_name():
    """Generate a horror cult/organization name."""
    prefix = random.choice(HORROR_ORG_PREFIXES)
    suffix = random.choice(HORROR_ORG_SUFFIXES)
    return f"{prefix} {suffix}"

def generate_stronghold_name():
    """Generate a horror stronghold/location name."""
    prefix = random.choice(HORROR_LOCATION_PREFIXES)
    name = random.choice(HORROR_LOCATION_NAMES)
    return f"{prefix} {name}"

def generate_faction_name(faction_type):
    """Generate a faction name based on type."""
    name_components = {}
    
    if faction_type == "Occult Cult":
        cult_name = generate_cult_name()
        stronghold = generate_stronghold_name()
        name_components = {
            "cult_name": cult_name,
            "stronghold": stronghold
        }
        return cult_name, name_components
    elif faction_type == "Secret Society":
        society_name = random.choice(HORROR_FACTION_TYPES[faction_type]["society_names"])
        stronghold = generate_stronghold_name()
        name_components = {
            "society_name": society_name,
            "stronghold": stronghold
        }
        return society_name, name_components
    elif faction_type == "Monster Hunters":
        hunter_name = random.choice(HORROR_FACTION_TYPES[faction_type]["hunter_names"])
        stronghold = generate_stronghold_name()
        name_components = {
            "hunter_name": hunter_name,
            "stronghold": stronghold
        }
        return hunter_name, name_components
    else:
        # Fallback
        return generate_cult_name(), {"stronghold": generate_stronghold_name()}

def generate_horror_factions(num_factions=3, female_percentage=50, male_percentage=50):
    """Generate a set of Horror factions with detailed information."""
    faction_types = list(HORROR_FACTION_TYPES.keys())
    
    # Ensure we have enough faction types
    if num_factions > len(faction_types):
        faction_types = faction_types * ((num_factions // len(faction_types)) + 1)
    
    # Randomly select faction types
    selected_types = random.sample(faction_types, num_factions)
    
    factions = []
    
    for faction_type in selected_types:
        faction_name, name_components = generate_faction_name(faction_type)
        faction_template = HORROR_FACTION_TYPES[faction_type]
        
        # Generate description
        description_template = random.choice(faction_template["description_templates"])
        adjective = random.choice(HORROR_ADJECTIVES)
        
        # Get the appropriate type key for the template
        if faction_type == "Occult Cult":
            type_key = "devotion_type"
            type_value = random.choice(faction_template["devotion_types"])
        elif faction_type == "Secret Society":
            type_key = "secrecy_type"
            type_value = random.choice(faction_template["secrecy_types"])
        elif faction_type == "Monster Hunters":
            type_key = "dedication_type"
            type_value = random.choice(faction_template["dedication_types"])
        else:
            type_key = "type"
            type_value = "mysterious"
        
        # Fill in the template with generated components
        description = description_template.format(
            adjective=adjective,
            **{type_key: type_value},
            **name_components
        )
        
        # Generate faction personnel
        personnel = []
        
        # 1. Faction Leader
        leader_titles = HORROR_LEADER_TITLES.get(faction_type, HORROR_LEADER_TITLES["Occult Cult"])
        personnel.append(_generate_named_character(
            leader_titles, 
            "Faction Leader", 
            faction_type,
            female_percentage=female_percentage, 
            male_percentage=male_percentage
        ))
        
        # 2. Military/Operations Leader
        military_titles = HORROR_MILITARY_TITLES.get(faction_type, HORROR_MILITARY_TITLES["Occult Cult"])
        personnel.append(_generate_named_character(
            military_titles, 
            "Operations Leader", 
            faction_type,
            female_percentage=female_percentage, 
            male_percentage=male_percentage
        ))
        
        # 3. Administrative Staff (1-3 people)
        admin_titles = HORROR_ADMINISTRATIVE_TITLES.get(faction_type, HORROR_ADMINISTRATIVE_TITLES["Occult Cult"])
        for _ in range(random.randint(1, 3)):
            personnel.append(_generate_named_character(
                admin_titles, 
                "Administrative Staff", 
                faction_type,
                female_percentage=female_percentage, 
                male_percentage=male_percentage
            ))
        
        # 4. Specialized Personnel (1-2 people)
        specialized_titles = HORROR_SPECIALIZED_TITLES.get(faction_type, HORROR_SPECIALIZED_TITLES["Occult Cult"])
        for _ in range(random.randint(1, 2)):
            personnel.append(_generate_named_character(
                specialized_titles, 
                "Specialist", 
                faction_type,
                female_percentage=female_percentage, 
                male_percentage=male_percentage
            ))
        
        faction = {
            "faction_name": faction_name,
            "faction_type": faction_type,
            "description": description,
            "goals": random.sample(faction_template["goals"], min(4, len(faction_template["goals"]))),
            "resources": random.sample(faction_template["resources"], min(5, len(faction_template["resources"]))),
            "territories": random.sample(faction_template["territories"], min(4, len(faction_template["territories"]))),
            "allies": random.sample(faction_template["allies"], min(3, len(faction_template["allies"]))),
            "enemies": random.sample(faction_template["enemies"], min(3, len(faction_template["enemies"]))),
            "characters": personnel,  # Add the generated personnel
            "power_level": random.randint(3, 8),
            "influence_radius": random.choice(["Local", "Regional", "National", "International"]),
            "threat_level": random.choice(["Low", "Medium", "High", "Extreme", "Apocalyptic"]),
            "secrecy_level": random.choice(["Public", "Semi-Secret", "Secret", "Ultra-Secret", "Unknown"])
        }
        
        factions.append(faction)
    
    return factions

def save_horror_factions_to_file(factions, filename=None, timestamp=False):
    """Save Horror factions to a JSON file."""
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"horror_factions_{timestamp_str}.json"
        else:
            filename = "horror_factions.json"
    
    data = {
        "factions": factions,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_factions": len(factions),
            "genre": "Horror"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename

def test_horror_faction_generation():
    """Test function to generate and display Horror factions."""
    print("Generating Horror Factions...")
    factions = generate_horror_factions(3)
    
    for faction in factions:
        print(f"\n=== {faction['faction_name']} ===")
        print(f"Type: {faction['faction_type']}")
        print(f"Description: {faction['description']}")
        print(f"Power Level: {faction['power_level']}/10")
        print(f"Threat Level: {faction['threat_level']}")
        print(f"Secrecy Level: {faction['secrecy_level']}")
        print(f"Goals: {', '.join(faction['goals'])}")
    
    # Save to file
    filename = save_horror_factions_to_file(factions, timestamp=True)
    print(f"\nFactions saved to {filename}")

def _generate_named_character(title_list, role, faction_type="Unknown", female_percentage=50, male_percentage=50):
    """Generate a named character with title and role for horror factions."""
    # Determine gender based on percentages
    if random.randint(1, 100) <= female_percentage:
        gender = "female"
    else:
        gender = "male"
    
    # Generate name
    name, _ = generate_horror_name(gender)
    
    # Select title
    title = random.choice(title_list)
    
    return {
        "name": name,
        "gender": gender,
        "title": title,
        "role": role,
        "faction_type": faction_type,
        "display_name": f"{title} {name}",
        "full_name": name
    }

if __name__ == "__main__":
    test_horror_faction_generation() 