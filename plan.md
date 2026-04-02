# Music Recommender — Scoring & Ranking Plan

## Goal

For each song in the catalog, compute a **total score** (0.0 – 1.0) that reflects how well
the song matches the user's preferences. Songs with higher scores rank first.

---

## Features & Weights

| # | Feature | Type | Weight (w) | Rationale |
|---|---------|------|-----------|-----------|
| 1 | genre | categorical | **0.35** | Strongest preference signal |
| 2 | mood | categorical | **0.30** | Context-driven, highly discriminating |
| 3 | energy | numerical | **0.20** | Continuous; rewards closeness to target |
| 4 | acousticness | numerical | **0.10** | Maps to likes_acoustic boolean |
| 5 | valence | numerical | **0.05** | Tie-breaker; adds emotional nuance |

**Total weights = 1.00**

---

## Per-Feature Scoring Rules

### 1. Genre Score  `s_genre`  (weight 0.35)

Exact match only — genre is a hard preference, not a spectrum.

```
s_genre = 1.0   if song.genre == user.favorite_genre
          0.0   otherwise
```

### 2. Mood Score  `s_mood`  (weight 0.30)

Exact match, same reasoning as genre.

```
s_mood = 1.0   if song.mood == user.favorite_mood
         0.0   otherwise
```

### 3. Energy Score  `s_energy`  (weight 0.20)

Energy is a float in [0, 1]. We want to **reward closeness** to the user's target energy,
not just high or low values. We use the **absolute difference**, then invert it:

```
s_energy = 1 - |song.energy - user.target_energy|
```

**Why this works:**

| user.target_energy | song.energy | |delta| | s_energy |
|--------------------|-------------|---------|----------|
| 0.80 | 0.82 | 0.02 | **0.98** (near-perfect) |
| 0.80 | 0.42 | 0.38 | **0.62** (moderate penalty) |
| 0.80 | 0.28 | 0.52 | **0.48** (strong penalty) |

Because both values live in [0, 1], the delta is always in [0, 1],
so `s_energy` is always in [0, 1] — no clamping needed.

### 4. Acousticness Score  `s_acoustic`  (weight 0.10)

The user preference is a boolean (`likes_acoustic`). We convert the continuous
`acousticness` value into a score using a threshold of **0.6**:

```
if user.likes_acoustic:
    s_acoustic = song.acousticness          # higher acousticness = better
else:
    s_acoustic = 1.0 - song.acousticness    # lower acousticness = better
```

**Example:**
- User likes acoustic, song has acousticness 0.86 → score = **0.86**
- User dislikes acoustic, song has acousticness 0.86 → score = **0.14**

### 5. Valence Score  `s_valence`  (weight 0.05)

No direct user preference for valence — use a fixed target of **0.70** (moderately positive)
as a soft default, with same closeness formula as energy:

```
VALENCE_TARGET = 0.70
s_valence = 1 - |song.valence - VALENCE_TARGET|
```

> This can be promoted to a user preference later if needed.

---

## Total Score Formula

```
total_score = (w_genre      * s_genre)
            + (w_mood       * s_mood)
            + (w_energy     * s_energy)
            + (w_acoustic   * s_acoustic)
            + (w_valence    * s_valence)

total_score = (0.35 * s_genre)
            + (0.30 * s_mood)
            + (0.20 * s_energy)
            + (0.10 * s_acoustic)
            + (0.05 * s_valence)
```

**Result range: [0.0, 1.0]**  
A score of 1.0 means a perfect match on every feature.

---

## Worked Example

**User profile:** genre=pop, mood=happy, target_energy=0.80, likes_acoustic=False

**Song: "Sunrise City"** (pop, happy, energy=0.82, valence=0.84, acousticness=0.18)

| Feature | Calculation | Score | Weight | Contribution |
|---------|-------------|-------|--------|--------------|
| genre | pop == pop | 1.00 | 0.35 | 0.350 |
| mood | happy == happy | 1.00 | 0.30 | 0.300 |
| energy | 1 - \|0.82 - 0.80\| = 1 - 0.02 | 0.98 | 0.20 | 0.196 |
| acousticness | 1 - 0.18 (dislikes acoustic) | 0.82 | 0.10 | 0.082 |
| valence | 1 - \|0.84 - 0.70\| = 1 - 0.14 | 0.86 | 0.05 | 0.043 |
| | | | **Total** | **0.971** |

**Song: "Midnight Coding"** (lofi, chill, energy=0.42, valence=0.56, acousticness=0.71)

| Feature | Calculation | Score | Weight | Contribution |
|---------|-------------|-------|--------|--------------|
| genre | lofi != pop | 0.00 | 0.35 | 0.000 |
| mood | chill != happy | 0.00 | 0.30 | 0.000 |
| energy | 1 - \|0.42 - 0.80\| = 1 - 0.38 | 0.62 | 0.20 | 0.124 |
| acousticness | 1 - 0.71 (dislikes acoustic) | 0.29 | 0.10 | 0.029 |
| valence | 1 - \|0.56 - 0.70\| = 1 - 0.14 | 0.86 | 0.05 | 0.043 |
| | | | **Total** | **0.196** |

The scoring correctly surfaces "Sunrise City" (0.971) over "Midnight Coding" (0.196).

---

## Ranking Rule

The ranking rule takes **all scored songs** and decides which ones to return and in what order.
It operates after scoring is complete — it never looks at raw features, only at scores.

---

### Step 1 — Score Every Song

Apply the total score formula to every song in the catalog, producing a scored list:

```
scored = [(song_1, 0.971), (song_2, 0.196), (song_3, 0.183), ...]
```

---

### Step 2 — Filter: Minimum Score Threshold

Drop songs whose score is too low to be a meaningful recommendation.
A song below the threshold is irrelevant regardless of rank.

```
SCORE_THRESHOLD = 0.30

qualified = [(song, score) for (song, score) in scored
             if score >= SCORE_THRESHOLD]
```

**Why 0.30?**  
A song scoring below 0.30 means it matched none of the categorical features (genre, mood)
and performed poorly on all numerical features. Recommending it would feel random to the user.

| Score range | Meaning |
|---|---|
| 0.65 – 1.00 | Strong match — genre or mood aligned |
| 0.30 – 0.64 | Partial match — numerical features align even if genre/mood miss |
| 0.00 – 0.29 | Weak match — filtered out |

---

### Step 3 — Sort: Descending by Score

Sort the qualified list from highest to lowest score.

```
ranked = sort(qualified, by=score, descending=True)
```

This is the primary ranking rule: **higher score = better rank**.

---

### Step 4 — Tie-Breaking Rule

When two songs have identical scores (or scores within 0.01 of each other),
use **valence** as the tie-breaker — prefer the song whose valence is closer to 0.70
(the neutral-positive default).

```
if |score_A - score_B| <= 0.01:
    rank A above B  if  |valence_A - 0.70| < |valence_B - 0.70|
```

Valence is already scored in Step 1, so no extra computation is needed —
just use `s_valence` as the secondary sort key.

```
ranked = sort(qualified, by=(score DESC, s_valence DESC))
```

---

### Step 5 — Truncate to Top-K

Return only the top `k` results. `k` defaults to 5 but is caller-controlled.

```
top_k = ranked[:k]
```

---

### Full Ranking Pipeline (Pseudocode)

```
function recommend_songs(user_prefs, songs, k=5):

    # Step 1 — Score
    scored = []
    for song in songs:
        s = score_song(song, user_prefs)      # → float in [0, 1]
        scored.append((song, s))

    # Step 2 — Filter
    qualified = [(song, s) for (song, s) in scored if s >= 0.30]

    # Step 3 & 4 — Sort with tie-breaking
    ranked = sort(qualified, primary=score DESC, secondary=s_valence DESC)

    # Step 5 — Truncate
    return ranked[:k]
```

---

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

Top-3 (k=3) returned: Sunrise City, Rooftop Lights, Gym Hero.

---

## Explanation String

Each recommendation should include a human-readable explanation built from which features contributed most:

```
"Matches your genre (pop) and mood (happy). Energy is very close to your target (0.82 vs 0.80)."
```

Logic: collect features where contribution > their weight * 0.5 (i.e., scored above 50% of max possible), format into a sentence.

---

## Implementation Checklist

- [ ] Implement `load_songs(csv_path)` — parse CSV into list of dicts
- [ ] Implement per-feature scoring functions with the formulas above
- [ ] Implement `recommend_songs(user_prefs, songs, k)` — score all songs, sort descending, return top-k
- [ ] Implement `explain_recommendation(user, song)` — build explanation from top contributing features
- [ ] Implement `Recommender.recommend()` using `UserProfile` dataclass
- [ ] Implement `Recommender.explain_recommendation()` using `UserProfile` dataclass
