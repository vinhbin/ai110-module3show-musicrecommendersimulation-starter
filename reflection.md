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
