# Novel Writer Application: Overall Workflow

This document outlines the typical end-to-end workflow for generating a story using the Novel Writer application. The process is designed to be iterative and allows for user intervention and customization at various stages.

## Core Generation Steps

The application guides the user through a series of steps, typically corresponding to the tabs in the UI, to build a story from initial concept to final prose.

1.  **Define Novel Parameters (Parameters)**
    *   The user begins by specifying core details for their project in the "Novel Parameters" tab:
        *   Novel Title
        *   Author Name
        *   Genre and Subgenre (e.g., Science Fiction - Space Opera)
        *   Story Length (Short Story, Novella, Novel (Standard), Novel (Epic))
        *   The desired high-level Story Structure (e.g., 6-Act Structure, Hero's Journey)
        *   Output Directory (where all generated files will be saved, defaults to `current_work`)
        *   The LLM Model to be used for generation.
    *   These parameters are crucial as they guide all subsequent generation steps. They are saved to a `parameters.txt` file in the specified output directory.

2.  **Generate Universe Lore (Generate Lore)**
    *   Next, in the "Generate Lore" tab, the application assists in creating the foundational background for the story's universe.
    *   Based on the initial parameters (especially genre, subgenre, and any synopsis provided by the user if that feature is used), the LLM generates:
        *   Details about the setting's technology.
        *   A list of major planets with brief descriptions.
        *   In-depth profiles for major factions, including their goals, resources, and interrelations.
        *   A roster of key characters, outlining their physical descriptions, personalities, motivations, goals, strengths, flaws, and summarized backstories.
        *   A summary of significant relationships between characters.
    *   This detailed information is saved into structured files, primarily:
        *   `generated_lore.md`: Contains general world-building, technology, and planetary details.
        *   `characters.json`: Stores character profiles in a structured format.
        *   `factions.json`: Stores faction profiles in a structured format.

3.  **Develop Story Structure (Story Structure)**
    *   In the "Story Structure" tab, the application expands the chosen high-level story structure framework (from `parameters.txt`) into a more detailed plot.
    *   The process differs slightly based on the selected "Story Length":
        *   For **long-form works** (Novella, Novel, Epic): The system generates a detailed plot breakdown for *each major act or section* of the chosen structure. For example, using the "6-Act Structure," it would create separate detailed plans for the "Beginning," "Rising Action," "First Climax," etc. These are saved as individual markdown files (e.g., `6-act_structure_beginning.md`, `6-act_structure_rising_action.md`).
        *   For **Short Stories**: A single, comprehensive plot outline for the entire short story is generated, adhering to the chosen structure. This is saved as a file like `plot_short_story_[structure_name].md`.

4.  **Plan Chapters and Scenes (Scene Planning)**
    *   This stage, managed in the "Scene Planning" tab, further refines the plot into actionable scene descriptions.
    *   For **long-form works**:
        *   **Generate Chapter Outlines**: First, the user clicks "Generate Chapter Outlines." The system processes each detailed act/section plan (from Step 3) and generates a chapter-by-chapter outline for that specific section. These outlines suggest the number of chapters for the section, their main focus, and key elements like characters and locations. These are saved as `chapter_outlines_[structure]_[section].md` (e.g., `chapter_outlines_6-act_structure_beginning.md`).
        *   **Plan Scenes**: Next, the user clicks "Plan Scenes." The application then takes each chapter outline and generates detailed scene-by-scene plans for *every chapter* in the story. These detailed plans are saved into a dedicated subdirectory: `detailed_scene_plans/scenes_[structure]_[section]_ch[GlobalChapterNumber].md`.
    *   For **Short Stories**:
        *   The user clicks "Plan Scenes." The system uses the overall short story plot (from Step 3, e.g., `plot_short_story_freytags_pyramid.md`) to generate a detailed scene-by-scene plan for the entire story. This is saved as `scenes_short_story_[structure_name].md`.
    *   Each scene description in these plan files typically includes: setting details, characters present, key actions/events, important dialogue snippets or summaries, and how the scene contributes to plot progression or character development.

5.  **Write Prose (Write Chapters)**
    *   The "Write Chapters" tab is where the actual narrative prose is generated.
    *   For **long-form works**:
        *   The user enters a specific `target_chapter_number_global`.
        *   The "Write Chapter" button triggers the system to locate the correct detailed scene plan for that chapter from the `detailed_scene_plans` subdirectory.
        *   The application then processes this chapter scene by scene. For each scene, it constructs a detailed prompt (including the scene's plan, relevant full universe lore, character roster, and faction summaries) and sends it to the selected LLM to generate the prose for that individual scene.
        *   The prose for all scenes in the chapter is then assembled and saved as a single markdown file in a `chapters` subdirectory (e.g., `chapters/chapter_1.md`).
    *   For **Short Stories**:
        *   The "Write Short Story" button is used. The system loads the complete scene plan (e.g., `scenes_short_story_freytags_pyramid.md`).
        *   Similar to long-form chapters, it generates prose scene by scene, providing full context (lore, characters, factions) in each prompt to the LLM.
        *   All generated scene prose is concatenated and saved as a single markdown file (e.g., `prose_short_story_my_title.md`) in the main output directory.

6.  **Review and Rewrite (Optional Feature)**
    *   The "Write Chapters" tab also provides a "Re-Write" button (primarily for long-form works).
    *   This allows the user to select a previously written chapter (e.g., `chapters/chapter_1.md`), and the system will prompt the LLM to rewrite its content. This can be used to expand scenes, improve descriptions, or change the tone, based on refined instructions within the `rewrite_chapter` method's prompt. The rewritten chapter is saved with a prefix (e.g., `chapters/re_chapter_1.md`).

## Iteration and File Management

The entire process is designed to support iteration. Users can revisit earlier stages (e.g., regenerate lore, modify character details in `characters.json`, adjust a specific act's plot, or replan scenes for a chapter) and then regenerate subsequent parts of the story.

The application heavily relies on a set of markdown (`.md`) and JSON (`.json`) files stored in the user-defined output directory. Understanding the purpose and general structure of these files (which will be detailed in `file_formats.md`) can be beneficial, especially for advanced users who might wish to make manual edits to intermediate outputs. 