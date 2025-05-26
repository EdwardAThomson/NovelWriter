import random
import json
from datetime import datetime

def generate_western_names():
    """Generate names suitable for western characters"""
    first_names_male = [
        "Jake", "Cole", "Wyatt", "Jesse", "Colt", "Buck", "Hank", "Wade", "Clay", "Jed",
        "Luke", "Sam", "Tom", "Bill", "Jack", "Frank", "Joe", "Ben", "Matt", "Dan",
        "Clint", "Duke", "Rex", "Cash", "Tex", "Beau", "Zeke", "Ike", "Gus", "Bart",
        "Sheriff", "Marshal", "Deputy", "Judge", "Doc", "Preacher", "Captain", "Major"
    ]
    
    first_names_female = [
        "Belle", "Annie", "Rose", "Grace", "Faith", "Hope", "Ruby", "Pearl", "Daisy", "Lily",
        "Mary", "Sarah", "Emma", "Kate", "Jane", "Beth", "Sue", "May", "Joy", "Dawn",
        "Scarlett", "Violet", "Iris", "Sage", "Willow", "Sierra", "Dakota", "Cheyenne", "Savannah", "Georgia"
    ]
    
    last_names = [
        "Walker", "Rider", "Hunter", "Tracker", "Ranger", "Gunner", "Shooter", "Quick", "Swift", "Fast",
        "Strong", "Steel", "Iron", "Stone", "Rock", "Hill", "Mountain", "Valley", "River", "Creek",
        "Wild", "Free", "Brave", "True", "Just", "Fair", "Good", "Noble", "Wise", "Sharp",
        "Black", "White", "Gray", "Brown", "Green", "Blue", "Red", "Gold", "Silver", "Copper",
        "Wolf", "Bear", "Eagle", "Hawk", "Fox", "Coyote", "Bull", "Horse", "Mustang", "Bronco"
    ]
    
    return first_names_male, first_names_female, last_names

def generate_western_goals():
    """Generate goals appropriate for western characters"""
    lawman_goals = [
        "Bring a notorious outlaw to justice",
        "Clean up a lawless town",
        "Protect settlers from bandits",
        "Stop a range war",
        "Find the killer of their partner",
        "Escort a prisoner to trial",
        "Defend the town from raiders",
        "Investigate cattle rustling",
        "Stop a bank robbery gang",
        "Maintain peace in the territory"
    ]
    
    outlaw_goals = [
        "Pull off the biggest heist in the territory",
        "Escape from the law",
        "Get revenge on those who wronged them",
        "Build a criminal empire",
        "Find a legendary treasure",
        "Clear their name of false charges",
        "Protect their gang from rivals",
        "Take over a town",
        "Steal a fortune in gold",
        "Evade capture and start fresh"
    ]
    
    settler_goals = [
        "Build a successful ranch",
        "Protect their family from danger",
        "Find water for their land",
        "Defend their property from claim jumpers",
        "Make peace with local tribes",
        "Survive the harsh frontier",
        "Build a new life in the West",
        "Find their missing family member",
        "Establish a trading post",
        "Strike it rich in the gold fields"
    ]
    
    return lawman_goals + outlaw_goals + settler_goals

def generate_western_motivations():
    """Generate motivations for western characters"""
    return [
        "Seeking justice for past wrongs",
        "Protecting family and loved ones",
        "Pursuing freedom and independence",
        "Seeking redemption for past sins",
        "Driven by a sense of duty",
        "Seeking revenge for betrayal",
        "Pursuing wealth and prosperity",
        "Protecting the innocent",
        "Seeking adventure and excitement",
        "Driven by survival instinct",
        "Upholding the law",
        "Seeking a fresh start",
        "Protecting their land",
        "Pursuing honor and respect",
        "Seeking to right past wrongs",
        "Driven by loyalty to friends",
        "Pursuing the American dream",
        "Seeking to build a legacy",
        "Protecting their way of life",
        "Driven by moral conviction"
    ]

def generate_western_flaws():
    """Generate character flaws for western characters"""
    return [
        "Quick to draw their gun",
        "Has a drinking problem",
        "Haunted by their past",
        "Too proud for their own good",
        "Doesn't trust anyone",
        "Has a gambling addiction",
        "Prone to violence",
        "Stubborn and inflexible",
        "Holds grudges too long",
        "Reckless and impulsive",
        "Has a bad temper",
        "Too loyal to the wrong people",
        "Afraid of settling down",
        "Overly suspicious of strangers",
        "Can't forgive themselves",
        "Too independent for teamwork",
        "Haunted by war memories",
        "Prejudiced against certain groups",
        "Prone to taking unnecessary risks",
        "Has trouble with authority"
    ]

def generate_western_strengths():
    """Generate character strengths for western characters"""
    return [
        "Expert marksman",
        "Excellent horseman",
        "Skilled tracker",
        "Natural leader",
        "Quick draw artist",
        "Survival expert",
        "Good judge of character",
        "Loyal friend",
        "Brave under fire",
        "Strong moral compass",
        "Excellent negotiator",
        "Skilled fighter",
        "Good with animals",
        "Natural diplomat",
        "Resourceful problem solver",
        "Honest and trustworthy",
        "Protective of others",
        "Skilled craftsman",
        "Good storyteller",
        "Natural healer"
    ]

def generate_western_character_arcs():
    """Generate character development arcs for western characters"""
    return [
        "Learning to trust others again",
        "Finding redemption for past crimes",
        "Choosing law over revenge",
        "Learning to settle down",
        "Overcoming prejudice",
        "Finding peace after war",
        "Learning to work with others",
        "Choosing family over duty",
        "Finding their place in civilization",
        "Learning to forgive",
        "Overcoming their violent past",
        "Finding love on the frontier",
        "Learning to lead others",
        "Choosing justice over personal gain",
        "Finding their moral center",
        "Learning to trust the law",
        "Overcoming their fear of commitment",
        "Finding their true calling",
        "Learning to let go of the past",
        "Choosing hope over despair"
    ]

def generate_western_professions():
    """Generate professions suitable for western characters"""
    return [
        "Sheriff", "Marshal", "Deputy", "Gunfighter", "Outlaw", "Bounty Hunter", "Rancher",
        "Cowboy", "Cattle Rustler", "Bank Robber", "Saloon Owner", "Bartender", "Gambler",
        "Doctor", "Preacher", "Teacher", "Blacksmith", "Storekeeper", "Banker", "Judge",
        "Prospector", "Miner", "Railroad Worker", "Telegraph Operator", "Stage Driver",
        "Horse Trader", "Cattle Baron", "Homesteader", "Scout", "Indian Agent", "Soldier",
        "Cavalry Officer", "Fort Commander", "Trader", "Trapper", "Guide", "Newspaper Editor"
    ]

def generate_western_backgrounds():
    """Generate background stories for western characters"""
    return [
        "Former Civil War soldier",
        "Grew up on a ranch",
        "Orphaned at a young age",
        "Former outlaw turned lawman",
        "Came west to escape their past",
        "Lost their family to raiders",
        "Former cavalry officer",
        "Grew up in a frontier town",
        "Former slave seeking freedom",
        "Immigrant seeking opportunity",
        "Former Confederate soldier",
        "Raised by Native Americans",
        "Former Union soldier",
        "Came west for gold rush",
        "Former Texas Ranger",
        "Grew up in the mountains",
        "Former railroad worker",
        "Lost their ranch to drought",
        "Former army scout",
        "Came west to start over"
    ]

def generate_western_main_characters(num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
    """Generate main characters for western stories"""
    # Validate gender percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"WESTERN_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"WESTERN_CHAR_GEN: Using gender bias: Female {female_percentage}%, Male {male_percentage}%")

    # Try to load factions data for faction assignment
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
            print(f"Loaded western factions data: Found {len(factions_data)} factions")
    except FileNotFoundError:
        print("No factions file found - characters will be generated without faction affiliations")
    except json.JSONDecodeError as e:
        print(f"Error parsing factions.json: {e}")
    except Exception as e:
        print(f"Unexpected error loading factions: {e}")

    # Extract territories from factions for character assignment
    territories = []
    if factions_data:
        try:
            for faction in factions_data:
                faction_name = faction.get("name", "Unknown Faction")
                faction_type = faction.get("type", "Unknown Type")
                territory = faction.get("territory", "Unknown Territory")
                territories.append({
                    "name": territory,
                    "faction": faction_name,
                    "faction_type": faction_type
                })
            print(f"Found {len(territories)} territories from factions")
        except Exception as e:
            print(f"Error processing faction data: {e}")

    first_names_male, first_names_female, last_names = generate_western_names()
    goals = generate_western_goals()
    motivations = generate_western_motivations()
    flaws = generate_western_flaws()
    strengths = generate_western_strengths()
    arcs = generate_western_character_arcs()
    professions = generate_western_professions()
    backgrounds = generate_western_backgrounds()
    
    roles = ["protagonist", "deuteragonist", "antagonist"] + ["supporting"] * 7  # Allow up to 10 characters
    
    characters = []
    
    # Track faction assignments for protagonist and antagonist
    protagonist_faction = None
    antagonist_faction = None
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
                "age": random.randint(20, 60),
                "goals": [random.choice(goals)],
                "motivations": [random.choice(motivations)],
                "flaws": [random.choice(flaws)],
                "strengths": [random.choice(strengths)],
                "arc": random.choice(arcs),
                "background": random.choice(backgrounds),
                "profession": random.choice(professions),
                "description": "",
                "faction": None,
                "faction_role": None,
                "territory": None,
                "faction_type": None
            }
            
            # Initialize faction_role for supporting characters
            if role == "supporting":
                supporting_character_count += 1
                if supporting_character_count <= 2:
                    character["faction_role"] = "Protagonist Ally"
                elif supporting_character_count <= 4:
                    character["faction_role"] = "Antagonist Ally"
                else:
                    character["faction_role"] = "Neutral"
            else:
                character["faction_role"] = None
            
            # Assign territory/faction based on role and existing faction assignments
            if territories:
                if role == "protagonist":
                    territory = random.choice(territories)
                    protagonist_faction = territory["faction"]
                elif role == "antagonist":
                    # Antagonist should be from a different faction if possible
                    antagonist_territories = [t for t in territories if t["faction"] != protagonist_faction]
                    if not antagonist_territories and territories:
                        antagonist_territories = territories
                    territory = random.choice(antagonist_territories)
                    antagonist_faction = territory["faction"]
                elif role == "deuteragonist":
                    # Deuteragonist usually allies with protagonist
                    deuteragonist_territories = [t for t in territories if t["faction"] == protagonist_faction]
                    if not deuteragonist_territories:
                        deuteragonist_territories = territories
                    territory = random.choice(deuteragonist_territories)
                else:  # supporting
                    if character["faction_role"] == "Protagonist Ally":
                        supporting_territories = [t for t in territories if t["faction"] == protagonist_faction]
                        if not supporting_territories:
                            supporting_territories = territories
                        territory = random.choice(supporting_territories)
                    elif character["faction_role"] == "Antagonist Ally":
                        supporting_territories = [t for t in territories if t["faction"] == antagonist_faction]
                        if not supporting_territories:
                            supporting_territories = territories
                        territory = random.choice(supporting_territories)
                    else:  # Neutral
                        territory = random.choice(territories)
                
                character["territory"] = territory["name"]
                character["faction"] = territory["faction"]
                character["faction_type"] = territory["faction_type"]
            
            characters.append(character)
            
        except Exception as e:
            print(f"Error generating character {i} ({role}): {e}")
            continue
    
    return characters

def generate_western_relationships(characters):
    """Generate relationships between western characters"""
    relationships = []
    relationship_types = [
        "Lawman and outlaw", "Former partners", "Rivals", "Mentor and student", "Family members",
        "Old war buddies", "Enemies", "Allies", "Romantic interests", "Business partners",
        "Hunter and hunted", "Friends", "Neighbors", "Employer and employee", "Competitors"
    ]
    
    relationship_descriptions = [
        "One enforces the law, the other breaks it",
        "They once rode together but parted ways",
        "They compete for the same goal",
        "One taught the other to survive",
        "Blood ties bind them together",
        "They fought side by side in the war",
        "Old grievances divide them",
        "They work together for mutual benefit",
        "Love complicates their relationship",
        "They share business interests",
        "One pursues the other relentlessly",
        "They trust each other completely",
        "They live and work near each other",
        "One works for the other",
        "They vie for the same prize"
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

def save_western_characters_to_file(characters, filename="western_characters.json"):
    """Save western characters to a JSON file"""
    import json
    
    relationships = generate_western_relationships(characters)
    
    data = {
        "characters": characters,
        "relationships": relationships,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "Western"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename 