import streamlit as st
import streamlit.components.v1 as components
import json
import random
import html
from pathlib import Path
from data_loader import (
    get_ancestries,
    get_ancestry_names,
    get_ancestry_by_name,
    get_backgrounds,
    get_background_names,
    get_background_by_name,
    get_classes,
    get_class_names,
    get_class_by_name,
    get_gear_categories,
    get_gear_by_category,
    get_all_gear_items,
    get_languages,
    get_spells_by_class,
    get_spell_by_name,
    get_all_language_names,
    get_spells,
    get_spell_classes,
)

def default_character():
    return {
        "name": "",
        "level": 1,
        "hp": 0,
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
        "ancestry": "-",
        "background": "-",
        "class": "-",
        "gear": [],
        "languages": [],
        "spells": [],
        "talents": [],
        "additional_features": "",
        "gold": 0,
        "silver": 0,
        "copper": 0,
        "custom_gear": "",
    }


def normalize_character_data(data):
    character = default_character()
    character.update(data or {})

    # Normalize selection fields for required dropdowns
    for key in ["ancestry", "background", "class"]:
        value = character.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            character[key] = "-"
        else:
            character[key] = str(value)

    # Ensure numeric fields are properly typed
    try:
        character["level"] = int(character.get("level", 1))
    except (TypeError, ValueError):
        character["level"] = 1

    for attr in ["hp", "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma", "gold", "silver", "copper"]:
        try:
            character[attr] = int(character.get(attr, default_character()[attr]))
        except (TypeError, ValueError):
            character[attr] = default_character()[attr]

    for list_attr in ["gear", "languages", "spells", "talents"]:
        value = character.get(list_attr, [])
        if isinstance(value, str):
            character[list_attr] = [item.strip() for item in value.split(",") if item.strip()]
        elif value is None:
            character[list_attr] = []
        else:
            character[list_attr] = list(value)

    # Ensure string fields are properly typed
    for str_attr in ["additional_features", "custom_gear"]:
        value = character.get(str_attr, "")
        if value is None:
            character[str_attr] = ""
        else:
            character[str_attr] = str(value)

    return character


def build_spell_option(spell_name, tier="?"):
    return f"{spell_name} (Tier {tier})"


