# Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder 1.0 — a transparent, CLI-first song recommender.

---

## 2. Intended Use

VibeFinder suggests the top 5 songs from a small catalog based on a user's
favorite genre, favorite mood, and target energy level. It is designed for
classroom exploration of how simple scoring rules produce rankings, not for
real listeners. The system assumes the user can name a single preferred genre
and mood and provide a numeric energy target between 0.0 and 1.0. It is
explicitly *not* intended to drive a real music service or make decisions on
behalf of end users.

---

## 3. How the Model Works

Each song in the catalog is compared to the user's preferences and given a
score out of 3.5. The song gets 1.5 points if its genre matches the user's
favorite genre, 1.0 point if its mood matches the user's favorite mood, and
between 0.0 and 1.0 point depending on how close its energy is to the user's
target (perfect match is 1.0, far apart is 0.0). Scores from each song are
sorted highest-to-lowest, and the top 5 are returned along with a plain
explanation of which signals contributed how many points. The starter
weighting used +2.0 for genre, which caused a genre-only match to tie a
mood+energy match; we lowered the genre weight to +1.5 so mood and energy
together can outrank a genre-only match.

---

## 4. Data

The catalog is `data/songs.csv` with 20 songs. Each row includes id, title,
artist, genre, mood, energy, tempo_bpm, valence, danceability, and
acousticness. Genres represented: pop, lofi, rock, ambient, jazz, synthwave,
indie pop, country, soul, electronic. Moods represented: happy, chill,
intense, relaxed, moody, focused. The dataset is intentionally tiny and
leaves out several genres a real listener might want (hip-hop, classical,
metal, R&B, folk) and several moods (sad, romantic, angry, nostalgic), which
biases results toward the taste profile assumed by the starter data.

---

## 5. Strengths

The system is fully transparent: every recommendation arrives with the
numeric contributions of each matched signal, so a user can see exactly why
a song was ranked where it was. The top result for each of the three
"well-formed" profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock)
matched intuition — each surfaced a song with all three signals aligned.
The CLI-first design makes the scoring trivial to audit: no hidden embeddings
or opaque model weights, just three arithmetic rules a student can trace by
hand.

---

## 6. Limitations and Bias

The scorer reads only three of the ten CSV fields — genre, mood, and energy —
so tempo, valence, danceability, and acousticness are invisible to ranking.
Exact-string matching on genre and mood makes the system brittle: a rock fan
cannot be served indie pop even when acoustically adjacent. The adversarial
case (mood=sad with no sad songs in the catalog) silently drops the mood
signal rather than warning the user, which can mislead them into thinking the
top result matched their mood. The 20-song catalog is also far too small to
surface filter-bubble effects at scale; Max Pulse dominates multiple top-5
lists because the high-energy pop region is thinly populated.

---

## 7. Evaluation

Four profiles were tested against the 20-song catalog with k=5:
High-Energy Pop (pop/happy/0.85), Chill Lofi (lofi/chill/0.35),
Deep Intense Rock (rock/intense/0.9), and an adversarial case
(pop/sad/0.9). The first three each returned a full 3-signal match at rank 1
(scores 3.47–3.50). The adversarial case exposed that when no song matches a
requested mood, the system silently falls back to genre + energy rather than
flagging the mismatch.

**Experiment — weight shift on Deep Intense Rock** (0.5× genre, 2× energy):

| Rank | Baseline (genre=1.5, energy=1.0) | Experiment (genre=0.75, energy=2.0) |
|------|----------------------------------|-------------------------------------|
| 1    | Storm Runner 3.49                | Storm Runner 3.73                   |
| 2    | Broken Clocks 2.43 (rock/moody)  | Iron Resolve 3.00 (pop/intense)     |
| 3    | Iron Resolve 2.00                | Gym Hero 2.94 (pop/intense)         |
| 4    | Gym Hero 1.97                    | Bass Drop City 2.90                 |
| 5    | Bass Drop City 1.95              | Broken Clocks 2.61                  |

Amplifying energy and shrinking genre dropped Broken Clocks (rock but wrong
mood) from rank 2 to 5 and promoted three mood+energy matches above it.
Genre shifts from primary filter to tiebreaker.

---

## 8. Future Work

Next improvements, in order of payoff: (1) use the unused CSV columns —
adding a tempo-proximity term and an acousticness-preference term would let
the scorer distinguish "driving rock" from "slow rock" and reward acoustic
preferences. (2) Allow multi-valued preferences — a `favorite_genres` list
and fuzzy genre adjacency (e.g., indie pop ≈ pop) would remove the exact-
match brittleness. (3) Add a diversity penalty so the top 5 don't collapse to
one artist's catalog (currently Max Pulse monopolizes multiple profiles).
(4) Warn the user when a requested mood or genre has zero catalog matches,
rather than silently dropping the signal. (5) Explore scoring modes
(Genre-First / Mood-First / Energy-Focused) as a dict of scoring functions
to demonstrate the Strategy pattern.

---

## 9. Personal Reflection

See `reflection.md` for the full reflection.
