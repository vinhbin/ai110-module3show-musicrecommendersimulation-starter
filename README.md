# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo

 Genre, mood, energy, acousticness, valence
- What information does your `UserProfile` store
User profile: genre=string, mood=string, target_energy=float, likes_acoustic=Boolean

- How does your `Recommender` compute a score for each song
For each song in the catalog, compute a **total score** (0.0 – 1.0) that reflects how well
the song matches the user's preferences. Songs with higher scores rank first.
- How do you choose which songs to recommend
We will be using the ranking rule takes all scored songs and decides which ones to return and in what order.
You can include a simple diagram or bullet list if helpful.

### Algorithm Recipe

For each song in the catalog, the total score is calculated as follows:

| Condition | Points |
|-----------|--------|
| `song.genre == prefs.favorite_genre` | +1.5 |
| `song.mood == prefs.favorite_mood` | +1.0 |
| `max(0.0, 1.0 - abs(song.energy - prefs.target_energy))` | +0.0 to +1.0 |
| **Maximum possible score** | **3.5** |

Songs are then sorted by total score in descending order and the top-K are returned.

### Weighting Tradeoff

The genre bonus (+1.5) dominates the mood bonus (+1.0). A song that matches genre but misses on mood and energy can still score 1.5, while a song that matches mood perfectly and has near-perfect energy similarity can only reach 2.0. This means genre heavily influences the ranking, and two songs with a perfect mood + energy match (score: 2.0) will always beat a genre-only match (score: 1.5) — but a genre match alone ties a song that hits mood perfectly with 0.5 energy similarity (1.0 + 0.5 = 1.5). Consider doubling the energy weight or raising the mood bonus if you want a more nuanced feel-first ranking.

### System Flowchart

```mermaid
flowchart LR
    A["Input: User Preferences\n(favorite_genre, favorite_mood,\ntarget_energy, likes_acoustic)"]
    B["Process: Score Each Song\n• +1.5 if genre matches\n• +1.0 if mood matches\n• +0.0–1.0 energy similarity"]
    C["Output: Top-K Ranked Songs\n(sorted by score descending)"]

    A --> B --> C
```

### Ranking Worked Example

**User:** genre=pop, mood=happy, target_energy=0.80, likes_acoustic=False

| Rank | Song | Score | Passes threshold? |
|------|------|-------|-------------------|
| 1 | Sunrise City | **0.971** | Yes |
| 2 | Rooftop Lights | **0.891** | Yes |
| 3 | Gym Hero | **0.748** | Yes |
| 4 | Night Drive Loop | **0.412** | Yes |
| 5 | Coffee Shop Stories | **0.311** | Yes |
| — | Midnight Coding | 0.196 | **No — filtered** |
| — | Library Rain | 0.181 | **No — filtered** |
| — | Spacewalk Thoughts | 0.164 | **No — filtered** |

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

