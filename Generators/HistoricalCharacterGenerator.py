from .HistoricalGenerator import generate_faction_name, ADJECTIVES
import random
import json
from datetime import datetime
import re

class HistoricalCharacter:
    # Class-level title lists for historical settings
    NOBLE_TITLES = {
        "high": {
            "male": ["King", "Emperor", "Duke", "Prince", "Archduke", "Grand Duke", "Margrave"],
            "female": ["Queen", "Empress", "Duchess", "Princess", "Archduchess", "Grand Duchess", "Margravine"],
            "neutral": ["Sovereign", "Ruler", "Monarch", "Regent", "Chancellor"]
        },
        "mid": {
            "male": ["Count", "Earl", "Baron", "Viscount", "Lord", "Knight", "Baronet"],
            "female": ["Countess", "Baroness", "Viscountess", "Lady", "Dame"],
            "neutral": ["Noble", "Highborn", "Heir", "Scion"]
        },
        "low": {
            "male": ["Squire", "Page", "Gentleman"],
            "female": ["Squire", "Page", "Gentlewoman"],
            "neutral": ["Noble Apprentice", "Court Page", "Noble Ward", "Courtier"]
        }
    }
    
    MILITARY_TITLES = {
        "high": {
            "male": ["General", "Marshal", "Admiral", "Commander", "Colonel", "Knight-Commander"],
            "female": ["General", "Marshal", "Admiral", "Commander", "Colonel", "Dame Commander"],
            "neutral": ["High Commander", "War Leader", "Battle Master", "Supreme Commander"]
        },
        "mid": {
            "male": ["Captain", "Major", "Lieutenant", "Knight", "Sergeant-Major"],
            "female": ["Captain", "Major", "Lieutenant", "Dame", "Sergeant-Major"],
            "neutral": ["Squad Leader", "Battle Captain", "War Captain", "Officer"]
        },
        "low": {
            "male": ["Sergeant", "Corporal", "Soldier", "Guard", "Recruit"],
            "female": ["Sergeant", "Corporal", "Soldier", "Guard", "Recruit"],
            "neutral": ["Scout", "Archer", "Warrior", "Fighter", "Defender"]
        }
    }
    
    RELIGIOUS_TITLES = {
        "high": {
            "male": ["Archbishop", "Cardinal", "Bishop", "Abbot", "Prior", "High Priest"],
            "female": ["Archbishop", "Cardinal", "Bishop", "Abbess", "Prioress", "High Priestess"],
            "neutral": ["Elder", "Divine Speaker", "Sacred Guardian", "Temple Master"]
        },
        "mid": {
            "male": ["Priest", "Father", "Brother", "Chaplain", "Deacon"],
            "female": ["Priestess", "Mother", "Sister", "Chaplain", "Deacon"],
            "neutral": ["Cleric", "Divine Servant", "Temple Guardian", "Sacred Keeper"]
        },
        "low": {
            "male": ["Acolyte", "Novice", "Brother", "Monk"],
            "female": ["Acolyte", "Novice", "Sister", "Nun"],
            "neutral": ["Initiate", "Temple Student", "Sacred Apprentice", "Devotee"]
        }
    }

    SCHOLARLY_TITLES = {
        "high": {
            "male": ["Master", "Professor", "Doctor", "Scholar", "Philosopher"],
            "female": ["Master", "Professor", "Doctor", "Scholar", "Philosopher"],
            "neutral": ["Grand Scholar", "Master Teacher", "Chief Researcher", "Academic Leader"]
        },
        "mid": {
            "male": ["Teacher", "Tutor", "Lecturer", "Researcher"],
            "female": ["Teacher", "Tutor", "Lecturer", "Researcher"],
            "neutral": ["Instructor", "Academic", "Scholar", "Learned One"]
        },
        "low": {
            "male": ["Student", "Apprentice", "Pupil", "Assistant"],
            "female": ["Student", "Apprentice", "Pupil", "Assistant"],
            "neutral": ["Learner", "Novice Scholar", "Academic Apprentice", "Study Assistant"]
        }
    }

    # Occupational roles (not used as titles)
    OCCUPATIONAL_ROLES = {
        "high": {
            "male": ["Master Craftsman", "Guild Master", "Chief Merchant", "Royal Advisor"],
            "female": ["Master Craftswoman", "Guild Mistress", "Chief Merchant", "Royal Advisor"],
            "neutral": ["Master Trader", "Court Advisor", "Master Healer", "Spymaster", 
                       "Royal Diplomat", "Master Alchemist", "Chief Engineer"]
        },
        "mid": {
            "male": ["Craftsman", "Merchant", "Healer", "Diplomat"],
            "female": ["Craftswoman", "Merchant", "Healer", "Diplomat"],
            "neutral": ["Trader", "Scribe", "Alchemist", "Herbalist", 
                       "Bard", "Ranger", "Blacksmith", "Engineer"]
        },
        "low": {
            "male": ["Apprentice", "Assistant", "Laborer", "Servant"],
            "female": ["Apprentice", "Assistant", "Laborer", "Servant"],
            "neutral": ["Helper", "Messenger", "Stable Hand", "Kitchen Worker", 
                       "Farm Hand", "Courier", "Porter"]
        }
    }

    def __init__(self, name, role, age=None):
        self.name = name
        self.role = role
        self.age = age
        self.title = None
        self.occupation = None
        self.gender = None
        self.social_class = "Common"  # Common, Noble, Royal
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
        self.historical_period = None
        self.education_level = None
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

    def set_social_class(self, social_class=None):
        """Set the character's social class."""
        if social_class:
            self.social_class = social_class
        else:
            # Determine based on role
            if self.role == "protagonist":
                self.social_class = random.choices(
                    ["Noble", "Common", "Royal"],
                    weights=[0.6, 0.3, 0.1]
                )[0]
            elif self.role == "antagonist":
                self.social_class = random.choices(
                    ["Noble", "Royal", "Common"],
                    weights=[0.5, 0.4, 0.1]
                )[0]
            else:
                self.social_class = random.choices(
                    ["Common", "Noble", "Royal"],
                    weights=[0.7, 0.25, 0.05]
                )[0]

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
        if self.social_class and self.social_class != "Common":
            descriptions.append(f"{self.social_class} Class")
        return ", ".join(descriptions) if descriptions else ""

    def generate_family(self):
        """Generate family members for the character based on their age, role, and social class."""
        surname = self.name.split(" ")[-1] if " " in self.name else "UnknownSurname"
        
        # Parents - Always generate parents, but determine their status based on character's age and circumstances
        father_name = f"{generate_historical_name('Male')} {surname}"
        mother_name = f"{generate_historical_name('Female')} {surname}"
        
        # Determine parent status based on character's age and random factors
        def determine_parent_status(character_age):
            if not character_age:
                character_age = 30  # Default age if not set
            
            if character_age < 25:
                # Young character - parents very likely alive
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Exiled", "In Hiding"],
                    weights=[78, 12, 5, 2, 2, 1]
                )[0]
            elif character_age < 40:
                # Middle-aged character - parents likely alive but some chance of loss
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Exiled", "In Hiding"],
                    weights=[62, 25, 7, 3, 2, 1]
                )[0]
            elif character_age < 55:
                # Older character - higher chance parents are deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Exiled", "In Hiding"],
                    weights=[42, 46, 7, 3, 1, 1]
                )[0]
            else:
                # Very old character - parents likely deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "Exiled", "In Hiding"],
                    weights=[12, 76, 7, 3, 1, 1]
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

        # Siblings (more siblings for noble families)
        max_siblings = 3 if self.social_class == "Noble" else 2
        num_siblings = random.randint(0, max_siblings)
        for _ in range(num_siblings):
            sibling_gender = random.choice(["Male", "Female"])
            sibling_name = f"{generate_historical_name(sibling_gender)} {surname}"
            self.family['siblings'].append({
                'name': sibling_name,
                'relation': 'sibling',
                'gender': sibling_gender
            })

        # Spouse (marriage age varies by social class and period)
        min_marriage_age = 16 if self.social_class == "Noble" else 20
        if self.age and self.age > min_marriage_age and random.random() < 0.6:  # 60% chance
            spouse_gender = "Female" if self.gender == "Male" else "Male"
            spouse_surname = generate_historical_surname()
            spouse_name = f"{generate_historical_name(spouse_gender)} {spouse_surname}"
            self.family['spouse'] = {
                'name': spouse_name,
                'relation': 'spouse',
                'gender': spouse_gender
            }

        # Children (more children for noble families)
        if self.age and self.age > 25 and self.family['spouse'] and random.random() < 0.7:  # 70% chance if married & > 25
            max_children = 4 if self.social_class == "Noble" else 2
            num_children = random.randint(1, max_children)
            for _ in range(num_children):
                child_gender = random.choice(["Male", "Female"])
                child_name = f"{generate_historical_name(child_gender)} {surname}"
                self.family['children'].append({
                    'name': child_name,
                    'relation': 'child',
                    'gender': child_gender
                })

