# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I gave Claude Code (agent mode) the full Challenge 1 upgrade as one multi-step task: expand `data/songs.csv` from 10 to 20 songs covering genres/moods not in the starter file, add 5 advanced attributes not present in the baseline (popularity 0–100, release_decade, detailed mood_tags, instrumentalness, liveness), and update the scoring logic in `src/recommender.py` so all five new attributes actually affect scores (mood-tag partial credit, popularity boost, instrumentalness/liveness closeness, and an era-closeness rule for release decade — exercised by the `vintage_instrumental` profile).

**Prompts used:**

- "Analyze data/songs.csv and suggest which features would be most effective for a simple content-based recommender. Distinguish features where 'closer to target' matters from features where exact match matters."
- "Generate 10 additional songs in valid CSV format keeping the existing headers, covering diverse genres and moods not already present (hip hop, country, classical, metal, edm, r&b, indie folk, reggaeton, soul). Add 5 new advanced columns to ALL rows: popularity (0-100), release_decade, mood_tags (semicolon-separated detailed tags), instrumentalness, liveness. Include at least one 'sad but high-energy' track so I can test conflicting user preferences."
- "Update score_song so mood_tags give partial credit (+0.5) when the exact mood doesn't match, and popularity adds up to +0.3. Keep the reasons list explaining every point earned. Verify the math stays valid: no rule should be able to go negative."

**What did the agent generate or change?**

- `data/songs.csv`: 10 new rows (ids 11–20) and 5 new columns added to all 20 rows.
- `src/recommender.py`: `NUMERIC_FIELDS` for type conversion, mood-tag partial credit, popularity bonus, and the reasons strings for each.
- `tests/test_recommender.py`: four new tests written *before* the implementation (load/convert, genre-match reason, sorted top-k, diversity).
- Commands run: `python -m pytest -v` (before and after), `python -m src.main` per profile.

**What did you verify or fix manually?**

- Verified the CSV shape myself (`20 rows × 15 columns`) instead of trusting the agent's claim, and spot-checked that mood_tags used semicolons (commas would have silently broken the CSV).
- Made the new tests fail first, then pass — the agent's first version of the dataset had a trailing whitespace-only line that would have crashed `int(row["id"])`; we added a blank-row guard in `load_songs` after I caught it.
- Hand-checked two "why" breakdowns against the weight table (Sunrise City 5.07 and Bassline Horizon 3.74) to confirm the printed points summed to the score.
- Ran a second, adversarial AI review pass (four independent reviewers, each finding re-verified by a separate skeptic agent) over the finished project. It caught real problems I had missed: my headline bias explanation ("genre outbids mood") was contradicted by my own printed point breakdowns (the categorical points tied; energy + popularity decided it), three of the five advanced attributes were loaded but not yet wired into scoring, two experiment write-ups overstated what the diversity penalty actually did, and negative `--k` behaved inconsistently between code paths. I fixed all of these and re-verified — the corrected story is in the model card.
- The agent's judgment I overrode: it initially proposed adding tempo closeness to the balanced mode; I kept the recipe smaller so each weight stays explainable.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy pattern** for the scoring modes (Challenge 2) — `balanced`, `genre_first`, `mood_first`, `energy_focused`, `energy_experiment`.

**How did AI help you brainstorm or implement it?**

I asked the AI to brainstorm a design that would let a user switch ranking strategies in `main.py` without duplicating scoring code. It laid out two options: (a) a classic Strategy pattern with a `ScoringStrategy` base class and one subclass per mode, or (b) a lightweight "weights-as-strategy" variant where every mode is just a named dict of weights interpreted by one `score_song` function. We chose (b): the *rules* are identical across modes — only the numbers change — so subclasses would have been ceremony without benefit in a ~250-line module. The AI also pointed out a bonus: the Phase 4 weight-shift experiment becomes just another preset (`energy_experiment`) instead of a code edit, which makes the experiment reproducible from the CLI.

**How does the pattern appear in your final code?**

- `WEIGHT_PRESETS` in [src/recommender.py](src/recommender.py) — the strategy registry (one dict per mode).
- `score_song(user_prefs, song, weights=None)` — the single algorithm parameterized by the chosen strategy.
- `recommend_songs(..., mode=...)` and the `--mode` flag in [src/main.py](src/main.py) — where the strategy is selected at runtime.
