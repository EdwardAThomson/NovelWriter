"""
Shared helpers for the genre name generators.

Every genre used to roll names, genders and titles independently, which led to
three recurring problems:

  * the same first name turning up two or three times in a single cast,
  * gendered titles landing on the wrong character ("Queen ..." on a male
    faction leader), because the title was drawn before the gender was known,
  * genders recorded inconsistently ("female" in horror, "Female" everywhere
    else), which broke downstream comparisons.

The helpers here give all the generators one way of doing each of those things.
"""

import random

# --- Gender normalisation ---------------------------------------------------

def normalize_gender(gender):
    """
    Return a gender in the canonical "Female"/"Male" casing.

    Unrecognised values are passed through untouched so that genres which grow
    additional gender options later are not silently rewritten.
    """
    if not isinstance(gender, str):
        return gender

    lowered = gender.strip().lower()
    if lowered == "female":
        return "Female"
    if lowered == "male":
        return "Male"
    return gender


def pick_gender(female_percentage=50, male_percentage=50, context=""):
    """
    Choose "Female" or "Male" using the supplied bias percentages.

    Invalid percentages (out of range, or not summing to 100) fall back to an
    even split, matching the behaviour the generators had individually.
    """
    female_weight = 0.5
    male_weight = 0.5

    if (0 <= female_percentage <= 100 and
            0 <= male_percentage <= 100 and
            (female_percentage + male_percentage) == 100):
        female_weight = female_percentage / 100.0
        male_weight = male_percentage / 100.0
    elif context:
        print(f"{context}: Invalid gender percentages "
              f"(F:{female_percentage}%, M:{male_percentage}%). Defaulting to 50/50.")

    return random.choices(["Female", "Male"], weights=[female_weight, male_weight], k=1)[0]


# --- Gendered titles --------------------------------------------------------

# Masculine/feminine pairs drawn from the title lists used by the generators and
# by the faction profile JSON files. Titles that are not in this table (Marshal,
# Sheriff, Steward, Regent, Warden, Chancellor, ...) are treated as neutral and
# are left alone.
_TITLE_PAIRS = [
    # Nobility
    ("King", "Queen"),
    ("Emperor", "Empress"),
    ("Duke", "Duchess"),
    ("Prince", "Princess"),
    ("Marquess", "Marchioness"),
    ("Earl", "Countess"),
    ("Count", "Countess"),
    ("Viscount", "Viscountess"),
    ("Baron", "Baroness"),
    ("Baronet", "Baronetess"),
    ("Lord", "Lady"),
    ("High Lord", "High Lady"),
    ("City Lord", "City Lady"),
    ("Lord Mayor", "Lady Mayor"),
    ("Overlord", "Overlady"),
    ("Lord Commander", "Lady Commander"),
    ("Sir", "Dame"),
    ("Knight", "Dame"),
    # Magical
    ("Sorcerer", "Sorceress"),
    ("Grand Sorcerer", "Grand Sorceress"),
    ("High Sorcerer", "High Sorceress"),
    ("Enchanter", "Enchantress"),
    ("Master Enchanter", "Master Enchantress"),
    ("Grand Wizard", "Grand Sorceress"),
    ("Hedge Wizard", "Hedge Witch"),
    ("Warlock", "Witch"),
    # Religious
    ("Priest", "Priestess"),
    ("High Priest", "High Priestess"),
    ("Abbot", "Abbess"),
    ("Patriarch", "Matriarch"),
    ("Brother", "Sister"),
    ("Father", "Mother"),
]

_MASCULINE_TO_FEMININE = {}
_FEMININE_TO_MASCULINE = {}
for _masculine, _feminine in _TITLE_PAIRS:
    # The first pairing wins, so "Countess" maps back to "Count" rather than
    # "Earl", and "Dame" back to "Sir" rather than "Knight".
    _MASCULINE_TO_FEMININE.setdefault(_masculine.lower(), _feminine)
    _FEMININE_TO_MASCULINE.setdefault(_feminine.lower(), _masculine)


def title_for_gender(title, gender):
    """
    Return `title` adjusted to match `gender`.

    "Queen" for a male character becomes "King"; "Baron" for a female character
    becomes "Baroness". Neutral titles and unknown genders are returned
    unchanged, so a title list can freely mix gendered and neutral entries.
    """
    if not title or not isinstance(title, str):
        return title

    gender = normalize_gender(gender)
    key = title.strip().lower()

    if gender == "Female" and key in _MASCULINE_TO_FEMININE:
        return _MASCULINE_TO_FEMININE[key]
    if gender == "Male" and key in _FEMININE_TO_MASCULINE:
        return _FEMININE_TO_MASCULINE[key]
    return title


def pick_title_for_gender(title_list, gender):
    """Pick a random title from `title_list` and adjust it to match `gender`."""
    if not title_list:
        return None
    return title_for_gender(random.choice(title_list), gender)


# --- Unique name allocation -------------------------------------------------

class NameRegistry:
    """
    Tracks the names handed out during one generation pass so a cast does not
    end up with two characters sharing a name.

    `unique_name` retries the supplied builder, relaxing its requirements in
    stages so that a small name pool degrades gracefully instead of looping
    forever:

      1. both the first name and the full name are unseen (preferred),
      2. the full name is unseen, even if the first name repeats,
      3. whatever the builder last produced.
    """

    def __init__(self):
        self._first_names = set()
        self._full_names = set()

    def clear(self):
        """Forget every name seen so far, ready for a new generation pass."""
        self._first_names.clear()
        self._full_names.clear()

    @staticmethod
    def _first_of(full_name):
        parts = str(full_name).split()
        return parts[0].lower() if parts else ""

    def reserve(self, full_name):
        """Record `full_name` as used and return it."""
        self._full_names.add(str(full_name).lower())
        first = self._first_of(full_name)
        if first:
            self._first_names.add(first)
        return full_name

    def is_free(self, full_name, check_first_name=True):
        """Report whether `full_name` is still available."""
        if str(full_name).lower() in self._full_names:
            return False
        if check_first_name and self._first_of(full_name) in self._first_names:
            return False
        return True

    def unique_name(self, build, attempts=40):
        """
        Call `build()` until it returns an unused name, then reserve it.

        `build` must return either a name string or a (name, extra) tuple; the
        tuple form is passed straight back so callers can keep any additional
        data the builder produced alongside the name.
        """
        candidate = None
        for check_first_name in (True, False):
            for _ in range(attempts):
                candidate = build()
                name = candidate[0] if isinstance(candidate, tuple) else candidate
                if self.is_free(name, check_first_name=check_first_name):
                    self.reserve(name)
                    return candidate

        # Pool exhausted: keep the last candidate rather than failing outright.
        name = candidate[0] if isinstance(candidate, tuple) else candidate
        self.reserve(name)
        return candidate


_DEFAULT_REGISTRY = NameRegistry()


def default_registry():
    """
    The registry shared by generators that cannot easily thread one through
    their call chain (faction staff, governors, and similar).
    """
    return _DEFAULT_REGISTRY


# --- Character records ------------------------------------------------------

class DictAccessMixin:
    """
    Lets a character class be read with `char["name"]` as well as `char.name`.

    The genres are split between class-based and dict-based characters, so
    consumers were split between the two spellings - and using the wrong one
    returned a default instead of failing. Mixing this into the class-based
    characters means either spelling works everywhere.
    """

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            raise KeyError(key) from None

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()


class CharacterRecord:
    """
    A character that can be read either as an object or as a dictionary.

    Some genres build characters as plain dicts and others as classes, so
    consumers were split between `char["name"]` and `char.name` - and code using
    the wrong one silently got `None`/`'N/A'` instead of failing. This wrapper
    supports both spellings, plus `to_dict()` for the save functions.
    """

    def __init__(self, data=None, **kwargs):
        object.__setattr__(self, "_data", dict(data or {}))
        self._data.update(kwargs)

    # Attribute access
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, "_data")[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!r} has no attribute {name!r}") from None

    def __setattr__(self, name, value):
        self._data[name] = value

    def __delattr__(self, name):
        try:
            del self._data[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!r} has no attribute {name!r}") from None

    # Mapping access
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def setdefault(self, key, default=None):
        return self._data.setdefault(key, default)

    def update(self, *args, **kwargs):
        self._data.update(*args, **kwargs)

    def to_dict(self):
        return dict(self._data)

    def __repr__(self):
        return f"{type(self).__name__}({self._data!r})"


def as_dict(character):
    """Return `character` as a plain dictionary, whatever shape it arrived in."""
    if hasattr(character, "to_dict"):
        return character.to_dict()
    if isinstance(character, dict):
        return dict(character)
    return dict(getattr(character, "__dict__", {}))
