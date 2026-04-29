"""Command line runner for the Music Recommender Simulation.

Usage
-----
Standard mode (original transparent scorer):
    python -m src.main

Agentic mode (plan→recommend→critique→refine→finalize loop):
    python -m src.main --agent

The --agent flag runs the same four evaluation profiles through the agentic
loop defined in src/agent.py, which prints every intermediate reasoning step
so the full decision trace is visible.
"""

import argparse
import sys
import os

from tabulate import tabulate

# Support both `python src/main.py` and `python -m src.main`
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs


PROFILES = {
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


def print_recs(label: str, recs) -> None:
    print(f"\n=== {label} ===")
    rows = []
    for rank, (song, score, reasons) in enumerate(recs, start=1):
        reason_str = ", ".join(reasons) if reasons else "no matching signals"
        rows.append([rank, song["title"], song["artist"], f"{score:.2f}", reason_str])
    print(tabulate(
        rows,
        headers=["#", "Title", "Artist", "Score", "Reasons (with contributions)"],
        tablefmt="github",
    ))


def run_standard(songs) -> None:
    """Original transparent scorer — unchanged from prior phases."""
    for name, prefs in PROFILES.items():
        print_recs(name, recommend_songs(prefs, songs, k=5))

    print("\n--- With diversity penalty (artist -0.60, genre -0.30) ---")
    for name, prefs in PROFILES.items():
        print_recs(f"{name} [diverse]", recommend_songs(prefs, songs, k=5, diversity=True))


def run_agent_mode(songs) -> None:
    """Agentic loop — plan→recommend→critique→refine→finalize for each profile."""
    from agent import run_agent

    print("\n" + "#" * 70)
    print("  VIBEFINDER AGENT MODE")
    print("  Each profile runs a 5-step agentic loop.")
    print("  Intermediate reasoning is printed at every step.")
    print("#" * 70)

    all_results = {}
    for name, prefs in PROFILES.items():
        final_recs = run_agent(name, prefs, songs, k=5)
        all_results[name] = final_recs

    # Print final tabulated output for all profiles after all agent traces.
    print("\n\n" + "=" * 70)
    print("  FINAL RECOMMENDATIONS (agent mode)")
    print("=" * 70)
    for name, recs in all_results.items():
        print_recs(f"{name} [agent]", recs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VibeFinder Music Recommender"
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help=(
            "Run the agentic loop (plan→recommend→critique→refine→finalize) "
            "instead of the standard scorer."
        ),
    )
    args = parser.parse_args()

    # Resolve songs.csv relative to this file so both invocation styles work.
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(data_path)
    print(f"Loaded {len(songs)} songs.")

    if args.agent:
        run_agent_mode(songs)
    else:
        run_standard(songs)


if __name__ == "__main__":
    main()
