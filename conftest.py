"""pytest configuration: make both `src.*` and bare module imports work."""
import sys
import os

# Add repo root so `from src.recommender import ...` works.
sys.path.insert(0, os.path.dirname(__file__))
# Add src/ so `from recommender import ...` (used by agent and main) works.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
