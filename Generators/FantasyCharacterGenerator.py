from .FantasyGenerator import generate_character_name, generate_character_surname
import random
import json
from datetime import datetime
import re

class FantasyCharacter:
    # Class-level title lists for fantasy settings
    MILITARY_TITLES = {
        "high": {
            "male": ["General", "Marshal", "Knight-Commander", "Captain-General", "War Leader", "Lord Commander"],
            "female": ["General", "Marshal", "Knight-Commander", "Captain-General", "War Leader", "Lady Commander"],
            "neutral": ["Battle Master", "High Commander", "Champion", "Warlord"]
        },
        "mid": {
            "male": ["Captain", "Knight", "Lieutenant", "Sergeant-at-Arms", "Commander"],
            "female": ["Captain", "Dame", "Lieutenant", "Sergeant-at-Arms", "Commander"],
            "neutral": ["Squad Leader", "Battle Captain", "War Captain", "Guard Captain"]
        },
        "low": {
            "male": ["Sergeant", "Corporal", "Guard", "Soldier", "Recruit"],
            "female": ["Sergeant", "Corporal", "Guard", "Soldier", "Recruit"],
            "neutral": ["Scout", "Archer", "Spearman", "Warrior", "Fighter"]
        }
    }
    
    NOBLE_TITLES = {
        "high": {
            "male": ["King", "Duke", "Prince", "High Lord", "Sovereign", "Overlord"],
            "female": ["Queen", "Duchess", "Princess", "High Lady", "Sovereign", "Overlady"],
            "neutral": ["Regent", "Chancellor", "Ruler", "Monarch"]
        },
        "mid": {
            "male": ["Lord", "Baron", "Count", "Viscount", "Earl"],
            "female": ["Lady", "Baroness", "Countess", "Viscountess", "Countess"],
            "neutral": ["Noble", "Highborn", "Heir", "Scion"]
        },
        "low": {
            "male": ["Knight", "Squire", "Page", "Baronet"],
            "female": ["Dame", "Squire", "Page", "Baronetess"],
            "neutral": ["Noble Apprentice", "Court Page", "Noble Ward"]
        }
    }
    
    MAGICAL_TITLES = {
        "high": {
            "male": ["Archmage", "Grand Wizard", "High Sorcerer", "Master Enchanter", "Sage"],
            "female": ["Archmage", "Grand Sorceress", "High Sorceress", "Master Enchantress", "Sage"],
            "neutral": ["Grand Master", "High Mystic", "Elder Mage", "Arcane Master"]
        },
        "mid": {
            "male": ["Wizard", "Sorcerer", "Mage", "Enchanter", "Warlock"],
            "female": ["Sorceress", "Mage", "Enchantress", "Witch", "Mystic"],
            "neutral": ["Spellcaster", "Magician", "Conjurer", "Elementalist"]
        },
        "low": {
            "male": ["Apprentice", "Hedge Wizard", "Novice", "Acolyte"],
            "female": ["Apprentice", "Hedge Witch", "Novice", "Acolyte"],
            "neutral": ["Student", "Initiate", "Pupil", "Adept"]
        }
    }

    RELIGIOUS_TITLES = {
        "high": {
            "male": ["High Priest", "Archbishop", "Cardinal", "Pontiff", "Divine Oracle"],
            "female": ["High Priestess", "Archbishop", "Cardinal", "Pontiff", "Divine Oracle"],
            "neutral": ["Elder", "Divine Speaker", "Sacred Guardian", "Temple Master"]
        },
        "mid": {
            "male": ["Priest", "Cleric", "Chaplain", "Abbot", "Prior"],
            "female": ["Priestess", "Cleric", "Chaplain", "Abbess", "Prioress"],
            "neutral": ["Divine Servant", "Temple Guardian", "Sacred Keeper", "Holy Warrior"]
        },
        "low": {
            "male": ["Acolyte", "Novice", "Deacon", "Brother"],
            "female": ["Acolyte", "Novice", "Deacon", "Sister"],
            "neutral": ["Initiate", "Temple Student", "Sacred Apprentice", "Devotee"]
        }
    }

    # Occupational roles (not used as titles)
    OCCUPATIONAL_ROLES = {
        "high": {
            "male": ["Master Craftsman", "Guild Master", "Chief Scholar", "Royal Advisor"],
            "female": ["Master Craftswoman", "Guild Mistress", "Chief Scholar", "Royal Advisor"],
            "neutral": ["Master Trader", "Lore Keeper", "Court Advisor", "Master Healer", 
                       "Spymaster", "Royal Diplomat", "Master Alchemist"]
        },
        "mid": {
            "male": ["Craftsman", "Scholar", "Merchant", "Healer"],
            "female": ["Craftswoman", "Scholar", "Merchant", "Healer"],
            "neutral": ["Trader", "Scribe", "Diplomat", "Alchemist", 
                       "Herbalist", "Bard", "Ranger", "Blacksmith"]
        },
        "low": {
            "male": ["Apprentice", "Student", "Assistant", "Laborer"],
            "female": ["Apprentice", "Student", "Assistant", "Laborer"],
            "neutral": ["Helper", "Servant", "Messenger", "Stable Hand", 
                       "Kitchen Worker", "Farm Hand", "Courier"]
        }
    }

    def __init__(self, name, role, age=None):
        self.name = name
        self.role = role
        self.age = age
        self.title = None
        self.occupation = None
        self.gender = None
        self.race = "Human"  # Default race
        self.goals = []
        self.motivations = []
        self.flaws = []
        self.strengths = []
        self.background = ""
        self.arc = ""
        self.homeland = None
        self.home_region = None
        self.faction = None
        self.faction_role = None
        self.description = ""
        self.relationships = []
        self.magic_ability = None
        self.magic_school = None
        self.family = {
            'parents': [],
            'siblings': [],
            'spouse': None,
            'children': []
        }

    def set_title(self, title_type="noble", rank="mid"):
        """Set a title based on the specified type, rank, and character's gender."""
        # Handle occupational roles separately from formal titles
        if title_type == "specialized":
            self._set_occupation(rank)
            return

        title_list = getattr(self, f"{title_type.upper()}_TITLES", self.NOBLE_TITLES)
        if isinstance(title_list, dict):
            # Get the appropriate rank dictionary
            rank_dict = title_list.get(rank, title_list["mid"])
            
            # Determine which gender list to use
            if self.gender:
                gender_key = self.gender.lower()
                # If gender-specific titles exist, use them, otherwise fall back to neutral
                if gender_key in rank_dict:
                    available_titles = rank_dict[gender_key]
                else:
                    available_titles = rank_dict.get("neutral", [])
            else:
                # If no gender is set, use neutral titles
                available_titles = rank_dict.get("neutral", [])
            
            if available_titles:
                self.title = random.choice(available_titles)
            else:
                # Fallback to any available titles if no gender-specific ones exist
                all_titles = []
                for titles in rank_dict.values():
                    all_titles.extend(titles)
                if all_titles:
                    self.title = random.choice(all_titles)
        else:
            self.title = random.choice(title_list)

    def _set_occupation(self, rank="mid"):
        """Set an occupational role for the character."""
        rank_dict = self.OCCUPATIONAL_ROLES.get(rank, self.OCCUPATIONAL_ROLES["mid"])
        
        if self.gender:
            gender_key = self.gender.lower()
            if gender_key in rank_dict:
                available_roles = rank_dict[gender_key]
            else:
                available_roles = rank_dict.get("neutral", [])
        else:
            available_roles = rank_dict.get("neutral", [])
        
        if available_roles:
            self.occupation = random.choice(available_roles)
        else:
            all_roles = []
            for roles in rank_dict.values():
                all_roles.extend(roles)
            if all_roles:
                self.occupation = random.choice(all_roles)

    def set_magic_ability(self, magic_level=None, magic_school=None):
        """Set the character's magical abilities."""
        magic_levels = ["None", "Basic", "Intermediate", "Advanced", "Arcane", "Legendary"]
        magic_schools = ["Elemental", "Divine", "Arcane", "Nature", "Shadow", "Battle"]
        
        if magic_level:
            self.magic_ability = magic_level
        else:
            # Higher chance for lower magic levels
            weights = [40, 25, 15, 10, 7, 3]  # Weighted toward lower magic
            self.magic_ability = random.choices(magic_levels, weights=weights)[0]
        
        if self.magic_ability != "None":
            if magic_school:
                self.magic_school = magic_school
            else:
                self.magic_school = random.choice(magic_schools)

    @property
    def full_name(self):
        """Return the character's full name with title if set."""
        if self.title:
            return f"{self.title} {self.name}"
        return self.name

    def get_role_description(self):
        """Return a description of the character's role and occupation."""
        descriptions = []
        if self.occupation:
            descriptions.append(self.occupation)
        if self.magic_ability and self.magic_ability != "None":
            descriptions.append(f"{self.magic_ability} {self.magic_school} Magic User")
        return ", ".join(descriptions) if descriptions else ""

    def generate_family(self):
        """Generate family members for the character based on their age and role."""
        surname = self.name.split(" ")[-1] if " " in self.name else "UnknownSurname"
        
        # Parents - Always generate parents, but determine their status based on character's age and circumstances
        father_name = f"{generate_character_name('Male')} {surname}"
        mother_name = f"{generate_character_name('Female')} {surname}"
        
        # Determine parent status based on character's age and random factors
        def determine_parent_status(character_age):
            if not character_age:
                character_age = 30  # Default age if not set
            
            if character_age < 25:
                # Young character - parents very likely alive
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Cursed"],
                    weights=[80, 10, 6, 2, 2]
                )[0]
            elif character_age < 40:
                # Middle-aged character - parents likely alive but some chance of loss
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Cursed"],
                    weights=[65, 21, 8, 4, 2]
                )[0]
            elif character_age < 55:
                # Older character - higher chance parents are deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Cursed"],
                    weights=[45, 41, 8, 4, 2]
                )[0]
            else:
                # Very old character - parents likely deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Cursed"],
                    weights=[15, 71, 8, 4, 2]
                )[0]
        
        father_status = determine_parent_status(self.age)
        mother_status = determine_parent_status(self.age)
        
        self.family['parents'].append({
            'name': father_name,
            'relation': 'Father',
            'status': father_status,
            'gender': 'Male'
        })
        self.family['parents'].append({
            'name': mother_name,
            'relation': 'Mother',
            'status': mother_status,
            'gender': 'Female'
        })

        # Siblings
        num_siblings = random.randint(0, 3)  # Slightly more siblings in fantasy
        for _ in range(num_siblings):
            sibling_gender = random.choice(["Male", "Female"])
            sibling_name = f"{generate_character_name(sibling_gender)} {surname}"
            self.family['siblings'].append({
                'name': sibling_name,
                'relation': 'sibling',
                'gender': sibling_gender
            })

        # Spouse
        if self.age and self.age > 25 and random.random() < 0.6:  # 60% chance if > 25
            spouse_gender = "Female" if self.gender == "Male" else "Male"
            spouse_name = f"{generate_character_name(spouse_gender)} {generate_character_surname()}"
            self.family['spouse'] = {
                'name': spouse_name,
                'relation': 'spouse',
                'gender': spouse_gender
            }

        # Children
        if self.age and self.age > 28 and self.family['spouse'] and random.random() < 0.7:  # 70% chance if married & > 28
            num_children = random.randint(1, 3)  # Slightly more children in fantasy
            for _ in range(num_children):
                child_gender = random.choice(["Male", "Female"])
                child_name = f"{generate_character_name(child_gender)} {surname}"
                self.family['children'].append({
                    'name': child_name,
                    'relation': 'child',
                    'gender': child_gender
                })

def generate_fantasy_main_characters(num_characters=3, female_percentage=50, male_percentage=50, include_races=False):
    """
    Generate main fantasy characters using the name generation from FantasyGenerator.
    
    Args:
        num_characters (int): Number of characters to generate
        female_percentage (int): Percentage for female gender (0-100)
        male_percentage (int): Percentage for male gender (0-100)
        include_races (bool): Whether to include non-human races
    
    Returns:
        list: List of FantasyCharacter objects
    """
    MAX_CHARACTERS = 100
    if num_characters > MAX_CHARACTERS:
        raise ValueError(f"Cannot generate more than {MAX_CHARACTERS} characters. Requested: {num_characters}")

    # Validate and calculate gender weights directly from input percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"FANTASY_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"FANTASY_CHAR_GEN: Using direct gender bias: Female {female_percentage}%, Male {male_percentage}%")

    # Fantasy races
    fantasy_races = ["Human", "Elf", "Dwarf", "Halfling", "Orc", "Gnome", "Half-Elf", "Dragonborn"]
    
    # Try to load factions data
    factions_data = None
    try:
        with open("current_work/factions.json", 'r') as f:
            data = json.load(f)
            # Handle both direct list format and wrapped format
            if isinstance(data, list):
                factions_data = data
            elif isinstance(data, dict) and "factions" in data:
                factions_data = data["factions"]
            else:
                factions_data = data
            print(f"Loaded factions data: Found {len(factions_data)} factions")
    except FileNotFoundError:
        print("No factions file found - characters will be generated without faction affiliations")
    except json.JSONDecodeError as e:
        print(f"Error parsing factions.json: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error loading factions: {e}")
        return None

    # Get list of all regions if factions exist
    regions = []
    if factions_data:
        try:
            for faction in factions_data:
                for region in faction.get("regions", []):
                    regions.append({
                        "name": region.get("name", "Unknown"),
                        "faction": faction.get("faction_name", "Unknown"),
                        "terrain": region.get("terrain_type", "Unknown")
                    })
            print(f"Found {len(regions)} regions")
        except Exception as e:
            print(f"Error processing faction data: {e}")
            return None

    characters = []
    roles = ["protagonist", "deuteragonist", "antagonist"] + ["supporting"] * 7  # Allow up to 10 characters
    
    # Define character traits for each role (fantasy-themed)
    trait_sets = {
        "protagonist": {
            "goals": [
                "Defeat an ancient evil threatening the realm",
                "Find a legendary artifact to save their people",
                "Unite the warring kingdoms against a common threat",
                "Restore their family's lost honor and lands",
                "Master their magical abilities to protect the innocent"
            ],
            "motivations": [
                "Avenge their family's death",
                "Fulfill an ancient prophecy",
                "Protect their homeland from invasion",
                "Discover their true magical heritage",
                "Right the wrongs of the past"
            ],
            "flaws": [
                "Too trusting of strangers",
                "Haunted by visions of the future",
                "Struggles to control their magical power",
                "Overly protective of loved ones",
                "Refuses to retreat even when outmatched"
            ],
            "strengths": [
                "Natural leadership in battle",
                "Strong moral compass",
                "Exceptional magical potential",
                "Inspires loyalty in others",
                "Quick to adapt to new situations"
            ],
            "arcs": [
                "Learning to trust in their own power",
                "Balancing duty to the realm with personal desires",
                "Overcoming fear to embrace their destiny",
                "Learning the true cost of heroism",
                "Finding their place in a world of magic and politics"
            ]
        },
        "antagonist": {
            "goals": [
                "Conquer the known kingdoms",
                "Obtain forbidden magical knowledge",
                "Resurrect an ancient dark power",
                "Reshape the world according to their vision",
                "Achieve immortality through dark magic"
            ],
            "motivations": [
                "Revenge against those who wronged them",
                "Belief that only they can rule properly",
                "Fear of death and desire for eternal life",
                "Corrupted by dark magical influences",
                "Desire to prove their superiority"
            ],
            "flaws": [
                "Overwhelming pride and arrogance",
                "Cannot trust anyone completely",
                "Obsessed with power and control",
                "Underestimates the power of unity",
                "Corrupted by dark magic"
            ],
            "strengths": [
                "Brilliant strategic mind",
                "Vast magical knowledge",
                "Charismatic and persuasive",
                "Ruthlessly efficient",
                "Commands powerful dark forces"
            ],
            "arcs": [
                "Descent into complete darkness",
                "Tragic fall from a noble beginning",
                "Realizing the cost of their dark bargains",
                "Becoming the very evil they once fought",
                "Possible redemption through sacrifice"
            ]
        },
        "deuteragonist": {
            "goals": [
                "Support the protagonist's quest",
                "Prove their worth to their family",
                "Master their chosen craft or magic",
                "Protect their community",
                "Find their place in the larger conflict"
            ],
            "motivations": [
                "Loyalty to their friend",
                "Desire to make a difference",
                "Escape their humble origins",
                "Honor their family's legacy",
                "Seek adventure and glory"
            ],
            "flaws": [
                "Lives in the protagonist's shadow",
                "Impulsive and hot-headed",
                "Struggles with self-doubt",
                "Torn between conflicting loyalties",
                "Fear of not being good enough"
            ],
            "strengths": [
                "Specialized skills or knowledge",
                "Unwavering loyalty",
                "Practical problem-solving",
                "Strong moral foundation",
                "Complements the protagonist's abilities"
            ],
            "arcs": [
                "Finding their own path to heroism",
                "Learning to stand on their own",
                "Overcoming feelings of inadequacy",
                "Balancing friendship with duty",
                "Becoming a leader in their own right"
            ]
        },
        "supporting": {
            "goals": [
                "Establish a successful trading business",
                "Uncover ancient magical secrets",
                "Clear their family's tarnished name",
                "Find a cure for a magical curse",
                "Master forbidden magical arts",
                "Reform a corrupt institution",
                "Explore uncharted magical realms"
            ],
            "motivations": [
                "Thirst for magical knowledge",
                "Desire for wealth and status",
                "Search for belonging",
                "Need to prove themselves",
                "Love of adventure",
                "Religious or spiritual calling",
                "Family honor and duty"
            ],
            "flaws": [
                "Addicted to magical substances",
                "Overthinks every decision",
                "Harbors dangerous secrets",
                "Difficulty trusting others",
                "Reckless with magic",
                "Prejudiced against other races",
                "Haunted by past failures"
            ],
            "strengths": [
                "Expert in ancient lore",
                "Connections in the underworld",
                "Innovative magical techniques",
                "Understanding of different cultures",
                "Skilled in crafting or trade",
                "Healing and medical knowledge",
                "Survival and wilderness skills"
            ],
            "arcs": [
                "Finding purpose in chaos",
                "Learning to trust again",
                "Confronting their dark past",
                "Discovering hidden magical potential",
                "Breaking free from others' control",
                "Choosing between power and morality",
                "Accepting their true nature"
            ]
        }
    }

    # Track faction assignments for protagonist and antagonist
    protagonist_faction = None
    antagonist_faction = None
    supporting_character_count = 0

    for i in range(min(num_characters, len(roles))):
        try:
            # Generate gender first
            gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
            
            # Generate race
            if include_races:
                race = random.choice(fantasy_races)
            else:
                race = "Human"
            
            # Generate name using FantasyGenerator functions
            first_name = generate_character_name(gender)
            last_name = generate_character_surname()
            full_name = f"{first_name} {last_name}"
            
            role = roles[i]
            char = FantasyCharacter(full_name, role)
            char.gender = gender
            char.race = race
            
            # Assign age based on role and race
            min_age, max_age = 20, 40  # Default for Protagonist/Deuteragonist
            if role == "antagonist":
                min_age, max_age = 30, 60
            
            # Adjust for race (elves live longer, etc.)
            if race == "Elf":
                min_age += 50
                max_age += 150
            elif race == "Dwarf":
                min_age += 10
                max_age += 50
            elif race == "Halfling":
                min_age -= 5
                max_age += 20
            
            # Set appropriate title based on role
            if role == "protagonist":
                title_type = random.choices(
                    ["noble", "military", "magical"],
                    weights=[0.4, 0.4, 0.2]
                )[0]
                char.set_title(title_type, "high")
                min_age = max(min_age, 25)  # Ensure protagonist is experienced enough
            elif role == "deuteragonist":
                title_type = random.choices(
                    ["noble", "military", "magical", "religious"],
                    weights=[0.3, 0.3, 0.2, 0.2]
                )[0]
                rank = random.choices(["high", "mid"], weights=[0.3, 0.7])[0]
                char.set_title(title_type, rank)
                min_age = max(min_age, 22)
            elif role == "antagonist":
                # Antagonist title will come from faction generator or be set to high rank
                title_type = random.choices(
                    ["noble", "magical"],
                    weights=[0.6, 0.4]
                )[0]
                char.set_title(title_type, "high")
            elif role == "supporting":
                if random.random() < 0.6:  # 60% chance of any title
                    title_type = random.choices(
                        ["noble", "military", "magical", "religious", "specialized"],
                        weights=[0.2, 0.2, 0.2, 0.2, 0.2]
                    )[0]
                    
                    # Determine rank based on character's role in the story
                    if hasattr(char, 'faction_role') and char.faction_role == "Protagonist Ally":
                        rank = random.choices(["high", "mid", "low"], weights=[0.2, 0.5, 0.3])[0]
                    elif hasattr(char, 'faction_role') and char.faction_role == "Antagonist Ally":
                        rank = random.choices(["high", "mid", "low"], weights=[0.3, 0.4, 0.3])[0]
                    else:  # Neutral
                        rank = random.choices(["high", "mid", "low"], weights=[0.1, 0.4, 0.5])[0]
                    
                    char.set_title(title_type, rank)
                    
                    # Adjust minimum age based on title type and rank
                    if rank == "high":
                        min_age = max(min_age, 30)
                    elif rank == "mid":
                        min_age = max(min_age, 22)
                    else:  # low
                        min_age = max(min_age, 18)
            
            char.age = random.randint(min_age, max_age)
            
            # Set magic abilities
            if role == "protagonist":
                # Protagonist has higher chance of magic
                magic_chance = 0.8
            elif role == "antagonist":
                # Antagonist very likely to have magic
                magic_chance = 0.9
            else:
                # Others have moderate chance
                magic_chance = 0.4
            
            if random.random() < magic_chance:
                char.set_magic_ability()
            else:
                char.magic_ability = "None"
            
            # Generate family members
            char.generate_family()
            
            # Get random traits for this role
            traits = trait_sets[role]
            char.goals = [random.choice(traits["goals"])]
            char.motivations = [random.choice(traits["motivations"])]
            char.flaws = [random.choice(traits["flaws"])]
            char.strengths = [random.choice(traits["strengths"])]
            char.arc = random.choice(traits["arcs"])
            
            # Assign homeland based on role and existing faction assignments
            if regions:
                if role == "protagonist":
                    homeland = random.choice(regions)
                    protagonist_faction = homeland["faction"]
                elif role == "antagonist":
                    antagonist_regions = [r for r in regions if r["faction"] != protagonist_faction]
                    if not antagonist_regions and regions:
                        antagonist_regions = regions
                    homeland = random.choice(antagonist_regions)
                    antagonist_faction = homeland["faction"]
                elif role == "deuteragonist":
                    deuteragonist_regions = [r for r in regions if r["faction"] == protagonist_faction]
                    if not deuteragonist_regions:
                        deuteragonist_regions = regions
                    homeland = random.choice(deuteragonist_regions)
                else:  # supporting
                    supporting_character_count += 1
                    if supporting_character_count <= 2:
                        supporting_regions = [r for r in regions if r["faction"] == protagonist_faction]
                        if not supporting_regions:
                            supporting_regions = regions
                        homeland = random.choice(supporting_regions)
                        char.faction_role = "Protagonist Ally"
                    elif supporting_character_count <= 4:
                        supporting_regions = [r for r in regions if r["faction"] == antagonist_faction]
                        if not supporting_regions:
                            supporting_regions = regions
                        homeland = random.choice(supporting_regions)
                        char.faction_role = "Antagonist Ally"
                    else:
                        homeland = random.choice(regions)
                        char.faction_role = "Neutral"
                
                char.homeland = homeland["name"]
                char.home_region = homeland["terrain"]
                char.faction = homeland["faction"]
            
            characters.append(char)
            
        except Exception as e:
            print(f"Error generating character {i} ({role}): {e}")
            continue
    
    return characters

