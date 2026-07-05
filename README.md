# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version, **VibeMatch 1.0**, is a content-based recommender that scores every song in a 20-track catalog against a user's taste profile (favorite genre, mood, and target levels for energy, valence, danceability, and acousticness). Each song earns points for matching or being *close to* the user's preferences, and the top-k songs are returned **with human-readable reasons** for every score (e.g. `genre match: pop (+2.0)`). It also supports multiple scoring modes (genre-first, mood-first, energy-focused) and applies a diversity penalty so one artist can't monopolize the list.

---

## How The System Works

### How real platforms do it

Real services like Spotify and YouTube mostly blend two families of techniques. **Collaborative filtering** ignores what a song *sounds like* and instead uses behavior: if thousands of users who like the same songs you like also love a track you've never heard, it gets recommended to you. Its raw data is likes, skips, saves, playlist co-occurrence, and listening history. **Content-based filtering** works from the song's own attributes — tempo, energy, valence ("musical positiveness"), danceability, acousticness, genre labels, even audio embeddings learned from the waveform — and matches them against a profile of what you've enjoyed before. Big platforms combine both (plus context like time of day) because each covers the other's blind spot: collaborative filtering can't recommend a brand-new song with no listens (the "cold start" problem), and content-based filtering can't discover that you'd love something *unlike* anything you've played.

**My version is a pure content-based system.** It has no other users to learn from — just one user profile and a catalog of song attributes — so it prioritizes explainability: every recommendation comes with the exact point breakdown that produced it.

### The data

Each **Song** row in `data/songs.csv` uses these features:

- **Categorical:** `genre`, `mood`, `mood_tags` (detailed tags like `nostalgic;dreamy`)
- **Numerical (0.0–1.0):** `energy`, `valence`, `danceability`, `acousticness`, `instrumentalness`, `liveness`
- **Other:** `tempo_bpm`, `popularity` (0–100), `release_decade`, plus `id`, `title`, `artist`

The **UserProfile** stores target values for the features the user cares about:

- `genre` and `mood` (exact-match preferences)
- `energy` (0.0–1.0 target — the system rewards songs *close to* the target, not just high or low)
- Optional targets: `valence`, `danceability`, `acousticness`
- Optional `mode` to switch scoring strategies

### The Algorithm Recipe (scoring rule)

`score_song()` judges **one** song against the profile and returns a score plus a list of reasons:

| Rule | Points (balanced mode) |
|---|---|
| Exact genre match | **+2.0** |
| Related genre (e.g. synthwave ~ pop) | +1.0 |
| Exact mood match | **+1.0** |
| Preferred mood appears in `mood_tags` | +0.5 |
| Energy closeness | up to **+1.5** × (1 − \|target − song\|) |
| Valence / danceability / acousticness closeness (only if the profile sets a target) | up to +0.5 each |
| Popularity boost | up to +0.3 × (popularity / 100) |

Genre is weighted highest (2×) because genre is the strongest single predictor of whether a listener will accept a song; mood matters but is fuzzier (a "chill" listener may still enjoy a "focused" track), so it earns half. Numerical features use **closeness, not magnitude**: a user with `energy: 0.4` should get 0.42-energy lofi, not 0.97-energy metal, so points scale with `1 − |gap|`.

### The Ranking Rule (why scoring alone isn't enough)

A scoring rule only judges one song in isolation — it can't tell you *which* songs to show. `recommend_songs()` runs the scoring rule as a judge over **every** song in the catalog, sorts by score (highest first), then applies a **diversity penalty** during selection (−0.75 per already-recommended artist, −0.3 per genre repeat beyond the first) so the top-k isn't five near-identical tracks.

**Data flow:** Input (user prefs) → Process (the loop: `score_song()` judges all 20 songs) → Output (top-k ranked list with reasons).

### Biases I expect (before testing)

- **Genre over-prioritization:** a +2.0 genre bonus can outrank a song that fits the user's mood and energy *perfectly* but wears the wrong genre label — a classic filter bubble.
- **Popularity bias:** the popularity boost systematically nudges already-popular songs upward, which is how real systems make hits hittier.
- **No discovery:** a pure content-based system only ever recommends things similar to what the user already said they like.

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

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

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



