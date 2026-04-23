import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_json(filename):
    """Load a JSON file from the data directory."""
    filepath = DATA_DIR / filename
    with open(filepath, "r") as f:
        return json.load(f)


def get_ancestries():
    """Get all ancestries with their details."""
    data = load_json("ancestry.json")
    return data.get("ancestries", [])


def get_ancestry_names():
    """Get a list of ancestry names."""
    return [a["name"] for a in get_ancestries()]


def get_ancestry_by_name(name):
    """Get ancestry details by name."""
    for ancestry in get_ancestries():
        if ancestry["name"] == name:
            return ancestry
    return None


def get_backgrounds():
    """Get all backgrounds with their details."""
    data = load_json("background.json")
    return data.get("backgrounds", [])


def get_background_names():
    """Get a list of background names."""
    return [b["name"] for b in get_backgrounds()]


def get_background_by_name(name):
    """Get background details by name."""
    for bg in get_backgrounds():
        if bg["name"] == name:
            return bg
    return None


def get_classes():
    """Get all classes with their details."""
    data = load_json("classes.json")
    return data.get("classes", [])


def get_class_names():
    """Get a list of class names."""
    return [c["name"] for c in get_classes()]


def get_class_by_name(name):
    """Get class details by name."""
    for cls in get_classes():
        if cls["name"] == name:
            return cls
    return None


def get_gear():
    """Get all gear with their details."""
    data = load_json("gear.json")
    return data.get("gear_list", {})


def get_gear_categories():
    """Get gear categories."""
    return list(get_gear().keys())


def get_gear_by_category(category):
    """Get gear items in a specific category."""
    gear = get_gear()
    return gear.get(category, [])


def get_all_gear_items():
    """Get a flat list of all gear items."""
    gear = get_gear()
    items = []
    for category_items in gear.values():
        items.extend([item["item"] for item in category_items])
    return sorted(items)


def get_languages():
    """Get all languages with their rarity."""
    data = load_json("languages.json")
    return data.get("languages", {})


def get_all_language_names():
    """Get all language names."""
    langs = get_languages()
    all_langs = []
    for category_langs in langs.values():
        all_langs.extend(category_langs)
    return sorted(all_langs)


def get_spells():
    """Get all spells with their details."""
    data = load_json("spells.json")
    return data.get("spells", [])


def get_spell_names():
    """Get a list of spell names."""
    return [s["name"] for s in get_spells()]


def get_spells_by_class(class_name):
    """Get spells available for a specific class."""
    return [s for s in get_spells() if class_name in s.get("classes", [])]


def get_spell_classes():
    """Get a list of unique class names that have spells."""
    classes = set()
    for spell in get_spells():
        classes.update(spell.get("classes", []))
    return sorted(classes)


def get_spell_by_name(name):
    """Get spell details by name."""
    for spell in get_spells():
        if spell["name"] == name:
            return spell
    return None
