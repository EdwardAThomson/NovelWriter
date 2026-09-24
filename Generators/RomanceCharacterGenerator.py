import random
import json
from datetime import datetime

from .name_utils import (
    CharacterRecord,
    NameRegistry,
    apply_name_parts,
    as_dict,
    load_faction_data,
    normalize_gender,
    reserve_person_names,
    title_for_gender,
)

def generate_romance_names():
    """Generate names suitable for romance characters"""
    first_names_male = [
        "Alexander", "Sebastian", "Nicholas", "Christopher", "Benjamin", "Jonathan", "Matthew", "Andrew",
        "Gabriel", "Daniel", "Michael", "William", "James", "David", "Robert", "Thomas", "Charles",
        "Anthony", "Mark", "Steven", "Kevin", "Brian", "Edward", "Ronald", "Timothy", "Jason",
        "Jeffrey", "Ryan", "Jacob", "Gary", "Vincent", "Eric", "Stephen", "Julian", "Larry",
        "Justin", "Marcus", "Brandon", "Frank", "Gregory", "Raymond", "Samuel", "Patrick", "Jack"
    ]
    
    first_names_female = [
        "Isabella", "Sophia", "Charlotte", "Amelia", "Olivia", "Ava", "Emily", "Abigail", "Harper",
        "Evelyn", "Elizabeth", "Sofia", "Madison", "Avery", "Ella", "Scarlett", "Grace", "Chloe",
        "Victoria", "Riley", "Aria", "Lily", "Aubrey", "Zoey", "Penelope", "Lillian", "Addison",
        "Layla", "Natalie", "Camila", "Hannah", "Brooklyn", "Zoe", "Nora", "Leah", "Savannah",
        "Audrey", "Claire", "Eleanor", "Skylar", "Ellie", "Samantha", "Stella", "Paisley", "Violet"
    ]
    
    last_names = [
        "Anderson", "Thompson", "Wilson", "Martinez", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Brooks", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis",
        "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
        "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
        "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", "Cook"
    ]
    
    return first_names_male, first_names_female, last_names

def generate_romance_goals():
    """Generate goals appropriate for romance characters"""
    love_goals = [
        "Find their soulmate",
        "Learn to trust in love again",
        "Overcome past heartbreak",
        "Build a lasting relationship",
        "Start a family",
        "Find someone who accepts them completely",
        "Learn to love themselves first",
        "Reconnect with their first love",
        "Find love in an unexpected place",
        "Choose between two loves"
    ]
    
    personal_goals = [
        "Advance their career",
        "Start their own business",
        "Travel the world",
        "Write a novel",
        "Become a parent",
        "Buy their dream home",
        "Learn a new skill",
        "Help their family",
        "Achieve financial independence",
        "Make a difference in the world"
    ]
    
    relationship_goals = [
        "Win back their ex-lover",
        "Prove they're worthy of love",
        "Show their partner they've changed",
        "Plan the perfect wedding",
        "Save their marriage",
        "Learn to communicate better",
        "Balance work and love",
        "Introduce their partner to their family",
        "Move in together",
        "Take their relationship to the next level"
    ]
    
    return love_goals + personal_goals + relationship_goals

def generate_romance_motivations():
    """Generate motivations for romance characters"""
    return [
        "Desire for true love",
        "Fear of being alone",
        "Need for emotional connection",
        "Wanting to be understood",
        "Seeking companionship",
        "Desire for passion",
        "Need for security",
        "Wanting to start a family",
        "Seeking adventure with someone special",
        "Desire to heal from past wounds",
        "Need for acceptance",
        "Wanting to prove their worth",
        "Seeking redemption through love",
        "Desire for a fresh start",
        "Need to feel complete",
        "Wanting to honor a promise",
        "Seeking to overcome fear",
        "Desire for happiness",
        "Need to protect loved ones",
        "Wanting to build a legacy"
    ]

def generate_romance_flaws():
    """Generate character flaws for romance characters"""
    return [
        "Afraid of commitment",
        "Too trusting",
        "Overly romantic",
        "Jealous and possessive",
        "Workaholic",
        "Emotionally unavailable",
        "Too independent",
        "Clingy and needy",
        "Has trust issues",
        "Perfectionist",
        "Stubborn",
        "Impulsive in relationships",
        "Puts others before themselves",
        "Afraid of vulnerability",
        "Holds grudges",
        "Overly critical",
        "Avoids conflict",
        "Too focused on the past",
        "Unrealistic expectations",
        "Difficulty expressing emotions"
    ]

