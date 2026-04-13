"""Command line runner for the Music Recommender Simulation."""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")

    user_prefs = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.88,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for song, score, reasons in recommendations:
        print(f"{song['title']} by {song['artist']} - Score: {score:.2f}")
        print(f"  Because: {', '.join(reasons) if reasons else 'no matching signals'}")
        print()


if __name__ == "__main__":
    main()
