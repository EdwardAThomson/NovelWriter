import json
import random
import os
from datetime import datetime
import re

# --- Name fragments for Factions, Planets, Characters ---
FACTION_PREFIXES = [
    "Zora", "Val", "Tar", "Xeno", "Vela", "Kora", "Syla", "Mar", "Nova", "Rila",
    "Vex", "Thera", "Kalos", "Xer", "Sero", "Jyn", "Brev", "Crom", "Drak", "Elgo",
    "Fane", "Gral", "Hesk", "Ilum", "Karth", "Lyra", "Myr", "Nym", "Ordo", "Pryx",
    "Quell", "Rax", "Skarn", "Tyro", "Uth", "Vorn", "Wren", "Yss", "Zyl", "Axos",
    "Bryll", "Cthon", "Durn", "Hyth", "Ixor", "Jaxx", "Krell"
]
FACTION_MIDDLES = [
    "th", "o", "en", "av", "il", "ex", "ar", "end", "onis", "in", "a", "um", "el", "ir", "az",
    "ec", "yr", "oa", "iss", "eth", "orb", "ask", "ull", "emn", "ypt", "org", "osp", "ix", "ath", "yth"
]
FACTION_SUFFIXES = [
    "Prime", "dor", "zar", "ion", "us", "an", "ox", "ane", "on", "is", "o", "ia", "gard", "ium", "eth",
    "ica", "atis", "orim", "dyn"
]

PLANET_PREFIXES = [
    "Ar", "Xy", "Ko", "Ze", "Vi", "Gha", "Ri", "Mol", "Tar", "Ik", "Ul", "Ba", "Cy", "De", "El",
    "Fy", "Ho", "Ja", "Ke", "La", "Me", "Ni", "Ob", "Pa", "Qu", "Ra", "Si", "Te", "Ur", "Ve",
    "Wo", "Xe", "Yi", "Zo", "Aka", "Bel", "Cor", "Dra", "Eri", "Fen", "Gry", "Hyl", "Ist", "Jor"
]
PLANET_MIDDLES = [
    "a", "o", "er", "om", "in", "ir", "ul", "ex", "or", "us", "an", "ith", "yst", "orb", "ent", "ath",
    "emn", "ilv", "ond", "yrr", "ax", "ez", "ael", "ion", "yth", "ars", "esp", "ull", "oct", "id"
]
PLANET_SUFFIXES = [
    "dia", "mon", "rax", "gen", "tia", "n Prime", "lon", "nor", "xis", "phi", "lya", "seth", "tara", "vor",
    "clya", "dion", "goth", "hylon", "jovir", "kynth", "lyr", "myr", "nov", "pyr", "qor", "rhos", "syl",
    "thos", "vyl", "wynn", "zylos" #, "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "omega"
]

CHAR_PREFIXES = [
    "Aro", "Sola", "Tae", "Rev", "Zan", "Pyra", "Kel", "Xen", "Mira", "Vel", "Sy", "Rin", "Kor", "Jax", "Lys",
    "Bram", "Cael", "Dario", "Elara", "Finn", "Gwen", "Hale", "Iris", "Jorn", "Kael", "Lira", "Mael", "Nara",
    "Orin", "Perrin", "Quinn", "Roric", "Seraph", "Taryn", "Ulric", "Vanya", "Wynn", "Yara", "Zephyr", "Astrid",
    "Borin", "Cassia", "Draven", "Evian", "Faelan", "Galen", "Haven", "Illya", "Jovin", "Kyra", "Lucian", "Maeve"
]
CHAR_MIDDLES = [
    "a", "i", "o", "e", "u", "en", "il", "or", "av", "ex", "an", "ir", "ael", "ian", "ona", "ara", "eli",
    "ira", "eus", "ius", "ael", "ine", "ara", "ia", "ia", "ya", "ea", "eo", "ae", "io", "oi", "ai", "ay"
]
CHAR_SUFFIXES = [
    "th", "la", "n", "r", "x", "ia", "s", "ar", "us", "on", "ir", "el", "an", "en", "in", "os", "as", "es", "is",
    "ys", "ax", "ex", "ix", "ox", "ux", "lyn", "wyn", "den", "len", "ren", "sen", "van", "zan", "bal", "cal", "dal"
]
CHAR_TITLES = [
    "Captain", "Commander", "Chancellor", "Archon", "Envoy", "Warden", "High Councilor"
]

# Add new title lists for specific roles
LEADER_TITLES = [
    "Supreme Chancellor", "High Archon", "Grand Sovereign", "Prime Minister", 
    "Emperor", "High Councilor", "President", "Overlord", "Prime Director",
    "High Commander"
]

MILITARY_TITLES = [
    "Grand Admiral", "Supreme Commander", "Fleet Admiral", "High General",
    "War Marshal", "Chief Strategist", "Military Archon", "Battle Commander",
    "Supreme General", "Defense Director"
]

# Add governor titles
GOVERNOR_TITLES = [
    "Governor", "Planetary Regent", "Overseer", "Viceroy", "Administrator",
    "Planetary Commander", "Consul", "Provincial Director", "Sector Lord",
    "Colonial Minister"
]

