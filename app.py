import streamlit as st
import json
import random
from fpdf import FPDF
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
        st.session_state.character = {
            "name": "",
            "level": 1,
            "hp": 0,
            "ancestry": None,
            "background": None,
            "class": None,
            "gear": [],
            "languages": [],
            "spells": [],
        }
    
    # Character name
    st.session_state.character["name"] = st.text_input(
        "Character Name",
        value=st.session_state.character["name"],
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
    
    col1, col2, col3 = st.columns(3)
    
    # Ancestry selection
    with col1:
        st.subheader("Ancestry")
        ancestry_names = sorted(get_ancestry_names())
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
        background_names = sorted(get_background_names())
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
        class_names = sorted(get_class_names())
        selected_class = st.selectbox(
            "Choose your class:",
            class_names,
            index=class_names.index(st.session_state.character["class"])
            if st.session_state.character["class"] in class_names
            else 0,
            key="class_select",
        )
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
    
    # Display character summary
    st.divider()
    st.subheader("⚔️ Character Summary")
    
    col_summary1, col_summary2 = st.columns(2)
    
    with col_summary1:
        st.markdown(f"**Name:** {st.session_state.character['name'] or 'Unnamed'}")
        st.markdown(f"**Level:** {st.session_state.character['level']}")
        st.markdown(f"**HP:** {st.session_state.character['hp']}")
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

    # Dice Roller
    st.divider()
    st.subheader("🎲 Dice Roller")
    dice_col1, dice_col2, dice_col3 = st.columns([2, 1, 1])
    
    with dice_col1:
        dice_type = st.selectbox(
            "Select dice type:",
            ["d4", "d6", "d8", "d10", "d12", "d20"],
            key="dice_type",
        )
    
    with dice_col2:
        if st.button("Roll Dice", key="roll_dice"):
            dice_value = int(dice_type[1:])  # Extract number from "d4" etc.
            roll_result = random.randint(1, dice_value)
            st.success(f"Rolled {dice_type}: {roll_result}")
    
    with dice_col3:
        if st.button("Roll 3d6", key="roll_3d6"):
            rolls = [random.randint(1, 6) for _ in range(3)]
            total = sum(rolls)
            st.success(f"3d6: {rolls} = {total}")

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
                imported_data = json.load(uploaded_file)
                st.session_state.character = imported_data
                st.success("Character imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error importing character: {e}")

    # PDF Export
    st.divider()
    if st.button("📄 Export Character Sheet as PDF", key="export_pdf"):
        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="Shadowdark Character Sheet", ln=True, align='C')
        pdf.ln(10)
        
        # Character Info
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 10, txt="Name:", ln=False)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=st.session_state.character.get('name', 'Unnamed'), ln=True)
        
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 10, txt="Level:", ln=False)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=str(st.session_state.character.get('level', 1)), ln=True)
        
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 10, txt="HP:", ln=False)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=str(st.session_state.character.get('hp', 0)), ln=True)
        
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 10, txt="Ancestry:", ln=False)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=st.session_state.character.get('ancestry', ''), ln=True)
        
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 10, txt="Background:", ln=False)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=st.session_state.character.get('background', ''), ln=True)
        
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 10, txt="Class:", ln=False)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=st.session_state.character.get('class', ''), ln=True)
        
        pdf.ln(5)
        
        # Languages
        if st.session_state.character.get("languages"):
            pdf.set_font("Arial", size=12, style='B')
            pdf.cell(50, 10, txt="Languages:", ln=False)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt=", ".join(st.session_state.character["languages"]), ln=True)
        
        # Gear
        if st.session_state.character.get("gear"):
            pdf.set_font("Arial", size=12, style='B')
            pdf.cell(50, 10, txt="Gear:", ln=False)
            pdf.set_font("Arial", size=12)
            gear_text = ", ".join(st.session_state.character["gear"])
            # Handle long text
            if len(gear_text) > 100:
                gear_text = gear_text[:97] + "..."
            pdf.cell(0, 10, txt=gear_text, ln=True)
        
        # Spells
        if st.session_state.character.get("spells"):
            pdf.ln(5)
            pdf.set_font("Arial", size=12, style='B')
            pdf.cell(0, 10, txt="Spells:", ln=True)
            pdf.set_font("Arial", size=12)
            
            all_spells = get_spells()
            spell_tier_map = {spell["name"]: spell["tier"] for spell in all_spells}
            
            for spell in st.session_state.character["spells"]:
                tier = spell_tier_map.get(spell, '?')
                pdf.cell(0, 8, txt=f"• {spell} (Tier {tier})", ln=True)
        
        # Save PDF with error handling
        try:
            pdf_output = pdf.output()
            
            st.download_button(
                label="📥 Download PDF",
                data=pdf_output,
                file_name=f"{st.session_state.character.get('name', 'Character')}_Shadowdark_Sheet.pdf",
                mime="application/pdf",
                key="download_pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}. Try using simpler character names without special characters.")


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
