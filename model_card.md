# Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder 1.1 — a transparent, CLI-first song recommender with an opt-in
agentic loop.

---

## 2. Intended Use

VibeFinder suggests the top 5 songs from a small catalog based on a user's
favorite genre, favorite mood, and target energy level. It is designed for
classroom exploration of how simple scoring rules produce rankings, and how
an agentic layer can detect and correct known failure modes in those rankings.
The system is explicitly *not* intended to drive a real music service or make
decisions on behalf of end users. Standard mode (`python -m src.main`) runs
the original transparent scorer. Agent mode (`python -m src.main --agent`)
adds a five-step reasoning loop on top.

---

## 3. How the Model Works

**Standard mode:** each song in the catalog is compared to the user's
preferences and assigned a score from six numeric signals: genre match
(+1.50), mood match (+1.00), energy similarity (0.0–1.0), tempo similarity
(0.0–1.0), valence similarity (0.0–1.0), and acousticness fit (0.0–1.0).
The top 5 are returned with the exact point contribution of every signal, so
the ranking can be traced by arithmetic.

**Agent mode** wraps the same scorer in five observable steps:

1. **Plan** — inspect the profile. Probe the catalog to count how many songs
   match the requested mood and genre. If mood has zero matches, flag an
   energy+valence boost intent and plan a warning. If genre has two or fewer
   matches, pre-enable diversity mode.
2. **Recommend** — call the standard scorer with the planned config.
3. **Critique** — examine the result list for two specific failure modes:
   (a) an artist appearing two or more times in the top-5 (monopoly), and
   (b) a requested mood that zero top-5 songs satisfy.
4. **Refine** — if an artist monopoly was detected and diversity was not
   already active, re-run with the diversity penalty (artist −0.60, genre
   −0.30). If the mood is catalog-absent, inject a warning rather than a
   scoring change (nothing can be done mechanically).
5. **Finalize** — print a plain-language summary of every decision and the
   final tabulated recommendations.

Every step is logged to stdout so a grader can read the full reasoning trace
without reading source code.

---

## 4. Data

The catalog is `data/songs.csv` with 20 songs. Each row includes id, title,
artist, genre, mood, energy, tempo_bpm, valence, danceability, and
acousticness. Genres represented: pop, lofi, rock, ambient, jazz, synthwave,
indie pop, country, soul, electronic. Moods represented: happy, chill,
intense, relaxed, moody, focused. The dataset is intentionally tiny and
leaves out several genres a real listener might want (hip-hop, classical,
metal, R&B, folk) and several moods (sad, romantic, angry, nostalgic). The
adversarial profile (mood=sad) was specifically chosen to expose what happens
when a requested mood is entirely absent from the catalog.

---

## 5. Strengths

The system is fully transparent in both modes. Standard mode shows exact
numeric contributions per signal; agent mode additionally shows every
decision the loop made and why. The agentic loop specifically targets the
two behavioral failures documented in earlier evaluation: silently dropped
mood signals and single-artist monopolies. For the Chill Lofi profile, the
agent reduced LoRoom's presence from 3/5 to 2/5 and introduced a new artist
(Orbit Bloom) into the top-5. For the adversarial profile, the agent
replaced a silent fallback with an explicit WARNING printed in the finalized
output.

---

## 6. Limitations and Bias

The scorer reads only six of the ten CSV fields even in extended mode
(danceability is never used). Exact-string matching on genre and mood makes
the system brittle: a rock fan cannot be served indie pop even when
acoustically adjacent. The agent's refinement logic runs at most one round:
if diversity is already active and a monopoly still exists (because the
catalog is too thin to eliminate it), the agent flags it in the FINALIZE
summary but does not take further action.

The 20-song catalog is too small to fully break artist monopolies with the
diversity penalty alone: Max Pulse, Neon Echo, and LoRoom each have multiple
entries, so a 2-appearance ceiling is the practical floor — not 1. This is
a catalog constraint, not a logic error.

The agent does not have memory between profiles. Each run is independent and
shares no state.

---

## 7. Evaluation

### Standard evaluation (all 4 profiles, k=5)

Four profiles were tested against the 20-song catalog with k=5:
High-Energy Pop (pop/happy/0.85), Chill Lofi (lofi/chill/0.35),
Deep Intense Rock (rock/intense/0.9), and an adversarial case
(pop/sad/0.9). The first three each returned a full multi-signal match at
rank 1 (scores 6.13–6.30). The adversarial case exposed that when no song
matches a requested mood, the standard scorer silently falls back to genre
+ energy rather than flagging the mismatch.

**Experiment — weight shift on Deep Intense Rock** (0.5× genre, 2× energy):

| Rank | Baseline (genre=1.5, energy=1.0) | Experiment (genre=0.75, energy=2.0) |
|------|----------------------------------|-------------------------------------|
| 1    | Storm Runner 3.49                | Storm Runner 3.73                   |
| 2    | Broken Clocks 2.43 (rock/moody)  | Iron Resolve 3.00 (pop/intense)     |
| 3    | Iron Resolve 2.00                | Gym Hero 2.94 (pop/intense)         |
| 4    | Gym Hero 1.97                    | Bass Drop City 2.90                 |
| 5    | Bass Drop City 1.95              | Broken Clocks 2.61                  |

### Agent vs baseline comparison (8 checks across 4 profiles)

All 8 checks passed.

| Profile | Baseline mood_hits | Agent mood_hits | Baseline max_artist | Agent max_artist | Improvement |
|---|---|---|---|---|---|
| High-Energy Pop | 3/5 (60%) | 3/5 (60%) | 2 | 2 | diversity penalty activated post-hoc |
| Chill Lofi | 3/5 (60%) | 4/5 (80%) | 3 | 2 | LoRoom reduced 3→2; Orbit Bloom enters |
| Deep Intense Rock | 4/5 (80%) | 4/5 (80%) | 2 | 2 | diversity pre-enabled (rock thinly covered) |
| Adversarial sad | 0/5 (0%) | 0/5 (0%) | 2 | 2 | WARNING surfaced; silent fallback eliminated |

Notable: the Chill Lofi agent improved mood coverage from 60% to 80% (3→4
of 5 songs) by letting Arctic Wind (mood=chill, artist=Pale Summit) rise
after Pulse Train and Focus Flow were penalized for LoRoom repetition.

### pytest summary

```
11 passed in 0.03s
```

(2 original scorer tests + 9 agent evaluation tests)

---

## 8. Future Work

Next improvements, in order of payoff:
(1) Allow multi-valued mood preferences — `favorite_moods: [sad, melancholy]`
    — so a requested mood with zero direct catalog matches can be satisfied
    by an adjacent mood rather than silently failing.
(2) Add a second refinement round in the agent: re-critique after diversity
    is applied and check whether the monopoly is actually broken.
(3) Give the agent configurable per-signal weights rather than the
    per-profile diversity flag — e.g., for a sad-mood profile boost valence
    distance weight to compensate for mood absence.
(4) Expand the catalog beyond 20 songs so artist-diversity constraints are
    mechanically achievable (currently the catalog is too thin to guarantee
    max_artist=1 with diversity enabled).
(5) Add structured JSON logging alongside the stdout trace so the agent's
    decisions are machine-readable for automated auditing.

---

## 9. Personal Reflection

See `reflection.md` for the full reflection.
