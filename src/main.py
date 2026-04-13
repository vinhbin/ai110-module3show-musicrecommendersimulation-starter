"""Command line runner for the Music Recommender Simulation."""

from tabulate import tabulate

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


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")

    for name, prefs in PROFILES.items():
        print_recs(name, recommend_songs(prefs, songs, k=5))

    print("\n--- With diversity penalty (artist -0.60, genre -0.30) ---")
    for name, prefs in PROFILES.items():
        print_recs(f"{name} [diverse]", recommend_songs(prefs, songs, k=5, diversity=True))


if __name__ == "__main__":
    main()
