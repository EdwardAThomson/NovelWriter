"""Regression tests for the genre name generators.

These cover the defects found in the September 2026 audit of the generators:

  * casts containing two characters with the same first name (no uniqueness
    was enforced anywhere - a ten-character cast collided 32-64% of the time),
  * gendered titles drawn independently of the character's gender, so that
    roughly half of all titled faction characters were "Overlord ... Female",
  * ranks ("Agent", "Sheriff", "Commander") sitting in the first-name pools,
  * horror recording gender as "female" while every other genre used "Female",
    which made the gender tallies in core/gui/lore.py silently miscount,
  * three genres returning plain dicts while the rest returned objects, so
    consumers using attribute access logged every name as 'N/A',
  * duplicate entries inside the name pools, and names present in both the
    male and female pool of the same genre.
"""

import contextlib
import io
import re

import pytest

from Generators.GenreHandlers import get_genre_handler
from Generators.name_utils import (
    CharacterRecord,
    NameRegistry,
    normalize_gender,
    pick_title_for_gender,
    title_for_gender,
)

GENRES = [
    "Sci-Fi",
    "Fantasy",
    "Horror",
    "Mystery",
    "Romance",
    "Thriller",
    "Western",
    "Historical Fiction",
]

# Ranks and honorifics that are titles, not given names.
RANKS = {
    "Agent", "Detective", "Captain", "Major", "Colonel", "Commander",
    "Director", "Chief", "Sheriff", "Marshal", "Deputy", "Judge", "Doc",
    "Preacher",
}

FEMININE_TITLES = {
    "Queen", "Empress", "Duchess", "Princess", "Marchioness", "Countess",
    "Viscountess", "Baroness", "Baronetess", "Lady", "High Lady", "City Lady",
    "Lady Mayor", "Overlady", "Lady Commander", "Dame",
}
MASCULINE_TITLES = {
    "King", "Emperor", "Duke", "Prince", "Marquess", "Earl", "Count",
    "Viscount", "Baron", "Baronet", "Lord", "High Lord", "City Lord",
    "Lord Mayor", "Overlord", "Lord Commander", "Sir", "Knight",
}


def generate_cast(genre, num_characters=10, **kwargs):
    """Generate a cast, muting the generators' progress prints."""
    handler = get_genre_handler(genre)
    with contextlib.redirect_stdout(io.StringIO()):
        return handler.generate_characters(
            num_characters=num_characters,
            female_percentage=50,
            male_percentage=50,
            **kwargs,
        )


def character_name(character):
    """Read a name however the genre chose to represent its characters."""
    if isinstance(character, dict):
        return character["name"]
    return character.name


# --- Unique names within a cast ---------------------------------------------

@pytest.mark.parametrize("genre", GENRES)
def test_cast_has_no_repeated_names(genre):
    """A cast must not contain two characters sharing a first or full name."""
    for _ in range(20):
        names = [character_name(c) for c in generate_cast(genre)]
        first_names = [n.split()[0] for n in names]

        assert len(set(names)) == len(names), f"{genre}: duplicate full name in {names}"
        assert len(set(first_names)) == len(first_names), (
            f"{genre}: duplicate first name in {names}")


def test_registry_degrades_instead_of_hanging():
    """An exhausted name pool must return a name rather than loop forever."""
    registry = NameRegistry()
    pool = ["Ann Lee", "Bo Kay", "Cy Rex"]

    names = [registry.unique_name(lambda: pool[0]) for _ in range(5)]

    assert all(n == "Ann Lee" for n in names)
    assert registry.unique_name(lambda: "Ann Lee") == "Ann Lee"


def test_registry_prefers_unique_first_names_then_relaxes():
    registry = NameRegistry()
    candidates = iter(["Ann Lee", "Ann Kay", "Bo Rex"])

    assert registry.unique_name(lambda: next(candidates)) == "Ann Lee"
    # "Ann Kay" repeats the first name, so the registry keeps looking and
    # settles on "Bo Rex".
    assert registry.unique_name(lambda: next(candidates, "Bo Rex")) == "Bo Rex"


