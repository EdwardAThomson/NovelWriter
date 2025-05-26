import json
import random
import os
from datetime import datetime

# --- Mystery Name Generation System ---

# Law enforcement agency names
LAW_ENFORCEMENT_PREFIXES = [
    "Metropolitan", "Central", "Downtown", "Regional", "State", "Federal", "Special", "Elite",
    "Major", "Criminal", "Organized", "Violent", "Financial", "Cyber", "Homicide", "Detective"
]

LAW_ENFORCEMENT_TYPES = [
    "Police Department", "Sheriff's Office", "Detective Bureau", "Investigation Unit",
    "Task Force", "Crime Division", "Special Unit", "Enforcement Agency", "Security Division"
]

# Criminal organization names
CRIMINAL_PREFIXES = [
    "The", "Black", "Red", "Silver", "Golden", "Iron", "Shadow", "Dark", "Silent", "Hidden",
    "Underground", "Midnight", "Crimson", "Steel", "Diamond", "Emerald", "Viper", "Raven", "Wolf"
]

CRIMINAL_TYPES = [
    "Syndicate", "Family", "Cartel", "Organization", "Network", "Brotherhood", "Alliance",
    "Collective", "Enterprise", "Operation", "Ring", "Circle", "Guild", "Society", "Union"
]

# Private investigation firm names
PI_PREFIXES = [
    "Elite", "Premier", "Professional", "Confidential", "Discreet", "Private", "Exclusive",
    "Specialized", "Expert", "Advanced", "Strategic", "Tactical", "Precision", "Reliable"
]

PI_TYPES = [
    "Investigations", "Detective Agency", "Security Services", "Investigation Group",
    "Private Detectives", "Consulting Services", "Research Associates", "Investigation Bureau"
]

# City/Location names for mystery settings
CITY_ADJECTIVES = [
    "Metro", "Central", "Downtown", "Uptown", "Riverside", "Hillside", "Eastside", "Westside",
    "North", "South", "Harbor", "Bay", "Heights", "Valley", "Grove", "Park", "Square"
]

CITY_TYPES = [
    "City", "District", "Precinct", "Ward", "Borough", "Quarter", "Zone", "Area", "Sector"
]

# Mystery-specific faction types and their characteristics
MYSTERY_FACTION_TYPES = {
    "Police Department": {
        "description_templates": [
            "The city's main police force dedicated to solving crimes and maintaining order",
            "A professional law enforcement agency with specialized detective units",
            "A well-equipped police department with modern forensic capabilities",
            "An experienced police force known for their thorough investigations"
        ],
        "goals": [
            "Solve crimes and bring perpetrators to justice",
            "Protect citizens and maintain public safety",
            "Investigate criminal activities thoroughly",
            "Maintain law and order in the community",
            "Collaborate with other law enforcement agencies",
            "Prevent crime through community policing"
        ],
        "resources": [
            "Forensic laboratories and crime scene units",
            "Detective divisions and specialized units",
            "Patrol officers and emergency response teams",
            "Criminal databases and investigation tools",
            "Training facilities and equipment",
            "Community outreach programs"
        ],
        "territories": [
            "City jurisdiction and patrol areas",
            "Police precincts and stations",
            "Crime scenes and investigation sites",
            "Community neighborhoods",
            "Public safety zones",
            "Emergency response areas"
        ]
    },
    "Criminal Organization": {
        "description_templates": [
            "A powerful criminal network involved in various illegal activities",
            "An organized crime syndicate with extensive underground operations",
            "A sophisticated criminal enterprise with multiple revenue streams",
            "A dangerous organization that operates in the shadows of society"
        ],
        "goals": [
            "Expand criminal territory and influence",
            "Generate profits through illegal activities",
            "Eliminate rivals and competition",
            "Corrupt officials and law enforcement",
            "Maintain secrecy and avoid detection",
            "Control lucrative criminal markets"
        ],
        "resources": [
            "Financial assets from illegal operations",
            "Weapons and criminal equipment",
            "Network of informants and contacts",
            "Safe houses and hidden facilities",
            "Corrupt officials and connections",
            "Intimidation and enforcement capabilities"
        ],
        "territories": [
            "Underground criminal networks",
            "Illegal operation sites",
            "Criminal safe houses and hideouts",
            "Black market territories",
            "Corrupt business fronts",
            "Street-level operations"
        ]
    },
    "Private Investigation Agency": {
        "description_templates": [
            "Elite private detectives who take on cases the police can't or won't handle",
            "A professional investigation firm specializing in complex cases",
            "Independent investigators with expertise in specialized areas",
            "A reputable agency known for solving difficult mysteries"
        ],
        "goals": [
            "Solve complex cases for clients",
            "Uncover truth and gather evidence",
            "Provide professional investigation services",
            "Maintain client confidentiality",
            "Build reputation for excellence",
            "Collaborate with law enforcement when needed"
        ],
        "resources": [
            "Specialized investigation skills and training",
            "High-tech surveillance equipment",
            "Network of contacts and informants",
            "Legal expertise and court connections",
            "Client database and case files",
            "Professional investigation tools"
        ],
        "territories": [
            "Private investigation offices",
            "Client service areas",
            "Surveillance operation zones",
            "Professional networks",
            "Court and legal systems",
            "Information gathering networks"
        ]
    },
    "Federal Agency": {
        "description_templates": [
            "Federal agents investigating crimes that cross state lines or involve national security",
            "A specialized federal bureau with jurisdiction over major crimes",
            "Elite federal investigators with advanced resources and authority",
            "A federal agency focused on organized crime and terrorism"
        ],
        "goals": [
            "Investigate federal crimes and violations",
            "Protect national security interests",
            "Combat organized crime and terrorism",
            "Support local law enforcement agencies",
            "Gather intelligence on criminal activities",
            "Prosecute major criminal enterprises"
        ],
        "resources": [
            "Advanced technology and surveillance systems",
            "National criminal databases and intelligence",
            "Specialized units and expert agents",
            "Federal authority and jurisdiction",
            "International cooperation networks",
            "Witness protection programs"
        ],
        "territories": [
            "National jurisdiction and operations",
            "Federal investigation facilities",
            "Interstate crime networks",
            "International cooperation zones",
            "High-security federal buildings",
            "National security areas"
        ]
    },
    "District Attorney Office": {
        "description_templates": [
            "Prosecutors dedicated to bringing criminals to justice through the legal system",
            "A professional legal team focused on criminal prosecution",
            "Experienced attorneys who work closely with law enforcement",
            "A district attorney's office known for successful convictions"
        ],
        "goals": [
            "Prosecute criminals and seek justice",
            "Work with law enforcement on cases",
            "Protect victims and witnesses",
            "Maintain integrity of legal system",
            "Ensure fair and thorough prosecution",
            "Deter crime through successful convictions"
        ],
        "resources": [
            "Legal expertise and court experience",
            "Prosecutor teams and support staff",
            "Victim advocacy programs",
            "Witness protection services",
            "Court system access and authority",
            "Legal research and case databases"
        ],
        "territories": [
            "Court jurisdiction and legal system",
            "Prosecutor offices and facilities",
            "Victim services areas",
            "Legal proceedings and trials",
            "Witness protection networks",
            "Justice system operations"
        ]
    },
    "Forensic Laboratory": {
        "description_templates": [
            "A state-of-the-art forensic facility that analyzes evidence to solve crimes",
            "Expert forensic scientists who provide crucial evidence analysis",
            "An advanced laboratory specializing in criminal evidence processing",
            "A professional forensic team that supports criminal investigations"
        ],
        "goals": [
            "Analyze evidence with scientific precision",
            "Provide expert testimony in court",
            "Support law enforcement investigations",
            "Maintain chain of custody for evidence",
            "Advance forensic science techniques",
            "Ensure accurate and reliable results"
        ],
        "resources": [
            "Advanced scientific equipment and technology",
            "Expert forensic scientists and technicians",
            "Specialized analysis capabilities",
            "Evidence storage and processing facilities",
            "Quality control and certification programs",
            "Research and development capabilities"
        ],
        "territories": [
            "Forensic laboratory facilities",
            "Evidence collection and analysis areas",
            "Scientific research and development",
            "Court testimony and expert witness services",
            "Training and education programs",
            "Quality assurance operations"
        ]
    }
}

def generate_agency_name(agency_type):
    """Generate a name for a law enforcement agency."""
    if agency_type == "Police Department":
        prefix = random.choice(LAW_ENFORCEMENT_PREFIXES)
        agency_type_name = random.choice(LAW_ENFORCEMENT_TYPES)
        return f"{prefix} {agency_type_name}"
    elif agency_type == "Federal Agency":
        federal_names = [
            "Federal Bureau of Investigation", "Drug Enforcement Administration",
            "Bureau of Alcohol, Tobacco, Firearms and Explosives", "U.S. Marshals Service",
            "Secret Service", "Homeland Security Investigations", "Customs and Border Protection",
            "Federal Criminal Investigation Service", "National Security Agency",
            "Central Intelligence Agency"
        ]
        return random.choice(federal_names)
    elif agency_type == "District Attorney Office":
        city_name = f"{random.choice(CITY_ADJECTIVES)} {random.choice(CITY_TYPES)}"
        return f"{city_name} District Attorney's Office"
    elif agency_type == "Forensic Laboratory":
        prefix = random.choice(["State", "Regional", "Metropolitan", "Central", "Advanced", "Elite"])
        lab_type = random.choice(["Forensic Laboratory", "Crime Lab", "Forensic Science Center", "Evidence Analysis Lab"])
        return f"{prefix} {lab_type}"
    else:
        return f"{random.choice(LAW_ENFORCEMENT_PREFIXES)} {random.choice(LAW_ENFORCEMENT_TYPES)}"

def generate_criminal_name():
    """Generate a name for a criminal organization."""
    prefix = random.choice(CRIMINAL_PREFIXES)
    criminal_type = random.choice(CRIMINAL_TYPES)
    
    # Sometimes add descriptive elements
    descriptors = ["", " Crime", " Street", " Underground", " International", " Elite", " Shadow"]
    descriptor = random.choice(descriptors)
    
    if prefix == "The":
        return f"The {random.choice(['Black', 'Red', 'Silver', 'Iron', 'Shadow'])}{descriptor} {criminal_type}"
    else:
        return f"{prefix}{descriptor} {criminal_type}"

def generate_pi_name():
    """Generate a name for a private investigation agency."""
    prefix = random.choice(PI_PREFIXES)
    pi_type = random.choice(PI_TYPES)
    
    # Sometimes add surnames or descriptive elements
    surnames = ["& Associates", "& Partners", "Group", "Services", "Solutions", "Consultants"]
    if random.random() < 0.4:
        suffix = f" {random.choice(surnames)}"
    else:
        suffix = ""
    
    return f"{prefix} {pi_type}{suffix}"

def create_mystery_faction(faction_type=None):
    """
    Create a single mystery faction/organization.
    
    Args:
        faction_type: Specific type of faction to create, or None for random
    
    Returns:
        dict: Faction data structure
    """
    if faction_type is None:
        faction_type = random.choice(list(MYSTERY_FACTION_TYPES.keys()))
    
    faction_data = MYSTERY_FACTION_TYPES[faction_type]
    
    # Generate name based on faction type
    if faction_type == "Criminal Organization":
        name = generate_criminal_name()
    elif faction_type == "Private Investigation Agency":
        name = generate_pi_name()
    else:  # Law enforcement, federal, DA, forensic
        name = generate_agency_name(faction_type)
    
    # Select random elements from the faction type data
    description = random.choice(faction_data["description_templates"])
    goals = random.sample(faction_data["goals"], min(3, len(faction_data["goals"])))
    resources = random.sample(faction_data["resources"], min(4, len(faction_data["resources"])))
    territory = random.choice(faction_data["territories"])
    
    # Generate allies and enemies based on faction type
    allies, enemies = generate_faction_relationships(faction_type)
    
    return {
        "name": name,
        "type": faction_type,
        "description": description,
        "goals": goals,
        "resources": resources,
        "territory": territory,
        "allies": allies,
        "enemies": enemies,
        "jurisdiction": random.choice(["Local", "Regional", "State", "Federal", "International"]),
        "funding_level": random.choice(["Limited", "Adequate", "Well-funded", "Heavily funded", "Unlimited"]),
        "reputation": random.choice(["Unknown", "Emerging", "Established", "Respected", "Legendary"])
    }

def generate_faction_relationships(faction_type):
    """Generate allies and enemies for a faction based on its type."""
    
    relationship_map = {
        "Police Department": {
            "allies": ["Federal agencies", "District Attorney's Office", "Forensic laboratories", 
                      "Community leaders", "Victim advocacy groups", "Other police departments"],
            "enemies": ["Criminal organizations", "Corrupt officials", "Drug cartels", 
                       "Organized crime", "Gang networks", "Criminal enterprises"]
        },
        "Criminal Organization": {
            "allies": ["Corrupt officials", "Other criminal groups", "Money launderers", 
                      "Black market dealers", "Criminal lawyers", "Underground networks"],
            "enemies": ["Police departments", "Federal agencies", "Rival criminal groups", 
                       "Informants", "Undercover agents", "Honest officials"]
        },
        "Private Investigation Agency": {
            "allies": ["Former law enforcement", "Legal professionals", "Insurance companies", 
                      "Corporate clients", "Information brokers", "Security firms"],
            "enemies": ["Criminal organizations", "Corrupt officials", "Uncooperative witnesses", 
                       "Competing agencies", "Legal obstacles", "Dangerous suspects"]
        },
        "Federal Agency": {
            "allies": ["Local law enforcement", "International agencies", "Intelligence services", 
                      "Military units", "Prosecutor offices", "Specialized task forces"],
            "enemies": ["Terrorist organizations", "International crime syndicates", "Espionage networks", 
                       "Cyber criminals", "Drug cartels", "Organized crime families"]
        },
        "District Attorney Office": {
            "allies": ["Police departments", "Federal agencies", "Victim advocates", 
                      "Court system", "Witness protection", "Legal professionals"],
            "enemies": ["Defense attorneys", "Criminal organizations", "Corrupt judges", 
                       "Intimidated witnesses", "Legal loopholes", "Political pressure"]
        },
        "Forensic Laboratory": {
            "allies": ["Law enforcement agencies", "Medical examiners", "Scientific community", 
                      "Court system", "Research institutions", "Technology providers"],
            "enemies": ["Evidence tampering", "Budget constraints", "Political interference", 
                       "Equipment failures", "Contamination risks", "Time pressures"]
        }
    }
    
    faction_relationships = relationship_map.get(faction_type, {
        "allies": ["Law enforcement", "Legal system", "Community support"],
        "enemies": ["Criminal elements", "Corruption", "Opposition forces"]
    })
    
    # Select 2-4 allies and 2-3 enemies
    allies = random.sample(faction_relationships["allies"], 
                          min(random.randint(2, 4), len(faction_relationships["allies"])))
    enemies = random.sample(faction_relationships["enemies"], 
                           min(random.randint(2, 3), len(faction_relationships["enemies"])))
    
    return allies, enemies

def generate_mystery_world(num_factions=5, **kwargs):
    """
    Generate a complete mystery world with law enforcement and criminal organizations.
    
    Args:
        num_factions: Number of factions/organizations to generate
        **kwargs: Additional parameters (for compatibility)
    
    Returns:
        list: List of faction dictionaries
    """
    factions = []
    
    # Ensure we have a good mix of faction types
    faction_types = list(MYSTERY_FACTION_TYPES.keys())
    
    for i in range(num_factions):
        # For the first few factions, ensure variety
        if i < len(faction_types):
            faction_type = faction_types[i]
        else:
            # For additional factions, choose randomly but favor law enforcement and criminal orgs
            weighted_types = (
                ["Police Department"] * 3 + 
                ["Criminal Organization"] * 3 + 
                ["Private Investigation Agency"] * 2 + 
                ["Federal Agency"] * 1 + 
                ["District Attorney Office"] * 1 + 
                ["Forensic Laboratory"] * 1
            )
            faction_type = random.choice(weighted_types)
        
        faction = create_mystery_faction(faction_type)
        factions.append(faction)
    
    return factions

def save_mystery_factions_to_file(factions, filename=None, timestamp=False):
    """
    Save mystery factions to a JSON file.
    
    Args:
        factions: List of faction dictionaries
        filename: Output filename (optional)
        timestamp: Whether to add timestamp to filename
    
    Returns:
        str: Path to saved file
    """
    if filename is None:
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mystery_factions_{timestamp_str}.json"
        else:
            filename = "mystery_factions.json"
    
    # Ensure the filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(factions, f, indent=4, ensure_ascii=False)
        print(f"Mystery factions saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving mystery factions: {e}")
        return None

def print_mystery_factions(factions):
    """Print mystery factions in a readable format."""
    print("\n" + "="*60)
    print("MYSTERY WORLD - LAW ENFORCEMENT & CRIMINAL ORGANIZATIONS")
    print("="*60)
    
    for i, faction in enumerate(factions, 1):
        print(f"\n{i}. {faction['name']} ({faction['type']})")
        print("-" * 50)
        print(f"Description: {faction['description']}")
        print(f"Territory: {faction['territory']}")
        print(f"Jurisdiction: {faction['jurisdiction']} | Funding: {faction['funding_level']} | Reputation: {faction['reputation']}")
        
        print(f"\nGoals:")
        for goal in faction['goals']:
            print(f"  • {goal}")
        
        print(f"\nResources:")
        for resource in faction['resources']:
            print(f"  • {resource}")
        
        print(f"\nAllies: {', '.join(faction['allies'])}")
        print(f"Enemies: {', '.join(faction['enemies'])}")

# Main generation function for compatibility with existing system
def generate_mystery_factions(num_factions=5, **kwargs):
    """
    Main function to generate mystery factions.
    Compatible with the existing faction generation system.
    """
    return generate_mystery_world(num_factions=num_factions, **kwargs)

if __name__ == "__main__":
    # Test the generator
    print("Testing Mystery Generator...")
    factions = generate_mystery_factions(6)
    print_mystery_factions(factions)
    
    # Save to file
    save_mystery_factions_to_file(factions, "test_mystery_factions.json") 