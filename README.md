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

Output of `python -m src.main --profile high_energy_pop`:

```
Loaded songs: 20
Scoring mode: balanced

=== Profile: high_energy_pop (genre=pop, mood=happy, energy=0.9, danceability=0.85) ===

Rank  Title                    Artist           Genre      Mood        Score
----------------------------------------------------------------------------
1     Sunrise City             Neon Echo        pop        happy        5.07
      why: genre match: pop (+2.0); mood match: happy (+1.0); energy 0.82 vs target 0.90
           (+1.38); danceability 0.79 vs target 0.85 (+0.47); popularity 72/100 (+0.22)
2     Gym Hero                 Max Pulse        pop        intense      4.18
      why: genre match: pop (+2.0); energy 0.93 vs target 0.90 (+1.46); danceability 0.88 vs
           target 0.85 (+0.48); popularity 80/100 (+0.24)
3     Rooftop Lights           Indigo Parade    indie pop  happy        3.97
      why: related genre: indie pop ~ pop (+1.0); mood match: happy (+1.0); energy 0.76 vs
           target 0.90 (+1.29); danceability 0.82 vs target 0.85 (+0.48); popularity 66/100
           (+0.20)
4     Isla Caliente            Rumba Vista      reggaeton  happy        3.17
      why: mood match: happy (+1.0); energy 0.88 vs target 0.90 (+1.47); danceability 0.95 vs
           target 0.85 (+0.45); popularity 82/100 (+0.25)
5     Bassline Horizon         DJ Nova          edm        euphoric     3.16
      why: related genre: edm ~ pop (+1.0); energy 0.94 vs target 0.90 (+1.44); danceability
           0.93 vs target 0.85 (+0.46); popularity 85/100 (+0.26)
```

Run `python -m src.main` for all six evaluation profiles, `--mode` to switch scoring strategies (`balanced`, `genre_first`, `mood_first`, `energy_focused`, `energy_experiment`), `--k` for list length, and `--no-diversity` to disable the diversity penalty. Full outputs for every profile are in [model_card.md](model_card.md).

---

## Experiments You Tried

- **Weight shift (`--mode energy_experiment`: genre 2.0 → 1.0, energy 1.5 → 3.0).** The chill-lofi profile's #5 changed from Focus Flow (lofi) to Moonlight Study No. 3 (classical) — doubling energy's weight reached across genre lines and surfaced a quiet piano piece. Gym Hero fell from #2 to #4 for the pop profile once its genre advantage was halved. Verdict: lists became more genre-diverse but less taste-anchored — *different*, not clearly better. The #1 picks were mostly stable; the tail of each list is what's weight-sensitive.
- **Adversarial profiles.** A conflicted user (genre=edm, mood=sad, energy=0.95) got a *euphoric* track at #1 — genre (+2.0) outbids mood (+1.0) whenever they disagree. A user asking for a genre that isn't in the catalog (k-pop) degraded gracefully to mood/energy matching. A perfectly neutral user (all targets 0.5) got scores clustered within 0.2 points, meaning popularity effectively decided their ranking.
- **Diversity penalty on/off (`--no-diversity`).** Without it, LoRoom takes two of five chill-lofi slots; with it, the second LoRoom track pays −0.75 and drops, letting another artist in.

---

## Limitations and Risks

- **Tiny, imbalanced catalog:** 20 songs; lofi has 3 while rock, metal, country and most genres have exactly 1 — so most of a rock fan's list can't actually be rock.
- **Genre beats mood in conflicts:** a user asking for sad music still gets a euphoric track if the genre label matches (see the sad-banger experiment).
- **Universal donors:** high-energy, high-popularity songs (Gym Hero, Bassline Horizon) appear in nearly every profile's top 5 — a miniature popularity/filter-bubble effect, amplified by the deliberate popularity bonus.
- **No understanding of sound:** the system trusts CSV labels; it has never "heard" a song, knows no lyrics or language, and can't discover taste the user didn't state.

The [model card](model_card.md) goes deeper on each of these.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

What I learned about turning data into predictions: a recommendation is just three separable decisions — *what data represents taste* (the features), *how one song is judged* (the scoring rule), and *how judgments become a list* (the ranking rule). Once I separated those, the system stopped feeling like magic. The scoring rule is where all the opinions live: choosing +2.0 for genre and +1.0 for mood **is** the algorithm's worldview, and every ranking downstream inherits it. The most useful design decision was making numeric features reward *closeness* to a target instead of magnitude — that single change is why the chill profile never gets metal.

On bias: I expected bias to come from bad data, but I watched it emerge from *reasonable* choices. My hand-tuned weights silently decided that genre identity matters more than emotional state (the sad-EDM user got a euphoric anthem). My deliberate popularity bonus made already-popular songs show up for almost everyone — the exact feedback loop that makes real platforms homogenize taste. And my catalog's imbalance (3 lofi songs, 1 rock song) meant some users get served well and others get leftovers. None of that required malice or even a mistake — which is exactly why real systems need model cards, evaluation across diverse user profiles, and adversarial testing.



