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
    male and female pool of the same genre,
  * main characters reusing the name of a faction leader generated in an
    earlier pass, because the generators read a factions.json path that no
    longer existed and never saw the roster,
  * characters carrying only a bare `name`, with no separate first name,
    surname or title, and three genres carrying no title at all.
"""

import contextlib
import io
import json
import re

import pytest

from Generators.GenreHandlers import get_genre_handler
from Generators.name_utils import (
    CharacterRecord,
    NameRegistry,
    as_dict,
    display_name_for,
    iter_person_records,
    normalize_gender,
    pick_title_for_gender,
    reserve_person_names,
    resolve_faction_file,
    split_name,
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


# --- Name parts: title, first name, surname ---------------------------------

NAME_FIELDS = ("name", "first_name", "last_name", "title", "display_name")


@pytest.mark.parametrize("genre", GENRES)
def test_characters_carry_every_name_field(genre):
    """Every genre records the same five name fields."""
    for character in generate_cast(genre, num_characters=5):
        data = as_dict(character)
        missing = [field for field in NAME_FIELDS if field not in data]
        assert not missing, f"{genre}: missing {missing}"


@pytest.mark.parametrize("genre", GENRES)
def test_name_parts_reconstruct_the_name(genre):
    """first_name and last_name must add back up to name."""
    for character in generate_cast(genre, num_characters=5):
        data = as_dict(character)
        rebuilt = f"{data['first_name']} {data['last_name']}".strip()
        assert rebuilt == data["name"], f"{genre}: {rebuilt!r} != {data['name']!r}"
        assert data["first_name"], f"{genre}: empty first name"
        assert data["last_name"], f"{genre}: empty surname"


@pytest.mark.parametrize("genre", GENRES)
def test_display_name_shows_the_title(genre):
    """display_name is the title and name together, or just the name."""
    for character in generate_cast(genre, num_characters=5):
        data = as_dict(character)
        if data["title"]:
            assert data["display_name"] == f"{data['title']} {data['name']}"
        else:
            assert data["display_name"] == data["name"]


def test_split_name_keeps_compound_surnames():
    assert split_name("Ada Vance") == ("Ada", "Vance")
    assert split_name("Persephone Van Helsing") == ("Persephone", "Van Helsing")
    assert split_name("Cher") == ("Cher", "")
    assert split_name("") == ("", "")


def test_display_name_for():
    assert display_name_for("Ada Vance", "Sheriff") == "Sheriff Ada Vance"
    assert display_name_for("Ada Vance", None) == "Ada Vance"
    assert display_name_for("Ada Vance", "") == "Ada Vance"


@pytest.mark.parametrize("module_name, profession, expected", [
    ("Generators.WesternCharacterGenerator", "Sheriff", "Sheriff"),
    ("Generators.WesternCharacterGenerator", "Doctor", "Doc"),
    ("Generators.WesternCharacterGenerator", "Cowboy", ""),
    ("Generators.WesternCharacterGenerator", "Gambler", ""),
    ("Generators.ThrillerCharacterGenerator", "FBI Agent", "Agent"),
    ("Generators.ThrillerCharacterGenerator", "Agency Director", "Director"),
    ("Generators.ThrillerCharacterGenerator", "Smuggler", ""),
    ("Generators.RomanceCharacterGenerator", "Doctor", "Dr."),
    ("Generators.RomanceCharacterGenerator", "Florist", ""),
])
def test_title_follows_from_profession(module_name, profession, expected):
    """A character is addressed by their job, or not at all."""
    module = __import__(module_name, fromlist=["title_for_profession"])
    assert module.title_for_profession(profession, "Female") == expected


def test_western_honorific_follows_gender():
    from Generators.WesternCharacterGenerator import title_for_profession

    assert title_for_profession("Teacher", "Female") == "Miss"
    assert title_for_profession("Banker", "Male") == "Mr."


@pytest.mark.parametrize("genre", ["Western", "Thriller", "Romance"])
def test_profession_driven_titles_are_consistent(genre):
    """A character's title must be the one their profession implies."""
    module_name = {
        "Western": "Generators.WesternCharacterGenerator",
        "Thriller": "Generators.ThrillerCharacterGenerator",
        "Romance": "Generators.RomanceCharacterGenerator",
    }[genre]
    module = __import__(module_name, fromlist=["title_for_profession"])

    for _ in range(10):
        for character in generate_cast(genre):
            data = as_dict(character)
            expected = module.title_for_profession(data["profession"], data["gender"])
            assert data["title"] == expected, (
                f"{genre}: {data['profession']} titled {data['title']!r}")


def test_mystery_title_matches_the_profession():
    """An FBI agent gets a law-enforcement rank, not a private-security one."""
    from Generators.MysteryCharacterGenerator import (
        MYSTERY_PROFESSION_TITLE_TYPES,
        MysteryCharacter,
    )

    families = {
        "law_enforcement": MysteryCharacter.LAW_ENFORCEMENT_TITLES,
        "legal": MysteryCharacter.LEGAL_TITLES,
        "civilian": MysteryCharacter.CIVILIAN_TITLES,
        "private": MysteryCharacter.PRIVATE_TITLES,
    }

    def titles_in(family):
        found = set()
        for rank in family.values():
            for titles in rank.values():
                found.update(titles)
        return found

    for _ in range(10):
        for character in generate_cast("Mystery"):
            data = as_dict(character)
            expected_family = MYSTERY_PROFESSION_TITLE_TYPES.get(data["profession"])
            if expected_family and data["title"]:
                assert data["title"] in titles_in(families[expected_family]), (
                    f"{data['profession']} titled {data['title']!r}, "
                    f"which is not a {expected_family} title")


# --- Names are unique across generation passes ------------------------------

FACTION_GENRES_WITH_PEOPLE = ["Fantasy", "Sci-Fi", "Horror"]


@pytest.mark.parametrize("genre", FACTION_GENRES_WITH_PEOPLE)
def test_cast_does_not_reuse_faction_names(genre, tmp_path):
    """A main character must not be given a faction leader's name."""
    lore = tmp_path / "story" / "lore"
    lore.mkdir(parents=True)
    handler = get_genre_handler(genre)

    with contextlib.redirect_stdout(io.StringIO()):
        factions = handler.generate_factions(num_factions=4, female_percentage=50,
                                             male_percentage=50)
        handler.save_factions(factions, filename=str(lore / "factions.json"))

    saved = json.loads((lore / "factions.json").read_text())
    faction_names = {p.get("full_name") or p.get("name")
                     for p in iter_person_records(saved)}
    assert faction_names, f"{genre}: no named faction people to collide with"

    with contextlib.redirect_stdout(io.StringIO()):
        cast = handler.generate_characters(num_characters=10, female_percentage=50,
                                           male_percentage=50,
                                           output_dir=str(tmp_path))

    cast_names = {as_dict(c)["name"] for c in cast}
    assert not (faction_names & cast_names)


def test_resolve_faction_file_finds_the_project_layout(tmp_path):
    """factions.json lives under story/lore; the old flat path still works."""
    assert resolve_faction_file(str(tmp_path)) is None

    flat = tmp_path / "factions.json"
    flat.write_text("[]")
    assert resolve_faction_file(str(tmp_path)) == str(flat)

    lore = tmp_path / "story" / "lore"
    lore.mkdir(parents=True)
    structured = lore / "factions.json"
    structured.write_text("[]")
    # The structured location wins when both exist.
    assert resolve_faction_file(str(tmp_path)) == str(structured)


def test_iter_person_records_ignores_places():
    """Faction data mixes people with territories; only people are names."""
    data = {
        "faction_name": "The Iron Pact",
        "territory": {"name": "Stonereach"},
        "leader": {"full_name": "Ada Vance", "gender": "Female"},
        "staff": [{"full_name": "Bo Kay", "gender": "Male"},
                  {"name": "Cy Rex", "gender": "Female"}],
    }

    found = {p.get("full_name") or p.get("name") for p in iter_person_records(data)}

    assert found == {"Ada Vance", "Bo Kay", "Cy Rex"}


def test_reserve_person_names_blocks_reuse():
    registry = NameRegistry()
    data = {"leader": {"full_name": "Ada Vance", "gender": "Female"}}

    assert reserve_person_names(registry, data) == 1
    assert not registry.is_free("Ada Vance")
    # The first name is taken too, so a different surname is still a clash.
    assert not registry.is_free("Ada Kay")
    assert registry.is_free("Bo Kay")