def generate_historical_name(gender=None):
    """Generate a historical name based on gender"""
    # Mix of names from various historical periods
    male_names = [
        # Medieval/Renaissance
        "William", "Henry", "Edward", "Richard", "Thomas", "John", "Robert", "Geoffrey", "Edmund", "Arthur",
        # Victorian Era
        "Charles", "Albert", "Frederick", "George", "James", "Alexander", "Theodore", "Benjamin", "Samuel", "Daniel",
        # Ancient/Classical
        "Marcus", "Julius", "Augustus", "Constantine", "Maximus", "Lucius", "Gaius", "Antonius", "Cassius", "Brutus",
        # Various periods
        "Leonardo", "Michelangelo", "Galileo", "Napoleon", "Nelson", "Byron", "Shelley", "Keats", "Dante"
    ]
    
    female_names = [
        # Medieval/Renaissance
        "Eleanor", "Isabella", "Catherine", "Margaret", "Elizabeth", "Anne", "Mary", "Joan", "Beatrice", "Guinevere",
        # Victorian Era
        "Victoria", "Charlotte", "Emily", "Jane", "Caroline", "Sophia", "Adelaide", "Cordelia", "Evangeline", "Josephine",
        # Ancient/Classical
        "Cleopatra", "Livia", "Julia", "Octavia", "Agrippina", "Lucretia", "Cornelia", "Portia", "Calpurnia", "Fulvia",
        # Various periods
        "Anastasia", "Katarina", "Francesca", "Lucrezia", "Bianca", "Violante", "Seraphina", "Arabella", "Rosalind", "Cordelia"
    ]
    
    if gender == "Male":
        return random.choice(male_names)
    elif gender == "Female":
        return random.choice(female_names)
    else:
        # If no gender specified, return from combined list (for backwards compatibility)
        return random.choice(male_names + female_names)

def generate_historical_surname():
    """Generate a historical surname"""
    surnames = [
        # English/European nobility
        "Plantagenet", "Tudor", "Stuart", "Windsor", "Medici", "Borgia", "Habsburg", "Bourbon", "Valois", "Anjou",
        # Common historical surnames
        "Blackwood", "Ashford", "Pemberton", "Worthington", "Kensington", "Harrington", "Wellington", "Covington", "Huntington", "Lexington","Wellington",
        # Occupational/descriptive
        "Blacksmith", "Fletcher", "Cooper", "Mason", "Baker", "Miller", "Carpenter", "Weaver", "Tanner", "Merchant",
        # Geographic
        "Northwood", "Eastwood", "Westbrook", "Southfield", "Riverside", "Hillcrest", "Valmont", "Beaumont", "Fairfax", "Montague"
    ]
    return random.choice(surnames)

def generate_historical_main_characters(num_characters=3, female_percentage=50, male_percentage=50):
    """
    Generate main historical characters using comprehensive character generation.
    
    Args:
        num_characters (int): Number of characters to generate
        female_percentage (int): Percentage for female gender (0-100)
        male_percentage (int): Percentage for male gender (0-100)
    
    Returns:
        list: List of HistoricalCharacter objects
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
        print(f"HISTORICAL_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"HISTORICAL_CHAR_GEN: Using direct gender bias: Female {female_percentage}%, Male {male_percentage}%")

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

    # Get list of all territories if factions exist
    territories = []
    if factions_data:
        try:
            for faction in factions_data:
                territory = faction.get("territory", "Unknown Territory")
                territories.append({
                    "name": territory,
                    "faction": faction.get("faction_name", "Unknown"),
                    "type": faction.get("faction_type", "Unknown")
                })
            print(f"Found {len(territories)} territories")
        except Exception as e:
            print(f"Error processing faction data: {e}")
            return None

    characters = []
    roles = ["protagonist", "deuteragonist", "antagonist"] + ["supporting"] * 7  # Allow up to 10 characters
    
    # Define character traits for each role (historical-themed)
    trait_sets = {
        "protagonist": {
            "goals": [
                "Restore their family's lost honor and lands",
                "Unite warring factions against a common threat",
                "Overthrow a tyrannical ruler",
                "Protect their homeland from invasion",
                "Discover their true noble heritage",
                "Reform corrupt institutions",
                "Secure a strategic marriage alliance",
                "Reclaim their rightful throne"
            ],
            "motivations": [
                "Avenge their family's death",
                "Fulfill an ancient prophecy",
                "Protect their people from oppression",
                "Restore justice to the realm",
                "Honor their ancestors' legacy",
                "Prove their worthiness to rule",
                "Defend their faith and beliefs",
                "Right the wrongs of the past"
            ],
            "flaws": [
                "Too bound by honor and tradition",
                "Overly trusting of noble peers",
                "Haunted by family shame",
                "Struggles with the burden of leadership",
                "Too idealistic about human nature",
                "Torn between duty and personal desires",
                "Prejudiced against lower social classes",
                "Refuses to compromise principles"
            ],
            "strengths": [
                "Natural leadership in crisis",
                "Strong moral compass",
                "Excellent education and culture",
                "Inspiring presence",
                "Strategic military mind",
                "Diplomatic skills",
                "Unwavering courage",
                "Deep sense of justice"
            ],
            "arcs": [
                "Learning to lead with wisdom, not just authority",
                "Balancing duty to family with duty to people",
                "Overcoming prejudices to unite different classes",
                "Learning the true cost of power",
                "Finding their place in a changing world",
                "Choosing between personal happiness and duty",
                "Learning to trust others despite betrayal",
                "Discovering that true nobility comes from actions"
            ]
        },
        "antagonist": {
            "goals": [
                "Seize control of the throne",
                "Eliminate rival noble houses",
                "Accumulate vast wealth and power",
                "Reshape society according to their vision",
                "Achieve immortality through dark means",
                "Conquer neighboring kingdoms",
                "Destroy the current social order",
                "Prove their superiority over all others"
            ],
            "motivations": [
                "Revenge against those who wronged their family",
                "Belief in their divine right to rule",
                "Fear of losing their current position",
                "Desire to prove their superiority",
                "Twisted sense of justice",
                "Ambition for ultimate power",
                "Hatred of the current system",
                "Need to control everything around them"
            ],
            "flaws": [
                "Overwhelming pride and arrogance",
                "Cannot trust anyone completely",
                "Obsessed with power and control",
                "Underestimates the common people",
                "Refuses to admit mistakes",
                "Paranoid about threats to their position",
                "Cruel and ruthless methods",
                "Believes ends justify any means"
            ],
            "strengths": [
                "Brilliant strategic mind",
                "Vast resources and influence",
                "Charismatic and persuasive",
                "Ruthlessly efficient",
                "Deep knowledge of politics",
                "Ability to manipulate others",
                "Strong will and determination",
                "Excellent at reading people's weaknesses"
            ],
            "arcs": [
                "Descent into complete tyranny",
                "Tragic fall from noble intentions",
                "Realizing the cost of their ambition",
                "Becoming the very evil they once fought",
                "Possible path to redemption through sacrifice",
                "Learning that power without love is empty",
                "Discovering their methods have corrupted them",
                "Final confrontation with their past self"
            ]
        },
        "deuteragonist": {
            "goals": [
                "Support the protagonist's noble cause",
                "Prove their worth to their family",
                "Master their chosen profession",
                "Protect their community from harm",
                "Find their place in the larger conflict",
                "Earn recognition for their abilities",
                "Bridge differences between social classes",
                "Preserve important knowledge or traditions"
            ],
            "motivations": [
                "Loyalty to their friend and leader",
                "Desire to make a meaningful difference",
                "Escape their humble origins",
                "Honor their family's service",
                "Seek adventure and purpose",
                "Prove that common birth doesn't limit potential",
                "Protect those who cannot protect themselves",
                "Build a better future for their children"
            ],
            "flaws": [
                "Lives in the protagonist's shadow",
                "Impulsive and hot-headed",
                "Struggles with feelings of inadequacy",
                "Torn between conflicting loyalties",
                "Fear of not being good enough",
                "Sometimes acts without thinking",
                "Jealous of others' advantages",
                "Difficulty accepting help from others"
            ],
            "strengths": [
                "Specialized skills and knowledge",
                "Unwavering loyalty to friends",
                "Practical problem-solving ability",
                "Strong moral foundation",
                "Complements the protagonist's abilities",
                "Understanding of common people",
                "Courage in the face of danger",
                "Ability to see simple solutions"
            ],
            "arcs": [
                "Finding their own path to greatness",
                "Learning to stand on their own",
                "Overcoming feelings of inadequacy",
                "Balancing friendship with personal goals",
                "Becoming a leader in their own right",
                "Learning to value their unique contributions",
                "Discovering hidden potential within themselves",
                "Finding confidence in their own worth"
            ]
        },
        "supporting": {
            "goals": [
                "Establish a successful trading business",
                "Uncover ancient historical secrets",
                "Clear their family's tarnished name",
                "Find a cure for a mysterious plague",
                "Master forbidden knowledge",
                "Reform a corrupt institution",
                "Explore uncharted territories",
                "Preserve their cultural heritage"
            ],
            "motivations": [
                "Thirst for knowledge and learning",
                "Desire for wealth and status",
                "Search for belonging and acceptance",
                "Need to prove themselves worthy",
                "Love of adventure and discovery",
                "Religious or spiritual calling",
                "Family honor and duty",
                "Desire to help others"
            ],
            "flaws": [
                "Addicted to gambling or drink",
                "Overthinks every decision",
                "Harbors dangerous secrets",
                "Difficulty trusting others",
                "Reckless with their safety",
                "Prejudiced against other cultures",
                "Haunted by past failures",
                "Too focused on personal gain"
            ],
            "strengths": [
                "Expert in ancient lore",
                "Connections in various social circles",
                "Innovative thinking",
                "Understanding of different cultures",
                "Skilled in their chosen craft",
                "Healing and medical knowledge",
                "Survival and practical skills",
                "Ability to blend into any situation"
            ],
            "arcs": [
                "Finding purpose beyond personal gain",
                "Learning to trust again after betrayal",
                "Confronting their dark past",
                "Discovering hidden potential",
                "Breaking free from others' control",
                "Choosing between safety and doing right",
                "Accepting their true nature",
                "Finding family among friends"
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
            
            # Generate name
            first_name = generate_historical_name(gender)
            last_name = generate_historical_surname()
            full_name = f"{first_name} {last_name}"
            
            role = roles[i]
            char = HistoricalCharacter(full_name, role)
            char.gender = gender
            
            # Set social class based on role
            char.set_social_class()
            
            # Assign age based on role and social class
            min_age, max_age = 20, 45  # Default for Protagonist/Deuteragonist
            if role == "antagonist":
                min_age, max_age = 30, 60
            
            # Adjust for social class (nobles marry and take responsibility earlier)
            if char.social_class == "Noble":
                min_age -= 2
            elif char.social_class == "Royal":
                min_age -= 5
            
            # Set appropriate title based on role and social class
            if role == "protagonist":
                if char.social_class == "Royal":
                    char.set_title("noble", "high")
                elif char.social_class == "Noble":
                    char.set_title("noble", random.choices(["high", "mid"], weights=[0.3, 0.7])[0])
                else:
                    if random.random() < 0.4:  # 40% chance of military title for common protagonists
                        char.set_title("military", "mid")
                min_age = max(min_age, 25)  # Ensure protagonist is experienced enough
            elif role == "deuteragonist":
                if char.social_class == "Noble":
                    title_type = random.choices(
                        ["noble", "military", "religious", "scholarly"],
                        weights=[0.4, 0.3, 0.15, 0.15]
                    )[0]
                    rank = random.choices(["high", "mid"], weights=[0.2, 0.8])[0]
                    char.set_title(title_type, rank)
                else:
                    if random.random() < 0.5:  # 50% chance of some title
                        title_type = random.choices(
                            ["military", "religious", "scholarly"],
                            weights=[0.5, 0.3, 0.2]
                        )[0]
                        char.set_title(title_type, "mid")
                min_age = max(min_age, 22)
            elif role == "antagonist":
                if char.social_class in ["Noble", "Royal"]:
                    char.set_title("noble", "high")
                else:
                    # Ambitious commoner antagonist
                    title_type = random.choices(
                        ["military", "religious", "scholarly"],
                        weights=[0.5, 0.3, 0.2]
                    )[0]
                    char.set_title(title_type, "high")
            elif role == "supporting":
                if random.random() < 0.6:  # 60% chance of any title
                    title_type = random.choices(
                        ["noble", "military", "religious", "scholarly", "specialized"],
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
            
            # Set historical period
            char.historical_period = random.choice([
                "Medieval", "Renaissance", "Early Modern", "Classical Antiquity", 
                "Late Medieval", "High Medieval", "Byzantine", "Carolingian"
            ])
            
            # Set education level based on social class
            if char.social_class == "Royal":
                char.education_level = random.choice(["Excellent", "Superior"])
            elif char.social_class == "Noble":
                char.education_level = random.choice(["Good", "Excellent"])
            else:
                char.education_level = random.choice(["Basic", "Good", "Self-taught"])
            
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
            if territories:
                if role == "protagonist":
                    homeland = random.choice(territories)
                    protagonist_faction = homeland["faction"]
                elif role == "antagonist":
                    antagonist_territories = [t for t in territories if t["faction"] != protagonist_faction]
                    if not antagonist_territories and territories:
                        antagonist_territories = territories
                    homeland = random.choice(antagonist_territories)
                    antagonist_faction = homeland["faction"]
                elif role == "deuteragonist":
                    deuteragonist_territories = [t for t in territories if t["faction"] == protagonist_faction]
                    if not deuteragonist_territories:
                        deuteragonist_territories = territories
                    homeland = random.choice(deuteragonist_territories)
                else:  # supporting
                    supporting_character_count += 1
                    if supporting_character_count <= 2:
                        supporting_territories = [t for t in territories if t["faction"] == protagonist_faction]
                        if not supporting_territories:
                            supporting_territories = territories
                        homeland = random.choice(supporting_territories)
                        char.faction_role = "Protagonist Ally"
                    elif supporting_character_count <= 4:
                        supporting_territories = [t for t in territories if t["faction"] == antagonist_faction]
                        if not supporting_territories:
                            supporting_territories = territories
                        homeland = random.choice(supporting_territories)
                        char.faction_role = "Antagonist Ally"
                    else:
                        homeland = random.choice(territories)
                        char.faction_role = "Neutral"
                
                char.homeland = homeland["name"]
                char.home_region = homeland["type"]
                char.faction = homeland["faction"]
            
            characters.append(char)
            
        except Exception as e:
            print(f"Error generating character {i} ({role}): {e}")
            continue
    
    return characters

def print_historical_character(character):
    """Print historical character details in a formatted way."""
    print(f"\n{'='*50}")
    if character.title:
        print(f"=== {character.title} {character.name} ({character.role}) ===")
    else:
        print(f"=== {character.name} ({character.role}) ===")
    
    # Print basic info
    if character.gender:
        print(f"Gender: {character.gender}")
    if character.age:
        print(f"Age: {character.age}")
    if character.social_class:
        print(f"Social Class: {character.social_class}")
    if character.historical_period:
        print(f"Historical Period: {character.historical_period}")
    if character.education_level:
        print(f"Education: {character.education_level}")
    
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

def save_historical_characters_to_file(characters, filename="historical_characters.json"):
    """Save historical characters to a JSON file."""
    # Convert characters to dictionary format
    char_dicts = []
    for char in characters:
        char_dict = {
            "name": char.name,
            "role": char.role,
            "gender": char.gender,
            "age": char.age,
            "social_class": char.social_class,
            "historical_period": char.historical_period,
            "education_level": char.education_level,
            "goals": char.goals,
            "motivations": char.motivations,
            "flaws": char.flaws,
            "strengths": char.strengths,
            "arc": char.arc,
            "background": char.background,
            "description": char.description,
            "family": char.family
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
    relationships = generate_historical_relationships(characters)
    
    # Create the full data structure
    data = {
        "characters": char_dicts,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "Historical Fiction"
        }
    }
    
    # Save to file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"\nHistorical characters successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving historical characters to file: {e}")
        raise

def generate_historical_relationships(characters):
    """Generate relationships between historical characters."""
    relationships = []
    
    # Define possible relationship types for historical fiction
    relationship_types = {
        "protagonist-deuteragonist": [
            "Childhood friends", "Mentor and student", "Siblings", "Former rivals", 
            "Reluctant allies", "Knight and squire", "Fellow courtiers",
            "Rescued/savior", "Family members", "Military comrades", "Court companions"
        ],
        "protagonist-supporting-ally": [
            "Trusted advisor", "Loyal friend", "Family connection", "Owes life debt",
            "Battle companion", "Shared noble cause", "Romantic interest",
            "Court tutor", "Information provider", "Moral guide", "Fellow noble"
        ],
        "protagonist-antagonist": [
            "Former friends", "Bitter rivals", "Unknown to each other", "Family betrayal",
            "Ideological opposites", "Former mentor/student", "Competing for throne",
            "Mutual respect", "Personal vendetta", "Political enemies", "Corrupted ally"
        ],
        "antagonist-supporting-ally": [
            "Loyal lieutenant", "Fearful servant", "True believer", "Manipulated pawn",
            "Family member", "Co-conspirator", "Ambitious subordinate", "Enforcer",
            "Court spy", "Childhood connection", "Corrupted former ally"
        ],
        "supporting-supporting": [
            "Close friends", "Rivals", "Romantic partners", "Court colleagues",
            "Family members", "Mentor/student", "Uneasy alliance", "Secret connection",
            "Former enemies", "Complementary skills", "Political allies"
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
            "description": f"They share a common cause but sometimes disagree on methods."
        }
        relationships.append(relationship)
    
    # Generate protagonist-antagonist relationship
    if protagonist and antagonist:
        relationship = {
            "character1": protagonist.name,
            "character2": antagonist.name,
            "type": random.choice(relationship_types["protagonist-antagonist"]),
            "description": f"Their conflict drives the central historical drama."
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
                    "description": f"They work together toward common historical goals."
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
                    "description": f"They serve the antagonist's political agenda."
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