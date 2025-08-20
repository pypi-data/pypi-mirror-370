import asyncio
import json
import re
from datetime import datetime

import aiohttp
import nest_asyncio
import numpy as np
import pandas as pd
import polars as pl
from playwright.async_api import async_playwright
from selectolax.lexbor import LexborHTMLParser
from tqdm import tqdm
from ...core.utils import fetch_json, fetch_html_async, run_async_safe
from .parse import parse_html_pbp, parse_html_rosters
import requests

from typing import List, Dict, Union, Optional, Coroutine, Any

def convert_json_to_goal_url(json_url):
    parts = json_url.split('/')
    game_id = parts[-2]
    event_id = parts[-1].replace('ev', '').replace('.json', '')
    return f"https://www.nhl.com/ppt-replay/goal/{game_id}/{event_id}"

def get_goal_replay_data(json_url):
    """
    Convert a JSON URL to the NHL goal replay.
    
    Args:
        json_url (str): The URL of the JSON file containing goal data.
        
    Returns:
        list[dict]: A list of dictionaries containing goal replay data.
    """
    goal_url = convert_json_to_goal_url(json_url)
    

    # Custom headers to simulate a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": goal_url,  # goal URL as the referer
        "Origin": "https://www.nhl.com",
    }

    # Make the request
    response = requests.get(json_url, headers=headers)
    data = response.json() if response.status_code == 200 else []
    
    
    return data

