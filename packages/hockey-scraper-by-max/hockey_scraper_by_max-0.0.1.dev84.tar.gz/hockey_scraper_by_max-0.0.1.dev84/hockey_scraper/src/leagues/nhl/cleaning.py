from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import polars as pl



def clean_teams_data(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL teams data with standardized transformations.

    Args:
        data: Raw teams data from scraping functions

    Returns:
        List[Dict]: Cleaned teams data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Flatten nested firstSeason data
        if isinstance(cleaned_record.get("firstSeason"), dict):
            cleaned_record["firstSeasonId"] = cleaned_record["firstSeason"].get("id")
            del cleaned_record["firstSeason"]

        # Handle lastSeason (might be None)
        if isinstance(cleaned_record.get("lastSeason"), dict):
            cleaned_record["lastSeasonId"] = cleaned_record["lastSeason"].get("id")
            del cleaned_record["lastSeason"]
        elif cleaned_record.get("lastSeason") is None:
            cleaned_record["lastSeasonId"] = None
            if "lastSeason" in cleaned_record:
                del cleaned_record["lastSeason"]

        # Standardize team abbreviations (if available)
        if "triCode" in cleaned_record:
            cleaned_record["teamAbbr"] = cleaned_record["triCode"].upper()

        # Add derived fields
        cleaned_record["isActive"] = cleaned_record.get("lastSeasonId") is None

        # Parse scraping timestamp
        if "scrapedOn" in cleaned_record:
            try:
                cleaned_record["scrapedOnParsed"] = datetime.fromisoformat(
                    cleaned_record["scrapedOn"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                cleaned_record["scrapedOnParsed"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_schedule_data(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL schedule data with standardized transformations.

    Args:
        data: Raw schedule data from scraping functions

    Returns:
        List[Dict]: Cleaned schedule data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse game dates
        for date_field in ["gameDate", "startTimeUTC"]:
            if date_field in cleaned_record:
                try:
                    cleaned_record[f"{date_field}Parsed"] = datetime.fromisoformat(
                        cleaned_record[date_field].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    cleaned_record[f"{date_field}Parsed"] = None

        # Flatten team data if nested
        for team_type in ["homeTeam", "awayTeam"]:
            if isinstance(cleaned_record.get(team_type), dict):
                team_data = cleaned_record[team_type]
                for key, value in team_data.items():
                    cleaned_record[f"{team_type}_{key}"] = value

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_roster_data(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL roster data with standardized transformations.

    Args:
        data: Raw roster data from scraping functions

    Returns:
        List[Dict]: Cleaned roster data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse birth date
        if "birthDate" in cleaned_record:
            try:
                cleaned_record["birthDateParsed"] = datetime.strptime(
                    cleaned_record["birthDate"], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                cleaned_record["birthDateParsed"] = None

        # Standardize height/weight units
        if "heightInInches" in cleaned_record:
            try:
                cleaned_record["heightCm"] = int(cleaned_record["heightInInches"] * 2.54)
            except (ValueError, TypeError):
                cleaned_record["heightCm"] = None

        if "weightInPounds" in cleaned_record:
            try:
                cleaned_record["weightKg"] = round(cleaned_record["weightInPounds"] * 0.453592, 1)
            except (ValueError, TypeError):
                cleaned_record["weightKg"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_standings_data(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL standings data with standardized transformations.

    Args:
        data: Raw standings data from scraping functions

    Returns:
        List[Dict]: Cleaned standings data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Calculate additional metrics
        if all(k in cleaned_record for k in ["wins", "losses", "overtimeLosses"]):
            cleaned_record["totalGames"] = (
                cleaned_record["wins"]
                + cleaned_record["losses"]
                + cleaned_record.get("overtimeLosses", 0)
            )

            if cleaned_record["totalGames"] > 0:
                cleaned_record["winPercentage"] = round(
                    cleaned_record["wins"] / cleaned_record["totalGames"], 3
                )

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_team_stats_data(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL team stats data with standardized transformations.

    Args:
        data: Raw team stats data from scraping functions

    Returns:
        List[Dict]: Cleaned team stats data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse date fields
        if "date" in cleaned_record:
            try:
                cleaned_record["dateParsed"] = datetime.fromisoformat(
                    cleaned_record["date"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                cleaned_record["dateParsed"] = None

        # Calculate additional metrics if available
        if "goalsFor" in cleaned_record and "goalsAgainst" in cleaned_record:
            cleaned_record["goalDifference"] = (
                cleaned_record["goalsFor"] - cleaned_record["goalsAgainst"]
            )

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_draft_data(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL draft data with standardized transformations.

    Args:
        data: Raw draft data from scraping functions

    Returns:
        List[Dict]: Cleaned draft data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse draft date
        if "draftDate" in cleaned_record:
            try:
                cleaned_record["draftDateParsed"] = datetime.strptime(
                    cleaned_record["draftDate"], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                cleaned_record["draftDateParsed"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_records_draft(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL draft records data with standardized transformations.

    Args:
        data: Raw draft records data from scraping functions

    Returns:
        List[Dict]: Cleaned draft records data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse player birth date
        if "birthDate" in cleaned_record:
            try:
                cleaned_record["birthDateParsed"] = datetime.strptime(
                    cleaned_record["birthDate"], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                cleaned_record["birthDateParsed"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_records_team_draft_history(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL team draft history data with standardized transformations.

    Args:
        data: Raw team draft history data from scraping functions

    Returns:
        List[Dict]: Cleaned team draft history data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse draft year
        if "draftYear" in cleaned_record:
            try:
                cleaned_record["draftYearParsed"] = int(cleaned_record["draftYear"])
            except (ValueError, TypeError):
                cleaned_record["draftYearParsed"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data


def clean_player(data: List[Dict]) -> List[Dict]:
    """
    Clean NHL player data with standardized transformations.

    Args:
        data: Raw player data from scraping functions

    Returns:
        List[Dict]: Cleaned player data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Parse player birth date
        if "birthDate" in cleaned_record:
            try:
                cleaned_record["birthDateParsed"] = datetime.strptime(
                    cleaned_record["birthDate"], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                cleaned_record["birthDateParsed"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data


def apply_universal_cleaning(data: List[Dict]) -> List[Dict]:
    """
    Apply universal cleaning rules that apply to all data types.

    Args:
        data: Any raw data from scraping functions

    Returns:
        List[Dict]: Universally cleaned data
    """
    cleaned_data = []

    for record in data:
        cleaned_record = record.copy()

        # Remove null/empty string values (optional)
        cleaned_record = {k: v for k, v in cleaned_record.items() if v is not None and v != ""}

        # Standardize string fields
        for key, value in cleaned_record.items():
            if isinstance(value, str):
                cleaned_record[key] = value.strip()

        cleaned_data.append(cleaned_record)

    return cleaned_data

def clean_api_events_data(
    data: List[Dict],
    gameType: Union[str, int],
    homeData: Dict,
    awayData: Dict,
) -> List[Dict]:
    """
    Clean NHL API events data with standardized transformations.

    Args:
        data: Raw API events data from scraping functions
        gameType: 2 = regular season, 3 = playoffs, 1 = preseason
        homeData: Dict with home team info (must include 'id' and 'abbrev')
        awayData: Dict with away team info (must include 'id' and 'abbrev')

    Returns:
        List[Dict]: Cleaned and flattened API events data
    """
    cleaned_data = []
    

    # Initialize SOG and score trackers
    home_sog = away_sog = home_score = away_score = 0

    # Extract team IDs and abbreviations
    homeId = homeData.get("id")
    awayId = awayData.get("id")
    homeAbbrev = homeData.get("abbrev")
    awayAbbrev = awayData.get("abbrev")
    home_away_dict = {homeId: homeAbbrev, awayId: awayAbbrev}

    for i, record in enumerate(data):
        cleaned_record = record.copy()
        
        # Inject game metadata
        cleaned_record["gameType"] = gameType
        cleaned_record["homeId"] = homeId
        cleaned_record["awayId"] = awayId
        cleaned_record["homeAbbrev"] = homeAbbrev
        cleaned_record["awayAbbrev"] = awayAbbrev
        
        # Rename typeDescKey to event
        if "typeDescKey" in cleaned_record:
            cleaned_record["event"] = cleaned_record.pop("typeDescKey")
        else:
            cleaned_record["event"] = cleaned_record.get("typeDescKey", None)

        # Inject team IDs into record for later logic
        cleaned_record["homeId"] = homeId
        cleaned_record["awayId"] = awayId

        # Safely extract nested dictionaries
        details = cleaned_record.get("details", {}) or {}
        period_info = cleaned_record.get("periodDescriptor", {}) or {}

        # Fill forward SOG and score if missing
        home_sog = details.get("homeSOG", home_sog)
        away_sog = details.get("awaySOG", away_sog)
        home_score = details.get("homeScore", home_score)
        away_score = details.get("awayScore", away_score)

        # Overwrite None values
        details["homeSOG"] = home_sog
        details["awaySOG"] = away_sog
        details["homeScore"] = home_score
        details["awayScore"] = away_score

        # Flatten details and period info
        for key, value in details.items():
            cleaned_record[key] = value
        for key, value in period_info.items():
            cleaned_record["period" if key == "number" else key] = value

        # Remove original nested fields
        cleaned_record.pop("details", None)
        cleaned_record.pop("periodDescriptor", None)

        # --- Time Parsing ---
        try:
            for time_field in ["timeInPeriod", "timeRemaining"]:
                time_value = cleaned_record.get(time_field)

                if isinstance(time_value, str) and ":" in time_value:
                    minutes, seconds = map(int, time_value.split(":"))
                    parsed = timedelta(minutes=minutes, seconds=seconds)
                    total_seconds = minutes * 60 + seconds
                elif isinstance(time_value, (int, float)):
                    parsed = timedelta(seconds=int(time_value))
                    total_seconds = int(time_value)
                else:
                    parsed = None
                    total_seconds = None

                cleaned_record[f"{time_field}Parsed"] = parsed
                cleaned_record[f"{time_field}Seconds"] = total_seconds

        except (ValueError, TypeError):
            cleaned_record["timeInPeriodParsed"] = None
            cleaned_record["timeRemainingParsed"] = None
            cleaned_record["timeInPeriodSeconds"] = None
            cleaned_record["timeRemainingSeconds"] = None

        # --- Elapsed Time in Game ---
        try:
            period = int(cleaned_record.get("period", 0))
            time_in_period = cleaned_record.get("timeInPeriodParsed")
            time_in_period_seconds = cleaned_record.get("timeInPeriodSeconds")

            is_playoffs = str(gameType) == "3"
            is_regular_overtime = not is_playoffs or period <= 4

            if period > 0 and time_in_period and is_regular_overtime:
                cleaned_record["elapsedTimeInGame"] = time_in_period + timedelta(minutes=(period - 1) * 20)
                cleaned_record["elapsedTimeInGameSeconds"] = time_in_period_seconds + (period - 1) * 1200
            else:
                cleaned_record["elapsedTimeInGame"] = None
                cleaned_record["elapsedTimeInGameSeconds"] = None

        except (ValueError, TypeError):
            cleaned_record["elapsedTimeInGame"] = None
            cleaned_record["elapsedTimeInGameSeconds"] = None

        # --- Team Ownership & Coordinates ---
        try:
            team_id = cleaned_record.get("eventOwnerTeamId")
            cleaned_record["eventTeam"] = home_away_dict.get(team_id)
            cleaned_record["isHome"] = team_id == homeId

            x = float(cleaned_record.get("xCoord", None))
            y = float(cleaned_record.get("yCoord", None))
            defending_side = cleaned_record.get("homeTeamDefendingSide")

            # Apply coordinate flip if home team defends right and the event belongs to that side
            flip = (
                (team_id == homeId and defending_side == "right") or
                (team_id == awayId and defending_side == "right")
            )

            cleaned_record["xCoord"] = x
            cleaned_record["yCoord"] = y
            cleaned_record["x"] = -x if flip else x
            cleaned_record["y"] = -y if flip else y

        except (TypeError, ValueError):
            cleaned_record["eventTeam"] = None
            cleaned_record["isHome"] = None
            cleaned_record["x"] = None
            cleaned_record["y"] = None
            cleaned_record["xCoord"] = None
            cleaned_record["yCoord"] = None

        cleaned_data.append(cleaned_record)

    return cleaned_data

# Cleaning function registry
CLEANING_FUNCTIONS = {
    "teams": clean_teams_data,
    "schedule": clean_schedule_data,
    "roster": clean_roster_data,
    "standings": clean_standings_data,
    "team_stats": clean_team_stats_data,
}


def clean_data(data: Any, data_type: str = "universal") -> Any:
    """
    Apply appropriate cleaning based on data type.

    Args:
        data: Raw data from scraping functions
        data_type: Type of data ('teams', 'schedule', 'roster', 'standings', 'shifts', 'universal')

    Returns:
        Cleaned data (format depends on input)
    """
    # Handle HTML shifts data structure (dict with 'home'/'away' keys)
    if data_type == "shifts" and isinstance(data, dict) and 'home' in data and 'away' in data:
        # HTML shifts data - return as-is since it's already structured
        return data
    
    # Handle list data (traditional API format)
    if isinstance(data, list):
        # Always apply universal cleaning first
        cleaned_data = apply_universal_cleaning(data)

        # Apply specific cleaning if available
        if data_type in CLEANING_FUNCTIONS:
            cleaned_data = CLEANING_FUNCTIONS[data_type](cleaned_data)

        return cleaned_data
    
    # Handle single dict data
    elif isinstance(data, dict):
        # Apply universal cleaning if it looks like a record
        if any(isinstance(v, (str, int, float)) for v in data.values()):
            return apply_universal_cleaning([data])[0] if apply_universal_cleaning([data]) else data
        else:
            # Complex dict structure, return as-is
            return data
    
    # For other data types, return as-is
    return data
