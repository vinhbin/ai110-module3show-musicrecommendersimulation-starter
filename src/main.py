"""Command line runner for the Music Recommender Simulation."""

from recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.85},
    "Chill Lofi": {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.35},
    "Deep Intense Rock": {"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.9},
    "Adversarial (high-energy sad)": {"favorite_genre": "pop", "favorite_mood": "sad", "target_energy": 0.9},
}


def print_recs(label: str, recs) -> None:
    print(f"\n=== {label} ===")
    for song, score, reasons in recs:
        reason_str = ", ".join(reasons) if reasons else "no matching signals"
        print(f"  {song['title']} by {song['artist']} - {score:.2f}  [{reason_str}]")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")

    for name, prefs in PROFILES.items():
        print_recs(name, recommend_songs(prefs, songs, k=5))


if __name__ == "__main__":
    main()