# Add near other title lists
ADMINISTRATIVE_TITLES = [
    "Chief of Staff", "Grand Vizier", "Head Administrator", "Director of Operations",
    "Minister of State", "Chancellor's Adjutant", "Supreme Scribe", "Council Speaker",
    "Head of Bureaucracy", "Senior Archivist"
]
SCIENTIFIC_TITLES = [
    "Chief Scientist", "Head Researcher", "Director of Xenology", "Lead Engineer",
    "Master Archivist", "Head of Advanced Studies", "Director of Innovation", "Chief Cosmographer"
]
DIPLOMATIC_TITLES = [
    "Chief Diplomat", "Lead Ambassador", "Minister of Interstellar Relations", "Trade Envoy",
    "Head Negotiator", "Master of Protocol", "Interfaction Liaison"
]
INTELLIGENCE_TITLES = [
    "Director of Intelligence", "Spymaster", "Chief Analyst", "Head of Covert Ops",
    "Master of Whispers"
]
# New Title Lists for Operational/Mid-Lower Rank Characters
SHIP_CAPTAIN_TITLES = [
    "Captain", "Ship Commander", "Vessel Master", "Flight Leader", "Skipper"
]

GROUND_UNIT_COMMANDER_TITLES = [
    "Battalion Commander", "Major", "Legion Commander", "Centurion", # Added Legion Commander, Centurion
    "Force Commander", "Precinct Captain", "Garrison Chief"
]

TECHNICAL_SPECIALIST_TITLES = [
    "Lead Technician", "Engineering Chief", "Science Officer", "Systems Analyst",
    "Chief Medical Officer", "Quartermaster", "Logistics Officer" # Added more variety
]

ADMINISTRATIVE_JUNIOR_TITLES = [
    "Sector Clerk", "Logistics Coordinator", "Junior Attaché", "Department Aide",
    "Record Keeper", "Assistant Administrator", "Field Scribe"
]

# Add after the existing constants

TECH_LEVELS = [
    "Primitive",         # No space travel, limited technology (rarely used)
    "Foundational",      # Basic space exploration, no interplanetary colonization (like current Earth)
    "Intrastellar",      # Established solar system presence, no FTL
    "Interstellar",      # FTL travel, established multi-system civilization
    "Advanced",          # Energy manipulation, advanced physics
    "Transcendent"       # Reality/physics manipulation, post-singularity
]

# Technology categories and their advancements
TECH_CATEGORIES = {
    "Energy": [
        "Basic Energy Refinement",
        "Nuclear Fission",
        "Fusion Power",
        "Antimatter",
        "Zero-Point Energy",
        "Reality Manipulation"
    ],
    "Computing": [
        "No Computing", # Primitive
        "Basic Computing", # Foundational
        "Advanced Computing", # Intrastellar
        "Quantum Computing", # Interstellar
        "Planetary-Scale Computing", # Advanced
        "Reality Computation" # Transcendent
    ],
    "Transportation": [
        "Pre-Space Travel",     # Primitive
        "Chemical Rockets",      # Foundational
        "Advanced Propulsion",   # Intrastellar
        "FTL Drives",           # Interstellar
        "Transdimensional Propulsion",  # Advanced
        "Space-Time Manipulation" # Transcendent
    ],
    "Materials": [
        "Basic Alloys",
        "Advanced Composites",
        "Smart Materials",
        "Molecular Engineering",
        "Matter Synthesis",
        "Fundamental Force Control"
    ]
}

PLANET_CLIMATES = {
    "Temperate": 50,      # 40% chance
    "Tropical": 8,       # 10% chance
    "Forest World": 8,   # 10% chance
    "Ocean World": 8,    # 10% chance
    "Mountain World": 8, # 10% chance
    "Arid": 6,           # 8% chance
    "Arctic": 6,         # 6% chance
    "Desert": 6          # 6% chance
}

# Add these constants at the top with the other constants
STAR_TYPES = {
    "Blue Giant": 2,      # Rare, but can support many planets
    "Blue-White": 5,
    "White": 8,
    "Yellow": 45,         # Like our Sun, common and good for life
    "Orange": 25,
    "Red": 12,
    "Red Dwarf": 3
}

# Helper function to generate a base name using prefixes, middles, suffixes
def _generate_base_name(prefixes, middles, suffixes, middle_chance=0.5):
    prefix = random.choice(prefixes)
    middle_piece = random.choice(middles) if random.random() < middle_chance else ""
    suffix_piece = random.choice(suffixes)
    return prefix + middle_piece + suffix_piece

