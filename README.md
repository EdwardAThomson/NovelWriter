# NovelWriter
## Description

This repository contains Python code to generate a Sci-Fi novel using the OpenAI API. Currently, the code only uses the GPT-4o model. 

Running this code requires an **OpenAI API key** (support for Gemini added too).

The process can probably be fully automated now, but I haven't yet tried. The output is fairly rough and could be further refined.



## The Generation Process
The novel generation process is broken down as follows:

1. Collect parameters from user and generate a high level outline (parameters.py).
2. Generate Universe Background (multiple sub-processes) (lore.py).
3. Generate story act structure (5 acts) (story_structure.py).
4. Generate chapter outlines from the 5-act outline (story_structure.py).
5. Generate scenes for each chapter outline (scene_plan.py).
6. Generate prose on a scene-by-scene basis (chapter_writing.py).

More details can be found on the [discussion](discussion.md) page.

### Original Version
The original version was created as part of NaNoGenMo 2024 ([**completed**](https://github.com/NaNoGenMo/2024/issues/31)). The first version of the code was pushed to a different repo as I lost access to my GitHub account (fixed!), please find the original repo here: [NovelWriter](https://github.com/edthomson/NovelWriter). That code was not fully automated, but it did generate a 52,000-word novel (Echoes of Terra Nova).