st.set_page_config(
    page_title="Shadowdark TTRPG Character Builder",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ Shadowdark TTRPG Character Builder")

# Sidebar navigation
page = st.sidebar.radio(
    "Select a page:",
    ["Character Creator", "Wiki"],
)

if page == "Character Creator":
    st.header("✏️ Character Creator")
    
    # Initialize session state for character
    if "character" not in st.session_state:
        st.session_state.character = default_character()

    if "pending_import" in st.session_state:
        imported_data = st.session_state.pop("pending_import")
        st.session_state.character = imported_data
        st.session_state["name_input"] = imported_data["name"]
        st.session_state["level_select"] = imported_data["level"]
        st.session_state["hp_input"] = imported_data["hp"]
        st.session_state["strength_input"] = imported_data["strength"]
        st.session_state["dexterity_input"] = imported_data["dexterity"]
        st.session_state["constitution_input"] = imported_data["constitution"]
        st.session_state["intelligence_input"] = imported_data["intelligence"]
        st.session_state["wisdom_input"] = imported_data["wisdom"]
        st.session_state["charisma_input"] = imported_data["charisma"]
        st.session_state["ancestry_select"] = imported_data["ancestry"]
        st.session_state["background_select"] = imported_data["background"]
        st.session_state["class_select"] = imported_data["class"]
        st.session_state["languages_select"] = imported_data["languages"]
        st.session_state["talents_select"] = imported_data.get("talents", [])
        st.session_state["additional_features_input"] = imported_data.get("additional_features", "")
        st.session_state["gold_input"] = imported_data.get("gold", 0)
        st.session_state["silver_input"] = imported_data.get("silver", 0)
        st.session_state["copper_input"] = imported_data.get("copper", 0)
        st.session_state["custom_gear_input"] = imported_data.get("custom_gear", "")

        spell_options = []
        for spell in imported_data["spells"]:
            tier = next((s["tier"] for s in get_spells() if s["name"] == spell), "?")
            spell_options.append(build_spell_option(spell, tier))
        st.session_state["spells_select"] = sorted(spell_options)
        st.success("Character imported successfully!")
    
    # Character name
    st.session_state.character["name"] = st.text_input(
        "Character Name",
        value=st.session_state.character["name"],
        key="name_input",
    )
    
    # Level and HP
    col_level, col_hp = st.columns(2)
    with col_level:
        st.session_state.character["level"] = st.selectbox(
            "Level",
            list(range(1, 11)),
            index=st.session_state.character["level"] - 1,
            key="level_select",
        )
    with col_hp:
        st.session_state.character["hp"] = st.number_input(
            "Hit Points",
            min_value=0,
            value=st.session_state.character["hp"],
            key="hp_input",
        )
    
    # Ability Scores
    st.subheader("Ability Scores")
    attr_cols = st.columns(3)
    
    # Strength
    with attr_cols[0]:
        st.markdown("**Strength**")
        strength = st.number_input(
            "Score",
            min_value=1,
            max_value=25,
            value=st.session_state.character["strength"],
            key="strength_input",
        )
        st.session_state.character["strength"] = strength
        modifier = (strength - 10) // 2
        st.markdown(f"**Modifier:** {modifier:+d}")
    
    # Dexterity
    with attr_cols[1]:
        st.markdown("**Dexterity**")
        dexterity = st.number_input(
            "Score",
            min_value=1,
            max_value=25,
            value=st.session_state.character["dexterity"],
            key="dexterity_input",
        )
        st.session_state.character["dexterity"] = dexterity
        modifier = (dexterity - 10) // 2
        st.markdown(f"**Modifier:** {modifier:+d}")
    
    # Constitution
    with attr_cols[2]:
        st.markdown("**Constitution**")
        constitution = st.number_input(
            "Score",
            min_value=1,
            max_value=25,
            value=st.session_state.character["constitution"],
            key="constitution_input",
        )
        st.session_state.character["constitution"] = constitution
        modifier = (constitution - 10) // 2
        st.markdown(f"**Modifier:** {modifier:+d}")
    
    # Second row
    attr_cols2 = st.columns(3)
    
    # Intelligence
    with attr_cols2[0]:
        st.markdown("**Intelligence**")
        intelligence = st.number_input(
            "Score",
            min_value=1,
            max_value=25,
            value=st.session_state.character["intelligence"],
            key="intelligence_input",
        )
        st.session_state.character["intelligence"] = intelligence
        modifier = (intelligence - 10) // 2
        st.markdown(f"**Modifier:** {modifier:+d}")
    
    # Wisdom
    with attr_cols2[1]:
        st.markdown("**Wisdom**")
        wisdom = st.number_input(
            "Score",
            min_value=1,
            max_value=25,
            value=st.session_state.character["wisdom"],
            key="wisdom_input",
        )
        st.session_state.character["wisdom"] = wisdom
        modifier = (wisdom - 10) // 2
        st.markdown(f"**Modifier:** {modifier:+d}")
    
    # Charisma
    with attr_cols2[2]:
        st.markdown("**Charisma**")
        charisma = st.number_input(
            "Score",
            min_value=1,
            max_value=25,
            value=st.session_state.character["charisma"],
            key="charisma_input",
        )
        st.session_state.character["charisma"] = charisma
        modifier = (charisma - 10) // 2
        st.markdown(f"**Modifier:** {modifier:+d}")
    
    # Dice Roller Section
    st.subheader("🎲 Ability Score Dice Roller")
    
    # Single roll button
    col_roll, col_select, col_apply = st.columns([1, 2, 1])
    
    with col_roll:
        if st.button("🎲 Roll 3d6", key="roll_ability_dice"):
            st.session_state["last_roll_result"] = sum(random.randint(1, 6) for _ in range(3))

    with col_select:
        ability_options = ["-"] + ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        if "ability_select" not in st.session_state:
            st.session_state["ability_select"] = "-"
        selected_ability = st.selectbox(
            "Apply roll to:",
            ability_options,
            index=ability_options.index(st.session_state["ability_select"]),
            key="ability_select"
        )

    with col_apply:
        if st.button("Apply", key="apply_roll"):
            if "last_roll_result" not in st.session_state:
                st.warning("Roll first before applying the result.")
            elif selected_ability == "-":
                st.warning("Please choose a stat to apply the result to.")
            else:
                ability_map = {
                    "STR": "strength",
                    "DEX": "dexterity",
                    "CON": "constitution",
                    "INT": "intelligence",
                    "WIS": "wisdom",
                    "CHA": "charisma",
                }
                target = ability_map[selected_ability]
                st.session_state.character[target] = st.session_state["last_roll_result"]
                st.success(f"Applied {st.session_state['last_roll_result']} to {selected_ability}")
                st.session_state["last_roll_result"] = None

    # Display the last roll result if it exists
    last_roll = st.session_state.get("last_roll_result")
    if last_roll:
        st.markdown(f"**Last Roll Result:** {last_roll}")
    else:
        st.markdown("*No roll result yet*")
    
    col1, col2, col3 = st.columns(3)
    
    # Ancestry selection
    with col1:
        st.subheader("Ancestry")
        ancestry_names = ["-"] + sorted(get_ancestry_names())
        selected_ancestry = st.selectbox(
            "Choose your ancestry:",
            ancestry_names,
            index=ancestry_names.index(st.session_state.character["ancestry"])
            if st.session_state.character["ancestry"] in ancestry_names
            else 0,
            key="ancestry_select",
        )
        st.session_state.character["ancestry"] = selected_ancestry
        
        # Display ancestry details
        ancestry = get_ancestry_by_name(selected_ancestry)
        if ancestry:
            st.markdown(f"**Description:** {ancestry['description']}")
            st.markdown(f"**Trait:** {ancestry['trait']['name']}")
            st.markdown(f"*{ancestry['trait']['description']}*")
            st.markdown(f"**Languages:** {', '.join(ancestry['languages'])}")
    
    # Background selection
    with col2:
        st.subheader("Background")
        background_names = ["-"] + sorted(get_background_names())
        selected_background = st.selectbox(
            "Choose your background:",
            background_names,
            index=background_names.index(st.session_state.character["background"])
            if st.session_state.character["background"] in background_names
            else 0,
            key="background_select",
        )
        st.session_state.character["background"] = selected_background
        
        # Display background details
        background = get_background_by_name(selected_background)
        if background:
            st.markdown(f"**Description:** {background['description']}")
            if "roll" in background:
                st.markdown(f"*Roll: {background['roll']}*")
    
    # Class selection
    with col3:
        st.subheader("Class")
        class_names = ["-"] + sorted(get_class_names())
        previous_class = st.session_state.character["class"]
        selected_class = st.selectbox(
            "Choose your class:",
            class_names,
            index=class_names.index(st.session_state.character["class"])
            if st.session_state.character["class"] in class_names
            else 0,
            key="class_select",
        )
        if selected_class != previous_class:
            st.session_state.character["spells"] = []
            st.session_state.character["talents"] = []
        st.session_state.character["class"] = selected_class
        
        # Display class details
        character_class = get_class_by_name(selected_class)
        if character_class:
            st.markdown(f"**Description:** {character_class['description']}")
            st.markdown(f"**Hit Points:** {character_class['hit_points']}")
            st.markdown(f"**Armor:** {', '.join(character_class['armor'])}")
            st.markdown(f"**Weapons:** {', '.join(character_class['weapons'])}")
    
    # Gear selection
    st.subheader("Gear")
    col_gear1, col_gear2 = st.columns(2)
    
    with col_gear1:
        st.markdown("**Select gear by category:**")
        gear_categories = sorted(get_gear_categories())
        selected_category = st.selectbox(
            "Choose a gear category:",
            gear_categories,
            key="gear_category_select",
        )
    
    with col_gear2:
        st.markdown("**Available items:**")
        if selected_category:
            gear_items = get_gear_by_category(selected_category)
            # Sort alphabetically
            item_names = sorted([item["item"] for item in gear_items])
            selected_gear_item = st.selectbox(
                "Choose an item:",
                [""] + item_names,
                key="gear_item_select",
            )
            
            if selected_gear_item:
                # Find the item details
                item_detail = next(
                    (item for item in gear_items if item["item"] == selected_gear_item),
                    None,
                )
                if item_detail and selected_gear_item not in st.session_state.character["gear"]:
                    if st.button("Add to inventory", key="add_gear_btn"):
                        st.session_state.character["gear"].append(selected_gear_item)
                        st.success(f"Added {selected_gear_item} to inventory!")
    
    # Display current gear
    if st.session_state.character["gear"]:
        st.markdown("**Your Inventory:**")
        cols = st.columns(len(st.session_state.character["gear"]))
        for idx, item in enumerate(st.session_state.character["gear"]):
            with cols[idx]:
                if st.button(f"Remove\n{item}", key=f"remove_gear_{idx}"):
                    st.session_state.character["gear"].pop(idx)
                    st.rerun()
    
    # Languages selection
    st.subheader("Languages")
    all_languages = sorted(get_all_language_names())
    selected_languages = st.multiselect(
        "Choose your languages:",
        all_languages,
        default=st.session_state.character["languages"],
        key="languages_select",
    )
    st.session_state.character["languages"] = selected_languages
    
    # Spells selection (only if class has spells)
    if selected_class:
        class_spells = get_spells_by_class(selected_class)
        if class_spells:
            st.subheader(f"Spells ({selected_class})")
            # Create options with tier info
            spell_options = [f"{spell['name']} (Tier {spell['tier']})" for spell in class_spells]
            spell_options_sorted = sorted(spell_options)
            # Map back to just names for storage
            selected_spell_options = st.multiselect(
                "Choose your spells:",
                spell_options_sorted,
                default=[f"{spell} (Tier {next((s['tier'] for s in class_spells if s['name'] == spell), '?')})" 
                        for spell in st.session_state.character["spells"]],
                key="spells_select",
            )
            # Extract just the spell names
            st.session_state.character["spells"] = [option.split(' (Tier ')[0] for option in selected_spell_options]

        class_features = character_class.get("class_features", []) if character_class else []
        if class_features:
            st.subheader(f"Class Features ({selected_class})")
            for feature in class_features:
                st.markdown(f"**{feature.get('name', 'Unnamed feature')}**")
                st.markdown(feature.get("description", "No description available."))
                st.markdown("---")

        talents_table = character_class.get("talents_table", []) if character_class else []
        if talents_table:
            st.subheader("Class Talents")
            talent_options = [
                f"{talent['roll']}: {talent['effect']}"
                for talent in talents_table
            ]
            talent_options_sorted = sorted(talent_options)
            selected_talents = st.multiselect(
                "Choose your talents from the table:",
                talent_options_sorted,
                default=[talent for talent in st.session_state.character.get("talents", []) if talent in talent_options_sorted],
                key="talents_select",
            )
            st.session_state.character["talents"] = selected_talents
    
    # Additional Details
    st.subheader("Additional Details")
    
    # Currency
    st.markdown("**Currency:**")
    col_gold, col_silver, col_copper = st.columns(3)
    with col_gold:
        gold = st.number_input(
            "Gold Pieces",
            min_value=0,
            value=st.session_state.character["gold"],
            key="gold_input",
        )
        st.session_state.character["gold"] = gold
    with col_silver:
        silver = st.number_input(
            "Silver Pieces",
            min_value=0,
            value=st.session_state.character["silver"],
            key="silver_input",
        )
        st.session_state.character["silver"] = silver
    with col_copper:
        copper = st.number_input(
            "Copper Pieces",
            min_value=0,
            value=st.session_state.character["copper"],
            key="copper_input",
        )
        st.session_state.character["copper"] = copper
    
    # Additional Features
    additional_features = st.text_area(
        "Additional Features",
        value=st.session_state.character["additional_features"],
        key="additional_features_input",
    )
    st.session_state.character["additional_features"] = additional_features
    
    # Custom Gear
    custom_gear = st.text_area(
        "Custom Gear",
        value=st.session_state.character["custom_gear"],
        key="custom_gear_input",
    )
    st.session_state.character["custom_gear"] = custom_gear
    
    # Display character summary
    st.divider()
    st.subheader("⚔️ Character Summary")
    
    col_summary1, col_summary2 = st.columns(2)
    
    with col_summary1:
        st.markdown(f"**Name:** {st.session_state.character['name'] or 'Unnamed'}")
        st.markdown(f"**Level:** {st.session_state.character['level']}")
        st.markdown(f"**HP:** {st.session_state.character['hp']}")
        
        # Ability Scores
        st.markdown("**Ability Scores:**")
        str_mod = (st.session_state.character['strength'] - 10) // 2
        dex_mod = (st.session_state.character['dexterity'] - 10) // 2
        con_mod = (st.session_state.character['constitution'] - 10) // 2
        int_mod = (st.session_state.character['intelligence'] - 10) // 2
        wis_mod = (st.session_state.character['wisdom'] - 10) // 2
        cha_mod = (st.session_state.character['charisma'] - 10) // 2
        
        st.markdown(f"STR: {st.session_state.character['strength']} ({str_mod:+d}) | "
                   f"DEX: {st.session_state.character['dexterity']} ({dex_mod:+d}) | "
                   f"CON: {st.session_state.character['constitution']} ({con_mod:+d})")
        st.markdown(f"INT: {st.session_state.character['intelligence']} ({int_mod:+d}) | "
                   f"WIS: {st.session_state.character['wisdom']} ({wis_mod:+d}) | "
                   f"CHA: {st.session_state.character['charisma']} ({cha_mod:+d})")
        
        st.markdown(f"**Ancestry:** {st.session_state.character['ancestry']}")
        st.markdown(f"**Background:** {st.session_state.character['background']}")
        st.markdown(f"**Class:** {st.session_state.character['class']}")
    
    with col_summary2:
        if st.session_state.character["languages"]:
            st.markdown(
                f"**Languages:** {', '.join(st.session_state.character['languages'])}"
            )
        if st.session_state.character["gear"]:
            st.markdown(
                f"**Gear:** {', '.join(st.session_state.character['gear'][:5])}"
            )
            if len(st.session_state.character["gear"]) > 5:
                st.markdown(f"*...and {len(st.session_state.character['gear']) - 5} more items*")
        if st.session_state.character["gold"] or st.session_state.character["silver"] or st.session_state.character["copper"]:
            currency = []
            if st.session_state.character["gold"]:
                currency.append(f"{st.session_state.character['gold']} GP")
            if st.session_state.character["silver"]:
                currency.append(f"{st.session_state.character['silver']} SP")
            if st.session_state.character["copper"]:
                currency.append(f"{st.session_state.character['copper']} CP")
            st.markdown(f"**Currency:** {', '.join(currency)}")
        if st.session_state.character["additional_features"]:
            st.markdown(f"**Additional Features:** {st.session_state.character['additional_features'][:100]}{'...' if len(st.session_state.character['additional_features']) > 100 else ''}")
        if st.session_state.character["custom_gear"]:
            st.markdown(f"**Custom Gear:** {st.session_state.character['custom_gear'][:100]}{'...' if len(st.session_state.character['custom_gear']) > 100 else ''}")
        if st.session_state.character["spells"]:
            # Get spells with tiers
            all_spells = get_spells()
            spell_tier_map = {spell["name"]: spell["tier"] for spell in all_spells}
            spells_with_tiers = [f"{spell} (Tier {spell_tier_map.get(spell, '?')})" 
                                for spell in st.session_state.character["spells"][:3]]
            st.markdown(
                f"**Spells:** {', '.join(spells_with_tiers)}"
            )
            if len(st.session_state.character["spells"]) > 3:
                st.markdown(f"*...and {len(st.session_state.character['spells']) - 3} more spells*")
    # Class features, selected talents, and spells
    st.divider()
    st.subheader("🧠 Class Features, Talents & Spells")

    ancestry_info = get_ancestry_by_name(st.session_state.character.get("ancestry", ""))
    if ancestry_info and ancestry_info.get("trait"):
        with st.expander("Ancestry Trait"):
            st.markdown(f"**{ancestry_info['trait'].get('name', 'Trait')}**")
            st.markdown(ancestry_info['trait'].get("description", "No description available."))
            st.markdown("---")

    if character_class:
        class_features = character_class.get("class_features", [])
        if class_features:
            with st.expander("Class Features"):
                for feature in class_features:
                    st.markdown(f"**{feature.get('name', 'Unnamed feature')}**")
                    st.markdown(feature.get("description", "No description available."))
                    st.markdown("---")
        else:
            st.markdown("*No class features available.*")

    selected_talents = st.session_state.character.get("talents", [])
    if selected_talents:
        with st.expander("Selected Talents"):
            for talent in selected_talents:
                st.markdown(f"- {talent}")
    else:
        st.markdown("*No talents chosen.*")

    if st.session_state.character.get("spells"):
        for spell_name in st.session_state.character["spells"]:
            spell = get_spell_by_name(spell_name)
            with st.expander(spell_name):
                if spell:
                    st.markdown(f"**Tier:** {spell.get('tier', '?')}")
                    st.markdown(spell.get("description", "No description available."))
                else:
                    st.markdown("Spell details unavailable.")
    # Dice Roller
    st.divider()
    st.subheader("🎲 Dice Roller")
    dice_col1, dice_col2, dice_col3, dice_col4 = st.columns([2, 1, 1, 1])
    
    with dice_col1:
        dice_type = st.selectbox(
            "Select dice type:",
            ["d4", "d6", "d8", "d10", "d12", "d20"],
            key="dice_type",
        )
        dice_count = st.number_input(
            "Number of dice:",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
            key="dice_count",
        )
    
    with dice_col2:
        if st.button("Roll Dice", key="roll_dice"):
            dice_value = int(dice_type[1:])  # Extract number from "d4" etc.
            rolls = [random.randint(1, dice_value) for _ in range(dice_count)]
            total = sum(rolls)
            st.success(f"Rolled {dice_count}{dice_type}: {rolls} = {total}")
    
    with dice_col3:
        if st.button("Roll 3d6", key="roll_3d6"):
            rolls = [random.randint(1, 6) for _ in range(3)]
            total = sum(rolls)
            st.success(f"3d6: {rolls} = {total}")
    
    with dice_col4:
        st.markdown("*Use the selector to roll multiple dice of the chosen type.*")

    # Character Export/Import
    st.divider()
    st.subheader("💾 Character Save/Load")
    export_col, import_col = st.columns(2)
    
    with export_col:
        if st.button("📤 Export Character as JSON", key="export_json"):
            # Prepare character data for export
            export_data = st.session_state.character.copy()
            json_data = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"{st.session_state.character.get('name', 'Character')}_Shadowdark_Character.json",
                mime="application/json",
                key="download_json"
            )
    
    with import_col:
        uploaded_file = st.file_uploader("📁 Import Character JSON", type="json", key="import_json")
        if uploaded_file is not None and st.button("Import Character", key="import_button"):
            try:
                imported_data = normalize_character_data(json.load(uploaded_file))
                st.session_state["pending_import"] = imported_data
                st.rerun()
            except Exception as e:
                st.error(f"Error importing character: {e}")

    # HTML Export
    st.divider()
    if st.button("🌐 Export Character Sheet as HTML", key="export_html"):
        def html_escape(value):
            return html.escape(str(value))

        def html_list(items):
            return ", ".join(html_escape(item) for item in items)

        def generate_currency(character):
            gold = character.get("gold", 0)
            silver = character.get("silver", 0)
            copper = character.get("copper", 0)
            if gold or silver or copper:
                currency_parts = []
                if gold:
                    currency_parts.append(f"{gold} GP")
                if silver:
                    currency_parts.append(f"{silver} SP")
                if copper:
                    currency_parts.append(f"{copper} CP")
                return ", ".join(currency_parts)
            return "0 GP"

        def generate_html(character):
            character = normalize_character_data(character)
            class_info = get_class_by_name(character.get("class", "")) or {}

            template_path = Path(__file__).resolve().parent / "data" / "shadowdark_character_sheet_v4.html"
            template = template_path.read_text(encoding="utf-8")

            talent_lines = []
            if class_info.get("class_features"):
                for feature in class_info.get("class_features", []):
                    talent_lines.append(f"{feature.get('name', 'Feature')}: {feature.get('description', '')}")
            for talent in character.get("talents", []):
                talent_lines.append(f"Talent: {talent}")
            for spell_name in character.get("spells", []):
                spell = get_spell_by_name(spell_name)
                if spell:
                    talent_lines.append(f"Spell: {spell['name']} (Tier {spell.get('tier', '?')}): {spell.get('description', '')}")
                else:
                    talent_lines.append(f"Spell: {spell_name}")
            additional = character.get("additional_features", "").strip()
            if additional:
                talent_lines.append(f"Additional Features: {additional}")

            gear_items = list(character.get("gear", []))
            custom_gear = character.get("custom_gear", "").strip()
            if custom_gear:
                gear_items.append(f"Custom: {custom_gear}")

            replacements = {
                "__NAME__": html_escape(character.get("name", "")),
                "__ANCESTRY__": html_escape(character.get("ancestry", "")),
                "__CLASS__": html_escape(character.get("class", "")),
                "__TITLE__": html_escape(character.get("title", "")),
                "__ALIGNMENT__": html_escape(character.get("alignment", "")),
                "__BACKGROUND__": html_escape(character.get("background", "")),
                "__DEITY__": html_escape(character.get("deity", "")),
                "__XP__": html_escape(character.get("xp", "")),
                "__LEVEL__": html_escape(character.get("level", 1)),
                "__STR__": html_escape(character.get("strength", 10)),
                "__DEX__": html_escape(character.get("dexterity", 10)),
                "__CON__": html_escape(character.get("constitution", 10)),
                "__INT__": html_escape(character.get("intelligence", 10)),
                "__WIS__": html_escape(character.get("wisdom", 10)),
                "__CHA__": html_escape(character.get("charisma", 10)),
                "__HP__": html_escape(character.get("hp", 0)),
                "__AC__": html_escape(character.get("ac", "")),
                "__GP__": html_escape(character.get("gold", 0)),
                "__SP__": html_escape(character.get("silver", 0)),
                "__CP__": html_escape(character.get("copper", 0)),
                "__TALENTS__": html_escape("\n".join(talent_lines)),
                "__GEAR__": html_escape("\n".join(gear_items)),
            }

            for placeholder, value in replacements.items():
                template = template.replace(placeholder, value)

            return template

        html_content = generate_html(st.session_state.character)
        st.session_state["html_preview_content"] = html_content
        st.download_button(
            label="📥 Download HTML",
            data=html_content.encode("utf-8"),
            file_name=f"{st.session_state.character.get('name', 'Character')}_Shadowdark_Sheet.html",
            mime="text/html",
            key="download_html"
        )

    if st.session_state.get("html_preview_content"):
        st.divider()
        st.subheader("👁️ HTML Preview")
        components.html(
            st.session_state["html_preview_content"],
            height=600,
            scrolling=True,
        )


elif page == "Wiki":
    st.header("📖 Character Options Wiki")
    
    wiki_section = st.tabs(
        ["Ancestries", "Backgrounds", "Classes", "Gear", "Languages", "Spells"]
    )
    
    # Ancestries tab
    with wiki_section[0]:
        st.subheader("Ancestries")
        ancestry_search = st.text_input(
            "🔍 Search ancestries:", 
            key="ancestry_search"
        )
        ancestries = get_ancestries()
        # Filter by search
        if ancestry_search:
            ancestries = [
                a for a in ancestries 
                if ancestry_search.lower() in a["name"].lower()
            ]
        # Sort alphabetically
        ancestries = sorted(ancestries, key=lambda x: x["name"])
        for ancestry in ancestries:
            with st.expander(ancestry["name"]):
                st.markdown(f"**Description:** {ancestry['description']}")
                st.markdown(f"**Trait:** {ancestry['trait']['name']}")
                st.markdown(f"*{ancestry['trait']['description']}*")
                st.markdown(
                    f"**Languages:** {', '.join(ancestry['languages'])}"
                )
    
    # Backgrounds tab
    with wiki_section[1]:
        st.subheader("Backgrounds")
        background_search = st.text_input(
            "🔍 Search backgrounds:", 
            key="background_search"
        )
        backgrounds = get_backgrounds()
        # Filter by search
        if background_search:
            backgrounds = [
                b for b in backgrounds 
                if background_search.lower() in b["name"].lower()
            ]
        # Sort alphabetically
        backgrounds = sorted(backgrounds, key=lambda x: x["name"])
        for background in backgrounds:
            with st.expander(background["name"]):
                st.markdown(f"**Description:** {background['description']}")
                if "roll" in background:
                    st.markdown(f"*Roll Result: {background['roll']}*")
    
    # Classes tab
    with wiki_section[2]:
        st.subheader("Classes")
        class_search = st.text_input(
            "🔍 Search classes:", 
            key="class_search"
        )
        classes = get_classes()
        # Filter by search
        if class_search:
            classes = [
                c for c in classes 
                if class_search.lower() in c["name"].lower()
            ]
        # Sort alphabetically
        classes = sorted(classes, key=lambda x: x["name"])
        for character_class in classes:
            with st.expander(character_class["name"]):
                st.markdown(f"**Description:** {character_class['description']}")
                st.markdown(f"**Hit Points:** {character_class['hit_points']}")
                st.markdown(f"**Armor:** {', '.join(character_class['armor']) or 'None'}")
                st.markdown(f"**Weapons:** {', '.join(character_class['weapons'])}")
                
                st.markdown("**Class Features:**")
                for feature in character_class.get("class_features", []):
                    st.markdown(f"- **{feature['name']}:** {feature['description']}")
                
                # Display spell progression table if available at class level
                if "spells_known_progression" in character_class:
                    st.markdown("**Spells Known by Level:**")
                    progression = character_class["spells_known_progression"]
                    
                    # Create table data
                    table_data = []
                    for level_key in sorted(progression.keys(), key=lambda x: int(x.split('_')[1])):
                        level_num = int(level_key.split('_')[1])
                        spells_by_tier = progression[level_key]
                        
                        row = [f"Level {level_num}"]
                        for tier in range(1, 6):
                            tier_key = f"tier_{tier}"
                            if tier_key in spells_by_tier:
                                row.append(str(spells_by_tier[tier_key]))
                            else:
                                row.append("-")
                        table_data.append(row)
                    
                    # Display as markdown table
                    table_md = "| Level | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 |\n"
                    table_md += "|-------|--------|--------|--------|--------|--------|\n"
                    for row in table_data:
                        table_md += "| " + " | ".join(row) + " |\n"
                    st.markdown(table_md)
                
                # Display spell progression from class features if available
                for feature in character_class.get("class_features", []):
                    if "spells_known_by_level" in feature:
                        st.markdown(f"**Spells Known by Level ({feature['name']}):**")
                        progression = feature["spells_known_by_level"]
                        
                        # Create table data
                        table_data = []
                        for spell_row in progression:
                            level_num = spell_row.get("level", 0)
                            row = [f"Level {level_num}"]
                            for tier in range(1, 6):
                                tier_key = f"tier{tier}"
                                if tier_key in spell_row:
                                    count = spell_row[tier_key]
                                    row.append(str(count) if count > 0 else "-")
                                else:
                                    row.append("-")
                            table_data.append(row)
                        
                        # Display as markdown table
                        table_md = "| Level | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 |\n"
                        table_md += "|-------|--------|--------|--------|--------|--------|\n"
                        for row in table_data:
                            table_md += "| " + " | ".join(row) + " |\n"
                        st.markdown(table_md)
                
                if "talents_table" in character_class:
                    st.markdown("**Talents Table:**")
                    for talent in character_class["talents_table"]:
                        st.markdown(f"- **{talent['roll']}:** {talent['effect']}")
    
    # Gear tab
    with wiki_section[3]:
        st.subheader("Gear")
        col_gear_search, col_gear_category = st.columns(2)
        
        with col_gear_search:
            gear_search = st.text_input(
                "🔍 Search gear:", 
                key="wiki_gear_search"
            )
        
        with col_gear_category:
            gear_categories = get_gear_categories()
            selected_gear_category = st.selectbox(
                "Select gear category:",
                gear_categories,
                key="wiki_gear_category",
            )
        
        if selected_gear_category:
            gear_items = get_gear_by_category(selected_gear_category)
            
            # Filter by search
            if gear_search:
                gear_items = [
                    item for item in gear_items
                    if gear_search.lower() in item["item"].lower()
                ]
            
            # Sort alphabetically by item name
            gear_items = sorted(gear_items, key=lambda x: x["item"])
            
            # Create a nice table display
            for item in gear_items:
                with st.expander(f"{item['item']} ({item.get('cost', 'N/A')})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Cost:** {item.get('cost', 'N/A')}")
                        st.markdown(f"**Slots:** {item.get('slots', 'N/A')}")
                    with col2:
                        st.markdown(f"**Description:** {item.get('description', 'N/A')}")
                    
                    # Show additional weapon info if applicable
                    if "damage" in item:
                        st.markdown(f"**Damage:** {item['damage']}")
                    if "range" in item:
                        st.markdown(f"**Range:** {item['range']}")
                    if "properties" in item:
                        st.markdown(f"**Properties:** {', '.join(item['properties'])}")
    
    # Languages tab
    with wiki_section[4]:
        st.subheader("Languages")
        language_search = st.text_input(
            "🔍 Search languages:", 
            key="language_search"
        )
        languages = get_languages()
        
        for category, langs in languages.items():
            # Filter by search
            filtered_langs = langs
            if language_search:
                filtered_langs = [
                    lang for lang in langs
                    if language_search.lower() in lang.lower()
                ]
            
            if filtered_langs:
                with st.expander(f"{category.replace('_', ' ').title()} Languages"):
                    # Sort alphabetically
                    filtered_langs = sorted(filtered_langs)
                    cols = st.columns(min(3, len(filtered_langs)))
                    for idx, lang in enumerate(filtered_langs):
                        with cols[idx % len(cols)]:
                            st.markdown(f"- {lang}")
    
    # Spells tab
    with wiki_section[5]:
        st.subheader("Spells")
        
        col_spell_search, col_spell_class, col_spell_tier = st.columns(3)
        
        with col_spell_search:
            spell_search = st.text_input(
                "🔍 Search spells:", 
                key="wiki_spell_search"
            )
        
        with col_spell_class:
            classes = get_spell_classes()
            selected_spell_class = st.selectbox(
                "Filter by class:",
                ["All"] + classes,
                key="wiki_spell_class",
            )
        
        spells = get_spells()
        
        if selected_spell_class == "All":
            filtered_spells = spells
        else:
            filtered_spells = get_spells_by_class(selected_spell_class)
        
        with col_spell_tier:
            tiers = sorted(set(spell.get("tier", 0) for spell in filtered_spells))
            selected_tier = st.selectbox(
                "Filter by tier:",
                ["All"] + tiers,
                key="wiki_spell_tier",
            )
        
        if selected_tier != "All":
            filtered_spells = [s for s in filtered_spells if s.get("tier") == selected_tier]
        
        # Filter by search
        if spell_search:
            filtered_spells = [
                s for s in filtered_spells
                if spell_search.lower() in s["name"].lower()
            ]
        
        # Sort alphabetically
        filtered_spells = sorted(filtered_spells, key=lambda x: x["name"])
        
        # Display spells
        for spell in filtered_spells:
            with st.expander(f"{spell['name']} (Tier {spell.get('tier', 'N/A')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Class:** {', '.join(spell.get('classes', []))}")
                    st.markdown(f"**Tier:** {spell.get('tier', 'N/A')}")
                with col2:
                    st.markdown(f"**Range:** {spell.get('range', 'N/A')}")
                    st.markdown(f"**Duration:** {spell.get('duration', 'N/A')}")
                
                st.markdown(f"**Description:** {spell.get('description', 'N/A')}")
