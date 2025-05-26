import random
import json
from datetime import datetime

def generate_thriller_names():
    """Generate names suitable for thriller characters"""
    first_names_male = [
        "Jack", "Ryan", "Marcus", "Cole", "Blake", "Kane", "Rex", "Max", "Zane", "Jax",
        "Hunter", "Chase", "Steel", "Phoenix", "Storm", "Blade", "Raven", "Wolf", "Hawk", "Fox",
        "Victor", "Vincent", "Damien", "Adrian", "Ethan", "Nathan", "Logan", "Derek", "Tyler", "Kyle",
        "Agent", "Detective", "Captain", "Major", "Colonel", "Commander", "Director", "Chief"
    ]
    
    first_names_female = [
        "Alex", "Sam", "Jordan", "Casey", "Riley", "Taylor", "Morgan", "Avery", "Quinn", "Blake",
        "Raven", "Phoenix", "Storm", "Jade", "Scarlett", "Ivy", "Luna", "Nova", "Aria", "Zara",
        "Victoria", "Natasha", "Sophia", "Isabella", "Gabrielle", "Anastasia", "Valentina", "Serena",
        "Agent", "Detective", "Captain", "Major", "Colonel", "Commander", "Director", "Chief"
    ]
    
    last_names = [
        "Cross", "Stone", "Steel", "Black", "White", "Gray", "Sharp", "Quick", "Swift", "Strong",
        "Hunter", "Walker", "Knight", "King", "Queen", "Prince", "Duke", "Noble", "Savage", "Wild",
        "Storm", "Rain", "Snow", "Frost", "Burns", "Flame", "Blaze", "Spark", "Thunder", "Lightning",
        "Shadow", "Dark", "Light", "Bright", "Clear", "Sharp", "Edge", "Blade", "Arrow", "Bolt",
        "Wolf", "Fox", "Hawk", "Eagle", "Raven", "Crow", "Bear", "Lion", "Tiger", "Panther"
    ]
    
    return first_names_male, first_names_female, last_names

def generate_thriller_goals():
    """Generate goals appropriate for thriller characters"""
    protagonist_goals = [
        "Stop a terrorist attack",
        "Expose a government conspiracy",
        "Rescue a kidnapped loved one",
        "Prevent a nuclear disaster",
        "Catch a serial killer",
        "Survive an assassination attempt",
        "Uncover corporate corruption",
        "Stop a biological weapon release",
        "Prevent a cyber attack",
        "Escape from captivity"
    ]
    
    antagonist_goals = [
        "Execute the perfect heist",
        "Destroy their enemies",
        "Take over a corporation",
        "Start a war",
        "Release a deadly virus",
        "Assassinate a world leader",
        "Steal classified information",
        "Frame an innocent person",
        "Escape justice",
        "Build a criminal empire"
    ]
    
    survival_goals = [
        "Stay alive until help arrives",
        "Protect their family from danger",
        "Escape from a dangerous situation",
        "Find a way to communicate for help",
        "Gather evidence to prove their innocence",
        "Outwit their pursuers",
        "Find a safe place to hide",
        "Expose the truth before it's too late",
        "Stop the countdown",
        "Reach the extraction point"
    ]
    
    return protagonist_goals + antagonist_goals + survival_goals

def generate_thriller_motivations():
    """Generate motivations for thriller characters"""
    return [
        "Seeking revenge for past wrongs",
        "Protecting national security",
        "Saving innocent lives",
        "Pursuing justice at any cost",
        "Driven by personal vendetta",
        "Seeking redemption for past failures",
        "Protecting family and loved ones",
        "Uncovering the truth",
        "Stopping a greater evil",
        "Survival instinct",
        "Duty to country",
        "Personal honor",
        "Preventing catastrophe",
        "Seeking power and control",
        "Driven by greed",
        "Ideological beliefs",
        "Fear of exposure",
        "Desire for recognition",
        "Protecting secrets",
        "Eliminating threats"
    ]

def generate_thriller_flaws():
    """Generate character flaws for thriller characters"""
    return [
        "Trusts no one",
        "Prone to violence",
        "Haunted by past failures",
        "Obsessed with the mission",
        "Reckless and impulsive",
        "Paranoid about everything",
        "Struggles with PTSD",
        "Has a death wish",
        "Too emotionally invested",
        "Breaks rules to get results",
        "Has anger management issues",
        "Addicted to adrenaline",
        "Difficulty forming relationships",
        "Overly suspicious",
        "Prone to taking unnecessary risks",
        "Has a dark secret",
        "Struggles with authority",
        "Emotionally detached",
        "Perfectionist to a fault",
        "Haunted by guilt"
    ]