def scrapeTeams(source: str = "default") -> List[Dict]:
    """
    Scrapes NHL team data from various public endpoints.

    Parameters:
    - source (str): One of ["default", "calendar", "records"]

    Returns:
    - List[Dict]: Raw enriched team data with metadata.
    """
    source_dict = {
        "default": "https://api.nhle.com/stats/rest/en/franchise?sort=fullName&include=lastSeason.id&include=firstSeason.id",
        "calendar": "https://api-web.nhle.com/v1/schedule-calendar/now",
        "records": (
            "https://records.nhl.com/site/api/franchise?"
            "include=teams.id&include=teams.active&include=teams.triCode&"
            "include=teams.placeName&include=teams.commonName&include=teams.fullName&"
            "include=teams.logos&include=teams.conference.name&include=teams.division.name&"
            "include=teams.franchiseTeam.firstSeason.id&include=teams.franchiseTeam.lastSeason.id"
        ),
    }

    if source not in source_dict:
        print(f"[Warning] Invalid source '{source}', falling back to 'default'.")
        source = "default"

    try:
        url = source_dict[source]
        response = fetch_json(url)

        # Normalize nested keys
        if isinstance(response, dict) and "data" in response:
            data = response["data"]
        elif isinstance(response, dict) and "teams" in response:
            data = response["teams"]
        elif isinstance(response, list):
            data = response
        else:
            data = [response]

    except Exception as e:
        raise RuntimeError(f"Error fetching data from {source}: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": source}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeSchedule(team: str = "MTL", season: Union[str, int] = "20242025") -> List[Dict]:
    """
    Scrapes raw NHL schedule data for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")

    Returns:
    - List[Dict]: Raw schedule records with metadata
    """
    season = str(season)
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/{season}"

    try:
        response = fetch_json(url)

        if isinstance(response, dict) and "games" in response:
            data = response["games"]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except Exception as e:
        raise RuntimeError(f"Error fetching schedule data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Schedule API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeStandings(date: str = None) -> List[Dict]:
    """
    Scrapes NHL standings data for a given date.

    Parameters:
    - date (str, optional): Date in 'YYYY-MM-DD' format. Defaults to None (previous years' new year).

    Returns:
    - List[Dict]: Raw standings records with metadata
    """

    # If no date is provided, use the previous year's new year's date
    if date is None:
        date = f"{(datetime.utcnow() - pd.DateOffset(years=1)).strftime('%Y')}-01-01"

    url = f"https://api-web.nhle.com/v1/standings/{date}"

    try:
        response = fetch_json(url)

        if isinstance(response, dict) and "standings" in response:
            data = response["standings"]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except Exception as e:
        raise RuntimeError(f"Error fetching standings data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Standings API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeRoster(team: str = "MTL", season: Union[str, int] = "20242025") -> List[Dict]:
    """
    Scrapes NHL roster data for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")

    Returns:
    - List[Dict]: Raw roster records with metadata
    """
    season = str(season)
    url = f"https://api-web.nhle.com/v1/roster/{team}/{season}"
    print(f"Fetching roster data for team: {team}, season: {season} from {url}")

    try:
        response = fetch_json(url)

        data = [
            {**record}  # optional: create a shallow copy
            for key, value in response.items()
            if isinstance(value, list)
            for record in value
            if isinstance(record, dict)
        ]

    except Exception as e:
        raise RuntimeError(f"Error fetching roster data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Roster API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeTeamStats(
    team: str = "MTL",
    season: Union[str, int] = "20242025",
    session: Union[str, int] = 2,
    goalies: bool = False,
) -> List[Dict]:
    """
    Scrapes NHL team statistics for a given team and season.

    Parameters:
    - team (str): Team abbreviation (e.g., "MTL")
    - season (str or int): Season ID (e.g., "20242025")
    - session (str or int): Session ID (default is 2) - 1 for pre-season, 2 for regular season, 3 for playoffs

    Returns:
    - List[Dict]: Raw team statistics records with metadata
    """
    season = str(season)
    url = f"https://api-web.nhle.com/v1/club-stats/{team}/{season}/{session}"

    key = "goalies" if goalies else "skaters"

    # print(f"Fetching team stats for team: {team}, season: {season}, session: {session} from {url}")

    try:
        response = fetch_json(url)

        if isinstance(response, dict) and key in response:
            data = response[key]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except Exception as e:
        raise RuntimeError(f"Error fetching team stats data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Team Stats API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeDraftData(year: Union[str, int] = "2024", round: Union[str, int] = "all") -> List[Dict]:
    """
    Scrapes NHL draft data for a given season.

    Parameters:
    - season (str or int): Season ID (e.g., "2024")
    - round (str or int): Round number (default is "all" for all rounds)

    Returns:
    - List[Dict]: Raw draft records with metadata
    """
    year = str(year)
    url = f"https://api-web.nhle.com/v1/draft/picks/{year}/{round}"

    # print(f"Fetching draft data for season: {year} round: {round} from {url}")

    try:
        response = fetch_json(url)

        if isinstance(response, dict) and "picks" in response:
            data = response["picks"]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except Exception as e:
        raise RuntimeError(f"Error fetching draft data: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "year": year, "scrapedOn": now, "source": "NHL Draft API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeRecordsDraft(year: Union[str, int] = "2024") -> List[Dict]:
    """
    Scrapes NHL draft records for a given season from NHL Records API.

    Parameters:
    - year (str or int): Season ID (e.g., "2024")

    Returns:
    - List[Dict]: Raw draft records with metadata
    """
    year = str(year)
    url = f"https://records.nhl.com/site/api/draft?include=draftProspect.id&include=player.birthStateProvince&include=player.birthCountry&include=player.position&include=player.onRoster&include=player.yearsPro&include=player.firstName&include=player.lastName&include=player.id&include=team.id&include=team.placeName&include=team.commonName&include=team.fullName&include=team.triCode&include=team.logos&include=franchiseTeam.franchise.mostRecentTeamId&include=franchiseTeam.franchise.teamCommonName&include=franchiseTeam.franchise.teamPlaceName&cayenneExp=%20draftYear%20=%20{year}&start=0&limit=500"

    print(f"Fetching draft records for season: {year} round: {round} from {url}")

    try:
        response = fetch_json(url)

        if isinstance(response, dict) and "data" in response:
            data = response["data"]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except Exception as e:
        raise RuntimeError(f"Error fetching draft records: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "year": year, "scrapedOn": now, "source": "NHL Draft Records API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapeRecordsTeamDraftHistory(franchise: Union[str, int] = 1) -> List[Dict]:
    """
    Scrapes NHL team draft history for a given franchise.

    Parameters:
    - franchise (str or int): Franchise ID

    Returns:
    - List[Dict]: Raw draft history records with metadata
    """
    franchise = str(franchise)
    url = f"https://records.nhl.com/site/api/draft?include=draftProspect.id&include=franchiseTeam&include=player.birthStateProvince&include=player.birthCountry&include=player.position&include=player.onRoster&include=player.yearsPro&include=player.firstName&include=player.lastName&include=player.id&include=team.id&include=team.placeName&include=team.commonName&include=team.fullName&include=team.triCode&include=team.logos&cayenneExp=franchiseTeam.franchiseId=%22{franchise}%22"
    print(f"Fetching team draft history for franchise: {franchise} from {url}")

    try:
        response = fetch_json(url)

        if isinstance(response, dict) and "data" in response:
            data = response["data"]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except Exception as e:
        raise RuntimeError(f"Error fetching team draft history: {e}")

    now = datetime.utcnow().isoformat()
    return [
        {**record, "scrapedOn": now, "source": "NHL Team Draft History API"}
        for record in data
        if isinstance(record, dict)
    ]


def scrapePlayer(player: Union[str, int] = "8481540") -> Dict:
    """
    Scrapes NHL player data for a given player and season.

    Parameters:
    - player (str or int): Player ID


    Returns:
    - List[Dict]: Raw player records with
            "playerId",
            "isActive",
            "currentTeamId",
            "currentTeamAbbrev",
            "fullTeamName",
            "teamCommonName",
            "teamPlaceNameWithPreposition",
            "firstName",
            "lastName",
            "teamLogo",
            "sweaterNumber",
            "position",
            "headshot",
            "heroImage",
            "heightInInches",
            "heightInCentimeters",
            "weightInPounds",
            "weightInKilograms",
            "birthDate",
            "birthCity",
            "birthStateProvince",
            "birthCountry",
            "shootsCatches",
            "draftDetails",
            "playerSlug",
            "inTop100AllTime",
            "inHHOF",
            "featuredStats",
            "careerTotals",
            "shopLink",
            "twitterLink",
            "watchLink",
            "last5Games",
            "seasonTotals",
            "currentTeamRoster".
    """

    url = f"https://api-web.nhle.com/v1/player/{player}/landing"

    # print(f"Fetching player data for player: {player} from {url}")

    try:
        response = fetch_json(url)
        data = response

    except Exception as e:
        raise RuntimeError(f"Error fetching player data: {e}")

    now = datetime.utcnow().isoformat()

    # Add metadata to the player data
    if isinstance(data, dict):
        record = {**data}
        record["scrapedOn"] = now
        record["source"] = "NHL Player API"
    else:
        raise ValueError(f"Unexpected response format: {data}")
    return record

def _add_normalized_coordinates(events: List) -> List:
    """Add normalized coordinate system (attacking direction)."""

    for event in events:
        details = event.get('details', {}) if isinstance(event, dict) else {}
        x_coord = details.get('x_coord') or details.get('xCoord')
        y_coord = details.get('y_coord') or details.get('yCoord')

        # Safely coerce to floats (or 0.0 if missing/invalid)
        try:
            xf = float(x_coord)
        except (TypeError, ValueError):
            xf = 0.0
        try:
            yf = float(y_coord)
        except (TypeError, ValueError):
            yf = 0.0

        # Store normalized coordinates
        event["x_normalized"] = xf
        event["y_normalized"] = yf

        # Euclidean distance from (0,0) as a proxy for distance from goal
        event["distance_from_goal"] = (xf ** 2 + yf ** 2) ** 0.5

    return events

def scrapeGameAPI(game: Union[str, int]) -> Dict:
    """
    Scrapes NHL game data from API for a given game ID.

    Parameters:
    - game (str or int): Game ID

    Returns:
    - Dict: Raw game data including enriched play-by-play records with metadata
    """
    game = str(game)
    url = f"https://api-web.nhle.com/v1/gamecenter/{game}/play-by-play"

    # print(f"Fetching play-by-play data for game: {game} from {url}")
    now = datetime.utcnow().isoformat()

    try:
        response = fetch_json(url)

        if response not in [None, {}, []]:
            data = response

            # List of metadata keys to include in each play
            extra_keys = [
                'gameDate', 'gameType', 
                'startTimeUTC', 'easternUTCOffset', 'venueUTCOffset', #'gameOutcome'
            ]

            # Enrich each play with pptReplayData and selected metadata
            enriched_plays = []
            for play in data.get('plays', []):
                enriched_play = {
                    **play,
                    'pptReplayData': get_goal_replay_data(play['pptReplayUrl']) if play.get('pptReplayUrl') else None,
                    'gameId': data.get('id'),
                    'venue': data.get('venue', {}).get('default'),
                    'venueLocation': data.get('venueLocation', {}).get('default'),
                    'scrapedOn': now,
                    'source': 'NHL Play-by-Play API',
                    **{key: data.get(key) for key in extra_keys}
                }
                enriched_plays.append(enriched_play)

            # Add normalized coordinate and distance fields to each play
            enriched_plays = _add_normalized_coordinates(enriched_plays)

            data['plays'] = enriched_plays
            
            
        else:
            raise ValueError(f"Unexpected response format: {response}")
        
        

    except Exception as e:
        raise RuntimeError(f"Error fetching play-by-play data: {e}")

    

    # Add scraping metadata
    data["scrapedOn"] = now
    data["source"] = "NHL Play-by-Play API"
    return data


async def scrapeHtmlPbp(game: Union[str, int]) -> Dict:
    """
    Asynchronously fetches NHL play-by-play data from HTML for a given game ID.

    Parameters:
    - game (str or int): Game ID

    Returns:
    - Dict: Contains both home and away team HTML play-by-play data
    """
    game_id = str(game)

    
    short_id = game_id[-6:].zfill(6)
    first_year = game_id[:4]
    second_year = str(int(first_year) + 1)

    url = f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/PL{short_id}.HTM"

    # print(f"Fetching play-by-play HTML data for game: {game_id}")
    

    try:
        # Fetch both home and away team HTML play-by-play data
        game_html = await fetch_html_async(url)

        if not game_html:
            raise ValueError(f"No HTML play-by-play data found for game {game_id}")

        # Return structured data with keys expected by pipeline
        result = {
            "data": game_html,
            "urls": {"home": url, "away": url},
            "game_id": game_id,
            "scraped_on": datetime.utcnow().isoformat(),
            "source": "NHL HTML Play-by-Play Reports",
        }

        # print(f"✅ Successfully fetched HTML play-by-play data for game {game_id}")
        return result

    except Exception as e:
        raise RuntimeError(f"Error fetching HTML play-by-play data for game {game_id}: {e}")


# def scrapeShifts(game: Union[str, int]) -> Dict:
#     """
#     ⚠️  DEPRECATED: Scrapes NHL shifts data from API (unreliable).
    
#     This function is deprecated due to API reliability issues.
#     Use scrapeHTMLShifts_* functions instead for more reliable shift data.

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - List[Dict]: Raw shifts records with metadata
    
#     Recommended alternatives:
#     - scrapeHTMLShifts_async() for async contexts
#     - scrapeHTMLShifts_sync() for sync contexts  
#     - scrapeHTMLShifts_smart() for auto-detection
#     """
#     import warnings
#     warnings.warn(
#         "scrapeShifts() using API is deprecated due to reliability issues. "
#         "Use scrapeHTMLShifts_* functions instead for better reliability.",
#         DeprecationWarning,
#         stacklevel=2
#     )
    
#     game = str(game)
#     url = f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game}"

#     print(f"⚠️  DEPRECATED: Fetching shifts data for game: {game} from {url}")
#     print("   Consider using scrapeHTMLShifts_* functions for better reliability.")

#     try:
#         response = fetch_json(url)

#         if response not in [None, {}, []]:
#             data = response.get("data", [])
#         else:
#             raise ValueError(f"Unexpected response format: {response}")

#     except Exception as e:
#         raise RuntimeError(f"Error fetching shifts data: {e}")

#     now = datetime.utcnow().isoformat()

#     # Add metadata to each record
#     for record in data:
#         if isinstance(record, dict):
#             record["scrapedOn"] = now
#             record["source"] = "NHL Shifts API (DEPRECATED)"
#         else:
#             raise ValueError("Each record in the shifts data should be a dictionary.")
#     return data


async def scrapeHTMLShifts_async(game: Union[str, int]) -> Dict:
    """
    Async version: Scrapes NHL shifts data from HTML for a given game ID.

    This scraper fetches HTML shift reports for both home and away teams,
    following the pattern from scraper_pandas.py for comprehensive shift data.

    Parameters:
    - game (str or int): Game ID

    Returns:
    - Dict: Contains both home and away team HTML shift data
    """
    game_id = str(game)

    # Generate URLs for home (TH) and away (TV) team shift reports
    short_id = game_id[-6:].zfill(6)
    first_year = game_id[:4]
    second_year = str(int(first_year) + 1)

    url_home = f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/TH{short_id}.HTM"
    url_away = f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/TV{short_id}.HTM"

    # print(f"Fetching shifts HTML data for game: {game_id}")
    # print(f"  Home team URL: {url_home}")
    # print(f"  Away team URL: {url_away}")

    try:
        # Fetch both home and away team HTML shift data
        html_home = await fetch_html_async(url_home)
        html_away = await fetch_html_async(url_away)

        if not html_home and not html_away:
            raise ValueError(f"No HTML shifts data found for game {game_id}")

        # Return structured data with keys expected by pipeline
        result = {
            "home": html_home,
            "away": html_away,
            "urls": {"home": url_home, "away": url_away},
            "game_id": game_id,
            "scraped_on": datetime.utcnow().isoformat(),
            "source": "NHL HTML Shifts Reports",
        }

        # print(f"✅ Successfully fetched HTML shifts data for game {game_id}")
        return result

    except Exception as e:
        raise RuntimeError(f"Error fetching HTML shifts data for game {game_id}: {e}")


# def scrapeHTMLShifts_sync(game: Union[str, int]) -> Dict:
#     """
#     Sync version: Scrapes NHL shifts data from HTML for a given game ID.

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict: Contains both home and away team HTML shift data
#     """
#     try:
#         # Check if we're in an async context
#         asyncio.get_running_loop()
#         raise RuntimeError(
#             f"scrapeHTMLShifts_sync() cannot be used in async context (like Jupyter). "
#             f"Use 'await scrapeHTMLShifts_async({game})' instead."
#         )
#     except RuntimeError as e:
#         if "no running event loop" in str(e):
#             # Safe to use async function with run_async_safe
#             return run_async_safe(scrapeHTMLShifts_async(game))
#         else:
#             # We're in an async context, re-raise with helpful message
#             raise e


# def scrapeHTMLShifts_smart(game: Union[str, int]) -> Union[Dict, Coroutine]:
#     """
#     Smart HTML shifts scraper that detects context and handles appropriately.

#     - In sync context: Returns HTML shifts data directly
#     - In async context: Returns coroutine to be awaited

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict or Coroutine: HTML shifts data or coroutine
#     """
#     try:
#         # Check if we're in an async context
#         asyncio.get_running_loop()
#         # In async context, return coroutine
#         return scrapeHTMLShifts_async(game)
#     except RuntimeError:
#         # Not in async context, use sync version
#         return scrapeHTMLShifts_sync(game)


# async def scrapeHTMLPbp_async(game: Union[str, int]) -> Dict:
#     """
#     Async version: Scrapes NHL play-by-play data from HTML for a given game ID.

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict: Parsed play-by-play data with events, columns, and on-ice information
#     """
#     game_id = str(game)
#     short_id = game_id[-6:].zfill(6)
#     first_year = game_id[:4]
#     second_year = str(int(first_year) + 1)
#     url = f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/PL{short_id}.HTM"
#     print(f"Fetching play-by-play data for game: {game_id} from {url}")

#     html_content = await fetch_html_async(url)
#     if not html_content:
#         raise ValueError(f"Failed to retrieve HTML content from {url}")

#     # Parse the HTML content using our improved parser
#     try:
#         parsed_data = parse_html_pbp(html_content)
#         print(f"✅ Parsed {len(parsed_data['data'])} play-by-play events")
#         return parsed_data
#     except Exception as e:
#         print(f"❌ Error parsing HTML: {e}")
#         raise ValueError(f"Failed to parse play-by-play HTML for game {game_id}: {e}")


# def scrapeHTMLPbp_sync(game: Union[str, int]) -> Dict:
#     """
#     Sync wrapper: Scrapes NHL play-by-play data from HTML for a given game ID.

#     ⚠️  This function cannot be used in async contexts (like Jupyter notebooks).
#     ⚠️  Use scrapeHTMLPbp_async() instead in async contexts.

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict: Parsed play-by-play data with events, columns, and on-ice information

#     Raises:
#     - RuntimeError: If called from an async context
#     """
#     try:
#         # Check if we're in an async context
#         asyncio.get_running_loop()
#         raise RuntimeError(
#             "scrapeHTMLPbp_sync() cannot be used in async context (like Jupyter). "
#             "Use 'await scrapeHTMLPbp_async()' instead."
#         )
#     except RuntimeError as e:
#         if "no running event loop" in str(e):
#             # Safe to use asyncio.run
#             return run_async_safe(scrapeHTMLPbp_async(game))
#         else:
#             # We're in an async context, re-raise with helpful message
#             raise e


# def scrapeHTMLPbp_smart(game: Union[str, int]) -> Union[Dict, Coroutine[None, None, Dict]]:
#     """
#     Smart version: Auto-detects context and returns appropriate result.

#     Usage:
#     - In sync context: result = scrapeHTMLPbp_smart(game_id)
#     - In async context: result = await scrapeHTMLPbp_smart(game_id)

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict | Coroutine: Parsed play-by-play data directly (sync) or coroutine (async)
#     """
#     try:
#         # Check if we're in an async context
#         asyncio.get_running_loop()
#         # We're in an async context, return the coroutine
#         return scrapeHTMLPbp_async(game)
#     except RuntimeError:
#         # No event loop, run synchronously
#         return run_async_safe(scrapeHTMLPbp_async(game))


# # Backward compatibility: Keep current function as async version
# async def scrapeHTMLPbp(game: Union[str, int]) -> Dict:
#     """
#     Backward compatibility: Async version of scrapeHTMLPbp.

#     This is the current implementation that works in Jupyter notebooks.
#     For sync usage, use scrapeHTMLPbp_sync() instead.
#     """
#     return await scrapeHTMLPbp_async(game)


# async def scrapeHTMLGameRosters_async(game: Union[str, int]) -> Dict[str, Any]:
#     """
#     Async version: Scrapes NHL game rosters from HTML for a given game ID.

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict[str, Any]: Parsed roster data with home and away teams
#     """
#     game_id = str(game)
#     short_id = game_id[-6:].zfill(6)
#     first_year = game_id[:4]
#     second_year = str(int(first_year) + 1)
#     url = f"https://www.nhl.com/scores/htmlreports/{first_year}{second_year}/RO{short_id}.HTM"

#     print(f"Fetching rosters for game: {game_id} from {url}")

#     html_content = await fetch_html_async(url)
#     if not html_content:
#         raise ValueError(f"Failed to retrieve HTML content from {url}")

#     # Parse the HTML content using our improved parser
#     try:
#         parsed_data = parse_html_rosters(html_content)
#         parsed_data["gameInfo"]["gameId"] = game_id
#         print(f"✅ Parsed roster data for game {game_id}")
#         return parsed_data
#     except Exception as e:
#         print(f"❌ Error parsing HTML: {e}")
#         raise ValueError(f"Failed to parse rosters HTML for game {game_id}: {e}")


# def scrapeHTMLGameRosters_sync(game: Union[str, int]) -> Dict[str, Any]:
#     """
#     Sync wrapper: Scrapes NHL game rosters from HTML for a given game ID.

#     ⚠️  This function cannot be used in async contexts (like Jupyter notebooks).
#     ⚠️  Use scrapeHTMLGameRosters_async() instead in async contexts.

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict[str, Any]: Parsed roster data with home and away teams

#     Raises:
#     - RuntimeError: If called from an async context
#     """
#     try:
#         # Check if we're in an async context
#         asyncio.get_running_loop()
#         raise RuntimeError(
#             "scrapeHTMLGameRosters_sync() cannot be used in async context (like Jupyter). "
#             "Use 'await scrapeHTMLGameRosters_async()' instead."
#         )
#     except RuntimeError as e:
#         if "no running event loop" in str(e):
#             # Safe to use asyncio.run
#             return run_async_safe(scrapeHTMLGameRosters_async(game))
#         else:
#             # We're in an async context, re-raise with helpful message
#             raise e


# def scrapeHTMLGameRosters_smart(
#     game: Union[str, int]
# ) -> Union[Dict[str, Any], Coroutine[None, None, Dict[str, Any]]]:
#     """
#     Smart version: Auto-detects context and returns appropriate result.

#     Usage:
#     - In sync context: result = scrapeHTMLGameRosters_smart(game_id)
#     - In async context: result = await scrapeHTMLGameRosters_smart(game_id)

#     Parameters:
#     - game (str or int): Game ID

#     Returns:
#     - Dict | Coroutine: Parsed roster data directly (sync) or coroutine (async)
#     """
#     try:
#         # Check if we're in an async context
#         asyncio.get_running_loop()
#         # We're in an async context, return the coroutine
#         return scrapeHTMLGameRosters_async(game)
#     except RuntimeError:
#         # No event loop, run synchronously
#         return run_async_safe(scrapeHTMLGameRosters_async(game))


# async def scrapeHTMLGameRosters(game: Union[str, int]) -> Dict[str, Any]:
#     """
#     Backward compatibility: Async version of scrapeHTMLGameRosters.

#     This is the current implementation that works in Jupyter notebooks.
#     For sync usage, use scrapeHTMLGameRosters_sync() instead.
#     """
#     return await scrapeHTMLGameRosters_async(game)
