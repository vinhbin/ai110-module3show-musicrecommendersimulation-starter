import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

NUMERIC_FLOAT_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


@dataclass
class Song:
    """Represents a song and its attributes."""
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
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
        }
        scored = [(s, *score_song(prefs, s.__dict__)) for s in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
        }
        _, reasons = score_song(prefs, song.__dict__)
        return "; ".join(reasons) if reasons else "no matching signals"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV, casting numeric fields."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in NUMERIC_FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user prefs. Returns (score, reasons with numeric contributions)."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("favorite_genre"):
        score += 1.5
        reasons.append("genre match (+1.50)")

    if song["mood"] == user_prefs.get("favorite_mood"):
        score += 1.0
        reasons.append("mood match (+1.00)")

    target_energy = user_prefs.get("target_energy")
    if target_energy is not None:
        energy_sim = max(0.0, 1.0 - abs(float(song["energy"]) - float(target_energy)))
        score += energy_sim
        reasons.append(f"energy similarity (+{energy_sim:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, List[str]]]:
    """Score all songs, return top-k as (song, score, reasons)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