def generate_thriller_strengths():
    """Generate character strengths for thriller characters"""
    return [
        "Expert in combat",
        "Exceptional marksmanship",
        "Master of disguise",
        "Skilled in surveillance",
        "Expert hacker",
        "Excellent strategist",
        "Quick thinking under pressure",
        "Exceptional physical fitness",
        "Master of escape and evasion",
        "Skilled interrogator",
        "Expert in explosives",
        "Excellent driver",
        "Skilled pilot",
        "Master of multiple languages",
        "Exceptional memory",
        "Skilled negotiator",
        "Expert in psychology",
        "Excellent tracker",
        "Skilled in stealth",
        "Natural leader"
    ]

def generate_thriller_character_arcs():
    """Generate character development arcs for thriller characters"""
    return [
        "Learning to trust others again",
        "Overcoming past trauma",
        "Finding redemption through sacrifice",
        "Learning the cost of revenge",
        "Discovering what's worth fighting for",
        "Choosing duty over personal desires",
        "Learning to work as part of a team",
        "Confronting their dark past",
        "Finding peace after violence",
        "Learning to let go of control",
        "Discovering their true loyalties",
        "Overcoming their greatest fear",
        "Learning the value of life",
        "Finding hope in darkness",
        "Choosing justice over revenge",
        "Learning to forgive themselves",
        "Discovering their moral limits",
        "Finding strength in vulnerability",
        "Learning to trust their instincts",
        "Choosing love over duty"
    ]

def generate_thriller_backgrounds():
    """Generate background stories for thriller characters"""
    return [
        "Former special forces operative",
        "Ex-CIA agent gone rogue",
        "Retired police detective",
        "Former military intelligence",
        "Ex-FBI profiler",
        "Former Navy SEAL",
        "Retired assassin",
        "Ex-Secret Service agent",
        "Former mercenary",
        "Retired spy",
        "Ex-military sniper",
        "Former undercover operative",
        "Retired bomb disposal expert",
        "Ex-counter-terrorism specialist",
        "Former hostage negotiator",
        "Retired black ops operative",
        "Ex-intelligence analyst",
        "Former security consultant",
        "Retired bodyguard",
        "Ex-private investigator"
    ]

def generate_thriller_specialties():
    """Generate specialties for thriller characters"""
    return [
        "Weapons Expert", "Demolitions Specialist", "Computer Hacker", "Surveillance Expert",
        "Interrogation Specialist", "Escape Artist", "Master of Disguise", "Sniper",
        "Hand-to-Hand Combat Expert", "Pilot", "Driver", "Tracker", "Negotiator",
        "Psychologist", "Linguist", "Strategist", "Infiltration Specialist", "Bodyguard",
        "Counter-Intelligence", "Cyber Security Expert"
    ]

