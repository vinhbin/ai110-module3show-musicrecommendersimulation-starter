# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0** — a content-based, weighted-score music recommender with explainable results.

---

## 2. Intended Use

VibeMatch suggests songs from a small, hand-built catalog to a single user based on their stated taste (favorite genre, mood, and target "vibe" levels like energy). It is built for **classroom exploration** — to make the mechanics of recommendation visible, not to serve real users. It assumes the user can state their taste up front, that taste is stable, and that a song's CSV attributes honestly describe how it sounds.

**Non-intended use:** production music recommendation, discovering music outside your stated taste, or any decision that matters. It has 20 songs and no idea what any of them sound like.

---

## 3. How the Model Works

Every song gets judged against your preferences and earns points:

- A song in your **favorite genre** earns the biggest bonus (+2.0). A *related* genre (like synthwave when you asked for pop) earns half credit.
- A song matching your **mood** earns +1.0, or +0.5 if your mood only appears in its detailed mood tags.
- For **numeric vibes** (energy, valence, danceability, acousticness, instrumentalness, liveness), the song earns points for being *close to your target* — a 0.4-energy song is nearly perfect for a 0.3-energy person, and a 0.97-energy metal track is not. Closeness matters, not "more is better."
- If you name a favorite **era**, songs from a nearby release decade earn points too (full credit at an exact match, fading to zero across 50 years).
- **Popular songs get a small extra nudge** (up to +0.3). This is deliberate, so we can observe popularity bias in action.

Then every song's score is computed, the list is sorted highest-first, and the top 5 are shown **with the reasons for every point earned**. A *diversity penalty* (−0.75 per repeated artist, −0.3 per genre pile-up) stops one artist or genre from filling the whole list. Compared to the starter logic (which recommended the first k songs unsorted), everything above is new, and there are five switchable scoring modes (balanced, genre-first, mood-first, energy-focused, and an experimental mode).

---

## 4. Data

- **20 songs**, expanded from the 10-song starter catalog.
- **15 columns per song**: genre, mood, energy, tempo, valence, danceability, acousticness, plus five added attributes — popularity (0–100), release decade, detailed mood tags, instrumentalness, and liveness. All five added attributes are scoring-active: mood tags give partial mood credit, popularity adds a small nudge to every song, and instrumentalness, liveness, and release decade are matched by closeness when a profile sets a target (the `vintage_instrumental` profile exercises them).
- **16 genres** (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, country, classical, metal, edm, r&b, indie folk, reggaeton, soul) — but very unevenly: lofi has 3 songs while rock, metal, country, and most others have exactly 1.
- **What's missing:** lyrics, language, era-authentic sound, artist identity/culture, and everything about the *user* except their one stated profile. Whole regions of musical taste (K-pop, Afrobeats, Bollywood, gospel…) simply don't exist in this catalog.

---

## 5. Strengths

- **Explainability**: every recommendation shows its exact point breakdown, so a wrong answer is easy to diagnose.
- Realistic profiles get intuitive results: the chill-lofi profile gets Library Rain / Midnight Coding / Spacewalk Thoughts — exactly what a study-playlist listener would expect — and the rock profile correctly puts Storm Runner first.
- **Closeness scoring works**: the 0.3-energy profile is never recommended metal, and the 0.9-energy profile is never recommended classical.
- **Graceful degradation**: a user whose favorite genre isn't in the catalog (k-pop) still gets sensible mood- and energy-matched suggestions instead of garbage.
- The diversity penalty visibly works — with honest limits: it demotes LoRoom's second lofi track from #4 to #5 in the chill-lofi list (−0.75 artist, −0.30 genre), and at `--k 4` it actually changes membership (Coffee Shop Stories replaces Focus Flow). But with only 20 songs there are often no close substitutes, so at k=5 it usually reorders rather than excludes — Neon Echo still holds two of five sad-banger slots, just with a visibly docked score.

---

