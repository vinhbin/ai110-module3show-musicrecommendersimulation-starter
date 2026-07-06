"""Core logic for the Music Recommender Simulation.

A content-based, weighted-score recommender:
- load_songs: read the catalog CSV, converting numeric columns to numbers
- score_song: judge ONE song against user preferences (score + reasons)
- recommend_songs: run score_song over the whole catalog and rank the top k

Scoring modes (WEIGHT_PRESETS) implement a simple Strategy pattern: each mode
is a named set of weights that score_song applies to the same rules.
"""

import csv
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

# CSV columns that must be converted from strings to numbers for scoring math.
NUMERIC_FIELDS = (
    "energy",
    "tempo_bpm",
    "valence",
    "danceability",
    "acousticness",
    "popularity",
    "release_decade",
    "instrumentalness",
    "liveness",
)

# Genres close enough to earn partial credit (a soft edge on the filter bubble).
RELATED_GENRES = {
    "pop": {"indie pop", "synthwave", "edm", "r&b"},
    "indie pop": {"pop", "indie folk"},
    "lofi": {"ambient", "jazz", "classical"},
    "ambient": {"lofi", "classical"},
    "jazz": {"lofi", "soul", "r&b"},
    "rock": {"metal", "synthwave"},
    "metal": {"rock"},
    "edm": {"pop", "synthwave", "reggaeton"},
    "synthwave": {"edm", "pop", "rock"},
    "r&b": {"soul", "pop", "jazz"},
    "soul": {"r&b", "jazz"},
    "hip hop": {"r&b", "reggaeton"},
    "reggaeton": {"hip hop", "edm"},
    "country": {"indie folk"},
    "indie folk": {"country", "indie pop"},
    "classical": {"ambient", "lofi"},
}

# Strategy pattern: each scoring mode is just a different set of weights
# applied to the same scoring rules. Switch modes without touching the logic.
WEIGHT_PRESETS: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 2.0,
        "related_genre": 1.0,
        "mood": 1.0,
        "mood_tag": 0.5,
        "energy": 1.5,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
        "instrumentalness": 0.5,
        "liveness": 0.3,
        "release_decade": 0.5,
        "popularity": 0.3,
    },
    "genre_first": {
        "genre": 3.5,
        "related_genre": 1.5,
        "mood": 0.5,
        "mood_tag": 0.25,
        "energy": 0.5,
        "valence": 0.25,
        "danceability": 0.25,
        "acousticness": 0.25,
        "instrumentalness": 0.25,
        "liveness": 0.15,
        "release_decade": 0.25,
        "popularity": 0.2,
    },
    "mood_first": {
        "genre": 0.5,
        "related_genre": 0.25,
        "mood": 2.5,
        "mood_tag": 1.0,
        "energy": 1.0,
        "valence": 0.75,
        "danceability": 0.5,
        "acousticness": 0.5,
        "instrumentalness": 0.5,
        "liveness": 0.25,
        "release_decade": 0.25,
        "popularity": 0.2,
    },
    "energy_focused": {
        "genre": 0.5,
        "related_genre": 0.25,
        "mood": 0.5,
        "mood_tag": 0.25,
        "energy": 3.0,
        "valence": 0.5,
        "danceability": 1.0,
        "acousticness": 0.5,
        "instrumentalness": 0.5,
        "liveness": 0.25,
        "release_decade": 0.25,
        "popularity": 0.2,
    },
    # Phase 4 experiment: genre halved (2.0 -> 1.0), energy doubled (1.5 -> 3.0).
    "energy_experiment": {
        "genre": 1.0,
        "related_genre": 0.5,
        "mood": 1.0,
        "mood_tag": 0.5,
        "energy": 3.0,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
        "instrumentalness": 0.5,
        "liveness": 0.3,
        "release_decade": 0.5,
        "popularity": 0.3,
    },
}

# Numeric features scored by closeness to the user's target (0.0-1.0 scales).
CLOSENESS_FEATURES = (
    "energy",
    "valence",
    "danceability",
    "acousticness",
    "instrumentalness",
    "liveness",
)

DIVERSITY_ARTIST_PENALTY = 0.75
DIVERSITY_GENRE_PENALTY = 0.3


@dataclass
class Song:
    """Represents a song and its attributes (required by tests)."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences (required by tests)."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Convert this profile to the prefs dict used by the functional API."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "acousticness": 0.8 if self.likes_acoustic else 0.25,
        }


class Recommender:
    """OOP wrapper around the functional scoring core (required by tests)."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for this user, best match first."""
        ranked = recommend_songs(user.to_prefs(), [asdict(s) for s in self.songs], k=k)
        by_id = {song.id: song for song in self.songs}
        return [by_id[row["id"]] for row, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain in one line why a song scored what it did for this user."""
        score, reasons = score_song(user.to_prefs(), asdict(song))
        detail = "; ".join(reasons) if reasons else "no strong matches"
        return f"Score {score:.2f}: {detail}"


def load_songs(csv_path: str) -> List[Dict]:
    """Load the song catalog from a CSV into dicts with real numeric types."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not (row.get("id") or "").strip():
                continue  # tolerate blank/whitespace-only lines
            song = dict(row)
            song["id"] = int(row["id"])
            for field in NUMERIC_FIELDS:
                if song.get(field) not in (None, ""):
                    song[field] = float(song[field])
            songs.append(song)
    return songs


def score_song(
    user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None
) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (score, reasons)."""
    if weights is None:
        weights = WEIGHT_PRESETS[user_prefs.get("mode", "balanced")]

    score = 0.0
    reasons: List[str] = []

    # Genre: full points for an exact match, partial for a related genre.
    pref_genre = str(user_prefs.get("genre", "")).strip().lower()
    song_genre = str(song.get("genre", "")).strip().lower()
    if pref_genre and song_genre:
        if pref_genre == song_genre:
            score += weights["genre"]
            reasons.append(f"genre match: {song_genre} (+{weights['genre']:.1f})")
        elif song_genre in RELATED_GENRES.get(pref_genre, set()):
            score += weights["related_genre"]
            reasons.append(
                f"related genre: {song_genre} ~ {pref_genre} (+{weights['related_genre']:.1f})"
            )

    # Mood: full points for an exact match, partial if it appears in mood_tags.
    pref_mood = str(user_prefs.get("mood", "")).strip().lower()
    song_mood = str(song.get("mood", "")).strip().lower()
    mood_tags = {t.strip().lower() for t in str(song.get("mood_tags", "")).split(";") if t.strip()}
    if pref_mood:
        if pref_mood == song_mood:
            score += weights["mood"]
            reasons.append(f"mood match: {song_mood} (+{weights['mood']:.1f})")
        elif pref_mood in mood_tags:
            score += weights["mood_tag"]
            reasons.append(f"mood tag match: {pref_mood} (+{weights['mood_tag']:.1f})")

    # Numeric features: reward CLOSENESS to the user's target, not magnitude.
    for feature in CLOSENESS_FEATURES:
        target = user_prefs.get(feature)
        value = song.get(feature)
        if target is None or not isinstance(value, (int, float)):
            continue
        closeness = 1.0 - abs(float(target) - float(value))
        points = closeness * weights.get(feature, 0)
        if points > 0:
            score += points
            reasons.append(
                f"{feature} {value:.2f} vs target {float(target):.2f} (+{points:.2f})"
            )

    # Era: reward songs whose release decade is near the user's preferred decade
    # (full credit at an exact match, fading to zero across 50 years).
    target_decade = user_prefs.get("release_decade")
    decade = song.get("release_decade")
    if target_decade is not None and isinstance(decade, (int, float)):
        closeness = 1.0 - min(1.0, abs(float(target_decade) - float(decade)) / 50.0)
        points = closeness * weights.get("release_decade", 0)
        if points > 0:
            score += points
            reasons.append(
                f"era {decade:.0f}s vs target {float(target_decade):.0f}s (+{points:.2f})"
            )

    # Popularity: a small, deliberate popularity bias (documented in the model card).
    popularity = song.get("popularity")
    if isinstance(popularity, (int, float)) and weights.get("popularity", 0) > 0:
        points = (float(popularity) / 100.0) * weights["popularity"]
        score += points
        reasons.append(f"popularity {popularity:.0f}/100 (+{points:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: Optional[str] = None,
    diversity: bool = True,
) -> List[Tuple[Dict, float, List[str]]]:
    """Rank every song with score_song and return the top k as (song, score, reasons)."""
    k = max(0, k)  # negative k is nonsense; both paths below should agree it means "none"
    weights = WEIGHT_PRESETS[mode] if mode else None

    scored = [(song, *score_song(user_prefs, song, weights)) for song in songs]
    # sorted() returns a NEW list (unlike list.sort(), which mutates in place),
    # so the caller's `songs` list is left untouched.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    if not diversity:
        return ranked[:k]

    # Greedy re-rank: each pick penalizes remaining songs that repeat an
    # already-recommended artist or pile onto the same genre.
    picked: List[Tuple[Dict, float, List[str]]] = []
    remaining = list(ranked)
    while remaining and len(picked) < k:
        best_index = 0
        best_adjusted = None
        best_notes: List[str] = []
        for i, (song, score, _) in enumerate(remaining):
            artist_repeats = sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
            genre_repeats = sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
            penalty = (
                DIVERSITY_ARTIST_PENALTY * artist_repeats
                + DIVERSITY_GENRE_PENALTY * max(0, genre_repeats - 1)
            )
            adjusted = score - penalty
            if best_adjusted is None or adjusted > best_adjusted:
                best_index = i
                best_adjusted = adjusted
                best_notes = []
                if artist_repeats:
                    best_notes.append(
                        f"diversity penalty: artist repeated (-{DIVERSITY_ARTIST_PENALTY * artist_repeats:.2f})"
                    )
                if genre_repeats > 1:
                    best_notes.append(
                        f"diversity penalty: genre repeated (-{DIVERSITY_GENRE_PENALTY * (genre_repeats - 1):.2f})"
                    )
        song, _, reasons = remaining.pop(best_index)
        picked.append((song, best_adjusted, reasons + best_notes))
    return picked