def generate_thriller_main_characters(num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
    """Generate main characters for thriller stories"""
    # Validate gender percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"THRILLER_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"THRILLER_CHAR_GEN: Using gender bias: Female {female_percentage}%, Male {male_percentage}%")

    # Try to load factions data for agency assignment
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
            print(f"Loaded thriller agencies data: Found {len(factions_data)} agencies")
    except FileNotFoundError:
        print("No agencies file found - characters will be generated without agency affiliations")
    except json.JSONDecodeError as e:
        print(f"Error parsing factions.json: {e}")
    except Exception as e:
        print(f"Unexpected error loading agencies: {e}")

    # Extract headquarters from agencies for character assignment
    headquarters = []
    if factions_data:
        try:
            for agency in factions_data:
                agency_name = agency.get("name", "Unknown Agency")
                agency_type = agency.get("type", "Unknown Type")
                territory = agency.get("territory", "Unknown Location")
                headquarters.append({
                    "name": territory,
                    "agency": agency_name,
                    "agency_type": agency_type
                })
            print(f"Found {len(headquarters)} headquarters from agencies")
        except Exception as e:
            print(f"Error processing agency data: {e}")

    first_names_male, first_names_female, last_names = generate_thriller_names()
    goals = generate_thriller_goals()
    motivations = generate_thriller_motivations()
    flaws = generate_thriller_flaws()
    strengths = generate_thriller_strengths()
    arcs = generate_thriller_character_arcs()
    backgrounds = generate_thriller_backgrounds()
    specialties = generate_thriller_specialties()
    
    roles = ["protagonist", "deuteragonist", "antagonist"] + ["supporting"] * 7  # Allow up to 10 characters
    
    characters = []
    
    # Track agency assignments for protagonist and antagonist
    protagonist_agency = None
    antagonist_agency = None
    supporting_character_count = 0
    
    for i in range(min(num_characters, len(roles))):
        try:
            # Generate gender using weights
            gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
            
            # Select name based on gender
            if gender == "Female":
                first_name = random.choice(first_names_female)
            else:
                first_name = random.choice(first_names_male)
            
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Assign role
            role = roles[i]
            
            # Generate character details
            character = {
                "name": name,
                "role": role,
                "gender": gender,
                "age": random.randint(28, 55),
                "goals": [random.choice(goals)],
                "motivations": [random.choice(motivations)],
                "flaws": [random.choice(flaws)],
                "strengths": [random.choice(strengths)],
                "arc": random.choice(arcs),
                "background": random.choice(backgrounds),
                "specialty": random.choice(specialties),
                "description": "",
                "agency": None,
                "agency_role": None,
                "headquarters": None,
                "agency_type": None
            }
            
            # Initialize agency_role for supporting characters
            if role == "supporting":
                supporting_character_count += 1
                if supporting_character_count <= 2:
                    character["agency_role"] = "Protagonist Ally"
                elif supporting_character_count <= 4:
                    character["agency_role"] = "Antagonist Ally"
                else:
                    character["agency_role"] = "Neutral"
            else:
                character["agency_role"] = None
            
            # Assign headquarters/agency based on role and existing agency assignments
            if headquarters:
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
                    if character["agency_role"] == "Protagonist Ally":
                        supporting_hqs = [h for h in headquarters if h["agency"] == protagonist_agency]
                        if not supporting_hqs:
                            supporting_hqs = headquarters
                        hq = random.choice(supporting_hqs)
                    elif character["agency_role"] == "Antagonist Ally":
                        supporting_hqs = [h for h in headquarters if h["agency"] == antagonist_agency]
                        if not supporting_hqs:
                            supporting_hqs = headquarters
                        hq = random.choice(supporting_hqs)
                    else:  # Neutral
                        hq = random.choice(headquarters)
                
                character["headquarters"] = hq["name"]
                character["agency"] = hq["agency"]
                character["agency_type"] = hq["agency_type"]
            
            characters.append(character)
            
        except Exception as e:
            print(f"Error generating character {i} ({role}): {e}")
            continue
    
    return characters

def generate_thriller_relationships(characters):
    """Generate relationships between thriller characters"""
    relationships = []
    relationship_types = [
        "Former partners", "Enemies", "Allies", "Handler and agent", "Mentor and student",
        "Rivals", "Target and hunter", "Protector and protected", "Betrayer and betrayed",
        "Team members", "Former lovers", "Family members", "Informant and contact",
        "Hostage and captor", "Pursuer and pursued"
    ]
    
    relationship_descriptions = [
        "Their partnership ended in betrayal",
        "They are sworn enemies",
        "They work together despite mistrust",
        "One gives orders, the other follows",
        "One taught the other everything they know",
        "They compete for the same objective",
        "One is hunting the other",
        "One must keep the other safe",
        "Trust was broken between them",
        "They depend on each other for survival",
        "Romance complicates their mission",
        "Family ties create conflict",
        "One provides crucial information",
        "One holds the other captive",
        "The chase never ends between them"
    ]
    
    # Generate relationships between main characters
    for i in range(len(characters)):
        for j in range(i + 1, min(i + 3, len(characters))):
            relationship = {
                "character1": characters[i]["name"],
                "character2": characters[j]["name"],
                "type": random.choice(relationship_types),
                "description": random.choice(relationship_descriptions)
            }
            relationships.append(relationship)
    
    return relationships

def save_thriller_characters_to_file(characters, filename="thriller_characters.json"):
    """Save thriller characters to a JSON file"""
    import json
    
    relationships = generate_thriller_relationships(characters)
    
    data = {
        "characters": characters,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "Thriller"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename 