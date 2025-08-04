class FantasyConfigs:
    CONFIGS = {
        "High Fantasy": {
            "implied_settings": {
                "magic_system": True,
                "medieval_setting": True,
                "mythical_creatures": True,
                "epic_scale": True
            },
            "protagonist_types": [
                "Chosen One",
                "Magic User",
                "Knight/Warrior",
                "Royal Heir",
                "Common Hero",
                "Prophesied One"
            ],
            "conflict_scales": [
                "Personal Quest",
                "Kingdom-wide",
                "World-saving",
                "Good vs Evil",
                "Political Intrigue"
            ],
            "tones": [
                "Epic",
                "Heroic",
                "Noble",
                "Mythic",
                "Adventure"
            ]
        },
        "Dark Fantasy": {
            "implied_settings": {
                "grim_world": True,
                "dangerous_magic": True,
                "moral_ambiguity": True,
                "supernatural_threats": True
            },
            "protagonist_types": [
                "Antihero",
                "Cursed Individual",
                "Monster Hunter",
                "Corrupted Noble",
                "Reluctant Chosen One",
                "Morally Gray Wizard"
            ],
            "conflict_scales": [
                "Personal Survival",
                "Moral Choice",
                "Power Corruption",
                "Existential Horror",
                "Societal Decay"
            ],
            "tones": [
                "Grim",
                "Morally Ambiguous",
                "Horror-tinged",
                "Psychological",
                "Brutal"
            ]
        },
        "Urban Fantasy": {
            "implied_settings": {
                "hidden_magic": True,
                "modern_world": True,
                "supernatural_society": True,
                "masquerade": True
            },
            "protagonist_types": [
                "Magical Detective",
                "Hidden World Guardian",
                "Modern Witch/Wizard",
                "Supernatural Creature",
                "Normal Person Discovered",
                "Magic Shop Owner"
            ],
            "conflict_scales": [
                "Personal",
                "City-wide",
                "Hidden Society",
                "Supernatural Politics",
                "World-threatening"
            ],
            "tones": [
                "Modern",
                "Mysterious",
                "Action-packed",
                "Detective Noir",
                "Secret World"
            ]
        },
        "Sword and Sorcery": {
            "implied_settings": {
                "low_magic": True,
                "dangerous_world": True,
                "ancient_ruins": True,
                "barbaric_lands": True
            },
            "protagonist_types": [
                "Warrior",
                "Rogue",
                "Barbarian",
                "Mercenary",
                "Wandering Wizard",
                "Treasure Hunter"
            ],
            "conflict_scales": [
                "Personal Gain",
                "Adventure",
                "Survival",
                "Quest",
                "Local Threat"
            ],
            "tones": [
                "Adventurous",
                "Gritty",
                "Action-focused",
                "Pulp",
                "Personal"
            ]
        },
        "Mythic Fantasy": {
            "implied_settings": {
                "ancient_gods": True,
                "legendary_creatures": True,
                "mythological_world": True,
                "divine_intervention": True
            },
            "protagonist_types": [
                "Demigod",
                "Legendary Hero",
                "Oracle",
                "Divine Champion",
                "Monster Slayer",
                "Mythical Creature"
            ],
            "conflict_scales": [
                "Divine Politics",
                "Legendary Quests",
                "Fate of Gods",
                "Mythic Prophecy",
                "World-shaping"
            ],
            "tones": [
                "Legendary",
                "Epic",
                "Mythological",
                "Divine",
                "Larger than Life"
            ]
        },
        "Fairy Tale": {
            "implied_settings": {
                "enchanted_world": True,
                "moral_lessons": True,
                "magical_rules": True,
                "transformation": True
            },
            "protagonist_types": [
                "Innocent Hero",
                "Clever Trickster",
                "Transformed Being",
                "Royal Figure",
                "Magical Helper",
                "Common Person"
            ],
            "conflict_scales": [
                "Personal Journey",
                "Moral Test",
                "Magical Challenge",
                "Kingdom Fate",
                "Breaking Curses"
            ],
            "tones": [
                "Whimsical",
                "Moral",
                "Magical",
                "Traditional",
                "Transformative"
            ]
        }
    }

    @classmethod
    def validate_genre_parameters(cls, genre, params):
        """Validate parameters for specific genre"""
        genre_config = cls.CONFIGS.get(genre)
        if not genre_config:
            return False
        # Add validation logic
        return True

    @classmethod
    def get_compatible_settings(cls, genre):
        """Get settings that work well with this genre"""
        return cls.CONFIGS[genre].get("implied_settings", {})

    @classmethod
    def suggest_combinations(cls, genre):
        """Suggest good parameter combinations for this genre"""
        # Add recommendation logic
        pass 