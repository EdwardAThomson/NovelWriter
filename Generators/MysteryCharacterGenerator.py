import random
import json
from datetime import datetime

class MysteryCharacter:
    """Character class for Mystery genre with proper title and family handling"""
    
    # Mystery-specific title lists
    LAW_ENFORCEMENT_TITLES = {
        "high": {
            "male": ["Chief", "Commissioner", "Captain", "Lieutenant", "Inspector"],
            "female": ["Chief", "Commissioner", "Captain", "Lieutenant", "Inspector"],
            "neutral": ["Chief Inspector", "Senior Detective", "Division Commander"]
        },
        "mid": {
            "male": ["Detective", "Sergeant", "Agent", "Investigator"],
            "female": ["Detective", "Sergeant", "Agent", "Investigator"],
            "neutral": ["Senior Officer", "Lead Investigator", "Case Manager"]
        },
        "low": {
            "male": ["Officer", "Deputy", "Constable", "Patrol Officer"],
            "female": ["Officer", "Deputy", "Constable", "Patrol Officer"],
            "neutral": ["Junior Detective", "Beat Officer", "Rookie"]
        }
    }
    
    LEGAL_TITLES = {
        "high": {
            "male": ["Judge", "District Attorney", "Chief Prosecutor"],
            "female": ["Judge", "District Attorney", "Chief Prosecutor"],
            "neutral": ["Chief Justice", "Attorney General", "Legal Director"]
        },
        "mid": {
            "male": ["Prosecutor", "Defense Attorney", "Legal Counsel"],
            "female": ["Prosecutor", "Defense Attorney", "Legal Counsel"],
            "neutral": ["Assistant DA", "Public Defender", "Legal Advisor"]
        },
        "low": {
            "male": ["Paralegal", "Court Clerk", "Legal Assistant"],
            "female": ["Paralegal", "Court Clerk", "Legal Assistant"],
            "neutral": ["Junior Attorney", "Law Student", "Legal Intern"]
        }
    }
    
    CIVILIAN_TITLES = {
        "high": {
            "male": ["Doctor", "Professor", "Director", "Chief"],
            "female": ["Doctor", "Professor", "Director", "Chief"],
            "neutral": ["Medical Examiner", "Forensic Expert", "Lab Director"]
        },
        "mid": {
            "male": ["Analyst", "Specialist", "Consultant"],
            "female": ["Analyst", "Specialist", "Consultant"],
            "neutral": ["Crime Scene Technician", "Forensic Analyst", "Lab Technician"]
        },
        "low": {
            "male": ["Assistant", "Technician", "Clerk"],
            "female": ["Assistant", "Technician", "Clerk"],
            "neutral": ["Junior Analyst", "Lab Assistant", "Research Assistant"]
        }
    }
    
    PRIVATE_TITLES = {
        "high": {
            "male": ["Private Investigator", "Security Chief", "Investigation Director"],
            "female": ["Private Investigator", "Security Chief", "Investigation Director"],
            "neutral": ["Senior PI", "Investigation Manager", "Security Director"]
        },
        "mid": {
            "male": ["Investigator", "Security Officer", "Consultant"],
            "female": ["Investigator", "Security Officer", "Consultant"],
            "neutral": ["Private Detective", "Security Specialist", "Investigation Consultant"]
        },
        "low": {
            "male": ["Security Guard", "Assistant", "Trainee"],
            "female": ["Security Guard", "Assistant", "Trainee"],
            "neutral": ["Junior Investigator", "Security Assistant", "Investigation Trainee"]
        }
    }

    def __init__(self, name, role, age=None):
        self.name = name
        self.role = role
        self.age = age
        self.title = None
        self.profession = None
        self.gender = None
        self.goals = []
        self.motivations = []
        self.flaws = []
        self.strengths = []
        self.background = ""
        self.arc = ""
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

    def set_title(self, title_type="law_enforcement", rank="mid"):
        """Set a title based on the specified type, rank, and character's gender."""
        title_map = {
            "law_enforcement": self.LAW_ENFORCEMENT_TITLES,
            "legal": self.LEGAL_TITLES,
            "civilian": self.CIVILIAN_TITLES,
            "private": self.PRIVATE_TITLES
        }
        
        title_list = title_map.get(title_type, self.LAW_ENFORCEMENT_TITLES)
        rank_dict = title_list.get(rank, title_list["mid"])
        
        # Determine which gender list to use
        if self.gender:
            gender_key = self.gender.lower()
            if gender_key in rank_dict:
                available_titles = rank_dict[gender_key]
            else:
                available_titles = rank_dict.get("neutral", [])
        else:
            available_titles = rank_dict.get("neutral", [])
        
        if available_titles:
            self.title = random.choice(available_titles)
        else:
            # Fallback to any available titles
            all_titles = []
            for titles in rank_dict.values():
                all_titles.extend(titles)
            if all_titles:
                self.title = random.choice(all_titles)

    @property
    def full_name(self):
        """Return the character's full name with title if set."""
        if self.title:
            return f"{self.title} {self.name}"
        return self.name

    def generate_family(self):
        """Generate family members for the character based on their age and role."""
        surname = self.name.split(" ")[-1] if " " in self.name else "UnknownSurname"
        
        # Parents - Always generate parents, but determine their status based on character's age and circumstances
        father_name = f"{generate_mystery_first_name('Male')} {surname}"
        mother_name = f"{generate_mystery_first_name('Female')} {surname}"
        
        # Determine parent status based on character's age and random factors
        def determine_parent_status(character_age):
            if not character_age:
                character_age = 30  # Default age if not set
            
            if character_age < 25:
                # Young character - parents very likely alive
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "In Witness Protection"],
                    weights=[82, 10, 5, 2, 1]
                )[0]
            elif character_age < 40:
                # Middle-aged character - parents likely alive but some chance of loss
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "In Witness Protection"],
                    weights=[68, 21, 7, 3, 1]
                )[0]
            elif character_age < 55:
                # Older character - higher chance parents are deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "In Witness Protection"],
                    weights=[48, 41, 7, 3, 1]
                )[0]
            else:
                # Very old character - parents likely deceased
                return random.choices(
                    ["Living", "Deceased", "Estranged", "Missing", "In Witness Protection"],
                    weights=[18, 71, 7, 3, 1]
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
            sibling_name = f"{generate_mystery_first_name(sibling_gender)} {surname}"
            self.family['siblings'].append({
                'name': sibling_name,
                'relation': 'sibling',
                'gender': sibling_gender
            })

        # Spouse
        if self.age and self.age > 28 and random.random() < 0.6:
            spouse_gender = "Female" if self.gender == "Male" else "Male"
            spouse_first = generate_mystery_first_name(spouse_gender)
            spouse_last = generate_mystery_last_name()
            spouse_name = f"{spouse_first} {spouse_last}"
            self.family['spouse'] = {
                'name': spouse_name,
                'relation': 'spouse',
                'gender': spouse_gender
            }

        # Children
        if self.age and self.age > 30 and self.family['spouse'] and random.random() < 0.7:
            num_children = random.randint(1, 2)
            for _ in range(num_children):
                child_gender = random.choice(["Male", "Female"])
                child_name = f"{generate_mystery_first_name(child_gender)} {surname}"
                self.family['children'].append({
                    'name': child_name,
                    'relation': 'child',
                    'gender': child_gender
                })

def generate_mystery_first_name(gender=None):
    """Generate appropriate first names for mystery characters (no titles)"""
    first_names_male = [
        "Jack", "Sam", "Nick", "Mike", "Tom", "Dan", "Alex", "Chris", "Matt", "Dave",
        "Paul", "Mark", "Steve", "Jim", "Bob", "Ray", "Joe", "Ben", "Rick", "Frank",
        "John", "James", "Robert", "Michael", "William", "David", "Richard", "Charles",
        "Joseph", "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
        "Steven", "Kenneth", "Joshua", "Kevin", "Brian", "George", "Edward", "Ronald",
        "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric",
        "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin"
    ]
    
    first_names_female = [
        "Sarah", "Kate", "Emma", "Lisa", "Anna", "Jane", "Mary", "Susan", "Linda", "Carol",
        "Nancy", "Beth", "Amy", "Julie", "Helen", "Ruth", "Joan", "Diane", "Laura", "Grace",
        "Jennifer", "Patricia", "Elizabeth", "Barbara", "Margaret", "Dorothy", "Sandra",
        "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa",
        "Deborah", "Stephanie", "Rebecca", "Sharon", "Cynthia", "Kathleen", "Amy", "Angela",
        "Brenda", "Emma", "Olivia", "Cynthia", "Marie", "Janet", "Catherine", "Frances"
    ]
    
    if gender == "Male":
        return random.choice(first_names_male)
    elif gender == "Female":
        return random.choice(first_names_female)
    else:
        return random.choice(first_names_male + first_names_female)

def generate_mystery_last_name():
    """Generate appropriate last names for mystery characters"""
    last_names = [
        "Holmes", "Watson", "Poirot", "Marple", "Stone", "Cross", "Black", "White", "Gray",
        "Sharp", "Quick", "Smart", "Wise", "Fox", "Wolf", "Hunter", "Chase", "Knight",
        "Steel", "Iron", "Gold", "Silver", "Diamond", "Pierce", "Blade", "Storm", "Rain",
        "Snow", "Frost", "Burns", "Woods", "Rivers", "Hill", "Vale", "Moore", "Lane",
        "Park", "Bell", "King", "Queen", "Prince", "Duke", "Lord", "Noble", "Rich",
        "Strong", "Bold", "Brave", "True", "Just", "Fair", "Good", "Best", "Prime",
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thomson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
    ]
    
    return random.choice(last_names)

def generate_mystery_goals():
    """Generate goals appropriate for mystery characters"""
    detective_goals = [
        "Solve a decades-old cold case",
        "Catch a serial killer before they strike again",
        "Uncover corruption in the police department",
        "Find a missing person before it's too late",
        "Prove an innocent person's innocence",
        "Stop a criminal organization",
        "Solve their partner's murder",
        "Protect a key witness",
        "Uncover the truth behind a conspiracy",
        "Bring justice to victims' families"
    ]
    
    suspect_goals = [
        "Prove their innocence",
        "Find the real killer",
        "Protect their family from danger",
        "Escape false accusations",
        "Clear their name",
        "Uncover who framed them",
        "Stay hidden until they can prove the truth",
        "Gather evidence of their innocence",
        "Find an alibi witness",
        "Expose the real criminal"
    ]
    
    criminal_goals = [
        "Complete the perfect crime",
        "Avoid capture by the authorities",
        "Frame someone else for their crimes",
        "Eliminate all witnesses",
        "Steal a priceless artifact",
        "Get revenge on those who wronged them",
        "Cover up their past crimes",
        "Escape from prison",
        "Start a new life with a new identity",
        "Protect their criminal empire"
    ]
    
    witness_goals = [
        "Stay alive long enough to testify",
        "Remember what they saw clearly",
        "Protect their family from retaliation",
        "Find the courage to come forward",
        "Help solve the case",
        "Get justice for the victim",
        "Overcome their fear of the criminal",
        "Find a safe place to hide",
        "Trust the right people",
        "Do the right thing despite the danger"
    ]
    
    return detective_goals + suspect_goals + criminal_goals + witness_goals

def generate_mystery_motivations():
    """Generate motivations for mystery characters"""
    return [
        "Seeking justice for the innocent",
        "Driven by a need for truth",
        "Haunted by past failures",
        "Protecting loved ones",
        "Seeking redemption",
        "Driven by guilt",
        "Seeking revenge",
        "Pursuing personal glory",
        "Upholding the law",
        "Protecting society",
        "Solving puzzles and mysteries",
        "Proving their worth",
        "Overcoming past trauma",
        "Fighting corruption",
        "Seeking closure",
        "Driven by curiosity",
        "Protecting the vulnerable",
        "Seeking the truth at any cost",
        "Driven by a sense of duty",
        "Seeking to right past wrongs"
    ]

def generate_mystery_flaws():
    """Generate character flaws for mystery characters"""
    return [
        "Obsessive about details",
        "Trusts no one",
        "Drinks too much",
        "Has anger management issues",
        "Haunted by past cases",
        "Overly suspicious of everyone",
        "Breaks rules to get results",
        "Has a gambling problem",
        "Struggles with relationships",
        "Too emotionally invested in cases",
        "Arrogant and condescending",
        "Paranoid about being watched",
        "Has trouble sleeping",
        "Prone to taking unnecessary risks",
        "Struggles with authority",
        "Has a dark secret",
        "Overly protective of others",
        "Tends to work alone",
        "Has trust issues",
        "Prone to making assumptions"
    ]

def generate_mystery_strengths():
    """Generate character strengths for mystery characters"""
    return [
        "Exceptional observational skills",
        "Logical thinking ability",
        "Strong intuition",
        "Excellent memory",
        "Good at reading people",
        "Persistent and determined",
        "Skilled interrogator",
        "Expert in forensics",
        "Quick thinking under pressure",
        "Strong moral compass",
        "Excellent deductive reasoning",
        "Good at connecting dots",
        "Skilled in combat",
        "Expert marksman",
        "Good at going undercover",
        "Excellent research skills",
        "Strong leadership abilities",
        "Good at building rapport",
        "Skilled negotiator",
        "Excellent problem solver"
    ]

def generate_mystery_character_arcs():
    """Generate character development arcs for mystery characters"""
    return [
        "Learning to trust others again",
        "Overcoming past trauma",
        "Finding balance between work and life",
        "Learning to follow the rules",
        "Discovering the truth about themselves",
        "Learning to forgive",
        "Overcoming addiction",
        "Finding redemption",
        "Learning to work as part of a team",
        "Confronting their dark past",
        "Learning to let go of control",
        "Finding peace with past failures",
        "Learning to trust their instincts",
        "Overcoming fear",
        "Finding their moral center",
        "Learning to accept help",
        "Discovering their true calling",
        "Learning to move on from loss",
        "Finding the courage to do what's right",
        "Learning to see the bigger picture"
    ]

def generate_mystery_backgrounds():
    """Generate background stories for mystery characters"""
    return [
        "Former military with combat experience",
        "Grew up in a rough neighborhood",
        "Lost a family member to crime",
        "Former criminal turned good",
        "Comes from a family of law enforcement",
        "Studied criminology in college",
        "Former journalist turned detective",
        "Survived a traumatic crime",
        "Has a background in psychology",
        "Former lawyer turned investigator",
        "Grew up in foster care",
        "Has experience with organized crime",
        "Former federal agent",
        "Comes from a wealthy family",
        "Has a background in forensic science",
        "Former undercover operative",
        "Survived a near-death experience",
        "Has a photographic memory",
        "Former victim of crime",
        "Comes from a small town"
    ]

def generate_mystery_main_characters(num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
    """Generate main characters for mystery stories"""
    MAX_CHARACTERS = 100
    if num_characters > MAX_CHARACTERS:
        raise ValueError(f"Cannot generate more than {MAX_CHARACTERS} characters. Requested: {num_characters}")

    # Validate and calculate gender weights directly from input percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"MYSTERY_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"MYSTERY_CHAR_GEN: Using direct gender bias: Female {female_percentage}%, Male {male_percentage}%")

    goals = generate_mystery_goals()
    motivations = generate_mystery_motivations()
    flaws = generate_mystery_flaws()
    strengths = generate_mystery_strengths()
    arcs = generate_mystery_character_arcs()
    backgrounds = generate_mystery_backgrounds()
    
    roles = ["protagonist", "deuteragonist", "antagonist", "supporting", "supporting"]
    
    characters = []
    
    # Define character traits for each role
    trait_sets = {
        "protagonist": {
            "title_types": ["law_enforcement", "private", "legal"],
            "title_ranks": ["high", "mid"],
            "professions": ["Detective", "Private Investigator", "FBI Agent", "Police Officer"]
        },
        "deuteragonist": {
            "title_types": ["law_enforcement", "civilian", "legal"],
            "title_ranks": ["mid", "low"],
            "professions": ["Partner Detective", "Forensic Expert", "Assistant DA", "Crime Reporter"]
        },
        "antagonist": {
            "title_types": ["civilian", "legal"],
            "title_ranks": ["high", "mid"],
            "professions": ["Criminal Mastermind", "Corrupt Official", "Defense Attorney", "Crime Boss"]
        },
        "supporting": {
            "title_types": ["law_enforcement", "civilian", "legal", "private"],
            "title_ranks": ["high", "mid", "low"],
            "professions": ["Witness", "Victim", "Informant", "Lab Technician", "Court Reporter"]
        }
    }
    
    for i in range(num_characters):
        # Generate gender using weighted random selection (same as SciFi generator)
        gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
        
        # Generate name
        first_name = generate_mystery_first_name(gender)
        last_name = generate_mystery_last_name()
        full_name = f"{first_name} {last_name}"
        
        role = roles[i] if i < len(roles) else "supporting"
        char = MysteryCharacter(full_name, role)
        char.gender = gender
        
        # Set age based on role
        if role == "protagonist":
            char.age = random.randint(30, 50)
        elif role == "deuteragonist":
            char.age = random.randint(25, 45)
        elif role == "antagonist":
            char.age = random.randint(35, 65)
        else:  # supporting
            char.age = random.randint(20, 70)
        
        # Set title based on role
        role_traits = trait_sets[role]
        title_type = random.choice(role_traits["title_types"])
        title_rank = random.choice(role_traits["title_ranks"])
        char.set_title(title_type, title_rank)
        
        # Set profession
        char.profession = random.choice(role_traits["professions"])
        
        # Generate family
        char.generate_family()
        
        # Generate character details
        char.goals = [random.choice(goals)]
        char.motivations = [random.choice(motivations)]
        char.flaws = [random.choice(flaws)]
        char.strengths = [random.choice(strengths)]
        char.arc = random.choice(arcs)
        char.background = random.choice(backgrounds)
        
        characters.append(char)
    
    # Try to load agencies data for character assignment after all characters are created
    try:
        with open("current_work/factions.json", 'r') as f:
            data = json.load(f)
            # Handle both direct list format and wrapped format
            if isinstance(data, list):
                agencies_data = data
            elif isinstance(data, dict) and "factions" in data:
                agencies_data = data["factions"]
            else:
                agencies_data = data
            print(f"Loaded mystery agencies data: Found {len(agencies_data)} agencies")
            
            # Extract headquarters from agencies for character assignment
            headquarters = []
            for agency in agencies_data:
                agency_name = agency.get("name", "Unknown Agency")
                agency_type = agency.get("type", "Unknown Type")
                territory = agency.get("territory", "Unknown Location")
                headquarters.append({
                    "name": territory,
                    "agency": agency_name,
                    "agency_type": agency_type
                })
            
            if headquarters:
                # Track agency assignments for protagonist and antagonist
                protagonist_agency = None
                antagonist_agency = None
                supporting_character_count = 0
                
                for char in characters:
                    role = char.role
                    
                    # Initialize agency_role for supporting characters
                    if role == "supporting":
                        supporting_character_count += 1
                        if supporting_character_count <= 2:
                            char.agency_role = "Protagonist Ally"
                        elif supporting_character_count <= 4:
                            char.agency_role = "Antagonist Ally"
                        else:
                            char.agency_role = "Neutral"
                    else:
                        char.agency_role = None
                    
                    # Assign headquarters/agency based on role and existing agency assignments
                    if role == "protagonist":
                        hq = random.choice(headquarters)
                        protagonist_agency = hq["agency"]
                    elif role == "antagonist":
                        # Antagonist should be from a different agency if possible
                        antagonist_hqs = [h for h in headquarters if h["agency"] != protagonist_agency]
                        if not antagonist_hqs and headquarters:
                            antagonist_hqs = headquarters
                        hq = random.choice(antagonist_hqs)
                        antagonist_agency = hq["agency"]
                    elif role == "deuteragonist":
                        # Deuteragonist usually allies with protagonist
                        deuteragonist_hqs = [h for h in headquarters if h["agency"] == protagonist_agency]
                        if not deuteragonist_hqs:
                            deuteragonist_hqs = headquarters
                        hq = random.choice(deuteragonist_hqs)
                    else:  # supporting
                        if char.agency_role == "Protagonist Ally":
                            supporting_hqs = [h for h in headquarters if h["agency"] == protagonist_agency]
                            if not supporting_hqs:
                                supporting_hqs = headquarters
                            hq = random.choice(supporting_hqs)
                        elif char.agency_role == "Antagonist Ally":
                            supporting_hqs = [h for h in headquarters if h["agency"] == antagonist_agency]
                            if not supporting_hqs:
                                supporting_hqs = headquarters
                            hq = random.choice(supporting_hqs)
                        else:  # Neutral
                            hq = random.choice(headquarters)
                    
                    char.headquarters = hq["name"]
                    char.agency = hq["agency"]
                    char.agency_type = hq["agency_type"]
                    
                print(f"Assigned {len(characters)} characters to agencies")
            
    except FileNotFoundError:
        print("No agencies file found - characters will be generated without agency affiliations")
        # Initialize empty agency attributes for all characters
        for char in characters:
            char.agency = None
            char.agency_role = None
            char.headquarters = None
            char.agency_type = None
    except json.JSONDecodeError as e:
        print(f"Error parsing factions.json: {e}")
        # Initialize empty agency attributes for all characters
        for char in characters:
            char.agency = None
            char.agency_role = None
            char.headquarters = None
            char.agency_type = None
    except Exception as e:
        print(f"Unexpected error loading agencies: {e}")
        # Initialize empty agency attributes for all characters
        for char in characters:
            char.agency = None
            char.agency_role = None
            char.headquarters = None
            char.agency_type = None
    
    return characters

def generate_mystery_relationships(characters):
    """Generate relationships between mystery characters"""
    relationships = []
    relationship_types = [
        "Partners", "Former partners", "Rivals", "Mentor and student", "Colleagues",
        "Suspect and detective", "Witness and investigator", "Victim and perpetrator",
        "Allies", "Enemies", "Family members", "Friends", "Romantic interests",
        "Informant and handler", "Lawyer and client"
    ]
    
    relationship_descriptions = [
        "They work together to solve cases",
        "Their past partnership ended badly",
        "They compete for the same cases",
        "One taught the other everything they know",
        "They share information and resources",
        "One is investigating the other",
        "One saw something the other needs to know",
        "Their conflict drives the story",
        "They support each other's goals",
        "They are working against each other",
        "Family ties complicate their relationship",
        "Their friendship is tested by the case",
        "Romance complicates their professional relationship",
        "One provides information to the other",
        "Professional relationship with personal stakes"
    ]
    
    # Generate relationships between main characters
    for i in range(len(characters)):
        for j in range(i + 1, min(i + 3, len(characters))):
            relationship = {
                "character1": characters[i].name,
                "character2": characters[j].name,
                "type": random.choice(relationship_types),
                "description": random.choice(relationship_descriptions)
            }
            relationships.append(relationship)
    
    return relationships

def save_mystery_characters_to_file(characters, filename="mystery_characters.json"):
    """Save mystery characters to a JSON file"""
    import json
    
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
            "profession": char.profession,
            "description": char.description,
            "family": char.family
        }
        
        # Add optional attributes if they exist
        if char.title:
            char_dict["title"] = char.title
        if char.faction:
            char_dict["faction"] = char.faction
        if char.faction_role:
            char_dict["faction_role"] = char.faction_role
        if hasattr(char, 'agency') and char.agency:
            char_dict["agency"] = char.agency
        if hasattr(char, 'agency_role') and char.agency_role:
            char_dict["agency_role"] = char.agency_role
        if hasattr(char, 'headquarters') and char.headquarters:
            char_dict["headquarters"] = char.headquarters
        if hasattr(char, 'agency_type') and char.agency_type:
            char_dict["agency_type"] = char.agency_type
            
        char_dicts.append(char_dict)
    
    relationships = generate_mystery_relationships(characters)
    
    data = {
        "characters": char_dicts,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "Mystery"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename 