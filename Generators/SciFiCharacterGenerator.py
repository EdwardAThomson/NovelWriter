from .SciFiGenerator import _generate_base_name, generate_character_name, CHAR_PREFIXES, CHAR_MIDDLES, CHAR_SUFFIXES
import random
import json
from datetime import datetime
import re

class Character:
    # Class-level title lists
    MILITARY_TITLES = {
        "high": {
            "male": ["Admiral", "Commander", "Captain", "Colonel", "Major", "General"],
            "female": ["Admiral", "Commander", "Captain", "Colonel", "Major", "General"],
            "neutral": ["Fleet Commander", "Wing Commander"]
        },
        "mid": {
            "male": ["Lieutenant", "Sergeant", "Ensign", "Corporal"],
            "female": ["Lieutenant", "Sergeant", "Ensign", "Corporal"],
            "neutral": ["Flight Officer", "Squad Leader", "Tactical Officer"]
        },
        "low": {
            "male": ["Private", "Cadet", "Recruit"],
            "female": ["Private", "Cadet", "Recruit"],
            "neutral": ["Specialist", "Technician", "Gunner", "Scout"]
        }
    }
    
    CIVILIAN_TITLES = {
        "high": {
            "male": ["Doctor", "Professor", "Director", "Consul", "Minister"],
            "female": ["Doctor", "Professor", "Director", "Consul", "Minister"],
            "neutral": ["Ambassador", "Chancellor", "Archon", "Overseer"]
        },
        "mid": {
            "male": ["Senior Researcher", "Senior Analyst", "Senior Supervisor"],
            "female": ["Senior Researcher", "Senior Analyst", "Senior Supervisor"],
            "neutral": ["Senior Coordinator", "Senior Manager", "Senior Consultant", "Senior Specialist"]
        },
        "low": {
            "male": ["Assistant", "Technician", "Clerk"],
            "female": ["Assistant", "Technician", "Clerk"],
            "neutral": ["Operator", "Junior Researcher", "Junior Analyst", "Junior Supervisor"]
        }
    }
    
    NOBLE_TITLES = {
        "high": {
            "male": ["Lord", "Baron", "Count", "Duke", "Prince"],
            "female": ["Lady", "Baroness", "Countess", "Duchess", "Princess"],
            "neutral": ["Noble", "Highborn"]
        },
        "mid": {
            "male": ["Knight", "Viscount", "Baronet"],
            "female": ["Dame", "Viscountess", "Baronetess"],
            "neutral": ["Noble Scion", "Noble Heir"]
        },
        "low": {
            "male": ["Squire", "Page"],
            "female": ["Squire", "Page"],
            "neutral": ["Noble Apprentice", "Noble Cadet", "Noble Scion"]
        }
    }

    # Occupational roles (not used as titles)
    OCCUPATIONAL_ROLES = {
        "high": {
            "male": ["Master Trader", "Chief Engineer", "Head Scientist"],
            "female": ["Master Trader", "Chief Engineer", "Head Scientist"],
            "neutral": ["Fleet Admiral", "High Priest", "Grand Master", "Chief Medical Officer", 
                       "Intelligence Director", "Security Chief", "Diplomatic Envoy"]
        },
        "mid": {
            "male": ["Senior Trader", "Senior Engineer", "Research Scientist"],
            "female": ["Senior Trader", "Senior Engineer", "Research Scientist"],
            "neutral": ["Ship Captain", "Priest", "Master", "Medical Officer", 
                       "Intelligence Officer", "Security Officer", "Diplomatic Attaché"]
        },
        "low": {
            "male": ["Junior Trader", "Junior Engineer", "Lab Technician"],
            "female": ["Junior Trader", "Junior Engineer", "Lab Technician"],
            "neutral": ["Acolyte", "Apprentice", "Medical Assistant", 
                       "Intelligence Analyst", "Security Guard", "Diplomatic Aide"]
        }
    }

    def __init__(self, name, role, age=None):
        self.name = name
        self.role = role
        self.age = age
        self.title = None
        self.occupation = None  # New field for occupational roles
        self.gender = None
        self.goals = []
        self.motivations = []
        self.flaws = []
        self.strengths = []
        self.background = ""
        self.arc = ""
        self.homeworld = None
        self.home_system = None
        self.faction = None
        self.faction_role = None
        self.description = ""
        self.relationships = []
        self.family = {
            'parents': [],
            'siblings': [],
            'spouse': None,
            'children': []
        }

    def set_title(self, title_type="civilian", rank="mid"):
        """Set a title based on the specified type, rank, and character's gender."""
        # Handle occupational roles separately from formal titles
        if title_type == "specialized":
            self._set_occupation(rank)
            return

        title_list = getattr(self, f"{title_type.upper()}_TITLES", self.CIVILIAN_TITLES)
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

    @property
    def full_name(self):
        """Return the character's full name with title if set."""
        if self.title:
            return f"{self.title} {self.name}"
        return self.name

    def get_role_description(self):
        """Return a description of the character's role and occupation."""
        if self.occupation:
            return f"{self.occupation}"
        return ""

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
                    ["Living", "Deceased", "Estranged", "Missing"],
                    weights=[85, 8, 5, 2]
                )[0]
            elif character_age < 40:
                # Middle-aged character - parents likely alive but some chance of loss
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing"],
                    weights=[70, 20, 7, 3]
                )[0]
            elif character_age < 55:
                # Older character - higher chance parents are deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing"],
                    weights=[50, 40, 7, 3]
                )[0]
            else:
                # Very old character - parents likely deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing"],
                    weights=[20, 70, 7, 3]
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
        num_siblings = random.randint(0, 2)
        for _ in range(num_siblings):
            sibling_gender = random.choice(["Male", "Female"])
            sibling_name = f"{generate_character_name(sibling_gender)} {surname}"
            self.family['siblings'].append({
                'name': sibling_name,
                'relation': 'sibling',
                'gender': sibling_gender
            })

        # Spouse
        if self.age and self.age > 28 and random.random() < 0.6:  # 60% chance if > 28
            spouse_gender = "Female" if self.gender == "Male" else "Male"
            spouse_name = f"{generate_character_name(spouse_gender)} {_generate_base_name(CHAR_PREFIXES, CHAR_MIDDLES, CHAR_SUFFIXES)}"
            self.family['spouse'] = {
                'name': spouse_name,
                'relation': 'spouse',
                'gender': spouse_gender
            }

        # Children
        if self.age and self.age > 30 and self.family['spouse'] and random.random() < 0.7:  # 70% chance if married & > 30
            num_children = random.randint(1, 2)
            for _ in range(num_children):
                child_gender = random.choice(["Male", "Female"])
                child_name = f"{generate_character_name(child_gender)} {surname}"
                self.family['children'].append({
                    'name': child_name,
                    'relation': 'child',
                    'gender': child_gender
                })

def generate_main_characters(num_characters=3, female_percentage=50, male_percentage=50):
    """
    Generate main characters using the name generation from SciFiGenerator.
    
    Args:
        num_characters (int): Number of characters to generate
        female_percentage (int): Percentage for female gender (0-100)
        male_percentage (int): Percentage for male gender (0-100)
    
    Returns:
        list: List of Character objects
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
        print(f"CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"CHAR_GEN: Using direct gender bias: Female {female_percentage}%, Male {male_percentage}%")

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

    # Get list of all habitable planets if factions exist
    habitable_planets = []
    if factions_data:
        try:
            for faction in factions_data:
                for system in faction.get("systems", []):
                    for planet in system.get("habitable_planets", []):
                        habitable_planets.append({
                            "name": planet.get("name", "Unknown"),
                            "system": system.get("name", "Unknown"),
                            "faction": faction.get("faction_name", "Unknown")
                        })
            print(f"Found {len(habitable_planets)} habitable planets")
        except Exception as e:
            print(f"Error processing faction data: {e}")
            return None

    characters = []
    roles = ["protagonist", "deuteragonist", "antagonist"] + ["supporting"] * 7  # Allow up to 10 characters
    
    # Define character traits for each role
    trait_sets = {
        "protagonist": {
            "goals": [
                "Uncover a galactic conspiracy",
                "Find a lost alien artifact",
                "Protect their home system from invasion",
                "Prove their innocence in an interstellar crime",
                "Unite warring factions against a common threat"
            ],
            "motivations": [
                "Restore family honor",
                "Avenge a personal loss",
                "Discover their true identity",
                "Protect the innocent",
                "Right a past wrong"
            ],
            "flaws": [
                "Overconfident in their abilities",
                "Too trusting of others",
                "Haunted by past failures",
                "Struggles with authority",
                "Places loyalty above reason"
            ],
            "strengths": [
                "Natural leadership ability",
                "Quick tactical thinking",
                "Exceptional pilot skills",
                "Strong moral compass",
                "Adaptable to any situation"
            ],
            "arcs": [
                "Learning to trust others after betrayal",
                "Finding balance between duty and personal desires",
                "Overcoming fear to become a leader",
                "Learning the true meaning of sacrifice",
                "Discovering their place in the galaxy"
            ]
        },
        "antagonist": {
            "goals": [
                "Seize control of key star systems",
                "Acquire ancient alien technology",
                "Overthrow the current power structure",
                "Achieve technological supremacy",
                "Reshape society according to their vision"
            ],
            "motivations": [
                "Revenge against the establishment",
                "Belief in their superior vision",
                "Fear of losing power",
                "Twisted sense of justice",
                "Desire to prove their superiority"
            ],
            "flaws": [
                "Overwhelming pride",
                "Inability to trust anyone",
                "Obsession with power",
                "Underestimates opponents",
                "Refuses to admit mistakes"
            ],
            "strengths": [
                "Brilliant strategic mind",
                "Vast resources and influence",
                "Charismatic leadership",
                "Ruthless efficiency",
                "Advanced technological knowledge"
            ],
            "arcs": [
                "Descent into complete tyranny",
                "Tragic fall from grace",
                "Realizing the cost of their ambition",
                "Becoming what they once fought against",
                "Possible path to redemption"
            ]
        },
        "deuteragonist": {
            "goals": [
                "Support the protagonist's mission",
                "Prove their own worth",
                "Protect their loved ones",
                "Find their place in the conflict",
                "Maintain peace in their sector"
            ],
            "motivations": [
                "Debt to the protagonist",
                "Shared ideals and beliefs",
                "Personal growth and challenge",
                "Escape their past",
                "Build a better future"
            ],
            "flaws": [
                "Lives in protagonist's shadow",
                "Conflicted loyalties",
                "Past trauma affects judgment",
                "Impulsive decision-making",
                "Fear of failure"
            ],
            "strengths": [
                "Specialized technical skills",
                "Unwavering loyalty",
                "Unique perspective on events",
                "Diplomatic abilities",
                "Combat expertise"
            ],
            "arcs": [
                "Finding their own path",
                "Learning to stand alone",
                "Overcoming past trauma",
                "Balancing duty and personal goals",
                "Becoming a leader in their own right"
            ]
        },
        "supporting": {
            "goals": [
                "Establish their own trading empire",
                "Solve an ancient mystery",
                "Clear their family's name",
                "Find a new home for refugees",
                "Master forbidden technology",
                "Reform a corrupt institution",
                "Chart unknown space"
            ],
            "motivations": [
                "Pursuit of knowledge",
                "Desire for wealth",
                "Search for belonging",
                "Need to prove themselves",
                "Sense of adventure",
                "Religious/spiritual calling",
                "Family obligations"
            ],
            "flaws": [
                "Prone to addiction",
                "Overanalyzes everything",
                "Holds dangerous secrets",
                "Trust issues",
                "Reckless behavior",
                "Cultural biases",
                "Survivor's guilt"
            ],
            "strengths": [
                "Expert knowledge",
                "Underground connections",
                "Innovative thinking",
                "Cultural understanding",
                "Technical expertise",
                "Medical training",
                "Survival skills"
            ],
            "arcs": [
                "Finding purpose in chaos",
                "Learning to trust again",
                "Confronting their past",
                "Discovering hidden potential",
                "Breaking free from control",
                "Choosing between duty and dreams",
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
            
            # Use generate_character_name from SciFiGenerator for name generation
            first_name = generate_character_name(gender)
            last_name = _generate_base_name(CHAR_PREFIXES, CHAR_MIDDLES, CHAR_SUFFIXES, middle_chance=0.4)
            full_name = f"{first_name} {last_name}"
            
            role = roles[i]
            char = Character(full_name, role)
            char.gender = gender
            
            # Initialize faction_role for supporting characters
            if role == "supporting":
                supporting_character_count += 1
                if supporting_character_count <= 2:
                    char.faction_role = "Protagonist Ally"
                elif supporting_character_count <= 4:
                    char.faction_role = "Antagonist Ally"
                else:
                    char.faction_role = "Neutral"
            else:
                char.faction_role = None
            
            # Assign age based on role
            min_age, max_age = 25, 45  # Default for Protagonist/Deuteragonist
            if role == "antagonist":
                min_age, max_age = 35, 65
            
            # Set appropriate title based on role
            if role == "protagonist":
                char.set_title("military", "high")  # Protagonist typically has a high military rank
                min_age = max(min_age, 30)  # Ensure protagonist is experienced enough for their rank
            elif role == "deuteragonist":
                if random.random() < 0.7:  # 70% chance of military title
                    char.set_title("military", random.choices(["high", "mid"], weights=[0.3, 0.7])[0])
                    min_age = max(min_age, 28)  # Ensure deuteragonist is experienced enough
            elif role == "antagonist":
                # Antagonist title will come from faction generator
                pass
            elif role == "supporting":
                if random.random() < 0.4:  # 40% chance of any title
                    title_type = random.choices(
                        ["military", "civilian", "noble", "specialized"],
                        weights=[0.3, 0.3, 0.2, 0.2]
                    )[0]
                    
                    # Determine rank based on character's role in the story
                    if char.faction_role == "Protagonist Ally":
                        rank = random.choices(["high", "mid", "low"], weights=[0.2, 0.5, 0.3])[0]
                    elif char.faction_role == "Antagonist Ally":
                        rank = random.choices(["high", "mid", "low"], weights=[0.3, 0.4, 0.3])[0]
                    else:  # Neutral
                        rank = random.choices(["high", "mid", "low"], weights=[0.1, 0.4, 0.5])[0]
                    
                    char.set_title(title_type, rank)
                    
                    # Adjust minimum age based on title type and rank
                    if rank == "high":
                        min_age = max(min_age, 35)
                    elif rank == "mid":
                        min_age = max(min_age, 25)
                    else:  # low
                        min_age = max(min_age, 20)
            
            char.age = random.randint(min_age, max_age)
            
            # Generate family members
            char.generate_family()
            
            # Get random traits for this role
            traits = trait_sets[role]
            char.goals = [random.choice(traits["goals"])]
            char.motivations = [random.choice(traits["motivations"])]
            char.flaws = [random.choice(traits["flaws"])]
            char.strengths = [random.choice(traits["strengths"])]
            char.arc = random.choice(traits["arcs"])
            
            # Assign homeworld based on role and existing faction assignments
            if habitable_planets:
                if role == "protagonist":
                    homeworld = random.choice(habitable_planets)
                    protagonist_faction = homeworld["faction"]
                elif role == "antagonist":
                    antagonist_planets = [p for p in habitable_planets if p["faction"] != protagonist_faction]
                    if not antagonist_planets and habitable_planets:
                        antagonist_planets = habitable_planets
                    homeworld = random.choice(antagonist_planets)
                    antagonist_faction = homeworld["faction"]
                elif role == "deuteragonist":
                    deuteragonist_planets = [p for p in habitable_planets if p["faction"] == protagonist_faction]
                    if not deuteragonist_planets:
                        deuteragonist_planets = habitable_planets
                    homeworld = random.choice(deuteragonist_planets)
                else:  # supporting
                    if char.faction_role == "Protagonist Ally":
                        supporting_planets = [p for p in habitable_planets if p["faction"] == protagonist_faction]
                        if not supporting_planets:
                            supporting_planets = habitable_planets
                        homeworld = random.choice(supporting_planets)
                    elif char.faction_role == "Antagonist Ally":
                        supporting_planets = [p for p in habitable_planets if p["faction"] == antagonist_faction]
                        if not supporting_planets:
                            supporting_planets = habitable_planets
                        homeworld = random.choice(supporting_planets)
                    else:  # Neutral
                        homeworld = random.choice(habitable_planets)
                
                char.homeworld = homeworld["name"]
                char.home_system = homeworld["system"]
                char.faction = homeworld["faction"]
            
            characters.append(char)
            
        except Exception as e:
            role_name = roles[i] if i < len(roles) else "unknown"
            print(f"Error generating character {i} ({role_name}): {e}")
            continue
    
    return characters

def print_character(character):
    """Print character details in a formatted way."""
    print(f"\n{'='*50}")
    if character.title:
        print(f"=== {character.title} {character.name} ({character.role}) ===")
    else:
        print(f"=== {character.name} ({character.role}) ===")
    
    # Print gender and age
    if character.gender:
        print(f"Gender: {character.gender}")
    if character.age:
        print(f"Age: {character.age}")
    
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
    if hasattr(character, 'homeworld') and character.homeworld:
        print(f"Homeworld: {character.homeworld}")
        print(f"Star System: {character.home_system}")
    elif hasattr(character, 'homeland') and character.homeland:
        print(f"Homeland: {character.homeland}")
        print(f"Home Region: {character.home_region}")
        if hasattr(character, 'race') and character.race:
            print(f"Race: {character.race}")
    
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

def save_characters_to_file(characters, filename="characters.json"):
    """Save characters to a JSON file."""
    # Convert characters to dictionary format
    char_dicts = []
    for char in characters:
        char_dict = {
            "name": char.name,
            "role": char.role,
            "gender": char.gender,
            "age": char.age,
            "goals": char.goals,
            "motivations": char.motivations,
            "flaws": char.flaws,
            "strengths": char.strengths,
            "arc": char.arc,
            "background": char.background,
            "faction": char.faction,
            "description": char.description,
            "family": char.family  # Add family information to the saved data
        }
        
        # Add optional attributes if they exist
        if char.title:
            char_dict["title"] = char.title
        if char.faction_role:
            char_dict["faction_role"] = char.faction_role
            
        # Add genre-specific attributes if they exist
        # Sci-Fi attributes
        if hasattr(char, 'homeworld') and char.homeworld:
            char_dict["homeworld"] = char.homeworld
        if hasattr(char, 'home_system') and char.home_system:
            char_dict["home_system"] = char.home_system
            
        # Fantasy attributes
        if hasattr(char, 'homeland') and char.homeland:
            char_dict["homeland"] = char.homeland
        if hasattr(char, 'home_region') and char.home_region:
            char_dict["home_region"] = char.home_region
        if hasattr(char, 'race') and char.race:
            char_dict["race"] = char.race
            
        char_dicts.append(char_dict)
    
    # Generate relationships between characters
    relationships = generate_relationships(characters)
    
    # Create the full data structure
    data = {
        "characters": char_dicts,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters)
        }
    }
    
    # Save to file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"\nCharacters successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving characters to file: {e}")
        raise

def generate_relationships(characters):
    """Generate relationships between characters."""
    relationships = []
    
    # Define possible relationship types
    relationship_types = {
        "protagonist-deuteragonist": [
            "Old friends", "Mentor and student", "Siblings", "Former rivals", 
            "Reluctant allies", "Commander and subordinate", "Childhood friends",
            "Rescued/savior", "Family members", "Professional colleagues"
        ],
        "protagonist-supporting-ally": [
            "Trusted advisor", "Loyal friend", "Family connection", "Owes life debt",
            "Military comrade", "Shared traumatic past", "Romantic interest",
            "Technical support", "Intelligence provider", "Moral compass"
        ],
        "protagonist-antagonist": [
            "Former friends", "Bitter rivals", "Unknown to each other", "Family betrayal",
            "Ideological opposites", "Former mentor/student", "Professional competitors",
            "Mutual respect", "Personal vendetta", "Symbolic opposites"
        ],
        "antagonist-supporting-ally": [
            "Loyal lieutenant", "Fearful servant", "True believer", "Manipulated pawn",
            "Family member", "Co-conspirator", "Ambitious subordinate", "Enforcer",
            "Technical genius", "Childhood connection"
        ],
        "supporting-supporting": [
            "Close friends", "Rivals", "Romantic partners", "Professional colleagues",
            "Family members", "Mentor/student", "Uneasy alliance", "Secret connection",
            "Former enemies", "Complementary skills"
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
            "description": f"They share a common goal but sometimes disagree on methods."
        }
        relationships.append(relationship)
    
    # Generate protagonist-antagonist relationship
    if protagonist and antagonist:
        relationship = {
            "character1": protagonist.name,
            "character2": antagonist.name,
            "type": random.choice(relationship_types["protagonist-antagonist"]),
            "description": f"Their conflict is the central tension of the story."
        }
        relationships.append(relationship)
    
    # Generate protagonist-supporting relationships for allies
    if protagonist:
        for char in supporting_chars:
            if char.faction_role == "Protagonist Ally":
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
            if char.faction_role == "Antagonist Ally":
                relationship = {
                    "character1": antagonist.name,
                    "character2": char.name,
                    "type": random.choice(relationship_types["antagonist-supporting-ally"]),
                    "description": f"They serve the antagonist's agenda."
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