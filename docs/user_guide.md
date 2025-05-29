# User Guide: How to Use NovelWriter

This guide will walk you through using the NovelWriter application to generate your science fiction novel. No technical expertise required!

The overall design is this: click each button in turn. Click once, let the process finish, then go to the next button.

## Getting Started

1. **Launch the Application**
   - Open your terminal/command prompt
   - Navigate to the NovelWriter folder
   - Type `python main.py` and press Enter
   - The NovelWriter window will appear with several tabs at the top

2. **Select Your AI Model**
   - At the top of the window, you'll see a dropdown menu labeled "Model"
   - Choose your preferred AI model (e.g., "gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro")
   - Each model has different strengths, but all will work well for novel generation

## Step-by-Step Novel Generation

### Step 1: Set Your Novel Parameters

Click on the **"Novel Parameters"** tab to begin.

**What you'll do:**
- **Novel Title**: Enter the title of your story
- **Genre**: Select your desired genre (e.g., Science Fiction, Fantasy, Western, Mystery, Romance, Horror, Thriller, Historical Fiction)
- **Subgenre**: Choose from options like Space Opera, Cyberpunk, Hard Science Fiction, etc.
- **Tone**: Select the mood of your story (e.g., Dark, Optimistic, Gritty)
- **Themes**: Pick themes you want to explore (e.g., Identity, Power, Survival)
- **Setting Details**: Customize your universe with options specific to your chosen subgenre

**Tips:**
- Don't worry about getting everything perfect - you can experiment with different combinations
- The subgenre selection will show you relevant setting options
- Each choice influences how your story will be generated

**When finished:** Click the **"Save Parameters"** button

### Step 2: Generate Your Universe Lore

Click on the **"Generate Lore"** tab.

**What happens here:**
- The app creates factions, locations (e.g., planets for Sci-Fi, cities for Fantasy), and characters for your universe
- Main characters (protagonist, deuteragonist, antagonist) are developed with backstories
- The AI generates rich lore that ties everything together

**What you'll do:**
1. Click **"Generate Initial Data"** - this creates factions, locations, and characters
2. Click **"Generate Character Backstories"** - this adds depth to your main characters
3. Click **"Generate Universe Lore"** - this creates the full background narrative

**What you'll see:**
- Character profiles with names, roles, and relationships
- Faction descriptions with their goals and conflicts
- Rich backstory text that sets up your universe

**Tips:**
- Each step builds on the previous one, so go in order
- The generation may take a minute or two - the AI is creating detailed content
- You can regenerate any step if you want different results

### Step 3: Create Your Story Structure

Click on the **"Story Structure"** tab.

**What happens here:**
- Character arcs are developed based on the backstories
- Faction conflicts are mapped out
- A 6-act story structure is created (Beginning, Rising Action, First Climax, Solution Finding, Second Climax, Resolution)

**What you'll do:**
1. Click **"Generate Character Arcs"**
2. Click **"Generate Faction Arcs"**
3. Click **"Reconcile Character and Faction Arcs"**
4. Click **"Generate Story Structure"**
5. Click **"Refine Story Structure"** for more detail

**What you'll see:**
- Individual character development paths
- How faction conflicts drive the plot
- A complete story outline broken into acts

**Tips:**
- This step is crucial - it's your story's backbone
- The reconciliation step ensures character and faction goals align properly
- The refinement step adds important details to each act

### Step 4: Plan Your Scenes

Click on the **"Scene Planning"** tab.

**What happens here:**
- Your 6-act structure is broken down into individual chapters
- Each chapter is divided into detailed scenes
- You get a roadmap for the actual writing

**What you'll do:**
1. Click **"Generate Chapter Outlines"**
2. Click **"Generate Scene Plans"**

**What you'll see:**
- A list of chapters with their purposes and key events
- Detailed scene breakdowns showing what happens, where, and which characters are involved

**Tips:**
- This is where your abstract story structure becomes concrete
- Each scene should advance the plot or develop characters
- Don't worry if some scenes seem short - they'll expand during writing

### Step 5: Write Your Chapters

Click on the **"Chapter Writing"** tab.

**What happens here:**
- Individual scenes are converted into full prose
- The AI writes actual story content based on all your previous work

**What you'll do:**
1. Select a chapter from the dropdown menu
2. Click **"Generate Chapter"**
3. Review the generated text
4. If you want improvements, click **"Regenerate Chapter"**

**What you'll see:**
- Full chapter text with dialogue, descriptions, and narrative
- Professional-quality prose that follows your story structure

**Tips:**
- Start with Chapter 1 and work sequentially
- Each chapter takes a few minutes to generate
- You can regenerate chapters as many times as you want
- The chapters are saved as individual files in the `current_work/chapters/` folder

## Finishing Your Novel

### Combining Your Chapters

Once you've generated all your chapters:

1. **Option 1: Use the Combine Script**
   - Open terminal/command prompt
   - Navigate to your NovelWriter folder
   - Type `python combine.py` and press Enter
   - This creates a single file with your complete novel

2. **Option 2: Manual Assembly**
   - Go to the `current_work/chapters/` folder
   - Open each chapter file and copy the text into a single document

### Your Final Novel

You'll have:
- A complete science fiction novel (typically 50,000+ words)
- Rich characters with development arcs
- A well-structured plot with proper pacing
- Detailed world-building and lore

## Tips for Success

### Before You Start
- **Have your API keys ready**: Make sure your `.env` file is properly configured
- **Plan your time**: Full novel generation can take 1-2 hours depending on your computer and internet speed
- **Choose your model wisely**: Different AI models have different writing styles

### During Generation
- **Be patient**: AI generation takes time, especially for longer content
- **Save frequently**: Use the save buttons after each major step
- **Experiment**: Try regenerating sections if you want different results
- **Review as you go**: Check that each step builds logically on the previous one

### After Generation
- **Edit and revise**: The generated novel is a strong first draft - feel free to edit
- **Check consistency**: Make sure character names and details remain consistent
- **Add personal touches**: Insert your own style and voice where desired

## Troubleshooting

### Common Issues

**"No model selected" error:**
- Make sure you've chosen a model from the dropdown at the top

**Generation seems stuck:**
- Check your internet connection
- Verify your API keys are correct
- Some models are slower than others

**Generated content seems inconsistent:**
- Make sure you completed all previous steps in order
- Try regenerating the problematic section

**App won't start:**
- Check that you've installed all dependencies: `pip install -r requirements.txt`
- Verify your Python version is 3.7 or higher

### Getting Help

- Check the detailed documentation in the `docs/` folder
- Review the README.md file for technical setup issues
- Make sure your `.env` file contains valid API keys

## What Makes a Good Generated Novel

The best results come from:
- **Clear parameters**: Be specific about your preferred tone and themes
- **Interesting subgenre choices**: Each subgenre creates different story possibilities
- **Patience with the process**: Let each step complete fully before moving on
- **Willingness to regenerate**: Don't settle for the first result if it doesn't feel right

Remember: NovelWriter creates a strong foundation for your novel. The generated content is designed to be edited, expanded, and personalized to match your vision!