def print_fantasy_character(character):
    """Print fantasy character details in a formatted way."""
    print(f"\n{'='*50}")
    if character.title:
        print(f"=== {character.title} {character.name} ({character.role}) ===")
    else:
        print(f"=== {character.name} ({character.role}) ===")
    
    # Print basic info
    if character.gender:
        print(f"Gender: {character.gender}")
    if character.race:
        print(f"Race: {character.race}")
    if character.age:
        print(f"Age: {character.age}")
    
    # Print magic abilities
    if character.magic_ability and character.magic_ability != "None":
        magic_desc = f"Magic: {character.magic_ability}"
        if character.magic_school:
            magic_desc += f" ({character.magic_school})"
        print(magic_desc)
    
    # Print family information
    if character.family:
        print("\nFamily:")
        if character.family['parents']:
            parents_str = ", ".join([f"{p['name']} ({p['relation']}, {p['gender']}, {p.get('status', 'status unknown')})" 
                                   for p in character.family['parents']])
            print(f"Parents: {parents_str}")
        if character.family['siblings']:
            siblings_str = ", ".join([f"{s['name']} ({s['relation']}, {s['gender']})" 
                                    for s in character.family['siblings']])
            print(f"Siblings: {siblings_str}")
        if character.family['spouse']:
            print(f"Spouse: {character.family['spouse']['name']} ({character.family['spouse']['gender']})")
        if character.family['children']:
            children_str = ", ".join([f"{c['name']} ({c['relation']}, {c['gender']})" 
                                    for c in character.family['children']])
            print(f"Children: {children_str}")
    
    # Print faction information if it exists
    if character.faction:
        print(f"\nFaction: {character.faction}")
        if character.faction_role:
            print(f"Faction Role: {character.faction_role}")
    
    # Print location information if it exists
    if character.homeland:
        print(f"Homeland: {character.homeland}")
        if character.home_region:
            print(f"Home Region: {character.home_region}")
    
    # Print character traits
    print("\nCharacter Details:")
    print(f"Goals: {', '.join(character.goals)}")
    print(f"Motivations: {', '.join(character.motivations)}")
    print(f"Flaws: {', '.join(character.flaws)}")
    print(f"Strengths: {', '.join(character.strengths)}")
    
    # Print character arc
    print(f"\nCharacter Arc: {character.arc}")
    
    # Print background if it exists
    if character.background:
        print(f"\nBackground: {character.background}")
    
    print('='*50)

def save_fantasy_characters_to_file(characters, filename="fantasy_characters.json"):
    """Save fantasy characters to a JSON file."""
    # Convert characters to dictionary format
    char_dicts = []
    for char in characters:
        char_dict = {
            "name": char.name,
            "role": char.role,
            "gender": char.gender,
            "race": char.race,
            "age": char.age,
            "goals": char.goals,
            "motivations": char.motivations,
            "flaws": char.flaws,
            "strengths": char.strengths,
            "arc": char.arc,
            "background": char.background,
            "description": char.description,
            "family": char.family,
            "magic_ability": char.magic_ability,
            "magic_school": char.magic_school
        }
        
        # Add optional attributes if they exist
        if char.title:
            char_dict["title"] = char.title
        if char.occupation:
            char_dict["occupation"] = char.occupation
        if char.faction_role:
            char_dict["faction_role"] = char.faction_role
        if char.homeland:
            char_dict["homeland"] = char.homeland
        if char.home_region:
            char_dict["home_region"] = char.home_region
        if char.faction:
            char_dict["faction"] = char.faction
            
        char_dicts.append(char_dict)
    
    # Generate relationships between characters
    relationships = generate_fantasy_relationships(characters)
    
    # Create the full data structure
    data = {
        "characters": char_dicts,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "fantasy"
        }
    }
    
    # Save to file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"\nFantasy characters successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving fantasy characters to file: {e}")
        raise

def generate_fantasy_relationships(characters):
    """Generate relationships between fantasy characters."""
    relationships = []
    
    # Define possible relationship types for fantasy
    relationship_types = {
        "protagonist-deuteragonist": [
            "Childhood friends", "Mentor and apprentice", "Siblings", "Former rivals", 
            "Reluctant allies", "Knight and squire", "Fellow adventurers",
            "Rescued/savior", "Family members", "Guild companions", "Magic teacher and student"
        ],
        "protagonist-supporting-ally": [
            "Trusted advisor", "Loyal friend", "Family connection", "Owes life debt",
            "Battle companion", "Shared quest experience", "Romantic interest",
            "Magic tutor", "Information provider", "Moral guide", "Fellow guild member"
        ],
        "protagonist-antagonist": [
            "Former friends", "Bitter rivals", "Unknown to each other", "Family betrayal",
            "Ideological opposites", "Former mentor/student", "Competing for same goal",
            "Mutual respect", "Personal vendetta", "Prophetic enemies", "Corrupted ally"
        ],
        "antagonist-supporting-ally": [
            "Loyal lieutenant", "Fearful servant", "True believer", "Manipulated pawn",
            "Family member", "Co-conspirator", "Ambitious subordinate", "Dark enforcer",
            "Magic apprentice", "Childhood connection", "Corrupted former ally"
        ],
        "supporting-supporting": [
            "Close friends", "Rivals", "Romantic partners", "Guild colleagues",
            "Family members", "Mentor/student", "Uneasy alliance", "Secret connection",
            "Former enemies", "Complementary skills", "Magic study partners"
        ]
    }
    
    # Get character by role
    protagonist = next((c for c in characters if c.role == "protagonist"), None)
    antagonist = next((c for c in characters if c.role == "antagonist"), None)
    deuteragonist = next((c for c in characters if c.role == "deuteragonist"), None)
    supporting_chars = [c for c in characters if c.role == "supporting"]
    
    # Generate protagonist-deuteragonist relationship
    if protagonist and deuteragonist:
        relationship = {
            "character1": protagonist.name,
            "character2": deuteragonist.name,
            "type": random.choice(relationship_types["protagonist-deuteragonist"]),
            "description": f"They share a common quest but sometimes disagree on methods."
        }
        relationships.append(relationship)
    
    # Generate protagonist-antagonist relationship
    if protagonist and antagonist:
        relationship = {
            "character1": protagonist.name,
            "character2": antagonist.name,
            "type": random.choice(relationship_types["protagonist-antagonist"]),
            "description": f"Their conflict drives the central story."
        }
        relationships.append(relationship)
    
    # Generate protagonist-supporting relationships for allies
    if protagonist:
        for char in supporting_chars:
            if hasattr(char, 'faction_role') and char.faction_role == "Protagonist Ally":
                relationship = {
                    "character1": protagonist.name,
                    "character2": char.name,
                    "type": random.choice(relationship_types["protagonist-supporting-ally"]),
                    "description": f"They work together toward common goals."
                }
                relationships.append(relationship)
    
    # Generate antagonist-supporting relationships for allies
    if antagonist:
        for char in supporting_chars:
            if hasattr(char, 'faction_role') and char.faction_role == "Antagonist Ally":
                relationship = {
                    "character1": antagonist.name,
                    "character2": char.name,
                    "type": random.choice(relationship_types["antagonist-supporting-ally"]),
                    "description": f"They serve the antagonist's dark agenda."
                }
                relationships.append(relationship)
    
    # Generate relationships between supporting characters
    for i, char1 in enumerate(supporting_chars):
        for char2 in supporting_chars[i+1:]:
            # Higher chance of relationship if in same faction
            if char1.faction == char2.faction and random.random() < 0.8:
                relationship = {
                    "character1": char1.name,
                    "character2": char2.name,
                    "type": random.choice(relationship_types["supporting-supporting"]),
                    "description": f"They share faction loyalty and work together."
                }
                relationships.append(relationship)
            # Lower chance if different factions
            elif random.random() < 0.3:
                relationship = {
                    "character1": char1.name,
                    "character2": char2.name,
                    "type": random.choice(relationship_types["supporting-supporting"]),
                    "description": f"Despite faction differences, they have a connection."
                }
                relationships.append(relationship)
    
    return relationships 