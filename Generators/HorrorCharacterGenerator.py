import json
import random
from datetime import datetime
from .HorrorGenerator import generate_horror_name, HORROR_FIRST_NAMES, HORROR_SURNAMES

# Horror-specific character roles and attributes
HORROR_ROLES = ["protagonist", "deuteragonist", "antagonist", "supporting", "minor"]

HORROR_OCCUPATIONS = [
    "Paranormal Investigator", "Occult Scholar", "Priest/Clergy", "Detective", "Journalist", "Psychologist",
    "Archaeologist", "Librarian", "Museum Curator", "Antique Dealer", "Mortician", "Coroner",
    "Asylum Worker", "Night Watchman", "Caretaker", "Groundskeeper", "Historian", "Professor",
    "Medium", "Psychic", "Witch", "Exorcist", "Monster Hunter", "Cult Leader",
    "Surgeon", "Nurse", "Pharmacist", "Therapist", "Social Worker", "Police Officer"
]

HORROR_TITLES = [
    "Dr.", "Professor", "Father", "Sister", "Reverend", "Detective", "Inspector", "Agent",
    "Lord", "Lady", "Master", "Mistress", "High Priest", "High Priestess", "Elder",
    "Keeper", "Guardian", "Warden", "Curator", "Archivist", "Scholar"
]

HORROR_GOALS = [
    "Uncover the truth behind supernatural events",
    "Protect loved ones from dark forces",
    "Gain forbidden knowledge and power",
    "Destroy an ancient evil",
    "Escape from a supernatural threat",
    "Solve a mysterious disappearance",
    "Stop a cult's apocalyptic ritual",
    "Find a cure for a supernatural curse",
    "Avenge a supernatural murder",
    "Prevent the awakening of an ancient entity",
    "Expose a conspiracy of supernatural beings",
    "Master dark arts and occult powers",
    "Summon and control otherworldly entities",
    "Achieve immortality through dark means",
    "Spread fear and terror",
    "Convert others to a dark faith"
]

HORROR_MOTIVATIONS = [
    "Driven by scientific curiosity about the paranormal",
    "Haunted by a traumatic supernatural encounter",
    "Seeking revenge against supernatural killers",
    "Protecting family legacy and secrets",
    "Obsessed with forbidden knowledge",
    "Called by religious duty to fight evil",
    "Desperate to save a loved one's soul",
    "Compelled by visions and nightmares",
    "Seeking to understand their own supernatural nature",
    "Driven by guilt over past failures",
    "Addicted to the thrill of danger",
    "Corrupted by exposure to dark forces",
    "Seeking power over life and death",
    "Believing they are chosen for a dark purpose",
    "Consumed by hatred for humanity",
    "Driven mad by cosmic revelations"
]

HORROR_FLAWS = [
    "Prone to supernatural nightmares and visions",
    "Obsessed with the occult to a dangerous degree",
    "Suffers from paranoia and trust issues",
    "Addicted to substances to cope with horror",
    "Recklessly brave in the face of danger",
    "Haunted by guilt over past supernatural encounters",
    "Struggles with sanity and reality",
    "Overly skeptical, dismissing real threats",
    "Cursed with supernatural bad luck",
    "Marked by dark entities for persecution",
    "Unable to form lasting relationships",
    "Compulsively drawn to dangerous situations",
    "Suffers from supernatural phobias",
    "Prone to violent outbursts under stress",
    "Gradually losing their humanity",
    "Slowly being corrupted by dark influences"
]

HORROR_STRENGTHS = [
    "Strong willpower against supernatural influence",
    "Extensive knowledge of occult lore",
    "Natural psychic or supernatural abilities",
    "Blessed protection against evil forces",
    "Exceptional courage in terrifying situations",
    "Keen investigative and deductive skills",
    "Strong faith that repels dark entities",
    "Natural leadership in crisis situations",
    "Ability to see through supernatural deceptions",
    "Resistance to fear and mental manipulation",
    "Deep understanding of human psychology",
    "Skilled in combat against monsters",
    "Access to powerful protective artifacts",
    "Ability to communicate with spirits",
    "Natural empathy for supernatural victims",
    "Intuitive understanding of supernatural threats"
]

