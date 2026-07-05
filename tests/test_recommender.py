from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    load_songs,
    score_song,
    recommend_songs,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Functional API tests (load_songs / score_song / recommend_songs) ---

POP_SONG = {
    "id": 1,
    "title": "Pop Anthem",
    "artist": "Artist A",
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "tempo_bpm": 120.0,
    "valence": 0.9,
    "danceability": 0.8,
    "acousticness": 0.2,
}


def test_load_songs_converts_numeric_fields():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 20
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["popularity"], float)


def test_score_song_rewards_genre_match_with_reason():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    matched_score, reasons = score_song(prefs, POP_SONG)
    other_score, _ = score_song(prefs, dict(POP_SONG, genre="country"))

    assert matched_score > other_score
    assert any("genre" in reason for reason in reasons)


def test_recommend_songs_sorted_and_k():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    recs = recommend_songs(prefs, songs, k=5)

    assert len(recs) == 5
    scores = [score for _, score, _ in recs]
    assert scores == sorted(scores, reverse=True)


def test_diversity_penalty_prefers_new_artists():
    clones = [dict(POP_SONG, id=i, title=f"Clone {i}") for i in range(1, 4)]
    rival = dict(POP_SONG, id=9, title="Rival", artist="Artist B", energy=0.7)
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recs = recommend_songs(prefs, clones + [rival], k=3)
    artists = {song["artist"] for song, _, _ in recs}
    assert "Artist B" in artists
