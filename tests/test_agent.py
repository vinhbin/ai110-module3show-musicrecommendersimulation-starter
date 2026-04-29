"""Evaluation harness: agent vs baseline on all 4 profiles.

Run with:
    pytest tests/test_agent.py -v

Or for the printed summary table only:
    python tests/test_agent.py

Pass/fail criteria per profile:

  1. High-Energy Pop     — agent must surface >= 1 mood='happy' song in top-5
                           AND top artist appears <= 2 times (diversity reduces
                           but cannot eliminate monopoly in a 20-song catalog).
  2. Chill Lofi          — agent must surface >= 1 mood='chill' song in top-5
                           AND top artist appears <= 2 times.
  3. Deep Intense Rock   — agent must surface >= 1 mood='intense' song in top-5
                           AND top artist appears <= 2 times.
  4. Adversarial sad     — agent must emit a WARNING flag (mood absent from
                           catalog) — checked via the FINALIZE step output.
                           Artist count <= 2 (same threshold).

Metrics captured per profile:
  - mood_coverage   : fraction of top-5 songs matching requested mood
  - artist_spread   : 1 - (max_artist_count / k)   [1.0 = fully diverse]
  - monopoly_broken : bool, was a monopoly present in baseline but absent in agent?
"""

from __future__ import annotations

import io
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import pytest

# ---------------------------------------------------------------------------
# Path setup so tests can import from src/ regardless of invocation style
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from recommender import load_songs, recommend_songs  # noqa: E402
from agent import run_agent, _dominant_artist, _mood_hit_count  # noqa: E402

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

DATA_PATH = os.path.join(REPO_ROOT, "data", "songs.csv")

PROFILES: Dict[str, Dict[str, Any]] = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "target_tempo": 125,
        "target_valence": 0.8,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "target_tempo": 75,
        "target_valence": 0.4,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "target_tempo": 145,
        "target_valence": 0.5,
        "likes_acoustic": False,
    },
    "Adversarial (high-energy sad)": {
        "favorite_genre": "pop",
        "favorite_mood": "sad",
        "target_energy": 0.9,
        "target_tempo": 140,
        "target_valence": 0.2,
        "likes_acoustic": False,
    },
}


@pytest.fixture(scope="module")
def songs():
    return load_songs(DATA_PATH)


def _run_baseline(prefs, songs, k=5):
    return recommend_songs(prefs, songs, k=k, diversity=False)


def _run_agent_capture(name, prefs, songs, k=5):
    """Run agent, capture stdout, return (recs, captured_output)."""
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        recs = run_agent(name, prefs, songs, k=k)
    finally:
        sys.stdout = old_stdout
    return recs, buf.getvalue()


def _metrics(recs, requested_mood: str, k: int = 5) -> Dict[str, Any]:
    mood_hits = _mood_hit_count(recs, requested_mood)
    artist_counts: Dict[str, int] = {}
    for song, _, _ in recs:
        a = song.get("artist", "Unknown")
        artist_counts[a] = artist_counts.get(a, 0) + 1
    max_artist = max(artist_counts.values()) if artist_counts else 0
    return {
        "mood_coverage": mood_hits / k if k else 0.0,
        "artist_spread": 1.0 - (max_artist / k) if k else 1.0,
        "max_artist_count": max_artist,
        "mood_hits": mood_hits,
    }


# ---------------------------------------------------------------------------
# Individual profile tests
# ---------------------------------------------------------------------------

class TestHighEnergyPop:
    PROFILE = "High-Energy Pop"

    def test_mood_coverage_agent_vs_baseline(self, songs):
        prefs = PROFILES[self.PROFILE]
        baseline_recs = _run_baseline(prefs, songs)
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)

        base_m = _metrics(baseline_recs, prefs["favorite_mood"])
        agent_m = _metrics(agent_recs, prefs["favorite_mood"])

        # At least 1 mood match expected from agent
        assert agent_m["mood_hits"] >= 1, (
            f"Agent returned no 'happy' songs for {self.PROFILE}. "
            f"Baseline mood_hits={base_m['mood_hits']}, "
            f"Agent mood_hits={agent_m['mood_hits']}"
        )

    def test_no_artist_monopoly(self, songs):
        prefs = PROFILES[self.PROFILE]
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)
        m = _metrics(agent_recs, prefs["favorite_mood"])
        assert m["max_artist_count"] <= 2, (
            f"Artist over-concentration in agent output for {self.PROFILE}: "
            f"max_artist_count={m['max_artist_count']} (threshold: 2)"
        )


