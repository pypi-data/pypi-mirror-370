# hockey_scraper/__init__.py
"""
Hockey Scraper - A comprehensive Python package for scraping hockey data
"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

# Import main functions for easy access
from nhl_scraper.src.leagues.nhl.pipeline import (
    scrape_teams,
    scrape_schedule, 
    scrape_roster,
    scrape_team_stats,
    scrape_game,
    scrape_shifts,
    scrape_game_
)

from .src.leagues.nhl.analyzing import (
    seconds_matrix,
    strengths_by_second,
    toi_by_strength_all,
    shared_toi_teammates_by_strength,
    shared_toi_opponents_by_strength,
    combo_toi_by_strength,
    combo_shot_metrics_by_strength
)

__all__ = [
    "__version__",
    "scrape_teams",
    "scrape_schedule", 
    "scrape_roster",
    "scrape_team_stats", 
    "scrape_game",
    "scrape_shifts",
    "scrape_game_",
    "seconds_matrix",
    "strengths_by_second", 
    "toi_by_strength_all",
    "shared_toi_teammates_by_strength",
    "shared_toi_opponents_by_strength",
    "combo_toi_by_strength",
    "combo_shot_metrics_by_strength"
]