def generate_romance_strengths():
    """Generate character strengths for romance characters"""
    return [
        "Loyal and devoted",
        "Great listener",
        "Emotionally intelligent",
        "Romantic and thoughtful",
        "Supportive partner",
        "Good communicator",
        "Passionate and intense",
        "Caring and nurturing",
        "Honest and trustworthy",
        "Adventurous spirit",
        "Strong sense of humor",
        "Empathetic and understanding",
        "Confident and self-assured",
        "Creative and artistic",
        "Ambitious and driven",
        "Generous and giving",
        "Patient and forgiving",
        "Spontaneous and fun",
        "Protective of loved ones",
        "Optimistic about love"
    ]

def generate_romance_character_arcs():
    """Generate character development arcs for romance characters"""
    return [
        "Learning to open their heart again",
        "Overcoming fear of commitment",
        "Finding balance between independence and love",
        "Learning to trust after betrayal",
        "Discovering self-worth through love",
        "Choosing love over career ambition",
        "Learning to forgive past mistakes",
        "Overcoming family disapproval",
        "Finding courage to pursue true love",
        "Learning to communicate honestly",
        "Overcoming social barriers for love",
        "Learning to love without conditions",
        "Finding strength through vulnerability",
        "Choosing happiness over security",
        "Learning to let go of the past",
        "Discovering what they really want in love",
        "Overcoming personal insecurities",
        "Learning to fight for their relationship",
        "Finding love in unexpected circumstances",
        "Learning to believe in second chances"
    ]

def generate_romance_professions():
    """Generate professions suitable for romance characters"""
    return [
        "Doctor", "Nurse", "Teacher", "Lawyer", "Chef", "Artist", "Writer", "Photographer",
        "Architect", "Engineer", "Veterinarian", "Florist", "Baker", "Designer", "Musician",
        "Journalist", "Therapist", "Social Worker", "Librarian", "Event Planner", "Real Estate Agent",
        "Marketing Executive", "Fashion Designer", "Interior Designer", "Travel Agent", "Fitness Trainer",
        "Bookstore Owner", "Café Owner", "Gallery Owner", "Wedding Planner", "Dance Instructor",
        "Personal Assistant", "HR Manager", "Financial Advisor", "Consultant", "Entrepreneur"
    ]

# Romance characters are addressed by name, not rank; only the handful of
# professions that carry an honorific get a title.
ROMANCE_PROFESSION_TITLES = {
    "Doctor": "Dr.",
    "Veterinarian": "Dr.",
    "Therapist": "Dr.",
    "Lawyer": "Counselor",
    "Chef": "Chef",
}


def title_for_profession(profession, gender=None):
    """Return the honorific for a profession, or "" if it carries none."""
    return ROMANCE_PROFESSION_TITLES.get(profession, "")


def generate_romance_backgrounds():
    """Generate background stories for romance characters"""
    return [
        "Grew up in a small town",
        "Comes from a wealthy family",
        "Raised by a single parent",
        "Has a large, close-knit family",
        "Moved around a lot as a child",
        "Lost a parent at a young age",
        "Was adopted",
        "Grew up on a farm",
        "Lived in the city all their life",
        "Comes from a military family",
        "Parents divorced when they were young",
        "Was the youngest of many siblings",
        "Grew up in foster care",
        "Had a privileged upbringing",
        "Struggled financially growing up",
        "Parents had a perfect marriage",
        "Witnessed a difficult divorce",
        "Raised by grandparents",
        "Moved to the country for a fresh start",
        "Has always lived in the same neighborhood"
    ]

def generate_romance_main_characters(num_characters=5, female_percentage=50, male_percentage=50, output_dir=None, **kwargs):
    """Generate main characters for romance stories"""
    # Validate gender percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"ROMANCE_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"ROMANCE_CHAR_GEN: Using gender bias: Female {female_percentage}%, Male {male_percentage}%")

    # Try to load factions data for social group assignment
    factions_data = load_faction_data(output_dir, label="social groups")

    # Extract venues from social groups for character assignment
    venues = []
    if factions_data:
        try:
            for group in factions_data:
                group_name = group.get("name", "Unknown Group")
                group_type = group.get("type", "Unknown Type")
                territory = group.get("territory", "Unknown Location")
                venues.append({
                    "name": territory,
                    "social_group": group_name,
                    "group_type": group_type
                })
            print(f"Found {len(venues)} venues from social groups")
        except Exception as e:
            print(f"Error processing social group data: {e}")

    first_names_male, first_names_female, last_names = generate_romance_names()
    goals = generate_romance_goals()
    motivations = generate_romance_motivations()
    flaws = generate_romance_flaws()
    strengths = generate_romance_strengths()
    arcs = generate_romance_character_arcs()
    professions = generate_romance_professions()
    backgrounds = generate_romance_backgrounds()
    
    roles = ["protagonist", "love_interest", "supporting"] + ["supporting"] * 7  # Allow up to 10 characters
    
    characters = []
    
    # Track social group assignments for protagonist and love interest
    protagonist_group = None
    love_interest_group = None
    supporting_character_count = 0
    
    # One registry per cast so no two characters share a name, seeded with
    # the social group roster so they cannot reuse a name from there either.
    name_registry = NameRegistry()
    reserve_person_names(name_registry, factions_data)

    for i in range(min(num_characters, len(roles))):
        try:
            # Generate gender using weights
            gender = random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]
            
            # A character's honorific, if any, follows from their profession.
            profession = random.choice(professions)

            # Select name based on gender
            name = name_registry.unique_name(
                lambda: f"{random.choice(first_names_female if gender == 'Female' else first_names_male)} "
                        f"{random.choice(last_names)}")
            
            # Assign role
            role = roles[i]
            
            # Generate character details
            character = {
                "name": name,
                "role": role,
                "gender": gender,
                "age": random.randint(22, 45),
                "goals": [random.choice(goals)],
                "motivations": [random.choice(motivations)],
                "flaws": [random.choice(flaws)],
                "strengths": [random.choice(strengths)],
                "arc": random.choice(arcs),
                "background": random.choice(backgrounds),
                "profession": profession,
                "description": "",
                "social_group": None,
                "group_role": None,
                "venue": None,
                "group_type": None
            }
            
            # Initialize group_role for supporting characters
            if role == "supporting":
                supporting_character_count += 1
                if supporting_character_count <= 2:
                    character["group_role"] = "Protagonist Ally"
                elif supporting_character_count <= 4:
                    character["group_role"] = "Love Interest Ally"
                else:
                    character["group_role"] = "Neutral"
            else:
                character["group_role"] = None
            
            # Assign venue/social group based on role and existing group assignments
            if venues:
                if role == "protagonist":
                    venue = random.choice(venues)
                    protagonist_group = venue["social_group"]
                elif role == "love_interest":
                    # Love interest could be from same or different group (romance trope)
                    if random.random() < 0.6:  # 60% chance same group, 40% different
                        love_interest_venues = [v for v in venues if v["social_group"] == protagonist_group]
                        if not love_interest_venues:
                            love_interest_venues = venues
                    else:
                        love_interest_venues = [v for v in venues if v["social_group"] != protagonist_group]
                        if not love_interest_venues:
                            love_interest_venues = venues
                    venue = random.choice(love_interest_venues)
                    love_interest_group = venue["social_group"]
                else:  # supporting
                    if character["group_role"] == "Protagonist Ally":
                        supporting_venues = [v for v in venues if v["social_group"] == protagonist_group]
                        if not supporting_venues:
                            supporting_venues = venues
                        venue = random.choice(supporting_venues)
                    elif character["group_role"] == "Love Interest Ally":
                        supporting_venues = [v for v in venues if v["social_group"] == love_interest_group]
                        if not supporting_venues:
                            supporting_venues = venues
                        venue = random.choice(supporting_venues)
                    else:  # Neutral
                        venue = random.choice(venues)
                
                character["venue"] = venue["name"]
                character["social_group"] = venue["social_group"]
                character["group_type"] = venue["group_type"]
            
            # Record the title, first name, surname and display name.
            apply_name_parts(character, character["name"],
                             title_for_profession(profession, gender))

            # Wrapped so consumers can use either char["name"] or char.name.
            characters.append(CharacterRecord(character))
            
        except Exception as e:
            print(f"Error generating character {i} ({role}): {e}")
            continue
    
    return characters

def generate_romance_relationships(characters):
    """Generate relationships between romance characters"""
    relationships = []
    relationship_types = [
        "Romantic interests", "Ex-lovers", "Best friends", "Rivals in love", "Siblings",
        "Colleagues", "Mentor and student", "Neighbors", "Childhood friends", "Enemies to lovers",
        "Friends with benefits", "Arranged marriage", "Secret lovers", "Star-crossed lovers",
        "Second chance romance"
    ]
    
    relationship_descriptions = [
        "Their chemistry is undeniable",
        "They have a complicated history",
        "They support each other through everything",
        "They're competing for the same person",
        "Family bonds complicate their relationship",
        "They work together every day",
        "One taught the other about love",
        "Proximity leads to unexpected feelings",
        "They've known each other forever",
        "Hate slowly turns to love",
        "They try to keep things casual",
        "Their families arranged their union",
        "They must hide their relationship",
        "Society keeps them apart",
        "They get a second chance at love"
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

def save_romance_characters_to_file(characters, filename="romance_characters.json"):
    """Save romance characters to a JSON file"""
    import json
    
    relationships = generate_romance_relationships(characters)
    
    data = {
        "characters": [as_dict(char) for char in characters],
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "Romance"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename 