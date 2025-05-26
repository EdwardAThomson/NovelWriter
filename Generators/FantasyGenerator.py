import json
import random
import os
from datetime import datetime
import re

# --- Fantasy Name Generation System ---

# Syllable-based name generation for fantasy settings
FACTION_SYLLABLES = {
    "start": ["Aer", "Bel", "Cor", "Dra", "Eld", "Fel", "Gar", "Hal", "Ith", "Jor",
              "Kel", "Lor", "Mor", "Nor", "Ost", "Pel", "Quen", "Rav", "Sil", "Tor",
              "Ul", "Val", "Wyr", "Xan", "Yor", "Zel", "Ath", "Bri", "Cal", "Del"],
    "middle": ["a", "e", "i", "o", "an", "ar", "en", "er", "in", "ir", "on", "or",
               "al", "el", "il", "ol", "am", "em", "im", "om", "and", "end", "ind"],
    "end": ["heim", "gard", "burg", "haven", "ford", "shire", "moor", "vale", "wood", "fell",
            "march", "hold", "keep", "gate", "bridge", "crown", "throne", "realm", "land", "wick"]
}

CITY_SYLLABLES = {
    "start": ["Ash", "Black", "Gold", "Silver", "White", "Red", "Green", "Blue", "Iron", "Stone",
              "Oak", "Pine", "Rose", "Thorn", "Star", "Moon", "Sun", "Storm", "Wind", "Fire",
              "Water", "Earth", "High", "Low", "North", "South", "East", "West", "Old", "New"],
    "middle": ["", "en", "er", "ing", "ly", "ton", "ham", "ley", "by", "thorpe"],
    "end": ["haven", "port", "ford", "bridge", "gate", "hall", "burg", "stead", "ton", "ham",
            "wick", "by", "thorpe", "moor", "fell", "wood", "vale", "hill", "rock", "keep"]
}

# Character names - more fantasy appropriate
CHAR_FIRST_SYLLABLES = {
    "start": ["Ae", "Al", "Ar", "Bel", "Bri", "Cae", "Dar", "El", "Fen", "Gar", 
              "Hal", "Ith", "Jor", "Kel", "Ler", "Mor", "Nar", "Ok", "Pel", "Quin", 
              "Rav", "Sil", "Tar", "Ul", "Val", "Wyr", "Xan", "Yor", "Zel", "Ash"],
    "end": ["a", "an", "ar", "as", "en", "er", "est", "ia", "in", "is", "on", "or", 
            "us", "yn", "ys", "el", "al", "il", "ol", "ul", "wen", "wyn", "dor", "mor"]
}

CHAR_LAST_SYLLABLES = {
    "start": ["Ash", "Black", "Bright", "Dark", "Fair", "Grey", "Iron", "Silver", "Stone",
              "Storm", "Swift", "Thorn", "White", "Wild", "Wolf", "Dragon", "Eagle", "Raven", "Bear",
              "Hart", "Stag", "Fox", "Hawk", "Lion", "Oak", "Pine", "Rose", "Star", "Moon"],
    "end": ["bane", "born", "blade", "heart", "shield", "sword", "bow", "spear", "helm", "guard",
            "ward", "watch", "walker", "rider", "hunter", "slayer", "bringer", "keeper", "master", "lord",
            "song", "wind", "fire", "stone", "wood", "steel", "gold", "silver", "crown", "throne"]
}

# Phonetic compatibility rules (same as sci-fi)
VOWELS = set('aeiou')
CONSONANTS = set('bcdfghjklmnpqrstvwxyz')

def is_phonetically_compatible(syllable1, syllable2):
    """Check if two syllables flow well together phonetically."""
    if not syllable1 or not syllable2:
        return True
    
    end_char = syllable1[-1].lower()
    start_char = syllable2[0].lower()
    
    # Avoid double vowels or consonants that don't flow
    if end_char in VOWELS and start_char in VOWELS:
        # Some vowel combinations are okay
        if end_char + start_char in ['ae', 'ai', 'ao', 'ea', 'ei', 'eo', 'ia', 'ie', 'io', 'oa', 'oe', 'oi', 'ua', 'ue', 'ui']:
            return True
        return False
    
    # Avoid harsh consonant clusters
    if end_char in CONSONANTS and start_char in CONSONANTS:
        harsh_clusters = ['ck', 'gk', 'pk', 'tk', 'xk', 'zk', 'qx', 'xq']
        if end_char + start_char in harsh_clusters:
            return False
    
    return True

def generate_fantasy_name(syllable_dict, max_syllables=2, min_length=3, max_length=15, force_multi_syllable=False):
    """
    Generate a fantasy name using syllable dictionary with phonetic rules.
    
    Args:
        syllable_dict: Dictionary with 'start', 'middle' (optional), 'end' keys
        max_syllables: Maximum number of syllables (default 2 for shorter names)
        min_length: Minimum character length
        max_length: Maximum character length
        force_multi_syllable: If True, always generate at least 2 syllables
    """
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        name_parts = []
        
        # Always start with a start syllable
        start_syl = random.choice(syllable_dict["start"])
        name_parts.append(start_syl)
        
        # Decide how many total syllables
        if force_multi_syllable:
            num_syllables = random.randint(2, max_syllables)  # Force at least 2
        else:
            num_syllables = random.randint(1, max_syllables)
        
        # Add middle syllables if we have them and need more than 2 total
        if num_syllables > 2 and "middle" in syllable_dict:
            for _ in range(num_syllables - 2):
                middle_candidates = [m for m in syllable_dict["middle"] 
                                   if is_phonetically_compatible(name_parts[-1], m)]
                if middle_candidates:
                    middle_syl = random.choice(middle_candidates)
                    name_parts.append(middle_syl)
        
        # Add end syllable if we need more than 1 syllable
        if num_syllables > 1:
            end_candidates = [e for e in syllable_dict["end"] 
                            if is_phonetically_compatible(name_parts[-1], e)]
            if end_candidates:
                end_syl = random.choice(end_candidates)
                name_parts.append(end_syl)
        
        # Combine and check length
        name = "".join(name_parts)
        if min_length <= len(name) <= max_length:
            return name.capitalize()
        
        attempts += 1
    
    # Fallback: create a simple 2-syllable name
    start_syl = random.choice(syllable_dict["start"])
    end_syl = random.choice(syllable_dict["end"])
    return (start_syl + end_syl).capitalize()

def generate_character_name(gender=None):
    """Generate a fantasy character first name, optionally gender-specific."""
    if gender == "Male":
        # Generate male-sounding fantasy names
        male_names = [
            "Aelred", "Aldric", "Baelon", "Caelum", "Darian", "Edric", "Gareth", "Hadrian",
            "Kael", "Lysander", "Magnus", "Nolan", "Orion", "Percival", "Roderick", "Soren",
            "Theron", "Ulric", "Varian", "Weston", "Xander", "Yorick", "Zephyr", "Alaric",
            "Bastian", "Caspian", "Dorian", "Evander", "Finnian", "Gideon", "Hector", "Idris",
            "Jasper", "Kieran", "Leander", "Matthias", "Nathaniel", "Octavius", "Phoenix", "Quinlan"
        ]
        return random.choice(male_names)
    elif gender == "Female":
        # Generate female-sounding fantasy names
        female_names = [
            "Aeliana", "Brenna", "Celeste", "Delara", "Elara", "Fiona", "Gwyneth", "Helena",
            "Isadora", "Juliana", "Kira", "Lyanna", "Morgana", "Nora", "Ophelia", "Penelope",
            "Quinn", "Rosalind", "Seraphina", "Thalia", "Ursula", "Vivienne", "Willa", "Xara",
            "Ysabel", "Zara", "Aria", "Beatrice", "Cordelia", "Diana", "Evangeline", "Freya",
            "Gwendolyn", "Hazel", "Iris", "Jasmine", "Katarina", "Luna", "Mira", "Natasha"
        ]
        return random.choice(female_names)
    else:
        # Original behavior for backwards compatibility
        return generate_fantasy_name(CHAR_FIRST_SYLLABLES, max_syllables=2, min_length=3, max_length=10, force_multi_syllable=True)

def generate_character_surname():
    """Generate a fantasy character surname."""
    return generate_fantasy_name(CHAR_LAST_SYLLABLES, max_syllables=2, min_length=4, max_length=12, force_multi_syllable=True)

def generate_faction_name_base():
    """Generate the base name part of a faction (before descriptors)."""
    return generate_fantasy_name(FACTION_SYLLABLES, max_syllables=3, min_length=4, max_length=15)

def generate_city_name():
    """Generate a city or town name."""
    return generate_fantasy_name(CITY_SYLLABLES, max_syllables=2, min_length=4, max_length=15, force_multi_syllable=True)

# Fantasy-specific constants

# Magic levels instead of tech levels
MAGIC_LEVELS = [
    "None",           # No magic users
    "Basic",          # Hedge wizards, simple spells
    "Intermediate",   # Trained mages, useful magic
    "Advanced",       # Powerful wizards, significant magic
    "Arcane",         # Master mages, reality-altering magic
    "Legendary"       # Archmages, world-shaping power
]

# Magic schools/types
MAGIC_SCHOOLS = {
    "Elemental": ["Fire Magic", "Water Magic", "Earth Magic", "Air Magic", "Lightning Magic", "Ice Magic"],
    "Divine": ["Healing Magic", "Protection Magic", "Divine Wrath", "Blessing Magic", "Undead Turning", "Divine Light"],
    "Arcane": ["Illusion Magic", "Transmutation", "Enchantment", "Divination", "Teleportation", "Time Magic"],
    "Nature": ["Plant Growth", "Animal Communication", "Weather Control", "Shapeshifting", "Druidcraft", "Natural Healing"],
    "Shadow": ["Necromancy", "Shadow Magic", "Mind Control", "Curses", "Soul Magic", "Dark Rituals"],
    "Battle": ["Weapon Enhancement", "Armor Spells", "Battle Fury", "Tactical Magic", "Siege Magic", "War Wards"]
}

# Terrain types for regions
TERRAIN_TYPES = {
    "Plains": 30,        # Most common
    "Forest": 25,
    "Mountains": 20,
    "Hills": 15,
    "Coastal": 10,
    "Desert": 8,
    "Swamp": 5,
    "Tundra": 3
}

# City/town climates (similar to planets but fantasy appropriate)
CITY_CLIMATES = {
    "Temperate": 40,
    "Tropical": 15,
    "Forest": 15,
    "Mountain": 10,
    "Coastal": 10,
    "Arid": 5,
    "Arctic": 3,
    "Swamp": 2
}

# Fantasy titles for different roles
LEADER_TITLES = [
    "King", "Queen", "Duke", "Duchess", "Prince", "Princess", "Lord", "Lady",
    "High Lord", "High Lady", "Sovereign", "Regent", "Chancellor", "Overlord"
]

MILITARY_TITLES = [
    "General", "Marshal", "Knight-Commander", "Captain-General", "War Leader",
    "Battle Master", "High Commander", "Lord Commander", "Champion", "Warlord"
]

GOVERNOR_TITLES = [
    "Lord Mayor", "Baron", "Baroness", "Count", "Countess", "Sheriff", "Castellan",
    "City Lord", "City Lady", "Magistrate", "Steward", "Warden", "Keeper"
]

ADMINISTRATIVE_TITLES = [
    "Seneschal", "Chamberlain", "Treasurer", "Master of Coin", "Court Scribe",
    "Royal Secretary", "Chief Administrator", "Keeper of Records", "Master of Laws", "Justiciar"
]

MAGICAL_TITLES = [
    "Court Wizard", "Archmage", "High Mage", "Master of Magic", "Enchanter",
    "Battle Mage", "Royal Sorcerer", "Keeper of Mysteries", "Loremaster", "Sage"
]

RELIGIOUS_TITLES = [
    "High Priest", "High Priestess", "Archbishop", "Bishop", "Abbot", "Abbess",
    "Prior", "Prioress", "Temple Master", "Divine Oracle", "Holy Keeper", "Sacred Guardian"
]

DIPLOMATIC_TITLES = [
    "Ambassador", "Envoy", "Herald", "Emissary", "Diplomat", "Royal Messenger",
    "Trade Master", "Guild Representative", "Court Liaison", "Foreign Minister"
]

INTELLIGENCE_TITLES = [
    "Spymaster", "Master of Whispers", "Intelligence Chief", "Shadow Lord",
    "Information Broker", "Court Spy", "Secret Keeper", "Eyes and Ears"
]

# Operational/lower rank titles
KNIGHT_TITLES = [
    "Knight", "Sir", "Dame", "Knight-Captain", "Paladin", "Templar", "Guardian"
]

GUARD_TITLES = [
    "Captain of Guards", "Guard Captain", "Watch Captain", "Sergeant", "Lieutenant",
    "Gate Keeper", "Tower Guard", "City Watch", "Palace Guard"
]

SPECIALIST_TITLES = [
    "Master Craftsman", "Guild Master", "Quartermaster", "Master of Arms",
    "Chief Engineer", "Master Builder", "Royal Physician", "Court Bard"
]

JUNIOR_TITLES = [
    "Squire", "Page", "Apprentice", "Junior Clerk", "Assistant", "Aide",
    "Messenger", "Scout", "Junior Guard", "Trainee"
]

# Race options (optional)
FANTASY_RACES = [
    "Human", "Elf", "Dwarf", "Halfling", "Gnome", "Half-Elf", "Half-Orc", "Tiefling", "Dragonborn"
]

def _generate_named_character(title_list, role, specific_title=None, race=None, female_percentage=50, male_percentage=50):
    """Generates a fantasy character with a name, title, role, and optional race."""
    first_name = generate_character_name()
    last_name = generate_character_surname()
    
    title = specific_title if specific_title else random.choice(title_list)

    # Validate and calculate gender weights
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"FANTASY_GEN/_generate_named_character: Invalid gender percentages (F:{female_percentage}%, M:{male_percentage}%). Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0

    gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
    
    # Add race if specified
    character_race = race if race else "Human"  # Default to Human if no race specified
    
    full_name = f"{first_name} {last_name}"
    display_name = f"{title} {full_name}".strip() if title else full_name

    return {
        "title": title,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "display_name": display_name,
        "role": role,
        "gender": gender,
        "race": character_race
    }

def load_faction_profiles(file_path="Generators/fantasy_faction_profiles.json"):
    """
    Loads fantasy faction profiles from a JSON file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
            return profiles
    except Exception as e:
        print(f"Error loading fantasy faction profiles: {e}")
        print(f"Attempted to load from: {os.path.abspath(file_path)}")
        raise

def choose_faction_profile(profiles):
    """
    Chooses a profile randomly with respect to the 'weight' in each profile.
    """
    weights = [p["weight"] for p in profiles]
    chosen_profile = random.choices(population=profiles, weights=weights, k=1)[0]
    return chosen_profile

def generate_faction_name(profile):
    """
    Generate a faction name using the profile's descriptors and
    randomly chosen fantasy syllables.
    """
    base_name = generate_faction_name_base()
    descriptor = random.choice(profile["descriptors"])
    return f"{base_name} {descriptor}"

def get_city_count(profile):
    """
    Determines how many cities a faction should have based on their profile.
    """
    is_expansionist = "expansionist" in [trait.lower() for trait in profile["primary_traits"]]
    is_mercantile = "mercantile" in [trait.lower() for trait in profile["primary_traits"]]
    
    if is_expansionist or is_mercantile:
        return random.randint(4, 8)
    return random.randint(2, 4)

def get_region_count(profile):
    """
    Determines how many regions a faction should control based on their profile.
    """
    # Check if profile has explicit size constraints
    if "max_regions" in profile:
        return min(profile["max_regions"], random.randint(1, profile["max_regions"]))
    
    # Legacy logic for factions without explicit constraints
    is_expansionist = "expansionist" in [trait.lower() for trait in profile["primary_traits"]]
    magic_level = profile.get("magic_level", 2)
    faction_type = profile.get("type", "")
    
    # Base ranges based on faction type and magic level
    if faction_type == "Kingdom":
        return random.randint(3, 5)  # Kingdoms are large
    elif magic_level <= 1:  # Low magic civilizations
        return 1
    elif is_expansionist:
        return random.randint(2, 4)  # Expansionist factions control more regions
    else:
        return random.randint(1, 2)  # Most factions control fewer regions

def determine_faction_magic_level(profile):
    """
    Determines magic level based on faction profile.
    Returns a dictionary with overall level and school levels.
    """
    base_level = profile.get("magic_level", 2)
    overall_magic = MAGIC_LEVELS[base_level]
    
    # Determine which magic schools this faction uses
    schools = {}
    num_schools = min(base_level + 1, 3)  # Higher magic level = more schools
    
    # Some faction types prefer certain schools
    faction_type = profile["type"]
    preferred_schools = []
    
    if faction_type == "Religious Order":
        preferred_schools = ["Divine"]
    elif faction_type == "Magical Academy":
        preferred_schools = ["Arcane", "Elemental"]
    elif faction_type == "Dark Cult":
        preferred_schools = ["Shadow"]
    elif faction_type == "Druid Circle":
        preferred_schools = ["Nature"]
    elif faction_type in ["Kingdom", "Mercenary Company"]:
        preferred_schools = ["Battle"]
    
    # Select schools
    available_schools = list(MAGIC_SCHOOLS.keys())
    selected_schools = []
    
    # Add preferred schools first
    for school in preferred_schools:
        if school in available_schools and len(selected_schools) < num_schools:
            selected_schools.append(school)
            available_schools.remove(school)
    
    # Fill remaining slots randomly
    while len(selected_schools) < num_schools and available_schools:
        school = random.choice(available_schools)
        selected_schools.append(school)
        available_schools.remove(school)
    
    # Generate developments for each school
    for school in selected_schools:
        developments = MAGIC_SCHOOLS[school][0:base_level + 1]
        schools[school] = {
            "level": overall_magic,
            "developments": developments
        }
    
    return {
        "overall_level": overall_magic,
        "base_level": base_level,
        "schools": schools
    }

def generate_region(profile, region_number, faction_race="Human", female_percentage=50, male_percentage=50):
    """
    Generate a complete region with terrain and cities.
    """
    region_name = generate_region_name()
    terrain_type = random.choices(
        list(TERRAIN_TYPES.keys()),
        weights=list(TERRAIN_TYPES.values())
    )[0]
    
    # Determine if this is the capital region (first region)
    is_capital_region = (region_number == 0)
    
    # Check for city count constraints from profile
    max_cities_override = profile.get("max_cities_per_region", None)
    city_count = determine_region_composition(terrain_type, is_capital_region=is_capital_region, 
                                            max_cities_override=max_cities_override)
    
    cities = []
    for i in range(city_count):
        city_name = generate_city_name()
        
        # Determine if this specific city is THE capital city
        is_capital_city = (is_capital_region and i == 0)
        
        stats = generate_city_stats(
            profile.get("magic_level", 2),
            is_capital=is_capital_city
        )
        
        governor = generate_governor(profile, city_name, faction_race=faction_race, 
                                   female_percentage=female_percentage, male_percentage=male_percentage)
        
        city = {
            "name": city_name,
            "governor": governor,
            "stats": stats,
            "is_capital": is_capital_city
        }
        cities.append(city)
    
    return {
        "name": region_name,
        "terrain_type": terrain_type,
        "cities": cities,
        "total_cities": city_count,
        "is_capital_region": is_capital_region
    }

def generate_region_name():
    """
    Generate a name for a region.
    """
    base_name = generate_faction_name_base()
    suffix = random.choice(["Lands", "March", "Reach", "Shire", "Province", "Territory", "Realm"])
    return f"{base_name} {suffix}"

def determine_region_composition(terrain_type, is_capital_region=False, max_cities_override=None):
    """
    Determine number of cities based on terrain type.
    If is_capital_region is True, ensures at least one city.
    If max_cities_override is provided, caps the number of cities.
    """
    # Base ranges for different terrain types
    terrain_ranges = {
        "Plains": (2, 5),      # Good for cities
        "Forest": (1, 4),
        "Mountains": (1, 3),   # Harder to build cities
        "Hills": (2, 4),
        "Coastal": (2, 6),     # Good for trade cities
        "Desert": (1, 2),      # Few cities
        "Swamp": (1, 2),       # Few cities
        "Tundra": (1, 2)       # Few cities
    }
    
    min_cities, max_cities = terrain_ranges.get(terrain_type, (1, 3))
    
    # Apply override if provided
    if max_cities_override is not None:
        max_cities = min(max_cities, max_cities_override)
        min_cities = min(min_cities, max_cities)
    
    # Capital regions get at least 1 city
    if is_capital_region:
        min_cities = max(1, min_cities)
    
    return random.randint(min_cities, max_cities)

def generate_regions_for_faction(profile, num_regions=2, faction_race="Human", female_percentage=50, male_percentage=50):
    """
    Generate multiple regions for a faction.
    First region is the capital region.
    """
    regions = []
    
    # Generate capital region first
    capital_region = generate_region(profile, 0, faction_race=faction_race, 
                                   female_percentage=female_percentage, male_percentage=male_percentage)
    regions.append(capital_region)
    
    # Generate additional regions
    for i in range(num_regions - 1):
        region = generate_region(profile, i + 1, faction_race=faction_race, 
                               female_percentage=female_percentage, male_percentage=male_percentage)
        regions.append(region)
    
    return regions

def generate_governor(profile, city_name, faction_race="Human", female_percentage=50, male_percentage=50):
    """Generate a governor for a city with faction-specific title and faction race."""
    governor_title_list = profile.get("governor_titles", GOVERNOR_TITLES)
    return _generate_named_character(governor_title_list, f"Governor of {city_name}", 
                                   race=faction_race, female_percentage=female_percentage, male_percentage=male_percentage)

def generate_city_stats(magic_level, is_capital=False):
    """
    Generate statistics for a city based on magic level.
    """
    # Base stats
    base_stats = {
        "climate": random.choices(
            list(CITY_CLIMATES.keys()), 
            weights=list(CITY_CLIMATES.values())
        )[0],
        "resources": random.choice([
            "Abundant", "Rich", "Moderate", "Poor", "Scarce"
        ]),
        "stability": random.randint(50, 100),  # Percentage
        "fortification": random.choice([
            "Unfortified", "Palisade", "Stone Walls", "Great Fortress", "Magical Barriers"
        ])
    }
    
    # Get infrastructure level and quality
    infra_level, infra_quality = get_infrastructure_level(magic_level, is_capital)
    base_stats["infrastructure"] = {
        "level": infra_level,
        "quality": infra_quality,
        "description": f"{infra_level} ({infra_quality}%)"
    }

    # Population ranges by magic level (in thousands)
    pop_ranges = {
        0: (1, 10),        # No magic: 1K to 10K
        1: (5, 25),        # Basic: 5K to 25K
        2: (10, 50),       # Intermediate: 10K to 50K
        3: (20, 100),      # Advanced: 20K to 100K
        4: (50, 200),      # Arcane: 50K to 200K
        5: (100, 500)      # Legendary: 100K to 500K
    }
    
    # Get base population range
    pop_range = pop_ranges.get(magic_level, (10, 50))
    
    # Calculate modifiers based on city conditions
    resource_modifiers = {
        "Abundant": 1.5,
        "Rich": 1.2,
        "Moderate": 1.0,
        "Poor": 0.7,
        "Scarce": 0.4
    }

    climate_modifiers = {
        "Temperate": 1.3,
        "Tropical": 1.1,
        "Forest": 1.0,
        "Mountain": 0.8,
        "Coastal": 1.2,
        "Arid": 0.7,
        "Arctic": 0.5,
        "Swamp": 0.6
    }

    # Infrastructure level modifiers
    infrastructure_level_modifiers = {
        "Legendary": 1.5,
        "Arcane": 1.3,
        "Advanced": 1.2,
        "Intermediate": 1.1,
        "Basic": 0.9,
        "None": 0.7
    }

    # Calculate total modifier
    resource_mod = resource_modifiers[base_stats["resources"]]
    climate_mod = climate_modifiers[base_stats["climate"]]
    stability_mod = base_stats["stability"] / 100
    
    infra_level_mod = infrastructure_level_modifiers[infra_level]
    infra_quality_mod = base_stats["infrastructure"]["quality"] / 100
    infrastructure_mod = infra_level_mod * infra_quality_mod

    total_modifier = (resource_mod * climate_mod * stability_mod * infrastructure_mod)

    # Generate base population
    base_population = random.uniform(*pop_range)

    # Apply modifier to population
    population = round(base_population * total_modifier, 1)

    # Combine all stats
    stats = {
        **base_stats,
        "population": f"{population}K",
        "population_modifier": round(total_modifier, 2)
    }
    
    return stats

def get_infrastructure_level(magic_level, is_capital=False):
    """
    Determines infrastructure level based on magic level and city importance.
    """
    max_infrastructure = {
        0: "None",
        1: "Basic",
        2: "Intermediate", 
        3: "Advanced",
        4: "Arcane",
        5: "Legendary"
    }
    
    quality_ranges = {
        0: (20, 50),
        1: (30, 60),
        2: (40, 70),
        3: (50, 80),
        4: (60, 90),
        5: (70, 100)
    }
    
    # Capital cities get better infrastructure
    if is_capital:
        level = max_infrastructure[magic_level]
        quality_min, quality_max = quality_ranges[magic_level]
        quality = random.randint(int((quality_min + quality_max) / 2), quality_max + 10)
    else:
        # Regular cities might be one level behind
        possible_levels = [
            max_infrastructure[max(0, magic_level - 1)],
            max_infrastructure[magic_level]
        ]
        weights = [30, 70]
        level = random.choices(possible_levels, weights=weights)[0]
        
        quality_min, quality_max = quality_ranges[magic_level]
        quality = random.randint(quality_min, quality_max)
    
    return level, min(100, quality)

def calculate_military_assets(faction):
    """
    Calculate military assets based on faction's cities and magic level.
    """
    # Calculate total population from all cities
    total_population = sum(
        float(city.get("stats", {}).get("population", "0K").rstrip("K"))
        for region in faction["regions"]
        for city in region["cities"]
    )
    magic_level = faction["magic"]["base_level"]
    
    # Base numbers adjusted by magic level and total population
    magic_multiplier = 1 + (magic_level * 0.2)  # Higher magic = more effective units
    
    # Calculate different types of military units (in hundreds/thousands)
    units = {
        "infantry": max(100, int(total_population * 2 * magic_multiplier)),
        "archers": max(50, int(total_population * 1 * magic_multiplier)),
        "cavalry": max(20, int(total_population * 0.5 * magic_multiplier)),
        "siege_engines": max(5, int(total_population * 0.1 * magic_multiplier)),
        "magical_units": max(10, int(total_population * 0.2 * magic_level)) if magic_level > 0 else 0
    }
    
    # Calculate personnel
    personnel = {
        "active_forces": sum(units.values()),
        "reserves": int(total_population * random.uniform(0.05, 0.1) * 1000),  # 5-10% of population
        "city_guards": int(total_population * random.uniform(0.02, 0.03) * 1000),  # 2-3% of population
        "support_staff": int(total_population * random.uniform(0.01, 0.02) * 1000)  # 1-2% of population
    }
    
    # Special forces and elite units
    special_forces = {
        "elite_units": max(50, int(personnel["active_forces"] * 0.05)),  # 5% of active forces
        "magical_specialists": max(10, int(total_population * magic_level * 2)) if magic_level > 0 else 0
    }
    
    return {
        "units": units,
        "personnel": personnel,
        "special_forces": special_forces,
        "total_military_personnel": sum(personnel.values()),
        "total_units": sum(units.values())
    }

def generate_faction_leader(profile, faction_race="Human", female_percentage=50, male_percentage=50):
    """Generates the primary faction leader with faction race and gender bias."""
    leader_title_list = profile.get("titles", LEADER_TITLES)
    return _generate_named_character(leader_title_list, "Faction Leader", race=faction_race, 
                                   female_percentage=female_percentage, male_percentage=male_percentage)

def generate_military_leader(profile, faction_race="Human", female_percentage=50, male_percentage=50):
    """Generates the head of the faction's military with faction race and gender bias."""
    mil_title_list = profile.get("military_titles", MILITARY_TITLES)
    return _generate_named_character(mil_title_list, "Head of Military", race=faction_race, 
                                   female_percentage=female_percentage, male_percentage=male_percentage)

def create_faction(profiles, include_races=False, female_percentage=50, male_percentage=50):
    """
    Select a random faction profile and generate complete faction data,
    including a richer set of named key personnel with optional race and gender bias.
    """
    profile = choose_faction_profile(profiles)
    faction_name = generate_faction_name(profile)
    
    # Determine faction race (mono-racial by default)
    if include_races:
        faction_race = random.choice(FANTASY_RACES)
    else:
        faction_race = "Human"
    
    # Generate magic levels
    magic_levels = determine_faction_magic_level(profile)
    
    # Determine number of regions
    num_regions = get_region_count(profile)
    
    # Generate regions (this also generates governors for cities)
    regions = generate_regions_for_faction(profile, num_regions, faction_race=faction_race, 
                                         female_percentage=female_percentage, male_percentage=male_percentage)
    
    # --- Assemble All Faction Personnel ---
    all_faction_personnel = []

    # 1. Faction Leader
    all_faction_personnel.append(generate_faction_leader(profile, faction_race=faction_race, 
                                                       female_percentage=female_percentage, male_percentage=male_percentage))
    
    # 2. Military Leader
    all_faction_personnel.append(generate_military_leader(profile, faction_race=faction_race, 
                                                        female_percentage=female_percentage, male_percentage=male_percentage))
    
    # 3. Add some basic staff (simplified for now)
    for _ in range(random.randint(3, 6)):
        role = random.choice(["Court Official", "Military Officer", "Administrator", "Advisor"])
        title_list = random.choice([ADMINISTRATIVE_TITLES, MILITARY_TITLES, MAGICAL_TITLES])
        all_faction_personnel.append(_generate_named_character(title_list, role, race=faction_race, 
                                                             female_percentage=female_percentage, male_percentage=male_percentage))

    # 4. Governors (extracted from generated regions)
    for region in regions:
        for city in region["cities"]:
            if "governor" in city and city["governor"]:
                all_faction_personnel.append(city["governor"])

    faction_data = {
        "faction_profile": profile["type"],
        "primary_traits": profile["primary_traits"],
        "notes": profile["notes"],
        "weight": profile["weight"],
        "faction_name": faction_name,
        "regions": regions,
        "characters": all_faction_personnel,
        "magic": magic_levels
    }
    
    # Calculate military assets based on all cities
    military_assets = calculate_military_assets(faction_data)
    faction_data["military_assets"] = military_assets
    
    return faction_data

def generate_fantasy_world(num_factions=5, include_races=False, female_percentage=50, male_percentage=50, world_type="balanced"):
    """
    Generates a fantasy setting with multiple factions.
    Each faction will have a defined set of leadership and staff roles, with optional race and gender bias.
    
    Parameters:
    - num_factions: Number of factions to generate (default 5)
    - include_races: Whether to include fantasy races (default False, uses only Humans)
    - female_percentage (int): Percentage for female gender (0-100)
    - male_percentage (int): Percentage for male gender (0-100)
    - world_type (str): Type of world to generate:
        - "balanced": Mix of all faction types (default)
        - "political": More kingdoms and independent states
        - "city_states": More city-states and trading entities
        - "magical": More magical academies and religious orders
    
    Returns a list of faction dictionaries configured for a fantasy setting.
    """
    faction_profiles = load_faction_profiles("Generators/fantasy_faction_profiles.json")
    
    # Adjust faction weights based on world type
    if world_type == "political":
        # Boost kingdoms and independent states
        for profile in faction_profiles:
            if profile["type"] in ["Kingdom", "Independent State"]:
                profile["weight"] *= 2
    elif world_type == "city_states":
        # Boost city-states and mercantile factions
        for profile in faction_profiles:
            if profile["type"] in ["City-State", "Guild Alliance"]:
                profile["weight"] *= 2
    elif world_type == "magical":
        # Boost magical and religious factions
        for profile in faction_profiles:
            if profile["type"] in ["Magical Academy", "Religious Order", "Dark Cult", "Druid Circle"]:
                profile["weight"] *= 2
    
    factions = []
    for _ in range(num_factions):
        new_faction = create_faction(faction_profiles, include_races=include_races, 
                                   female_percentage=female_percentage, male_percentage=male_percentage)
        factions.append(new_faction)
    
    return factions

def generate_political_world(num_factions=7, include_races=False, female_percentage=50, male_percentage=50):
    """
    Convenience function to generate a politically-focused world with more kingdoms and independent states.
    Recommended: 2-3 large kingdoms, 2-3 independent states, 1-2 city-states.
    """
    return generate_fantasy_world(num_factions, include_races, female_percentage, male_percentage, "political")

def generate_city_state_world(num_factions=6, include_races=False, female_percentage=50, male_percentage=50):
    """
    Convenience function to generate a world dominated by city-states and trading leagues.
    Think Italian Renaissance or Greek city-states.
    """
    return generate_fantasy_world(num_factions, include_races, female_percentage, male_percentage, "city_states")

def save_factions_to_file(factions, filename=None, timestamp=False):
    """
    Saves the generated fantasy factions to a JSON file.
    
    Parameters:
    - factions: List of faction dictionaries to save
    - filename: Name of the output file (optional)
    - timestamp: Whether to include timestamp in filename (default: False)
    """
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fantasy_factions_{timestamp_str}.json"
        else:
            filename = "generated_fantasy_factions.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(factions, f, indent=2, ensure_ascii=False)
        print(f"\nFantasy factions successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving fantasy factions to file: {e}")
        raise

def print_factions(factions):
    """
    Print detailed information about the generated fantasy factions.
    """
    for faction in factions:
        print("\n=== Fantasy Faction ===")
        print(f"Name: {faction['faction_name']}")
        print(f"Type: {faction['faction_profile']}")
        print(f"Magic Level: {faction['magic']['overall_level']}")
        
        print("\nRegions:")
        for region in faction["regions"]:
            region_tag = " (Capital Region)" if region.get("is_capital_region", False) else ""
            print(f"\n  {region['name']}{region_tag} ({region['terrain_type']})")
            print("  Cities:")
            for city in region["cities"]:
                capital_tag = " (Capital)" if city.get("is_capital", False) else ""
                print(f"    - {city['name']}{capital_tag}")
                print(f"      Governor: {city['governor']['display_name']} ({city['governor']['race']})")
                print(f"      Population: {city['stats']['population']}")
                print(f"      Climate: {city['stats']['climate']}")
                print(f"      Resources: {city['stats']['resources']}")
                print(f"      Fortification: {city['stats']['fortification']}")
                print(f"      Infrastructure: {city['stats']['infrastructure']['description']}")
                print(f"      Stability: {city['stats']['stability']}%")

        print("\nMilitary Assets:")
        assets = faction["military_assets"]
        print("  Units:")
        for unit_type, count in assets["units"].items():
            print(f"    {unit_type.replace('_', ' ').title()}: {count:,}")
        print("\n  Personnel:")
        print(f"    Active Forces: {assets['personnel']['active_forces']:,} troops")
        print(f"    Reserves: {assets['personnel']['reserves']:,} troops")
        print(f"    City Guards: {assets['personnel']['city_guards']:,} guards")
        print(f"    Support Staff: {assets['personnel']['support_staff']:,} personnel")
        print(f"    Elite Units: {assets['special_forces']['elite_units']:,} troops")
        if assets['special_forces']['magical_specialists'] > 0:
            print(f"    Magical Specialists: {assets['special_forces']['magical_specialists']:,} mages")
        print(f"\n  Total Military Personnel: {assets['total_military_personnel']:,}")
        
        print("\nMagic Schools:")
        for school, details in faction["magic"]["schools"].items():
            print(f"  {school}: {', '.join(details['developments'])}")
        
        print("\nKey Characters:")
        for character in faction["characters"]:
            if character.get('role'):
                if "Governor" not in character['role']:
                    race_info = f" ({character['race']})" if character.get('race') != 'Human' else ""
                    print(f"  - {character['display_name']}{race_info}")
                    print(f"    Role: {character['role']}")

if __name__ == "__main__":
    # Generate a standard fantasy setting
    factions = generate_fantasy_world(num_factions=5, include_races=True)
    
    # Print the factions
    print_factions(factions)
    
    # Save with timestamp
    save_factions_to_file(factions, timestamp=False)
    
    # Or save with custom name
    # save_factions_to_file(factions, "my_fantasy_world_factions.json", timestamp=False) 