## 6. Limitations and Bias

The clearest weakness came from the **conflicted profile experiment** (genre=edm, mood=sad, energy=0.95): the system's #1 pick was *Bassline Horizon* — a **euphoric festival anthem** — for a user who asked for sad music. My first explanation ("a genre match (+2.0) simply outbids a mood match (+1.0)") turned out to be **wrong** when I re-checked the point breakdowns: the sad track (*Neon Tears*) actually *ties* on categorical points (related genre +1.0 plus mood +1.0 = 2.0), and the euphoric track wins entirely on energy closeness (+0.24) and popularity (+0.06). The deeper bias is in the data: this catalog associates sadness with low energy, so a "sad banger" request can't be served faithfully, and the energy and popularity rules quietly resolve the conflict toward the crowd-pleaser. (Doubling the mood weight *would* flip the result — the weight asymmetry is real — but it wasn't the mechanism that decided this run.) Second, high-energy, high-popularity tracks like *Gym Hero* and *Bassline Horizon* appear in the top 5 of **half** the profiles tested — precisely the three with energy targets of 0.9+ — because a high energy target plus the popularity nudge rewards the same bangers regardless of genre. Third, the catalog itself is biased: lofi has three songs while most genres have one, so a "rock" fan's list is 80% not-rock after the single rock song is used up. Finally, users with no strong preferences (the neutral profile) get scores clustered within ~0.2 points, so their ranking is decided by "mid-ness" with tiny factors breaking near-ties — removing popularity entirely only swaps ranks #2 and #3 — meaning the least decisive users get the least meaningful ordering.

---

## 7. Evaluation Process

I tested seven profiles — three realistic (`high_energy_pop`, `chill_lofi`, `deep_intense_rock`), three adversarial (`conflicted_sad_banger` with clashing mood/energy, `unknown_genre` asking for k-pop which isn't in the catalog, and `perfectly_neutral` with no genre/mood and all numeric targets at 0.5), and one added after review to exercise the advanced attributes (`vintage_instrumental` with instrumentalness and release-decade targets). I also ran a weight-shift experiment (`energy_experiment` mode: genre halved, energy doubled). Full terminal outputs below.

### high_energy_pop (genre=pop, mood=happy, energy=0.9, danceability=0.85)

```
1     Sunrise City             Neon Echo        pop        happy        5.07
      why: genre match: pop (+2.0); mood match: happy (+1.0); energy 0.82 vs target 0.90
           (+1.38); danceability 0.79 vs target 0.85 (+0.47); popularity 72/100 (+0.22)
2     Gym Hero                 Max Pulse        pop        intense      4.18
      why: genre match: pop (+2.0); energy 0.93 vs target 0.90 (+1.46); danceability 0.88 vs
           target 0.85 (+0.48); popularity 80/100 (+0.24)
3     Rooftop Lights           Indigo Parade    indie pop  happy        3.97
4     Isla Caliente            Rumba Vista      reggaeton  happy        3.17
5     Bassline Horizon         DJ Nova          edm        euphoric     3.16
```

*Why did Sunrise City beat Gym Hero?* Gym Hero is actually **closer to the energy target** (0.93 vs 0.82 against a 0.9 target) and more popular — but Sunrise City's exact mood match (+1.0) outweighs both gaps combined. Under current weights, two categorical matches beat any amount of numeric closeness.

### chill_lofi (genre=lofi, mood=chill, energy=0.3, acousticness=0.8)

```
1     Library Rain             Paper Lanterns   lofi       chill        5.05
2     Midnight Coding          LoRoom           lofi       chill        4.97
3     Spacewalk Thoughts       Orbit Bloom      ambient    chill        4.04
4     Coffee Shop Stories      Slow Stereo      jazz       relaxed      3.00
5     Focus Flow               LoRoom           lofi       focused      2.97
      why: ... diversity penalty: artist repeated (-0.75); diversity penalty: genre repeated (-0.30)
```

### deep_intense_rock (genre=rock, mood=intense, energy=0.95)

```
1     Storm Runner             Voltline         rock       intense      4.61
2     Gym Hero                 Max Pulse        pop        intense      2.71
3     Iron Cathedral           Forgemind        metal      aggressive   2.66
4     Neon Tears               Neon Echo        synthwave  sad          2.44
5     Bassline Horizon         DJ Nova          edm        euphoric     1.74
```

### conflicted_sad_banger (genre=edm, mood=sad, energy=0.95) — adversarial

```
1     Bassline Horizon         DJ Nova          edm        euphoric     3.74
      why: genre match: edm (+2.0); energy 0.94 vs target 0.95 (+1.48); popularity 85/100 (+0.26)
2     Neon Tears               Neon Echo        synthwave  sad          3.44
      why: related genre: synthwave ~ edm (+1.0); mood match: sad (+1.0); energy 0.78 vs target
           0.95 (+1.25); popularity 66/100 (+0.20)
3     Gym Hero                 Max Pulse        pop        intense      2.71
4     Isla Caliente            Rumba Vista      reggaeton  happy        2.64
5     Sunrise City             Neon Echo        pop        happy        1.77
```

### unknown_genre (genre=k-pop, mood=happy, energy=0.7) — adversarial

```
1     Rooftop Lights           Indigo Parade    indie pop  happy        2.61
2     Sunrise City             Neon Echo        pop        happy        2.54
3     Isla Caliente            Rumba Vista      reggaeton  happy        2.48
4     Concrete Poetry          MC Verse         hip hop    confident    1.70
5     Sunday Morning Soul      The Gold Tones   soul       uplifting    1.52
```

### perfectly_neutral (energy=0.5, valence=0.5, danceability=0.5) — adversarial

```
1     Dust Road Home           Clay County      country    nostalgic    2.52
2     Velvet Hours             Amber Lane       r&b        romantic     2.49
3     Midnight Coding          LoRoom           lofi       chill        2.48
4     Library Rain             Paper Lanterns   lofi       chill        2.34
5     Coffee Shop Stories      Slow Stereo      jazz       relaxed      2.33
```

### vintage_instrumental (genre=classical, mood=calm, energy=0.2, instrumentalness=0.95, release_decade=1980)

```
1     Moonlight Study No. 3    Elena Voss       classical  calm         5.54
      why: genre match: classical (+2.0); mood match: calm (+1.0); energy 0.15 vs target 0.20
           (+1.42); instrumentalness 0.95 vs target 0.95 (+0.50); era 1980s vs target 1980s
           (+0.50); popularity 40/100 (+0.12)
2     Spacewalk Thoughts       Orbit Bloom      ambient    chill        3.21
3     Library Rain             Paper Lanterns   lofi       chill        3.00
4     Focus Flow               LoRoom           lofi       focused      2.95
5     Coffee Shop Stories      Slow Stereo      jazz       relaxed      2.17
```

### Comparing the profiles

- **high_energy_pop vs chill_lofi:** completely disjoint top-5 lists — the pop profile's list is all high-energy danceable tracks, the lofi profile's is all low-energy acoustic ones. This makes sense: their energy targets (0.9 vs 0.3) sit on opposite ends, so the closeness rule rewards opposite halves of the catalog, and genre anchors do the rest.
- **deep_intense_rock vs conflicted_sad_banger:** despite asking for different genres *and* different moods, they share Gym Hero and Bassline Horizon. Both profiles want 0.95 energy, and once each profile's single true genre match runs out, the same high-energy/high-popularity songs fill the tail of both lists. That's the dataset imbalance showing through.
- **high_energy_pop vs unknown_genre:** the k-pop user gets a *happier* list than the pop user (top 3 all mood=happy) but with much lower scores (2.6 vs 5.1). With no genre to anchor on, mood becomes the primary signal — reasonable fallback behavior, but the low scores reveal the system is guessing.
- **perfectly_neutral vs everyone:** the neutral user's scores span only 2.33–2.52. When nothing differentiates songs, the ranking is decided by "mid-ness," and factors as small as the popularity nudge break the near-ties (removing popularity swaps ranks #2 and #3) — evidence that this system serves decisive users far better than undecided ones.
- **vintage_instrumental vs chill_lofi:** both favor quiet, acoustic-leaning tracks, but the era and instrumentalness targets completely change the winner: Moonlight Study No. 3 — which never appears for chill_lofi — wins by 2.3 points as the only exact classical match with a perfect 1980s-era and instrumentalness fit, while the 2020s lofi tracks that dominate chill_lofi lose most of their era points (40 years off target). This is the advanced attributes doing real work.

**What surprised me:** the sad-banger result (a euphoric #1 for a sad user), and how often Gym Hero appears — it shows up for the pop, rock, *and* edm profiles because all three want 0.9+ energy, and "high energy + popular" pays off regardless of genre.

### Weight-shift experiment (genre ÷2, energy ×2)

In `energy_experiment` mode, chill_lofi's #5 changed from Focus Flow (lofi) to **Moonlight Study No. 3 (classical)** — the energy emphasis reached across genre lines to surface a quiet piano piece. Gym Hero fell from #2 to #4 for the pop profile (its genre advantage was halved and mood-matching songs caught up). The lists got more genre-diverse but *less* taste-anchored — different, not clearly better. Sunrise City stayed #1 for pop under both weightings, which suggests the top pick is robust but the tail of the list is very weight-sensitive.

---

## 8. Future Work / Ideas for Improvement

1. **Treat a stated mood as a constraint, not just a bonus** — the sad-banger experiment showed that additive scoring quietly resolves conflicting preferences toward high-energy crowd-pleasers (energy closeness and popularity broke the tie, not genre). Capping or vetoing mood-mismatched songs, or letting the user say which preference dominates, would keep a "sad" query from returning euphoric anthems.
2. **Normalize for catalog imbalance** — score songs relative to how many candidates share their genre, so one rock song doesn't guarantee 4 off-genre picks for rock fans.
3. **Add lightweight collaborative signals** — even simulated likes/skips from a few fake users would enable discovery beyond the user's stated taste and soften the filter bubble.

---

## 9. Personal Reflection

My biggest learning moment came in two stages. First, the conflicted profile returned a euphoric festival track to a user who asked for sad music — I had written the weights myself, they all looked reasonable individually, and the system still produced an emotionally wrong answer. Second, and more humbling: my *explanation* of that failure was also wrong. I confidently wrote "genre outbids mood," and an adversarial re-check of the point breakdowns showed the categorical points actually tied — energy closeness and popularity decided the winner. If even the person who wrote the dozen weights can misread why their own 20-song system did something, real teams auditing billion-parameter recommenders have no chance without rigorous, skeptical verification of every explanation.

AI tools accelerated everything — expanding the dataset, drafting the scoring function, generating adversarial profiles I wouldn't have thought of (the all-0.5 neutral user was more revealing than my hand-picked ones). But I had to double-check them constantly: I verified the CSV row count and types myself, made the tests fail before trusting the implementation, and ran an adversarial review pass over my own claims — which caught the misattributed bias story above, three "advanced" attributes that weren't actually wired into scoring yet, and two overstated experiment write-ups. The one thing AI couldn't do was tell me whether a ranking *felt* right — judging whether Coffee Shop Stories belongs in a lofi list required my own ears and taste.

What surprised me most is how little machinery it takes to *feel* like a real recommender: 20 rows, a dozen weights, and a sort — and the output already exhibits filter bubbles, popularity bias, and cold-start behavior that we usually attribute to billion-user systems. If I extended this, I'd add the simulated collaborative-filtering layer to see how behavior data and content data disagree about the same user.