# Internal helper to create a single named character dictionary
def _generate_named_character(title_list, role, specific_title=None, female_percentage=50, male_percentage=50):
    """Generates a character with a name, title, and role, using numerical gender percentages."""
    first_name = _generate_base_name(CHAR_PREFIXES, CHAR_MIDDLES, CHAR_SUFFIXES)
    last_name = _generate_base_name(CHAR_PREFIXES, CHAR_MIDDLES, CHAR_SUFFIXES, middle_chance=0.4) # Slightly less chance for middle in last name
    
    title = specific_title if specific_title else random.choice(title_list)

    # Validate and calculate gender weights directly from input percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        # This print might be noisy if called many times; consider logging for frequent calls
        print(f"SCIFI_GEN/_generate_named_character: Invalid gender percentages (F:{female_percentage}%, M:{male_percentage}%). Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        # Optional: print(f"SCIFI_GEN/_generate_named_character: Using F:{female_percentage}%, M:{male_percentage}%")

    gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
    
    full_name = f"{first_name} {last_name}"
    display_name = f"{title} {full_name}".strip() if title else full_name # Handle cases with no title

    return {
        "title": title,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "display_name": display_name,
        "role": role,
        "gender": gender # Add gender to the character dictionary
    }

def load_faction_profiles(file_path="Generators/faction_profiles.json"):
    """
    Loads faction profiles from a JSON file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
            return profiles
    except Exception as e:
        print(f"Error loading faction profiles: {e}")
        print(f"Attempted to load from: {os.path.abspath(file_path)}")
        raise

def choose_faction_profile(profiles):
    """
    Chooses a profile randomly with respect to the 'weight' in each profile.
    """
    # Extract all weights
    weights = [p["weight"] for p in profiles]
    # Use random.choices with the 'weights' parameter (available in Python 3.6+)
    chosen_profile = random.choices(population=profiles, weights=weights, k=1)[0]
    return chosen_profile

def generate_faction_name(profile):
    """
    Generate a faction name using the profile's descriptors and
    randomly chosen sci-fi syllables.
    """
    base_name = _generate_base_name(FACTION_PREFIXES, FACTION_MIDDLES, FACTION_SUFFIXES)
    descriptor = random.choice(profile["descriptors"])
    return f"{base_name} {descriptor}"

def get_planet_count(profile):
    """
    Determines how many planets a faction should have based on their profile.
    """
    is_expansionist = "expansionist" in [trait.lower() for trait in profile["primary_traits"]]
    if is_expansionist:
        return random.randint(5, 15)
    return random.randint(3, 5)

def get_system_count(profile):
    """
    Determines how many star systems a faction should control based on their profile.
    """
    is_expansionist = "expansionist" in [trait.lower() for trait in profile["primary_traits"]]
    tech_level = profile.get("tech_level", 3)
    
    # Base ranges based on tech level
    if tech_level <= 2:  # Pre-FTL civilizations
        return 1
    elif is_expansionist:
        return random.randint(3, 7)  # Expansionist factions control more systems
    else:
        return random.randint(1, 3)  # Most factions control fewer systems

def to_roman(num):
    """Convert an integer to Roman numerals"""
    roman_values = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I")
    ]
    roman = ''
    for value, numeral in roman_values:
        while num >= value:
            roman += numeral
            num -= value
    return roman

def generate_planet_names(profile, num_planets=3):
    """
    Generate planet names and their governors for a given faction.
    Returns a list of planet dictionaries containing name and governor info.
    """
    planets = []
    for _ in range(num_planets):
        prefix = random.choice(PLANET_PREFIXES)
        middle = random.choice(PLANET_MIDDLES) if random.random() < 0.7 else ""
        suffix = random.choice(PLANET_SUFFIXES)
        planet_name = prefix + middle + suffix
        
        # Generate governor for this planet with faction-specific title
        prefix = random.choice(CHAR_PREFIXES)
        middle = random.choice(CHAR_MIDDLES) if random.random() < 0.5 else ""
        suffix = random.choice(CHAR_SUFFIXES)
        first_name = prefix + middle + suffix

        prefix = random.choice(CHAR_PREFIXES)
        middle = random.choice(CHAR_MIDDLES) if random.random() < 0.4 else ""
        suffix = random.choice(CHAR_SUFFIXES)
        last_name = prefix + middle + suffix

        # Use faction-specific governor title
        title = random.choice(profile["governor_titles"])
        
        # TODO: shouldn't I be using the generate_governor function here?
        governor = {
            "title": title,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "display_name": f"{title} {first_name} {last_name}",
            "role": f"Governor of {planet_name}"
        }

        # Generate planet stats based on faction's tech level
        stats = generate_planet_stats(profile.get("tech_level", 3))
        
        planet = {
            "name": planet_name,
            "governor": governor,
            "stats": stats
        }
        planets.append(planet)
    return planets

def generate_character_names(profile, num_characters=5):
    """
    Placeholder: Generate character names for a given faction. 
    This will be refactored to use more specific staff generation functions.
    """
    characters = []
    # Example: Create leader and military leader (simplified)
    if num_characters >= 1:
        # Assuming profile["titles"] gives leader titles & profile["military_titles"] gives military titles
        # These profile keys need to be consistently populated from faction_profiles.json
        leader_title_list = profile.get("titles", LEADER_TITLES) # Fallback to general list
        characters.append(_generate_named_character(leader_title_list, "Faction Leader"))
    if num_characters >= 2:
        mil_title_list = profile.get("military_titles", MILITARY_TITLES)
        characters.append(_generate_named_character(mil_title_list, "Military Leader"))
    
    # Add some generic other characters if num_characters > 2
    for _ in range(num_characters - len(characters)):
        characters.append(_generate_named_character(CHAR_TITLES, "Notable Figure")) # Generic role
    return characters

def generate_governor(profile, planet_name, female_percentage=50, male_percentage=50):
    """Generate a governor for a planet with faction-specific title and gender bias."""
    # Ensure profile has "governor_titles", fallback to GOVERNOR_TITLES if not defined in profile
    governor_title_list = profile.get("governor_titles", GOVERNOR_TITLES)
    return _generate_named_character(governor_title_list, f"Governor of {planet_name}", female_percentage=female_percentage, male_percentage=male_percentage)

def generate_solar_system(profile, system_number, female_percentage=50, male_percentage=50):
    """
    Generate a complete solar system with a star and planets.
    """
    system_name = generate_system_name()
    star_type = random.choices(
        list(STAR_TYPES.keys()),
        weights=list(STAR_TYPES.values())
    )[0]
    
    # Pass is_capital_system flag based on system_number
    # This determines if the system itself is the capital system
    is_this_capital_system = (system_number == 0)
    habitable_count, uninhabitable_count = determine_system_composition(star_type, is_capital_system=is_this_capital_system)
    
    habitable_planets = []
    for i in range(habitable_count):
        prefix = random.choice(PLANET_PREFIXES)
        middle = random.choice(PLANET_MIDDLES) if random.random() < 0.7 else ""
        suffix = random.choice(PLANET_SUFFIXES)
        planet_name = prefix + middle + suffix
        
        # Determine if this specific planet is THE capital planet
        # It's the capital planet if it's the first habitable planet (i=0) in the capital system
        is_this_planet_capital = (is_this_capital_system and i == 0)
        
        stats = generate_planet_stats(
            profile.get("tech_level", 3),
            is_capital=is_this_planet_capital # Pass this flag to stats generation
        )
        
        governor = generate_governor(profile, planet_name, female_percentage=female_percentage, male_percentage=male_percentage)
        
        planet = {
            "name": planet_name,
            "governor": governor,
            "stats": stats,
            "is_capital": is_this_planet_capital  # Explicitly add the flag here
        }
        habitable_planets.append(planet)
    
    # Generate basic data for uninhabitable planets
    uninhabitable_planets = [
        {
            "name": f"{system_name.replace(' System', '')} {to_roman(j+1)}", 
            "type": random.choice([
                "Gas Giant", "Ice Giant", "Rocky World", "Asteroid Belt",
                "Molten World", "Frozen World", "Toxic World"
            ]),
            "resources": random.choice([
                "None", "Poor", "Moderate", "Rich", "Abundant"
            ])
        } for j in range(uninhabitable_count) # Used j to avoid conflict with i
    ]
    
    return {
        "name": system_name,
        "star_type": star_type,
        "habitable_planets": habitable_planets,
        "uninhabitable_planets": uninhabitable_planets,
        "total_planets": habitable_count + uninhabitable_count,
        "is_capital_system": is_this_capital_system  # Explicitly add the flag here
    }

def generate_systems_for_faction(profile, num_systems=2, female_percentage=50, male_percentage=50):
    """
    Generate multiple solar systems for a faction.
    First system is the capital system.
    """
    tech_level = profile.get("tech_level", 3)
    systems = []
    
    # Generate capital system first
    capital_system = generate_solar_system(profile, 0, female_percentage=female_percentage, male_percentage=male_percentage)
    systems.append(capital_system)
    
    # Generate additional systems
    for _ in range(num_systems - 1):
        system = generate_solar_system(profile, _ + 1, female_percentage=female_percentage, male_percentage=male_percentage)
        systems.append(system)
    
    return systems

def create_faction(profiles, female_percentage=50, male_percentage=50):
    """
    Select a random faction profile and generate complete faction data,
    including a richer set of named key personnel with gender bias.
    """
    profile = choose_faction_profile(profiles)
    faction_name = generate_faction_name(profile)
    
    # Generate tech levels
    tech_levels = determine_faction_tech_level(profile)
    
    # Determine number of systems
    num_systems = get_system_count(profile)
    
    # Generate solar systems (this also generates governors for habitable planets)
    systems = generate_systems_for_faction(profile, num_systems, female_percentage=female_percentage, male_percentage=male_percentage)
    
    # --- Assemble All Faction Personnel ---
    all_faction_personnel = []

    # 1. Faction Leader
    all_faction_personnel.append(generate_faction_leader(profile, female_percentage=female_percentage, male_percentage=male_percentage))
    
    # 2. Military Leader
    all_faction_personnel.append(generate_military_leader(profile, female_percentage=female_percentage, male_percentage=male_percentage))
    
    # 3. Military Staff (e.g., 2-4)
    all_faction_personnel.extend(generate_military_staff(profile, count=random.randint(2, 4), female_percentage=female_percentage, male_percentage=male_percentage))
    
    # 4. Administrative Staff (e.g., 2-3)
    all_faction_personnel.extend(generate_administrative_staff(profile, count=random.randint(2, 3), female_percentage=female_percentage, male_percentage=male_percentage))
    
    # 5. Specialized Staff (e.g., 1-3, could be a mix)
    #    Let's aim for one of each key type if possible, or a random selection
    specialized_staff_types = [
        {"titles": SCIENTIFIC_TITLES, "role_prefix": "Chief Scientist"}, # Top scientist
        {"titles": DIPLOMATIC_TITLES, "role_prefix": "Lead Diplomat"},   # Top diplomat
        {"titles": INTELLIGENCE_TITLES, "role_prefix": "Intelligence Director"} # Top intel
    ]
    # Shuffle to vary which ones are picked if we don't pick all
    random.shuffle(specialized_staff_types)
    num_specialized_to_generate = random.randint(1, len(specialized_staff_types)) # Generate 1 to all types
    for i in range(num_specialized_to_generate):
        spec = specialized_staff_types[i]
        all_faction_personnel.append(_generate_named_character(spec["titles"], spec["role_prefix"], female_percentage=female_percentage, male_percentage=male_percentage))

    # 6. Governors (extracted from generated systems)
    for system in systems:
        for planet in system["habitable_planets"]:
            if "governor" in planet and planet["governor"]:
                all_faction_personnel.append(planet["governor"])
                
    # 7. Operational Pool (mid-to-lower rank personnel)
    # Generate a random number of these, e.g., between 5 and 12
    num_operational_chars = random.randint(5, 12)
    all_faction_personnel.extend(generate_operational_pool(profile, count=num_operational_chars, female_percentage=female_percentage, male_percentage=male_percentage))
    # --- End Assembling Personnel ---

    faction_data = {
        "faction_profile": profile["type"],
        "primary_traits": profile["primary_traits"],
        "notes": profile["notes"],
        "weight": profile["weight"],
        "faction_name": faction_name,
        "systems": systems,
        "characters": all_faction_personnel, # Assign the consolidated list
        "technology": tech_levels
    }
    
    # Calculate military assets based on all habitable planets
    military_assets = calculate_military_assets(faction_data)
    faction_data["military_assets"] = military_assets
    
    return faction_data

def determine_faction_tech_level(profile):
    """
    Determines tech level based on faction profile.
    Most factions are Interstellar by default.
    Returns a dictionary with overall level and category levels.
    """
    # Base level is Interstellar (index 3) unless specified otherwise in profile
    base_level = profile.get("tech_level", 3)
    overall_tech = TECH_LEVELS[base_level]
    
    # All categories are at the same level as overall tech
    categories = {}
    for category in TECH_CATEGORIES:
        categories[category] = {
            "level": TECH_LEVELS[base_level],
            "developments": TECH_CATEGORIES[category][0:base_level + 1]
        }
    
    return {
        "overall_level": overall_tech,
        "base_level": base_level,
        "categories": categories
    }

def generate_universe(num_factions=5, female_percentage=50, male_percentage=50):
    """
    Generates a space opera setting with multiple interstellar factions.
    Each faction will have a defined set of leadership and staff roles, with gender bias.
    
    Parameters:
    - num_factions: Number of factions to generate (default 5)
    - female_percentage (int): Percentage for female gender (0-100)
    - male_percentage (int): Percentage for male gender (0-100)
    
    Returns a list of faction dictionaries configured for a space opera setting.
    """
    faction_profiles = load_faction_profiles("Generators/faction_profiles.json")
    factions = []
    for _ in range(num_factions):
        new_faction = create_faction(faction_profiles, female_percentage=female_percentage, male_percentage=male_percentage)
        factions.append(new_faction)
    
    return factions

def print_factions(factions):
    """
    Print detailed information about the generated factions.
    """
    for faction in factions:
        print("\n=== Faction ===")
        print(f"Name: {faction['faction_name']}")
        print(f"Type: {faction['faction_profile']}")
        print(f"Tech Level: {faction['technology']['overall_level']}")
        
        print("\nSystems:")
        for system in faction["systems"]:
            system_tag = " (Capital System)" if system.get("is_capital_system", False) else ""
            print(f"\n  {system['name']}{system_tag} ({system['star_type']})")
            print("  Habitable Planets:")
            for planet in system["habitable_planets"]:
                capital_tag = " (Capital)" if planet.get("is_capital", False) else ""
                print(f"    - {planet['name']}{capital_tag}")
                print(f"      Governor: {planet['governor']['display_name']}")
                print(f"      Population: {planet['stats']['population']}")
                print(f"      Climate: {planet['stats']['climate']}")
                print(f"      Resources: {planet['stats']['resources']}")
                print(f"      Infrastructure: {planet['stats']['infrastructure']['description']}")
                print(f"      Stability: {planet['stats']['stability']}%")
            
            print("  Uninhabitable Bodies:")
            for planet in system["uninhabitable_planets"]:
                print(f"    - {planet['name']} ({planet['type']}, Resources: {planet['resources']})")

        print("\nMilitary Assets:")
        assets = faction["military_assets"]
        print("  Ships:")
        for ship_type, count in assets["ships"].items():
            print(f"    {ship_type.replace('_', ' ').title()}: {count:,}")
        print("\n  Personnel:")
        print(f"    Fleet Personnel: {assets['personnel']['fleet_personnel']:,} crew")
        print(f"    Active Ground Forces: {assets['personnel']['active_ground_forces']:,} troops")
        print(f"    Reservists: {assets['personnel']['reservists']:,} troops")
        print(f"    Planetary Defense Forces: {assets['personnel']['planetary_defense_forces']:,} troops")
        print(f"    Support Staff: {assets['personnel']['support_staff']:,} personnel")
        print(f"    Elite Units: {assets['special_forces']['elite_units']:,} troops")
        print(f"\n  Total Military Personnel: {assets['total_military_personnel']:,}")
        print("\nKey Characters:")
        for character in faction["characters"]:
            if character.get('role'):  # Only print leadership roles here
                if "Governor" not in character['role']:
                    print(f"  - {character['display_name']}")
                    print(f"    Role: {character['role']}")

# Placeholder functions for later use
def generate_early_space_age(num_factions=3):
    """
    Generates a near-future setting where factions are just beginning space exploration.
    Override tech_level in profiles to be lower, fewer planets, etc.
    """
    pass

def generate_post_singularity(num_factions=2):
    """
    Generates a far-future setting with highly advanced civilizations.
    Override tech_level in profiles to be higher, more exotic tech, etc.
    """
    pass

def generate_custom_setting(config):
    """
    Generates a setting based on custom configuration parameters.
    Could include tech level ranges, faction counts, etc.
    """
    pass

def save_factions_to_file(factions, filename=None, timestamp=False):
    """
    Saves the generated factions to a JSON file.
    
    Parameters:
    - factions: List of faction dictionaries to save
    - filename: Name of the output file (optional)
    - timestamp: Whether to include timestamp in filename (default: False)
    """
    if filename is None:
        if timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"factions_{timestamp}.json"
        else:
            filename = "generated_factions.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(factions, f, indent=2, ensure_ascii=False)
        print(f"\nFactions successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving factions to file: {e}")
        raise

def get_infrastructure_level(tech_level, is_capital=False):
    """
    Determines infrastructure level based on tech level and planet importance.
    Returns tuple of (level, quality).
    
    Infrastructure Levels:
    - Primitive: Pre-industrial
    - Basic: Industrial/early space
    - Developed: Established space presence
    - Advanced: Full interstellar
    - Cutting-edge: Post-singularity
    
    Quality ranges from 0-100:
    0-20: Failing/Minimal
    21-40: Poor
    41-60: Standard
    61-80: Good
    81-100: Excellent
    """
    # Base infrastructure can't be higher than tech level allows
    max_infrastructure = {
        0: "Primitive",
        1: "Basic",
        2: "Developed",
        3: "Advanced",
        4: "Cutting-edge",
        5: "Transcendent"
    }
    
    # Quality ranges based on tech level
    quality_ranges = {
        0: (20, 50),   # Primitive: minimal to standard
        1: (30, 60),   # Basic: poor to standard
        2: (40, 70),   # Developed: standard to good
        3: (50, 80),   # Advanced: standard to good
        4: (60, 90),   # Cutting-edge: good to excellent
        5: (70, 100)   # Transcendent: good to excellent
    }
    
    # Capital worlds get better infrastructure
    if is_capital:
        level = max_infrastructure[tech_level]
        quality_min, quality_max = quality_ranges[tech_level]
        quality = random.randint(int((quality_min + quality_max) / 2), quality_max + 10)
    else:
        # Regular worlds might be one level behind
        possible_levels = [
            max_infrastructure[max(0, tech_level - 1)],
            max_infrastructure[tech_level]
        ]
        weights = [30, 70]  # 70% chance of max level, 30% chance of one below
        level = random.choices(possible_levels, weights=weights)[0]
        
        quality_min, quality_max = quality_ranges[tech_level]
        quality = random.randint(quality_min, quality_max)
    
    return level, quality

def generate_planet_stats(tech_level, is_capital=False):
    """
    Generate statistics for a planet based on tech level.
    Population is affected by resources, climate, stability, and infrastructure.
    """
    # First generate the basic stats
    base_stats = {
        "climate": random.choices(
            list(PLANET_CLIMATES.keys()), 
            weights=list(PLANET_CLIMATES.values())
        )[0],
        "resources": random.choice([
            "Abundant", "Rich", "Moderate", "Poor", "Scarce"
        ]),
        "stability": random.randint(50, 100),  # Percentage
        "urbanization": random.randint(20, 95)  # Percentage # Not used yet
    }
    
    # Get infrastructure level and quality
    infra_level, infra_quality = get_infrastructure_level(tech_level, is_capital)
    base_stats["infrastructure"] = {
        "level": infra_level,
        "quality": infra_quality,
        "description": f"{infra_level} ({infra_quality}%)"
    }

    # Population ranges by tech level (in billions)
    pop_ranges = {
        0: (0.001, 1),     # Primitive: 1M to 1B
        1: (1, 10),        # Foundational: 1B to 10B
        2: (0.5, 15),      # Intrastellar: 500M to 15B
        3: (1, 20),        # Interstellar: 1B to 20B
        4: (0.5, 25),      # Advanced: 500M to 25B
        5: (0.1, 30)       # Transcendent: 100M to 30B
    }
    
    # Get base population range
    pop_range = pop_ranges.get(tech_level, (1, 10))
    
    # Calculate modifiers based on planetary conditions
    resource_modifiers = {
        "Abundant": 1.2,
        "Rich": 1.1,
        "Moderate": 1.0,
        "Poor": 0.7,
        "Scarce": 0.4
    }

    climate_modifiers = {
        "Temperate": 1.7,
        "Tropical": 1.2,
        "Forest World": 1.1,
        "Ocean World": 0.9,
        "Mountain World": 0.8,
        "Arid": 0.7,
        "Arctic": 0.6,
        "Desert": 0.5
    }

    # Infrastructure level modifiers
    infrastructure_level_modifiers = {
        "Transcendent": 1.5,
        "Cutting-edge": 1.3,
        "Advanced": 1.2,
        "Developed": 1.1,
        "Basic": 0.85,
        "Primitive": 0.6
    }

    # Calculate total modifier
    resource_mod = resource_modifiers[base_stats["resources"]]
    climate_mod = climate_modifiers[base_stats["climate"]]
    stability_mod = base_stats["stability"] / 100  # Convert percentage to decimal
    
    # Infrastructure modifier combines both level and quality
    infra_level_mod = infrastructure_level_modifiers[infra_level]
    infra_quality_mod = base_stats["infrastructure"]["quality"] / 100
    infrastructure_mod = infra_level_mod * infra_quality_mod

    total_modifier = (resource_mod * climate_mod * stability_mod * infrastructure_mod)

    # Generate base population
    # if tech_level >= 3:
    #     # More variation in higher tech populations
    #     base_population = random.uniform(pop_range[0], pop_range[1]) * random.uniform(0.4, 1.0)
    # else:
    base_population = random.uniform(*pop_range)

    # Apply modifier to population
    population = round(base_population * total_modifier, 3)

    # Combine all stats
    stats = {
        **base_stats,
        "population": f"{population}B",
        "population_modifier": round(total_modifier, 2),  # Include modifier for reference
        "infrastructure_modifier": round(infrastructure_mod, 2)  # Include infrastructure modifier for reference # May not be needed
    }
    
    return stats

def calculate_military_assets(faction):
    """
    Calculate military assets based on faction's planets and tech level.
    """
    # Update to use new system structure
    total_population = sum(
        float(planet.get("stats", {}).get("population", "0B").rstrip("B"))
        for system in faction["systems"]
        for planet in system["habitable_planets"]
    )
    tech_level = faction["technology"]["base_level"]
    
    # Base numbers adjusted by tech level and total population
    # Higher tech = fewer but more effective units
    tech_multiplier = 1 / (tech_level + 1)  # Higher tech needs fewer assets
    
    # Calculate different types of ships
    ships = {
        "capital_ships": max(2, int(total_population * 0.3 * tech_multiplier)),
        "cruisers": max(5, int(total_population * 1.5 * tech_multiplier)),
        "frigates": max(10, int(total_population * 4 * tech_multiplier)),
        "corvettes": max(20, int(total_population * 6 * tech_multiplier)),
        "support_ships": max(30, int(total_population * 10 * tech_multiplier))
    }
    
    # Calculate personnel (in millions for large numbers)
    personnel = {
        "fleet_personnel": sum(ships.values()) * random.randint(1000, 1500),
        "active_ground_forces": int(total_population * random.uniform(0.02, 0.05) * 1000000),  # 2-5% of population
        "reservists": int(total_population * random.uniform(0.1, 0.2) * 1000000),  # 10-20% of population
        "support_staff": int(total_population * random.uniform(0.002, 0.003) * 1000000),  # 0.2-0.3% of population
        "planetary_defense_forces": int(total_population * random.uniform(0.05, 0.1) * 1000000)  # 5-10% of population
    }
    
    # Special forces and elite units
    special_forces = {
        "elite_units": max(1000, int(personnel["active_ground_forces"] * 0.02)),  # 2% of active forces
        "special_ops_teams": max(100, int(total_population * 0.2))
    }
    
    return {
        "ships": ships,
        "personnel": personnel,
        "special_forces": special_forces,
        "total_military_personnel": sum(personnel.values()),
        "total_ships": sum(ships.values())
    }

def generate_system_name():
    """
    Generate a name for a solar system.
    """
    prefix = random.choice(PLANET_PREFIXES)
    middle = random.choice(PLANET_MIDDLES) if random.random() < 0.5 else ""
    suffix = random.choice([
        "System", "Sector", "Cluster", "Star", "Prime", "Major", "Minor"
    ])
    return f"{prefix}{middle} {suffix}"

def determine_system_composition(star_type, is_capital_system=False):
    """
    Determine number and types of planets based on star type.
    Returns (num_habitable, num_uninhabitable) planets.
    If is_capital_system is True, ensures at least one habitable planet.
    """
    # Base ranges for different star types
    star_ranges = {
        "Blue Giant": (1, 8, 4, 12),    # (min_habitable, max_habitable, min_total, max_total)
        "Blue-White": (0, 5, 3, 10),
        "White": (0, 4, 2, 8),
        "Yellow": (0, 4, 4, 12),        # Like our solar system
        "Orange": (0, 3, 2, 8),
        "Red": (0, 2, 1, 6),
        "Red Dwarf": (0, 1, 1, 4)
    }
    
    min_habitable_orig, max_habitable_orig, min_total_orig, max_total_orig = star_ranges[star_type]
    
    # If it's a capital system, ensure at least 1 habitable planet and 1 total planet
    if is_capital_system:
        min_h = max(1, min_habitable_orig)
        max_h = max(min_h, max_habitable_orig) # Ensure max_h is at least min_h
        min_t = max(1, min_total_orig)
        max_t = max(min_t, max_total_orig) # Ensure max_t is at least min_t
    else:
        min_h, max_h = min_habitable_orig, max_habitable_orig
        min_t, max_t = min_total_orig, max_total_orig
    
    # Determine total planets
    # Ensure min_t is not greater than max_t (can happen if original max_t was 0 and we forced min_t to 1)
    if min_t > max_t:
        max_t = min_t # e.g. if range was (0,0) and became (1,0), make it (1,1)
    total_planets = random.randint(min_t, max_t)

    # Determine habitable planets (cannot exceed total)
    # Ensure min_h is not greater than max_h
    if min_h > max_h:
        max_h = min_h # e.g. if range was (0,0) and became (1,0), make it (1,1)

    habitable_planets = random.randint(min_h, max_h)
    habitable_planets = min(habitable_planets, total_planets) # Cannot have more habitable than total
    
    # Rest are uninhabitable
    uninhabitable_planets = total_planets - habitable_planets
    
    return habitable_planets, uninhabitable_planets

# New Specific Staff Generation Functions
def generate_faction_leader(profile, female_percentage=50, male_percentage=50):
    """Generates the primary faction leader with gender bias."""
    leader_title_list = profile.get("titles", LEADER_TITLES) # Fallback to general list
    return _generate_named_character(leader_title_list, "Faction Leader", female_percentage=female_percentage, male_percentage=male_percentage)

def generate_military_leader(profile, female_percentage=50, male_percentage=50):
    """Generates the head of the faction's military with gender bias."""
    mil_title_list = profile.get("military_titles", MILITARY_TITLES)
    return _generate_named_character(mil_title_list, "Head of Military", female_percentage=female_percentage, male_percentage=male_percentage)

def generate_military_staff(profile, count=3, female_percentage=50, male_percentage=50):
    """Generates a list of key military staff with gender bias."""
    staff = []
    # For staff, we might use general MILITARY_TITLES or a subset excluding top-tier ones
    staff_military_titles = [t for t in MILITARY_TITLES if t not in ["Grand Admiral", "Supreme Commander"]] # Example: exclude top 2
    if not staff_military_titles: staff_military_titles = MILITARY_TITLES # Fallback
    for _ in range(count):
        # Roles could be more varied, e.g., "Fleet Commander", "Chief of Strategy", "Logistics Officer"
        role = random.choice(["Senior Military Officer", "Fleet Commander", "Strategic Advisor"])
        staff.append(_generate_named_character(staff_military_titles, role, female_percentage=female_percentage, male_percentage=male_percentage))
    return staff

def generate_administrative_staff(profile, count=2, female_percentage=50, male_percentage=50):
    """Generates a list of key administrative staff with gender bias."""
    staff = []
    for _ in range(count):
        role = random.choice(["Senior Administrator", "Ministerial Aide", "Bureau Chief"])
        staff.append(_generate_named_character(ADMINISTRATIVE_TITLES, role, female_percentage=female_percentage, male_percentage=male_percentage))
    return staff

def generate_specialized_staff(profile, count=2, female_percentage=50, male_percentage=50):
    """Generates a list of specialized staff (scientific, diplomatic, intelligence) with gender bias."""
    staff = []
    specializations = [
        {"titles": SCIENTIFIC_TITLES, "role_prefix": "Scientific Advisor"},
        {"titles": DIPLOMATIC_TITLES, "role_prefix": "Diplomatic Attaché"},
        {"titles": INTELLIGENCE_TITLES, "role_prefix": "Intelligence Officer"}
    ]
    for i in range(count):
        spec = random.choice(specializations) # Pick a specialization type
        # Could also cycle through specializations if count allows: spec = specializations[i % len(specializations)]
        staff.append(_generate_named_character(spec["titles"], spec["role_prefix"], female_percentage=female_percentage, male_percentage=male_percentage))
    return staff

# New function to generate a pool of operational/mid-lower rank characters
def generate_operational_pool(profile, count=7, female_percentage=50, male_percentage=50): # Default to generating a pool of e.g. 5-10 characters
    """Generates a list of operational/mid-lower rank named characters with gender bias."""
    pool = []
    operational_categories = [
        {"titles": SHIP_CAPTAIN_TITLES, "role_template": "Ship Captain"},
        {"titles": GROUND_UNIT_COMMANDER_TITLES, "role_template": "Ground Force Commander"},
        {"titles": TECHNICAL_SPECIALIST_TITLES, "role_template": "Technical Specialist"},
        {"titles": ADMINISTRATIVE_JUNIOR_TITLES, "role_template": "Administrative Staff"}
    ]

    for _ in range(count):
        category = random.choice(operational_categories)
        # For roles like "Ship Captain", it's fine. For others, we might want more specific implied roles.
        # For now, the template is simple. We could add logic for e.g. "Science Officer on [Ship Name]" if ships were pre-generated.
        role = category["role_template"] 
        pool.append(_generate_named_character(category["titles"], role, female_percentage=female_percentage, male_percentage=male_percentage))
    return pool

if __name__ == "__main__":
    # Generate a standard space opera setting
    factions = generate_universe()
    
    # Print the factions
    print_factions(factions)
    
    # Save with timestamp
    save_factions_to_file(factions)
    
    # Or save with custom name
    # save_factions_to_file(factions, "my_space_opera_factions.json", timestamp=False)
