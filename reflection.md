# Reflection

## Phase 4 profile comparisons

- **High-Energy Pop vs Chill Lofi:** the rankings are completely disjoint,
  which is the reassuring case. Genre alone gives each profile its own top-5.
- **Deep Intense Rock vs High-Energy Pop:** both profiles want high energy,
  but the top-5s overlap only on second-tier items (Iron Resolve, Gym Hero).
  Genre is doing the heavy lifting — without it, the two profiles would blur.
- **Deep Intense Rock vs Adversarial (pop/sad/0.9):** the adversarial list is
  dominated by pop tracks that happen to have high energy, since no song has
  mood=sad. The system has no way to say "we couldn't honor your mood" — it
  just silently ranks on the remaining two signals.

## Biggest learning moment

Watching the weight-shift experiment flip the ranking. Dropping genre from
1.5 to 0.75 and doubling the energy term pushed Broken Clocks from rank 2 to
rank 5 on the "Deep Intense Rock" profile. Three numbers decided what a user
would see — and changing them by a single multiplier rearranged the entire
top-5. That's the whole thesis of recommender bias made concrete.

## Where AI helped vs where I had to check

AI sped up scaffolding — CSV parsing, sort-by-score boilerplate, markdown
tables — all low-risk things that just needed to be right. Where I had to
push back: any time AI proposed "smart" defaults (e.g., normalizing scores,
adding fallback values, hiding the mood-miss in the adversarial case). Those
were decisions about the system's *behavior*, not its plumbing, and the
right call depended on what I wanted the system to reveal vs conceal.

## What surprised me about simple algorithms

That three arithmetic rules produce rankings indistinguishable from
"intelligent" behavior on the well-formed profiles. The top song for each of
High-Energy Pop, Chill Lofi, and Deep Intense Rock looked like something a
real app would pick. No embeddings, no neural network, no training — just
three weights and a sort. The intelligence is in the weights, and the
weights are a human judgment call, not a learned artifact.

## What I'd try next

Use the unused CSV columns (tempo_bpm, valence, acousticness) instead of
leaving 4 of 10 fields inert. Then add a diversity penalty so one artist
can't dominate a top-5. Finally, make the system *announce* when a requested
signal (mood, genre) has zero catalog matches rather than silently dropping
it — that single change would have prevented the adversarial case from being
misleading.

---

## Phase 5 — Agentic Extension

### Limitations and biases

The agent can detect two specific failure modes (artist monopoly, absent
mood) but is blind to everything else: it does not detect genre monopolies
beyond the threshold, does not notice when the top result's score is
dominated by a single signal (e.g., pure genre match with no mood/energy
contribution), and does not adapt its reasoning to the content of the songs
themselves — only to the structure of the result list and the catalog counts.

The 20-song catalog constrains what the agent can mechanically achieve. With
only 4 lofi songs (all by LoRoom or Paper Lanterns) and only 3 pop songs,
the agent can reduce a 3-artist monopoly to 2 but cannot reach 1 without
discarding genre-matching songs entirely. Any evaluation of the agent must
be interpreted in light of this catalog-size ceiling.

### Misuse risks and mitigations

The WARNING injected for an absent mood is plain text — it could be
suppressed by a developer who only parses the tabulated output rows and
ignores the FINALIZE summary. A more robust mitigation would be to add a
structured field (e.g., `"mood_satisfied": false`) to a machine-readable
output format so downstream consumers cannot accidentally ignore it.

The agent's refinement logic is single-round. A malicious or careless
integrator could rely on the agent having "fixed" the monopoly and not check
the final artist-spread metric. The evaluation harness (test_agent.py)
checks this post-hoc to guard against that assumption.

### Surprises during reliability testing

The Chill Lofi profile was the most instructive case. The baseline scorer
returns LoRoom 3 times out of 5 (Focus Flow, Pulse Train, Midnight Coding)
because all three score above 4.99 on the extended signals. After the
agent's critique triggers diversity and re-runs, LoRoom drops to 2
appearances — but mood coverage *improves* from 3/5 to 4/5 because Arctic
Wind (mood=chill, a non-lofi song by Pale Summit) rises into the list now
that Pulse Train and Focus Flow are penalized. The diversity fix and the
mood improvement happened together, which was not predicted at design time.

The Deep Intense Rock profile revealed that the PLAN step's genre-thinness
check (<=2 rock songs) pre-empted the need for a post-hoc refine. Diversity
was already active when CRITIQUE ran, so CRITIQUE detected the monopoly but
REFINE correctly took no action — "no action taken" is the right output
when the already-active setting is the best available fix.

### AI collaboration: one helpful suggestion, one flawed one

**Helpful:** during the design of the critique step, the assistant suggested
checking catalog-level mood counts *before* scoring rather than only after,
so the agent can tell in PLAN whether a mood miss is structurally inevitable
(zero catalog matches) vs coincidental (songs exist but scored poorly). This
distinction is what allows the adversarial profile to get a WARNING in PLAN
rather than only a CRITIQUE note — making the reasoning trace earlier and
more useful to a reader.

**Flawed:** the assistant initially proposed setting `max_artist_count <= 1`
as the pass criterion in the test harness — asserting that the diversity
penalty would fully eliminate all monopolies. This is incorrect for a
20-song catalog: the three LoRoom songs score 5.95, 5.11, and 4.99 against
the Chill Lofi profile. After the artist penalty (−0.60) is applied to the
second and third appearances, they score 5.35 and 4.21 — both still rank in
the top-5 because no other non-LoRoom song scores higher than 4.58. Changing
the threshold to `<= 2` (and documenting why) was the correct fix, and this
is a meaningful difference: the flawed threshold would have caused four of
eight evaluation checks to fail even though the agent was behaving exactly
as designed.