HORROR_CHARACTER_ARCS = [
    "From skeptic to believer in the supernatural",
    "From innocent to corrupted by dark forces",
    "From victim to powerful supernatural hunter",
    "From faithful to questioning their beliefs",
    "From sane to gradually losing their mind",
    "From human to something more (or less) than human",
    "From powerless to wielding dark abilities",
    "From isolated to finding supernatural allies",
    "From hunter to becoming the hunted",
    "From living to existing between life and death",
    "From normal to accepting their supernatural destiny",
    "From good to embracing necessary evil",
    "From fearful to conquering their deepest terrors",
    "From follower to leader of supernatural resistance",
    "From mortal to achieving a form of immortality",
    "From savior to becoming the very evil they fought"
]

# Horror-specific supernatural attributes
HORROR_SUPERNATURAL_ENCOUNTERS = [
    "Witnessed a demonic possession",
    "Survived a vampire attack",
    "Escaped from a haunted location",
    "Encountered an ancient entity",
    "Participated in an occult ritual",
    "Was cursed by a witch or warlock",
    "Saw through the veil between worlds",
    "Was marked by supernatural forces",
    "Experienced prophetic nightmares",
    "Communicated with the dead",
    "Was temporarily possessed",
    "Discovered a family supernatural legacy",
    "Found forbidden occult knowledge",
    "Was saved by divine intervention",
    "Witnessed a supernatural murder",
    "Uncovered a conspiracy of monsters"
]

HORROR_FEARS = [
    "Fear of the dark and shadows",
    "Fear of being alone in isolated places",
    "Fear of supernatural possession",
    "Fear of losing their sanity",
    "Fear of ancient curses and hexes",
    "Fear of the undead and zombies",
    "Fear of demonic entities",
    "Fear of being watched by unseen forces",
    "Fear of forbidden knowledge",
    "Fear of losing their humanity",
    "Fear of eternal damnation",
    "Fear of supernatural transformation",
    "Fear of being hunted by monsters",
    "Fear of apocalyptic prophecies",
    "Fear of their own dark potential",
    "Fear of supernatural retribution"
]

HORROR_SANITY_LEVELS = [
    "Completely Stable",
    "Slightly Disturbed",
    "Moderately Affected",
    "Significantly Troubled",
    "Severely Damaged",
    "Barely Holding On",
    "Completely Shattered"
]

