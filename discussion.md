# Discussion

## Latest Updates

### Gemini
I've added the option to generate text using Google's Gemini. My primary testing was with Gemini 1.5 pro. The API allows for a huge input context window, potentially of 1 million tokens. This should be large enough for an entire model.

The output context window is far smaller, unfortunately it is only 8192 (confer 4o with 16,384). I'm finding that Gemini 1.5 can be lazy. If I ask it to preserve certain details it may well just ignore that request, or it changes the details (like minor character names) despite those details being in the prompt.

I haven't tested Gemini's reasoning models yet, but intuition suggests that non-reasoning models are missing some extra magic that makes them not quite fit-for-purpose for novel generation. I fear that better non-reasoning won't help. I could turn the temperature down to improve accuracy, but then it would affect creative output. 

## Process Details
Here are greater details of the generation process. Please note that the generation process is evolving, so there is a chance that some details are off.

1. Collect parameters, generate high-level outline: briefly outline the setting, major technologies, major factions, the major conflict in the story, plus the key themes.
2. Generate Universe Background:
    1. Generate background details about the technology of the setting.
    2. Generate a list of major planets.
    3. Generate more details for the factions. This goes beyond what is created by the first prompt.
    4. Generate a list of characters. This outlines their goals and motivations, but is a bit light in detail.
    5. Improve Character Details.
    6. Generate a list of relationships between the characters.
3. Generate a 5-act structure outline. This will build out a rough structure based upon the idea generated in the first prompt.
4. Generate chapter outlines. This takes the acts created in the previous step and turns them into a series of chapters with short descriptions. The overall flow of the structure should match, but now have more details. I've seen outlines ranging from 10 - 18 chapters in testing.
5. Generate Scenes. The next step is to create individual scenes based upon the chapter outlines. There can be say 3-6 scenes per chapter. The prompt provides the full list of chapters when generating scenes. I think this is a big factor in maintaining coherency.
6. Generate prose on a scene-by-scene basis. One prompt is one scene which generates 700 - 1200 words. Each chapter has multiple scenes, so the number of words quickly adds up. The overall length is still short of a good novel, but it's getting there.



## Background
For the curious readers, I will outline some of the thinking behind this project.

### Project Goals
When first discovering LLMs it became apparent that they could one-day generate novel-length prose. I started to think about how to approach the idea, I could see that the problem had to be broken down into smaller tasks.

Here are the goals I set for the project:

* Demonstrate the feasibility of using LLMs to write a novel by breaking down the creative process into smaller, manageable tasks.
* Participate in NaNoGenMo by generating 50,000 words of coherent text using AI. ([**completed**](https://github.com/NaNoGenMo/2024/issues/31)).
* Develop an approach that allows for improvement over time.

To break the task down I figured I could potentially use the [Snowflake technique](https://www.advancedfictionwriting.com/articles/snowflake-method/) (I read about it many years ago). I haven't followed that technique exactly, but it was inspiration for the process I followed.

While searching online for previous attempts at this challenge I came across [David Shapiro](https://www.youtube.com/@DaveShap) who had put some thought into [Novel generation with LLMs](https://www.youtube.com/watch?v=223ELutchs0), which he labelled AutoMuse, but seems he has paused that work. His ideas around cognitive architectures plus his general comments on how LLMs were helpful when I was developing this project.


### Impossible Goals?
I've seen a lot of people argue that it's not possible to write a novel with current LLMs, mainly due to the context window limitations or perhaps due to intelligence-level. However, neither of those are really the issue.

The idea is that since LLMs can't generate huge amounts of text at once, they're unsuitable for creating a cohesive story. But honestly, the idea of one-shotting a novel in a single LLM pass seems impractical—even for human authors, writing a novel is an iterative process. Authors like Stephen King might write fast, but they certainly don't write without planning, contemplation, and rewriting. So why would we expect an AI to one-shot a novel?

Smarter LLMs at the level of a professional writer with a giant context window may not still "solve" the problem, but I think some ability to plan and iteratve upon an answer should improve generation. Perhaps a more advanced version of o1, or an agent-based approach, would be best.

That being said, I've had a hypothesis for a while that GPT4 is sufficiently advanced that it could produce a novel if using multiple prompts and adding some extra process to ensur coherency. I think this project shows a path towards that goal. The limitations of context window can be somewhat mitigated by providing an over-arching plan for the code to follow: start at a high level, then delve into finer details while allowing the LLM to see some story context on either side of the section of interest. See The Generation Process for more details.

### Original Version
The original version was created as part of NaNoGenMo 2024 ([**completed**](https://github.com/NaNoGenMo/2024/issues/31)). The first version of the code was pushed to a different repo as I lost access to my GitHub account (fixed!), please find the original repo here: [NovelWriter](https://github.com/edthomson/NovelWriter). That code was not fully automated, but it did generate a 52,000-word novel (Echoes of Terra Nova).

The goal was to explore the potential of LLMs for long-form storytelling, breaking the problem into manageable pieces rather than attempting generation with a single prompt. The first version was rough and created in a rush to finished by the end of NaNoGenMo 2024, due to missing a lot of time during the month the code was less well-developed than I had hoped. In addition to not making the code quite as good as I had hoped, I didn't only use GPT-4o to generate the novel which had been a goal. I also o1-mini where I struggled to generate some background information with 4o, and then eventually I had to use o1-preview to generate the text. This was pretty expensive as I had to generate the text at least twice due to a logical error within the prompts.

Since then I've reworked the code such that it only needs to use the GPT-4o model for API calls, which has vastly reduced the costs and was a sub-goal when I started to goal. The big improvement came from adding a step in the process that generates individual scenes and not just high level chapter outlines.


