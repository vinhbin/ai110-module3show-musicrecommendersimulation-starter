"""Command line runner for the Music Recommender Simulation.

Runs one or all user profiles through the recommender and prints a ranked,
explained table of recommendations.

Usage:
    python -m src.main                          # all profiles, balanced mode
    python -m src.main --profile chill_lofi    # one profile
    python -m src.main --mode energy_experiment # weight-shift experiment
    python -m src.main --mode genre_first --k 3 --no-diversity
"""

import argparse
import textwrap

try:
    from src.recommender import WEIGHT_PRESETS, load_songs, recommend_songs
except ImportError:  # allows `python src/main.py` too
    from recommender import WEIGHT_PRESETS, load_songs, recommend_songs

# Evaluation profiles (Phase 4): three realistic tastes + three adversarial
# profiles designed to stress the scoring logic.
PROFILES = {
    "high_energy_pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "danceability": 0.85},
    "chill_lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3, "acousticness": 0.8},
    "deep_intense_rock": {"genre": "rock", "mood": "intense", "energy": 0.95},
    # Adversarial: conflicting preferences (sad mood but banger energy).
    "conflicted_sad_banger": {"genre": "edm", "mood": "sad", "energy": 0.95},
    # Adversarial: favorite genre does not exist in the catalog.
    "unknown_genre": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
    # Adversarial: no categorical anchors, all numeric targets dead center.
    "perfectly_neutral": {"energy": 0.5, "valence": 0.5, "danceability": 0.5},
}


def print_recommendations(name, prefs, recommendations) -> None:
    """Print one profile's ranked recommendations as an ASCII table with reasons."""
    pretty_prefs = ", ".join(f"{key}={value}" for key, value in prefs.items())
    print(f"\n=== Profile: {name} ({pretty_prefs}) ===\n")
    header = f"{'Rank':<5} {'Title':<24} {'Artist':<16} {'Genre':<10} {'Mood':<10} {'Score':>6}"
    print(header)
    print("-" * len(header))
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(
            f"{rank:<5} {song['title']:<24} {song['artist']:<16} "
            f"{song['genre']:<10} {song['mood']:<10} {score:>6.2f}"
        )
        why = "; ".join(reasons) if reasons else "no strong matches"
        print(textwrap.fill(f"why: {why}", width=95, initial_indent="      ", subsequent_indent="           "))
    print()


def main() -> None:
    """Load the catalog and print recommendations for the selected profile(s)."""
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--profile", choices=sorted(PROFILES), help="run a single profile (default: all)")
    parser.add_argument("--mode", choices=sorted(WEIGHT_PRESETS), default="balanced", help="scoring strategy")
    parser.add_argument("--k", type=int, default=5, help="number of recommendations")
    parser.add_argument("--no-diversity", action="store_true", help="disable the diversity penalty")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring mode: {args.mode}")

    selected = {args.profile: PROFILES[args.profile]} if args.profile else PROFILES
    for name, prefs in selected.items():
        recommendations = recommend_songs(
            prefs, songs, k=args.k, mode=args.mode, diversity=not args.no_diversity
        )
        print_recommendations(name, prefs, recommendations)


if __name__ == "__main__":
    main()