class HorrorCharacter:
    """Represents a character in a horror story."""
    
    def __init__(self, name, gender, role="supporting"):
        self.name = name
        self.gender = gender
        self.role = role
        self.age = random.randint(18, 70)
        self.occupation = random.choice(HORROR_OCCUPATIONS)
        self.title = random.choice(HORROR_TITLES) if random.random() < 0.3 else ""
        
        # Horror-specific attributes
        self.sanity = random.choice(HORROR_SANITY_LEVELS)
        self.supernatural_encounters = random.sample(HORROR_SUPERNATURAL_ENCOUNTERS, random.randint(1, 3))
        self.fears = random.sample(HORROR_FEARS, random.randint(2, 4))
        
        # Character development
        self.goals = random.sample(HORROR_GOALS, random.randint(1, 3))
        self.motivations = random.sample(HORROR_MOTIVATIONS, random.randint(1, 2))
        self.flaws = random.sample(HORROR_FLAWS, random.randint(1, 3))
        self.strengths = random.sample(HORROR_STRENGTHS, random.randint(1, 3))
        self.arc = random.choice(HORROR_CHARACTER_ARCS)
        
        # Faction affiliation (will be set later)
        self.faction = None
        self.faction_role = None
        self.stronghold = None
        self.faction_type = None
    
    def to_dict(self):
        """Convert character to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "role": self.role,
            "occupation": self.occupation,
            "title": self.title,
            "sanity": self.sanity,
            "supernatural_encounters": self.supernatural_encounters,
            "fears": self.fears,
            "goals": self.goals,
            "motivations": self.motivations,
            "flaws": self.flaws,
            "strengths": self.strengths,
            "arc": self.arc,
            "faction": self.faction,
            "faction_role": self.faction_role,
            "stronghold": self.stronghold,
            "faction_type": self.faction_type
        }

def generate_horror_main_characters(num_characters=5, female_percentage=50, male_percentage=50, **kwargs):
    """Generate main characters for horror stories."""
    # Validate gender percentages
    female_weight = 0.5  # Default
    male_weight = 0.5    # Default

    if not (0 <= female_percentage <= 100 and 
            0 <= male_percentage <= 100 and 
            (female_percentage + male_percentage) == 100):
        print(f"HORROR_CHAR_GEN: Invalid gender percentages (Female: {female_percentage}%, Male: {male_percentage}%). Sum must be 100 and values 0-100. Defaulting to 50/50.")
    else:
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
        print(f"HORROR_CHAR_GEN: Using gender bias: Female {female_percentage}%, Male {male_percentage}%")

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
            print(f"Loaded horror factions data: Found {len(factions_data)} factions")
    except FileNotFoundError:
        print("No factions file found - characters will be generated without faction affiliations")
    except json.JSONDecodeError as e:
        print(f"Error parsing factions.json: {e}")
    except Exception as e:
        print(f"Unexpected error loading factions: {e}")

    # Extract strongholds/territories from factions for character assignment
    strongholds = []
    if factions_data:
        try:
            for faction in factions_data:
                faction_name = faction.get("faction_name", "Unknown Faction")
                faction_type = faction.get("faction_type", "Unknown Type")
                territories = faction.get("territories", [])
                if territories:
                    # Use the first territory as the primary stronghold
                    primary_territory = territories[0]
                    strongholds.append({
                        "name": primary_territory,
                        "faction": faction_name,
                        "faction_type": faction_type
                    })
            print(f"Found {len(strongholds)} strongholds from factions")
        except Exception as e:
            print(f"Error processing faction data: {e}")

    characters = []
    roles = ["protagonist", "deuteragonist", "antagonist"] + ["supporting"] * 7  # Allow up to 10 characters
    
    # Track faction assignments for protagonist and antagonist
    protagonist_faction = None
    antagonist_faction = None
    supporting_character_count = 0
    
    for i in range(min(num_characters, len(roles))):
        try:
            # Generate gender using weights
            gender = random.choices(["female", "male"], weights=[female_weight, male_weight], k=1)[0]
            
            # Generate name
            name, _ = generate_horror_name(gender)
            
            # Assign role
            role = roles[i]
            
            # Create character
            character = HorrorCharacter(name, gender, role)
            
            # Initialize faction_role for supporting characters
            if role == "supporting":
                supporting_character_count += 1
                if supporting_character_count <= 2:
                    character.faction_role = "Protagonist Ally"
                elif supporting_character_count <= 4:
                    character.faction_role = "Antagonist Ally"
                else:
                    character.faction_role = "Neutral"
            else:
                character.faction_role = None
            
            # Adjust attributes based on role
            if role == "antagonist":
                # Antagonists are more likely to have dark goals and be corrupted
                character.goals = random.sample([
                    "Gain forbidden knowledge and power",
                    "Summon and control otherworldly entities",
                    "Achieve immortality through dark means",
                    "Spread fear and terror",
                    "Convert others to a dark faith"
                ], random.randint(1, 2))
                
                character.motivations = random.sample([
                    "Corrupted by exposure to dark forces",
                    "Seeking power over life and death",
                    "Believing they are chosen for a dark purpose",
                    "Consumed by hatred for humanity",
                    "Driven mad by cosmic revelations"
                ], random.randint(1, 2))
                
                character.sanity = random.choice(["Severely Damaged", "Barely Holding On", "Completely Shattered"])
            
            elif role == "protagonist":
                # Protagonists are more likely to be heroes fighting evil
                character.goals = random.sample([
                    "Uncover the truth behind supernatural events",
                    "Protect loved ones from dark forces",
                    "Destroy an ancient evil",
                    "Stop a cult's apocalyptic ritual",
                    "Prevent the awakening of an ancient entity"
                ], random.randint(1, 2))
                
                character.strengths = random.sample([
                    "Strong willpower against supernatural influence",
                    "Exceptional courage in terrifying situations",
                    "Strong faith that repels dark entities",
                    "Natural leadership in crisis situations",
                    "Resistance to fear and mental manipulation"
                ], random.randint(2, 3))
            
            # Assign stronghold/faction based on role and existing faction assignments
            if strongholds:
                if role == "protagonist":
                    stronghold = random.choice(strongholds)
                    protagonist_faction = stronghold["faction"]
                elif role == "antagonist":
                    # Antagonist should be from a different faction if possible
                    antagonist_strongholds = [s for s in strongholds if s["faction"] != protagonist_faction]
                    if not antagonist_strongholds and strongholds:
                        antagonist_strongholds = strongholds
                    stronghold = random.choice(antagonist_strongholds)
                    antagonist_faction = stronghold["faction"]
                elif role == "deuteragonist":
                    # Deuteragonist usually allies with protagonist
                    deuteragonist_strongholds = [s for s in strongholds if s["faction"] == protagonist_faction]
                    if not deuteragonist_strongholds:
                        deuteragonist_strongholds = strongholds
                    stronghold = random.choice(deuteragonist_strongholds)
                else:  # supporting
                    if character.faction_role == "Protagonist Ally":
                        supporting_strongholds = [s for s in strongholds if s["faction"] == protagonist_faction]
                        if not supporting_strongholds:
                            supporting_strongholds = strongholds
                        stronghold = random.choice(supporting_strongholds)
                    elif character.faction_role == "Antagonist Ally":
                        supporting_strongholds = [s for s in strongholds if s["faction"] == antagonist_faction]
                        if not supporting_strongholds:
                            supporting_strongholds = strongholds
                        stronghold = random.choice(supporting_strongholds)
                    else:  # Neutral
                        stronghold = random.choice(strongholds)
                
                character.faction = stronghold["faction"]
                character.stronghold = stronghold["name"]
                character.faction_type = stronghold["faction_type"]
            
            characters.append(character)
            
        except Exception as e:
            print(f"Error generating character {i} ({role}): {e}")
            continue
    
    return characters

def save_horror_characters_to_file(characters, filename="horror_characters.json"):
    """Save horror characters to a JSON file."""
    # Convert characters to dictionaries
    characters_data = []
    for char in characters:
        if hasattr(char, 'to_dict'):
            characters_data.append(char.to_dict())
        else:
            # Handle case where character is already a dict
            characters_data.append(char)
    
    data = {
        "characters": characters_data,
        "metadata": {
            "generation_date": datetime.now().isoformat(),
            "total_characters": len(characters),
            "genre": "Horror"
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return filename

def test_horror_character_generation():
    """Test function to generate and display horror characters."""
    print("Generating Horror Characters...")
    characters = generate_horror_main_characters(5, female_percentage=60, male_percentage=40)
    
    for char in characters:
        print(f"\n=== {char.name} ===")
        print(f"Gender: {char.gender}")
        print(f"Age: {char.age}")
        print(f"Role: {char.role}")
        print(f"Occupation: {char.occupation}")
        if char.title:
            print(f"Title: {char.title}")
        print(f"Sanity Level: {char.sanity}")
        print(f"Goals: {', '.join(char.goals)}")
        print(f"Fears: {', '.join(char.fears[:2])}")  # Show first 2 fears
    
    # Save to file
    filename = save_horror_characters_to_file(characters)
    print(f"\nCharacters saved to {filename}")

if __name__ == "__main__":
    test_horror_character_generation() 