@pytest.mark.parametrize("genre", GENRES)
def test_saved_characters_keep_every_name_field(genre, tmp_path):
    """The save functions build explicit field lists - they must not drop these."""
    handler = get_genre_handler(genre)
    target = tmp_path / "characters.json"

    with contextlib.redirect_stdout(io.StringIO()):
        cast = handler.generate_characters(num_characters=5, female_percentage=50,
                                           male_percentage=50)
        handler.save_characters(cast, filename=str(target))

    saved = json.loads(target.read_text())
    characters = saved["characters"] if isinstance(saved, dict) else saved
    assert characters

    for entry in characters:
        missing = [field for field in NAME_FIELDS if field not in entry]
        assert not missing, f"{genre}: save dropped {missing}"
        rebuilt = f"{entry['first_name']} {entry['last_name']}".strip()
        assert rebuilt == entry["name"]
        if entry["title"]:
            assert entry["display_name"] == f"{entry['title']} {entry['name']}"


# --- One name per character, style carried by the prompt --------------------

def build_project(tmp_path, genre, num_characters=6):
    """Generate and save a cast into a project directory, returning its path."""
    lore = tmp_path / "story" / "lore"
    lore.mkdir(parents=True, exist_ok=True)
    handler = get_genre_handler(genre)
    with contextlib.redirect_stdout(io.StringIO()):
        cast = handler.generate_characters(num_characters=num_characters,
                                           female_percentage=50, male_percentage=50,
                                           output_dir=str(tmp_path))
        handler.save_characters(cast, filename=str(lore / "characters.json"))
    return cast


@pytest.mark.parametrize("genre", GENRES)
def test_saved_output_names_each_character_once(genre, tmp_path):
    """
    A character must not appear under two names in one file.

    `name` is the single identity; `title` is a separate field and
    `display_name` is derived from the two, never a second identity.
    """
    build_project(tmp_path, genre)
    saved = json.loads((tmp_path / "story" / "lore" / "characters.json").read_text())
    characters = saved["characters"] if isinstance(saved, dict) else saved

    names = {c["name"] for c in characters}
    for entry in characters:
        assert entry["display_name"] in (entry["name"],
                                         f"{entry['title']} {entry['name']}")

    # Relationships must reference characters by that same canonical name.
    for relationship in (saved.get("relationships") or []):
        assert relationship["character1"] in names
        assert relationship["character2"] in names


@pytest.mark.parametrize("genre", GENRES)
def test_prompt_roster_lists_one_name_and_a_separate_title(genre, tmp_path):
    """The writing prompt sees each character once, with the title broken out."""
    from core.generation.helper_fns import summarize_character_roster

    cast = build_project(tmp_path, genre)
    summary, path = summarize_character_roster(str(tmp_path), genre=genre)

    assert path is not None
    assert summary.count(" Name: ") == len(cast)
    for character in cast:
        data = as_dict(character)
        assert f" Name: {data['name']}" in summary
        if data["title"]:
            assert f" - Title: {data['title']}" in summary
        # The titled form is never presented as a second name.
        if data["title"]:
            assert f" Name: {data['display_name']}" not in summary


def test_prompt_roster_carries_the_genre_address_style(tmp_path):
    from Generators.name_utils import address_style_for
    from core.generation.helper_fns import summarize_character_roster

    build_project(tmp_path, "Western")
    summary, _ = summarize_character_roster(str(tmp_path), genre="Western")

    assert "## Naming and Forms of Address:" in summary
    assert address_style_for("Western") in summary


def test_summarize_character_roster_handles_both_layouts(tmp_path):
    from core.generation.helper_fns import summarize_character_roster

    summary, path = summarize_character_roster(str(tmp_path), genre="Western")
    assert path is None
    assert summary == "Character roster not available."

    # The older flat layout still works.
    (tmp_path / "characters.json").write_text(json.dumps(
        {"characters": [{"name": "Gus True", "title": "Deputy", "role": "protagonist"}]}))
    summary, path = summarize_character_roster(str(tmp_path), genre="Western")
    assert path == str(tmp_path / "characters.json")
    assert " Name: Gus True" in summary
    assert " - Title: Deputy" in summary


def test_address_style_for_covers_every_genre():
    from Generators.name_utils import address_style_for

    styles = {genre: address_style_for(genre) for genre in GENRES}
    assert all(styles.values())
    # Each genre gets its own guidance rather than the generic fallback.
    assert len(set(styles.values())) == len(GENRES)
    # An unknown genre still gets usable guidance.
    assert address_style_for("Steampunk Noir")


def test_western_honorific_is_abbreviated():
    from Generators.WesternCharacterGenerator import title_for_profession

    assert title_for_profession("Banker", "Male") == "Mr."
    assert title_for_profession("Banker", "Female") == "Miss"