# --- Gender recorded consistently -------------------------------------------

@pytest.mark.parametrize("genre", GENRES)
def test_gender_uses_canonical_casing(genre):
    """core/gui/lore.py compares against "Female"/"Male" exactly."""
    for character in generate_cast(genre):
        gender = character["gender"] if isinstance(character, dict) else character.gender
        assert gender in ("Female", "Male"), f"{genre}: unexpected gender {gender!r}"


@pytest.mark.parametrize("genre", GENRES)
def test_gender_tally_sees_every_character(genre):
    """The lore.py tally uses hasattr/attribute access; it must reach them all."""
    cast = generate_cast(genre)

    counted = sum(1 for c in cast
                  if hasattr(c, "gender") and c.gender in ("Female", "Male"))

    assert counted == len(cast), f"{genre}: tallied {counted} of {len(cast)}"


@pytest.mark.parametrize("genre", GENRES)
def test_characters_support_attribute_and_item_access(genre):
    """Consumers are split between char.name and char["name"]; both must work."""
    for character in generate_cast(genre, num_characters=3):
        assert character.name
        assert character["name"] == character.name


def test_normalize_gender():
    assert normalize_gender("female") == "Female"
    assert normalize_gender("MALE") == "Male"
    assert normalize_gender("Female") == "Female"
    # Unknown values pass through rather than being rewritten.
    assert normalize_gender("Non-binary") == "Non-binary"
    assert normalize_gender(None) is None


# --- Titles agree with gender -----------------------------------------------

def test_title_for_gender_swaps_gendered_titles():
    assert title_for_gender("Queen", "Male") == "King"
    assert title_for_gender("Baron", "Female") == "Baroness"
    assert title_for_gender("High Lord", "Female") == "High Lady"
    # Already correct, and neutral titles, are left alone.
    assert title_for_gender("Queen", "Female") == "Queen"
    assert title_for_gender("Sheriff", "Female") == "Sheriff"
    assert title_for_gender("Marshal", "Male") == "Marshal"


@pytest.mark.parametrize("gender", ["Female", "Male"])
def test_pick_title_for_gender_never_contradicts_gender(gender):
    titles = ["King", "Queen", "Baron", "Baroness", "Lord", "Lady", "Steward"]
    wrong = MASCULINE_TITLES if gender == "Female" else FEMININE_TITLES

    for _ in range(100):
        assert pick_title_for_gender(titles, gender) not in wrong


@pytest.mark.parametrize("module_name, title_attr", [
    ("Generators.FantasyGenerator", "LEADER_TITLES"),
    ("Generators.FantasyGenerator", "GOVERNOR_TITLES"),
    ("Generators.SciFiGenerator", "LEADER_TITLES"),
])
def test_faction_characters_titles_match_their_gender(module_name, title_attr):
    """Faction leaders used to draw a title before their gender was known."""
    module = __import__(module_name, fromlist=["_generate_named_character"])
    titles = getattr(module, title_attr)

    for _ in range(200):
        with contextlib.redirect_stdout(io.StringIO()):
            character = module._generate_named_character(titles, "Faction Leader")

        title, gender = character["title"], character["gender"]
        if title in FEMININE_TITLES:
            assert gender == "Female", f"{title} assigned to {gender}"
        elif title in MASCULINE_TITLES:
            assert gender == "Male", f"{title} assigned to {gender}"


def test_faction_character_names_follow_the_gender_bias():
    """A 100% female faction roster must not be named from the neutral pool."""
    from Generators.FantasyGenerator import LEADER_TITLES, _generate_named_character
    from Generators.FantasyGenerator import generate_character_name

    female_pool = {generate_character_name("Female") for _ in range(400)}

    with contextlib.redirect_stdout(io.StringIO()):
        names = [_generate_named_character(
            LEADER_TITLES, "Faction Leader",
            female_percentage=100, male_percentage=0)["first_name"]
            for _ in range(30)]

    assert all(name in female_pool for name in names), (
        f"names drawn outside the female pool: "
        f"{[n for n in names if n not in female_pool]}")


# --- Name pool hygiene ------------------------------------------------------

@pytest.mark.parametrize("genre", ["Thriller", "Western"])
def test_ranks_are_not_used_as_first_names(genre):
    """"Agent Noble" and "Sheriff Creek" were characters, not job listings."""
    for _ in range(30):
        for character in generate_cast(genre):
            first_name = character_name(character).split()[0]
            assert first_name not in RANKS, f"{genre}: rank used as a name"


def _string_lists(path, name_pattern):
    """Yield (variable, items) for list literals whose name matches."""
    source = open(path, encoding="utf-8").read()
    pattern = re.compile(
        r"^\s*([A-Za-z_]*" + name_pattern + r"[A-Za-z_]*)\s*=\s*\[(.*?)\]",
        re.S | re.M)
    for match in pattern.finditer(source):
        items = re.findall(r'"([^"]+)"', match.group(2))
        if items:
            yield match.group(1), items


NAME_POOL_FILES = [
    "Generators/HistoricalCharacterGenerator.py",
    "Generators/HorrorGenerator.py",
    "Generators/MysteryCharacterGenerator.py",
    "Generators/RomanceCharacterGenerator.py",
    "Generators/SciFiGenerator.py",
    "Generators/ThrillerCharacterGenerator.py",
    "Generators/WesternCharacterGenerator.py",
]


@pytest.mark.parametrize("path", NAME_POOL_FILES)
def test_name_pools_have_no_duplicate_entries(path):
    """A repeated entry silently doubles that name's odds of being picked."""
    for variable, items in _string_lists(path, "(?:name|NAME|surname|SURNAME)"):
        duplicates = {item for item in items if items.count(item) > 1}
        assert not duplicates, f"{path}:{variable} repeats {sorted(duplicates)}"


@pytest.mark.parametrize("module_name, function_name", [
    ("Generators.ThrillerCharacterGenerator", "generate_thriller_names"),
    ("Generators.RomanceCharacterGenerator", "generate_romance_names"),
    ("Generators.WesternCharacterGenerator", "generate_western_names"),
])
def test_first_name_pools_do_not_overlap(module_name, function_name):
    """A name in both pools makes the recorded gender meaningless."""
    module = __import__(module_name, fromlist=[function_name])
    male, female, _ = getattr(module, function_name)()

    assert not set(male) & set(female)


@pytest.mark.parametrize("module_name, function_name", [
    ("Generators.ThrillerCharacterGenerator", "generate_thriller_names"),
    ("Generators.RomanceCharacterGenerator", "generate_romance_names"),
    ("Generators.WesternCharacterGenerator", "generate_western_names"),
])
def test_given_names_are_not_also_surnames(module_name, function_name):
    """Otherwise a character can end up called "Hunter Hunter"."""
    module = __import__(module_name, fromlist=[function_name])
    male, female, last = getattr(module, function_name)()

    assert not set(male) & set(last)
    assert not set(female) & set(last)


def test_scifi_first_name_pools_do_not_overlap():
    from Generators.SciFiGenerator import generate_character_name

    male = {generate_character_name("Male") for _ in range(2000)}
    female = {generate_character_name("Female") for _ in range(2000)}

    assert not male & female


# --- CharacterRecord --------------------------------------------------------

def test_character_record_supports_both_access_styles():
    record = CharacterRecord({"name": "Ada Vance", "role": "protagonist"})

    assert record.name == "Ada Vance"
    assert record["role"] == "protagonist"
    assert record.get("missing", "fallback") == "fallback"
    assert "name" in record
    assert record.to_dict() == {"name": "Ada Vance", "role": "protagonist"}

    record.age = 41
    record["gender"] = "Female"
    assert record["age"] == 41
    assert record.gender == "Female"

    assert not hasattr(record, "nickname")
    with pytest.raises(AttributeError):
        record.nickname
    with pytest.raises(KeyError):
        record["nickname"]