class TestChillLofi:
    PROFILE = "Chill Lofi"

    def test_mood_coverage(self, songs):
        prefs = PROFILES[self.PROFILE]
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)
        m = _metrics(agent_recs, prefs["favorite_mood"])
        assert m["mood_hits"] >= 1, (
            f"No 'chill' mood songs in agent top-5 for {self.PROFILE}."
        )

    def test_no_artist_monopoly(self, songs):
        prefs = PROFILES[self.PROFILE]
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)
        m = _metrics(agent_recs, prefs["favorite_mood"])
        assert m["max_artist_count"] <= 2


class TestDeepIntenseRock:
    PROFILE = "Deep Intense Rock"

    def test_mood_coverage(self, songs):
        prefs = PROFILES[self.PROFILE]
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)
        m = _metrics(agent_recs, prefs["favorite_mood"])
        assert m["mood_hits"] >= 1, (
            f"No 'intense' mood songs in agent top-5 for {self.PROFILE}."
        )

    def test_no_artist_monopoly(self, songs):
        prefs = PROFILES[self.PROFILE]
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)
        m = _metrics(agent_recs, prefs["favorite_mood"])
        assert m["max_artist_count"] <= 2


class TestAdversarialSad:
    PROFILE = "Adversarial (high-energy sad)"

    def test_warning_emitted(self, songs):
        """Agent must print a WARNING about the missing mood in FINALIZE."""
        prefs = PROFILES[self.PROFILE]
        _, output = _run_agent_capture(self.PROFILE, prefs, songs)
        assert "WARNING" in output, (
            "Agent did not emit a WARNING for unsatisfiable mood='sad'."
        )

    def test_mood_absent_acknowledged(self, songs):
        """Agent critique step must detect mood absence."""
        prefs = PROFILES[self.PROFILE]
        _, output = _run_agent_capture(self.PROFILE, prefs, songs)
        assert "MOOD ABSENT" in output or "absent" in output.lower(), (
            "Agent did not acknowledge absent mood in critique output."
        )

    def test_no_artist_monopoly(self, songs):
        prefs = PROFILES[self.PROFILE]
        agent_recs, _ = _run_agent_capture(self.PROFILE, prefs, songs)
        m = _metrics(agent_recs, prefs["favorite_mood"])
        assert m["max_artist_count"] <= 2


# ---------------------------------------------------------------------------
# Printed summary (when run as a script)
# ---------------------------------------------------------------------------

def print_summary(songs):
    print("\n" + "=" * 72)
    print("  AGENT vs BASELINE EVALUATION SUMMARY")
    print("=" * 72)

    total = 0
    passed = 0

    for name, prefs in PROFILES.items():
        mood = prefs["favorite_mood"]
        baseline_recs = _run_baseline(prefs, songs)
        agent_recs, agent_output = _run_agent_capture(name, prefs, songs)

        base_m = _metrics(baseline_recs, mood)
        agent_m = _metrics(agent_recs, mood)

        base_dominant = _dominant_artist(baseline_recs)
        agent_dominant = _dominant_artist(agent_recs)
        monopoly_broken = (base_dominant is not None) and (agent_dominant is None)

        mood_catalog = sum(1 for s in songs if s.get("mood") == mood)

        print(f"\n  Profile: {name}")
        print(f"    Requested mood       : {mood!r} ({mood_catalog} catalog songs)")
        print(f"    Baseline mood_hits   : {base_m['mood_hits']}/5  "
              f"(coverage {base_m['mood_coverage']:.0%})")
        print(f"    Agent    mood_hits   : {agent_m['mood_hits']}/5  "
              f"(coverage {agent_m['mood_coverage']:.0%})")
        print(f"    Baseline max_artist  : {base_m['max_artist_count']} "
              f"({'MONOPOLY' if base_dominant else 'OK'})")
        print(f"    Agent    max_artist  : {agent_m['max_artist_count']} "
              f"({'MONOPOLY' if agent_dominant else 'OK'})")
        print(f"    Monopoly broken      : {'YES' if monopoly_broken else 'NO'}")

        if mood_catalog == 0:
            has_warning = "WARNING" in agent_output
            print(f"    Warning emitted      : {'YES' if has_warning else 'NO'}")

        # Determine pass/fail for this profile
        profile_tests = []

        if mood_catalog > 0:
            mood_pass = agent_m["mood_hits"] >= 1
            profile_tests.append(("mood coverage >= 1", mood_pass))
        else:
            warn_pass = "WARNING" in agent_output
            profile_tests.append(("warning emitted", warn_pass))

        spread_pass = agent_m["max_artist_count"] <= 2
        profile_tests.append(("artist count <= 2 (diversity reduced)", spread_pass))

        for desc, result in profile_tests:
            total += 1
            status = "PASS" if result else "FAIL"
            if result:
                passed += 1
            print(f"      [{status}] {desc}")

    print(f"\n  Results: {passed}/{total} checks passed")
    print("=" * 72)


if __name__ == "__main__":
    s = load_songs(DATA_PATH)
    print_summary(s)
