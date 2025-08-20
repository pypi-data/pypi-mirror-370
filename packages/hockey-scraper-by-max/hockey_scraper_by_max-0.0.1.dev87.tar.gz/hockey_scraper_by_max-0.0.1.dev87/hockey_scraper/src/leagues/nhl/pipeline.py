"""
Enhanced NHL Data Pipeline Module

This module provides comprehensive pipeline functions to scrape all available NHL data types
up to the parsing/cleaning step, with configurable output formats for downstream storage.

Available Data Types:
- Teams
- Schedule  
- Standings
- Roster
- Team Stats
- Draft Data
- Records Draft
- Records Team Draft History  
- Player Data
- Game API Data
- Shifts
- HTML Play-by-Play
- HTML Game Rosters

Output Formats:
- dict: Raw Python dictionaries
- pandas: Pandas DataFrames
- polars: Polars DataFrames
- json: JSON strings
- list: List of records
"""

import asyncio
import json
from datetime import datetime
from typing import Union, Optional, Any, Literal, Dict, Mapping, Sequence
import pandas as pd
import polars as pl
import numpy as np

from .scrape import *
from ...core.base_scraper import convert_to_dataframe
from .cleaning import *
from .parse import parse_html_pbp, parse_html_shifts


def time_str_to_seconds(time_str):
    mins, secs = map(int, time_str.split(":"))
    return mins * 60 + secs

# Type definitions
OutputFormat = Literal["dict", "pandas", "polars", "json", "list"]

event_mapping = {
        'blocked-shot': 'BLOCK',
        'delayed-penalty': 'DELPEN',
        'faceoff': 'FAC',
        'giveaway': 'GIVE',
        'goal': 'GOAL',
        'hit': 'HIT',
        'missed-shot': 'MISS',
        'penalty': 'PENL',
        'shot-on-goal': 'SHOT',
        'stoppage': 'STOP',
        'takeaway': 'TAKE',
        'game-end': 'GEND',
        'period-end': 'PEND',
        'period-start': 'PSTR',
        'shootout-completed': 'SOC'
    }

def _is_mapping_list(x: Any) -> bool:
    return isinstance(x, list) and (not x or isinstance(x[0], Mapping))

def _to_records(data: Any) -> list[dict]:
    if isinstance(data, Mapping):
        return [data]
    if _is_mapping_list(data):
        return data
    if isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
        return [{"value": v} for v in data]
    return [{"value": data}]

def _flatten_dict(d: Mapping, parent_key: str = "", sep: str = ".") -> dict:
    flat = {}
    for k, v in d.items():
        key = f"{parent_key}{sep}{k}" if parent_key else str(k)
        if isinstance(v, Mapping):
            flat.update(_flatten_dict(v, key, sep=sep))
        else:
            flat[key] = v
    return flat

def _flatten_pandas_df(df, *, sep: str = ".", explode_lists: bool = False):
    import pandas as pd
    # Re-normalize while any cell contains a Mapping; cap passes to avoid loops
    for _ in range(3):
        if (df.map(lambda v: isinstance(v, Mapping)).any().any()):
            df = pd.json_normalize(df.to_dict(orient="records"), sep=sep)
        else:
            break
    # Optionally explode list-of-dicts columns
    if explode_lists:
        for col in list(df.columns):
            if df[col].apply(lambda v: isinstance(v, list) and (not v or isinstance(v[0], Mapping))).any():
                tmp = df.explode(col, ignore_index=True)
                norm = pd.json_normalize(tmp.pop(col), sep=sep).add_prefix(f"{col}{sep}")
                df = tmp.join(norm)
    return df

def _flatten_polars_df(df, *, sep: str = ".", explode_lists: bool = False):
    """Flatten nested structs in Polars DataFrame using json_normalize."""
    import polars as pl
    
    if not isinstance(df, pl.DataFrame):
        raise TypeError("Input must be a Polars DataFrame")
    
    try:
        # Convert DataFrame to dict records for json_normalize
        records = df.to_dicts()
        
        # Use Polars' built-in json_normalize with the specified separator
        flattened_df = pl.json_normalize(records, separator=sep)
        
        # print(f"✅ Polars json_normalize successful: {flattened_df.shape}")
        return flattened_df
        
    except Exception as e:
        print(f"⚠️ Polars json_normalize failed ({e}), trying fallback...")
        
        # Fallback: manual flattening for edge cases
        try:
            # Convert any Object columns to string first
            for col, dtype in df.schema.items():
                if dtype == pl.Object:
                    df = df.with_columns(
                        pl.col(col).map_elements(lambda x: str(x) if x is not None else None).alias(col)
                    )
            
            # Try json_normalize again with cleaned data
            records = df.to_dicts()
            flattened_df = pl.json_normalize(records, separator=sep)
            # print(f"✅ Polars json_normalize fallback successful: {flattened_df.shape}")
            return flattened_df
            
        except Exception as fallback_error:
            print(f"❌ All Polars flattening attempts failed ({fallback_error})")
            # Return original DataFrame as last resort
            return df

def _format_output(
    data: Any,
    output_format: OutputFormat = "dict",
    *,
    multi_frames: bool = False,
    json_ensure_ascii: bool = False,
    json_default: Any | None = None,
    flatten: bool = True,
    explode_lists: bool = False,
    sep: str = ".",
) -> Any:
    """Format output data with robust error handling."""
    fmt = output_format.lower()

    if fmt == "dict":
        return data

    if fmt == "json":
        return json.dumps(
            data,
            indent=2,
            ensure_ascii=json_ensure_ascii,
            default=(json_default if json_default is not None else str),
        )

    if fmt == "list":
        return data if isinstance(data, list) else [data]

    if fmt == "pandas":
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError("pandas is required for pandas output format") from e

        if isinstance(data, dict) and multi_frames:
            return {k: pd.json_normalize(v) for k, v in data.items()}

        try:
            if isinstance(data, dict):
                df = pd.json_normalize([data], sep=sep)
            elif _is_mapping_list(data):
                df = pd.json_normalize(data, sep=sep)
            else:
                df = pd.DataFrame(_to_records(data))
                
            if flatten and not isinstance(data, dict) and not _is_mapping_list(data):
                df = _flatten_pandas_df(df, sep=sep, explode_lists=explode_lists)
            
            # print(f"✅ Pandas DataFrame created: {df.shape}")
            return df
        except Exception as e:
            print(f"⚠️ Pandas conversion failed ({e}), returning simple DataFrame...")
            return pd.DataFrame([{"data": str(data)}])

    if fmt == "polars":
        try:
            import polars as pl
        except ImportError as e:
            raise ImportError("polars is required for polars output format") from e

        if isinstance(data, dict) and multi_frames:
            return {k: pl.DataFrame(_to_records(v)) for k, v in data.items()}

        try:
            if flatten and (isinstance(data, dict) or _is_mapping_list(data)):
                # Use json_normalize directly for nested data
                records = [data] if isinstance(data, dict) else data
                df = pl.json_normalize(records, separator=sep)
                # print(f"✅ Polars json_normalize direct: {df.shape}")
            else:
                # Simple DataFrame creation for non-nested data
                if isinstance(data, dict):
                    df = pl.DataFrame([data])
                elif _is_mapping_list(data):
                    df = pl.DataFrame(data)
                else:
                    df = pl.DataFrame(_to_records(data))
                # print(f"✅ Polars DataFrame created: {df.shape}")
            
            return df
            
        except Exception as polars_error:
            print(f"⚠️ Polars direct conversion failed ({polars_error})")
            try:
                # Fallback: pandas then convert to polars
                import pandas as pd
                print("🔄 Trying pandas -> polars conversion...")
                
                if isinstance(data, dict):
                    pandas_df = pd.json_normalize([data], sep=sep)
                elif _is_mapping_list(data):
                    pandas_df = pd.json_normalize(data, sep=sep)
                else:
                    pandas_df = pd.DataFrame(_to_records(data))
                
                df = pl.from_pandas(pandas_df)
                print(f"✅ Pandas fallback successful: {df.shape}")
                return df
                
            except Exception as pandas_error:
                print(f"❌ Pandas fallback failed ({pandas_error})")
                return pl.DataFrame([{"data": str(data)}])

    raise ValueError(f"Unsupported output format: {output_format!r}")

def scrape_teams(
    source: str = "calendar", output_format: str = "pandas", clean: bool = True,
    flatten: bool = True, explode_lists: bool = False, sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL teams data from the specified source and convert it to a DataFrame.

    Args:
        source (str): The source URL or file path to scrape data from. (options: 'default', 'calendar', 'records')
        output_format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
        flatten (bool): Whether to flatten nested structures in the DataFrame.
        explode_lists (bool): Whether to explode list-of-dicts columns.
        sep (str): Separator for flattening nested structures.

    Returns:
        pd.DataFrame or pl.DataFrame: The scraped teams data in the specified format.
    """
    # 1. Scrape the raw data
    data = scrapeTeams(source)
    # print(f"Raw data from scrapeTeams: {type(data)}, sample: {data[:5] if isinstance(data, list) else data}")

    # 2. Apply cleaning if requested
    if clean:
        data = clean_data(data, data_type="teams")
        # print(f"Cleaned data: {type(data)}, sample: {data[:5] if isinstance(data, list) else data}")

    # 3. Convert to DataFrame
    df = _format_output(data, output_format, flatten=flatten, explode_lists=explode_lists, sep=sep)
    return df


def scrape_schedule(
    team: str = "MTL", season: str = "20242025", format: str = "pandas", clean: bool = True,
    flatten: bool = True, explode_lists: bool = False, sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL schedule data and convert it to a DataFrame.

    Args:
        team (str): Team abbreviation (e.g., "MTL").
        season (str): Season ID (e.g., "20242025").
        format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
        flatten (bool): Whether to flatten nested structures in the DataFrame.
        explode_lists (bool): Whether to explode list-of-dicts columns.
        sep (str): Separator for flattening nested structures.

    Returns:
        pd.DataFrame or pl.DataFrame: The scraped schedule data in the specified format.
    """
    # 1. Scrape the raw data
    data = scrapeSchedule(team, season)

    # 2. Apply cleaning if requested
    if clean:
        data = clean_data(data, data_type="schedule")

    # 3. Convert to DataFrame
    df = _format_output(data, format, flatten=flatten, explode_lists=explode_lists, sep=sep)
    return df


def scrape_roster(
    team: str = "MTL", season: str = "20252026", format: str = "pandas", clean: bool = True,
    flatten: bool = True, explode_lists: bool = False, sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL roster data and convert it to a DataFrame.

    Args:
        team (str): Team abbreviation (e.g., "MTL").
        season (str): Season ID (e.g., "20242025").
        format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
        flatten (bool): Whether to flatten nested structures in the DataFrame.
        explode_lists (bool): Whether to explode list-of-dicts columns.
        sep (str): Separator for flattening nested structures.

    Returns:
        pd.DataFrame or pl.DataFrame: The scraped roster data in the specified format.
    """
    # 1. Scrape the raw data
    data = scrapeRoster(team, season)

    # 2. Apply cleaning if requested
    if clean:
        data = clean_data(data, data_type="roster")

    # 3. Convert to DataFrame
    df = _format_output(data, format, flatten=flatten, explode_lists=explode_lists, sep=sep)
    return df


def scrape_standings(
    date: str = None, format: str = "pandas", clean: bool = True,
    flatten: bool = True, explode_lists: bool = False, sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL standings data and convert it to a DataFrame.

    Args:
        date (str): Date in 'YYYY-MM-DD' format. Defaults to None.
        format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
        flatten (bool): Whether to flatten nested structures in the DataFrame.
        explode_lists (bool): Whether to explode list-of-dicts columns.
        sep (str): Separator for flattening nested structures.

    Returns:
        pd.DataFrame or pl.DataFrame: The scraped standings data in the specified format.
    """
    # 1. Scrape the raw data
    data = scrapeStandings(date)

    # 2. Apply cleaning if requested
    if clean:
        data = clean_data(data, data_type="standings")

    # 3. Convert to DataFrame
    df = _format_output(data, format, flatten=True, explode_lists=False, sep=".")
    return df


def scrape_team_stats(
    team: str = "MTL", season: str = "20242025", format: str = "pandas", clean: bool = True,
    flatten: bool = True, explode_lists: bool = False, sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL team stats data and convert it to a DataFrame.

    Args:
        team (str): Team abbreviation (e.g., "MTL").
        season (str): Season ID (e.g., "20242025").
        format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
        flatten (bool): Whether to flatten nested structures in the DataFrame.
        explode_lists (bool): Whether to explode list-of-dicts columns.
        sep (str): Separator for flattening nested structures.

    Returns:
        pd.DataFrame or pl.DataFrame: The scraped team stats data in the specified format.
    """
    # 1. Scrape the raw data
    data = scrapeTeamStats(team, season)

    # 2. Apply cleaning if requested
    if clean:
        data = clean_data(data, data_type="team_stats")

    # 3. Convert to DataFrame
    df = _format_output(data, format, flatten=flatten, explode_lists=explode_lists, sep=sep)
    return df


def scrape_draft_data(
    year: Union[int, str] = 2024,
    round: Union[int, str] = "all",
    format: str = "pandas",
    clean: bool = True,
    flatten: bool = True,
    explode_lists: bool = False,
    sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL draft data for a specific year and round, and convert it to a DataFrame.

    Args:
        year (Union[int, str]): The draft year (e.g., 2024).
        round (Union[int, str]): The draft round (e.g., "all" or 1).
        format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
        flatten (bool): Whether to flatten nested structures in the DataFrame.
        explode_lists (bool): Whether to explode list-of-dicts columns.
        sep (str): Separator for flattening nested structures.

    Returns:
        pd.DataFrame or pl.DataFrame: The scraped draft data in the specified format.
    """
    # 1. Scrape the raw data
    data = scrapeDraftData(year, round)

    # 2. Apply cleaning if requested
    if clean:
        data = clean_data(data, data_type="draft")

    # 3. Convert to DataFrame
    df = _format_output(data, format, flatten=flatten, explode_lists=explode_lists, sep=sep)
    return df


def scrape_player_career_stats(
    player: Union[str, int] = "8481540",
    format: str = "pandas",
    flatten: bool = True,
    explode_lists: bool = False,
    sep: str = "."
) -> Union[pd.DataFrame, pl.DataFrame]:
    """
    Scrape NHL player career stats and convert it to a DataFrame.
    Args:
        player (Union[str, int]): Player ID or name (e.g., "8481540").
        format (str): The format of the DataFrame ('pandas' or 'polars').
        clean (bool): Whether to apply data cleaning transformations.
    Returns:
        pd.DataFrame or pl.DataFrame: The scraped player career stats data in the specified format
    """
    # 1. Scrape the raw data
    data = scrapePlayer(player)

    # 2. Steps to add in parse.py
    # 2.1 Store bio information to add as columns later to the DataFrame
    player_bio = {
        "playerId": player,
        "firstName": data.get("firstName", "").get("default", ""),
        "lastName": data.get("lastName", "").get("default", ""),
        "fullName": f"{data.get('firstName', {}).get('default', '')} {data.get('lastName', {}).get('default', '')}",
        "headshot": data.get("headshot", ""),
        "position": data.get("position", ""),
        "heightInInches": data.get("heightInInches", ""),
        "heightInCentimeters": data.get("heightInCentimeters", ""),
        "weightInPounds": data.get("weightInPounds", ""),
        "weightInPounds": data.get("weightInPounds", ""),
        "birthDate": data.get("birthDate", ""),
        "birthCity": data.get("birthCity", "").get("default", ""),
        "birthStateProvince": data.get("birthStateProvince", "").get("default", ""),
        "birthCountry": data.get("birthCountry", ""),
        "shootsCatches": data.get("shootsCatches", ""),
        ### TODO : Need to account for players with more than one draft year ###
        "draftYear": data.get("draftDetails", "").get("year", ""),
        "draftRound": data.get("draftDetails", {}).get("round", ""),
        "draftPickInRound": data.get("draftDetails", {}).get("pickInRound", ""),
        "draftOverallPick": data.get("draftDetails", {}).get("overallPick", ""),
        "draftTeam": data.get("draftDetails", {}).get("teamAbbrev", {}),
        "scrapedOn": data.get("scrapedOn", ""),
        "source": data.get("source", ""),
    }

    # 3. Convert to DataFrame
    df = convert_to_dataframe(data.get("seasonTotals", []), format)

    # 4. Add player bio information as columns to the DataFrame
    for key, value in player_bio.items():
        if isinstance(value, dict):
            # If value is a dict, convert to string representation
            df[key] = str(value)
        else:
            df[key] = value

    # 5. Apply cleaning if requested ### Eventually when we have a cleaner for player stats

    return df


def split_time_range(value):
    match = re.match(r"(\d{1,2}:\d{2})(\d{1,2}:\d{2})", value)
    if match:
        return pd.Series([match.group(1).zfill(5), match.group(2).zfill(5)])
    return pd.Series([None, None])

def convert_str_to_seconds(time_str):
    """
    Convert a time string in the format "MM:SS" to seconds.
    """
    if len(time_str) == 5:
        time_parts = time_str.split(":")
        if len(time_parts) == 2:
            minutes, seconds = map(int, time_parts)
            return minutes * 60 + seconds
        else:
            raise ValueError("Invalid time format. Expected 'MM:SS'.")

async def scrape_html_pbp(
       game_id: int,
       return_raw: bool = False
) -> pd.DataFrame:
    """
    Scrape NHL play-by-play data for a specific game and convert it to a DataFrame.

    Args:
        game_id (int): The game ID (e.g., 2024020762).

    Returns:
        pd.DataFrame: The scraped play-by-play data in a DataFrame.
    """
    # 1. Scrape the raw data
    data = await scrapeHtmlPbp(game_id)

    # 2. Convert to DataFrame
    data = parse_html_pbp(data["data"])
    
    df = pd.DataFrame(
            data=data['data'],
            columns=data['columns'] 
            
        )
    
        
    df[["timeInPeriod", "timeRemaining"]] = df["Time:Elapsed Game"].apply(
            split_time_range
        )
    df["timeInPeriodSec"] = df["timeInPeriod"].apply(convert_str_to_seconds)
    df["timeRemainingSec"] = df["timeRemaining"].apply(convert_str_to_seconds)
    
    for col in ['home_on_ice', 'away_on_ice', 'home_goalie', 'away_goalie']:
        df[col] = data[col]

    if return_raw:
        return df, data
    
    return df



def _dedup_cols(cols: pd.Index) -> pd.Index:
    seen = {}
    out = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            out.append(c)
        else:
            seen[c] += 1
            out.append(f"{c}_{seen[c]}")
    return pd.Index(out)

async def scrape_game(game_id: int, include_rosters: bool = False) -> pd.DataFrame:
    """
    Scrape NHL game data for a specific game and convert it to a DataFrame.

    Args:
        game_id (int): The game ID (e.g., 2024020762).
        include_rosters (bool): Whether to include roster information in the output. (default: False)

    Returns:
        pd.DataFrame: The scraped game data in a DataFrame.
    """
    # 1) HTML PBP (assumed to return (df_html, raw_html))
    df_html, _ = await scrape_html_pbp(game_id, return_raw=True)

    # Ensure HTML has the time column we’ll merge on
    # Many HTML parsers name this "Time". If it’s named differently, map it here.
    if "Time" not in df_html.columns and "timeInPeriod" in df_html.columns:
        df_html = df_html.rename(columns={"timeInPeriod": "Time"})
    if not {"Event", "Per", "Time"}.issubset(df_html.columns):
        missing = {"Event", "Per", "Time"} - set(df_html.columns)
        raise KeyError(f"df_html missing required columns: {missing}")

    # 2) API PBP
    data_api = scrapeGameAPI(game=game_id)

    # Flatten API plays
    pbp_df = pd.json_normalize(data_api.get("plays", []), sep=".")

    rosters_df = pd.json_normalize(data_api.get("rosterSpots", []), sep=".")

    # Compare teamId to homeTeam id, then cast the boolean Series to int
    home_id = data_api.get("homeTeam", {}).get("id")
    home_abbrev = data_api.get("homeTeam", {}).get("abbrev")
    away_abbrev = data_api.get("awayTeam", {}).get("abbrev")
    rosters_df["isHome"] = (rosters_df["teamId"] == home_id).astype(int)
    rosters_df['fullName'] = rosters_df['firstName.default'] + ' ' + rosters_df['lastName.default']

    # Strip nested prefixes; rename a couple of fields
    pbp_df.columns = (
        pbp_df.columns
        .str.replace(r"^details\.", "", regex=True)
        .str.replace(r"^periodDescriptor\.", "", regex=True)
    )
    pbp_df = pbp_df.rename(columns={"number": "period", "typeDescKey": "api_event"})
    pbp_df['isHome'] = (pbp_df['eventOwnerTeamId'] == home_id).astype(int)

    pbp_df['eventTeam'] = pbp_df['isHome'].map({1: home_abbrev, 0: away_abbrev})

    # Map API event descriptor -> HTML event code

    pbp_df["html_event"] = pbp_df["api_event"].map(event_mapping)

    # Make sure merge keys exist in API table
    required_api = {"html_event", "period", "timeInPeriod"}
    if not required_api.issubset(pbp_df.columns):
        missing = required_api - set(pbp_df.columns)
        raise KeyError(f"pbp_df missing required API merge columns: {missing}")

    # Normalize key types for merge
    # HTML: Event (str), Per (int/str), Time (mm:ss as str)
    # API:  html_event (str), period (int/str), timeInPeriod (mm:ss as str)
    df_html["Event"] = df_html["Event"].astype(str)
    df_html["Per"] = df_html["Per"].astype(str)
    df_html["Time"] = df_html["Time"].astype(str)

    pbp_df["html_event"] = pbp_df["html_event"].astype(str)
    pbp_df["period"] = pbp_df["period"].astype(str)
    pbp_df["timeInPeriod"] = pbp_df["timeInPeriod"].astype(str)

    # Fill SOG / score columns if present
    for col in ["awaySOG", "homeSOG", "homeScore", "awayScore"]:
        if col not in pbp_df.columns:
            pbp_df[col] = pd.NA
        pbp_df[col] = pbp_df[col].ffill().fillna(0).astype(int)
        
    # Create a merge idx on both dfs
    mask = df_html["Event"].isin(event_mapping.values())
    df_html.loc[mask, "merge_idx"] = np.arange(mask.sum())
    
    mask_api = pbp_df["html_event"].isin(event_mapping.values())  # or api_event col
    pbp_df.loc[mask_api, "merge_idx"] = np.arange(mask_api.sum())

    # Merge without overwriting either side first
    left_on = ["Event", "Per", "Time", "timeRemaining", "merge_idx"]
    right_on = ["html_event", "period", "timeInPeriod", "timeRemaining", "merge_idx"]

    # print(len(df_html))
    df = df_html.merge(
        pbp_df,
        left_on=left_on,
        right_on=right_on,
        how="left",
        suffixes=("", "_api")
    )
    # print(len(df))

    # print(df_html[left_on].value_counts().head())
    # print(pbp_df[right_on].value_counts().head())

    # Ensure unique column names
    df.columns = _dedup_cols(df.columns)

    # Map playerNumber to playerId
    home_on_ids = map_number_to_key(_["home_on_ice"], rosters_df.query('isHome == 1'), "playerId")
    away_on_ids = map_number_to_key(_["away_on_ice"], rosters_df.query('isHome == 0'), "playerId")
    homeGoalie_on_ids = map_number_to_key(_["home_goalie"], rosters_df.query('isHome == 1'), "playerId")
    awayGoalie_on_ids = map_number_to_key(_["away_goalie"], rosters_df.query('isHome == 0'), "playerId")

    # Map playerNumber to fullName
    home_on_full_names = map_number_to_key(_["home_on_ice"], rosters_df.query('isHome == 1'), "fullName")
    away_on_full_names = map_number_to_key(_["away_on_ice"], rosters_df.query('isHome == 0'), "fullName")
    homeGoalie_on_full_names = map_number_to_key(_["home_goalie"], rosters_df.query('isHome == 1'), "fullName")
    awayGoalie_on_full_names = map_number_to_key(_["away_goalie"], rosters_df.query('isHome == 0'), "fullName")
    
    
    # print(len(home_on_ids), len(away_on_ids), len(homeGoalie_on_ids), len(awayGoalie_on_ids), len(df_html))

    # Validate that lengths match
    for col in ["home_on_ids", "away_on_ids", "homeGoalie_on_ids", "awayGoalie_on_ids"]:
        if len(eval(col)) != len(df):
            raise ValueError(f"Length mismatch: {col} has {len(eval(col))} elements, df has {len(df)} rows")
        

    # Add them as columns
    df["home_on_id"] = home_on_ids
    df["away_on_id"] = away_on_ids
    df["homeGoalie_on_id"] = homeGoalie_on_ids
    df["awayGoalie_on_id"] = awayGoalie_on_ids

    df["home_on_full_name"] = home_on_full_names
    df["away_on_full_name"] = away_on_full_names
    df["homeGoalie_on_full_name"] = homeGoalie_on_full_names
    df["awayGoalie_on_full_name"] = awayGoalie_on_full_names
    
    # Add number of items in list per list
    df["home_on_count"] = df["home_on_id"].apply(len)
    df["away_on_count"] = df["away_on_id"].apply(len)
    df["homeGoalie_on_count"] = df["homeGoalie_on_id"].apply(len)
    df["awayGoalie_on_count"] = df["awayGoalie_on_id"].apply(len)
    
    # Example: columns with lists
    list_columns = [
        "home_on_full_name",
        "away_on_full_name",
        "homeGoalie_on_full_name",
        "awayGoalie_on_full_name",
        "home_on_id",
        "away_on_id",
        "homeGoalie_on_id",
        "awayGoalie_on_id"
    ]

   # Compute max_players using generator expressions for efficiency
    max_players = {
        col: max(len(x) if isinstance(x, list) else 0 for x in df[col])
        for col in list_columns
    }

    # Collect all expanded DataFrames to concatenate once
    expanded_dfs = []
    for col in list_columns:
        # Use list comprehension to handle non-lists efficiently
        lists = [x if isinstance(x, list) else [None] for x in df[col]]
        
        # Create the expanded DataFrame
        expanded_df = pd.DataFrame(lists, index=df.index)
        
        # Rename columns based on the actual number of columns created
        expanded_df.columns = [f"{col}_{i+1}" for i in range(len(expanded_df.columns))]
        
        expanded_dfs.append(expanded_df)

    # Perform a single concatenation
    if expanded_dfs:
        df = pd.concat([df] + expanded_dfs, axis=1)

    m = df['home_on_count'].gt(0) & df['away_on_count'].gt(0)

    # Ensure booleans once
    is_home = df['isHome'].astype(bool)

    # Build base string pieces ONCE (StringDtype handles NA nicely)
    home_str = df['home_on_count'].astype('Int64').astype('string')
    away_str = df['away_on_count'].astype('Int64').astype('string')

    # Add goalie asterisk where goalie_on_count == 0 (avoid repeated np.where)
    home_strength = home_str.mask(df['homeGoalie_on_count'].eq(0), home_str + '*')
    away_strength = away_str.mask(df['awayGoalie_on_count'].eq(0), away_str + '*')

    # Game strength (pick side with .where instead of two loc-writes)
    game_left  = home_str.where(is_home, away_str)
    game_right = away_str.where(is_home, home_str)
    game_str   = game_left.str.cat(game_right, sep='v')

    # Detailed game strength
    det_left  = home_strength.where(is_home, away_strength)
    det_right = away_strength.where(is_home, home_strength)
    det_str   = det_left.str.cat(det_right, sep='v')

    # Single assignment back; only where both counts > 0
    df.loc[m, ['home_strength', 'away_strength', 'gameStrength', 'detailedGameStrength']] = \
        pd.DataFrame({
            'home_strength': home_strength[m],
            'away_strength': away_strength[m],
            'gameStrength': game_str[m],
            'detailedGameStrength': det_str[m],
        })
    

    df = df.drop(columns=['Time:Elapsed Game'])

    event_columns = {
            "faceoff": ["winningPlayerId", "losingPlayerId"],
            "hit": ["hittingPlayerId", "hitteePlayerId"],
            "blocked-shot": ["shootingPlayerId", "blockingPlayerId"],
            "shot-on-goal": ["shootingPlayerId", None],
            "missed-shot": ["shootingPlayerId", None],
            "goal": [
                "scoringPlayerId",
                "assist1PlayerId",
                "assist2PlayerId",
            ],
            "giveaway": ["playerId", None],
            "takeaway": ["playerId", None],
            "penalty": [
                "committedByPlayerId",
                "drawnByPlayerId",
                "servedByPlayerId",
            ],
            "failed-shot-attempt": ["shootingPlayerId", None],
        }
        
    # ensure target cols exist once
    for c in ("player1Id", "player2Id", "player3Id"):
        if c not in df.columns:
            df[c] = pd.NA

    api = df["api_event"]

    # fill player*Id by event using vectorized masked assignment
    for event, cols in event_columns.items():
        m = api.eq(event)
        if not m.any():
            continue
        for i, src in enumerate(cols[:3], start=1):
            if src and src in df.columns:
                # .to_numpy() avoids index alignment overhead
                df.loc[m, f"player{i}Id"] = df.loc[m, src].to_numpy()

    # build name map once; keep dtype alignment for reliable mapping
    name_map = rosters_df.set_index("playerId")["fullName"]

    for i in (1, 2, 3):
        # optional: ensure nullable int dtype so ids aren’t floats from NaN
        df[f"player{i}Id"] = df[f"player{i}Id"].astype("Int64")
        df[f"player{i}Name"] = df[f"player{i}Id"].map(name_map)
        
    # # Add elapsedTime column
    # # Make sure [gameType, period, timeInPeriodSec] are int
    # for col in ["gameType", "Per", "timeInPeriodSec"]:
    #     df[col] = pd.to_numeric(df[col], errors='coerce', downcast='integer')
        
    # # Elapsed time calculation for non-playoff games non shootout periods
    # df.loc[(df["gameType"] != 3) & (df["Per"] != 5), "elapsedTime"] = (
    #     df["timeInPeriodSec"] + (df["Per"] - 1) * 60 * 20
    # )
    # # Elapsed time calculation for playoff games
    # df.loc[(df["gameType"] == 3), "elapsedTime"] = (
    #     df["timeInPeriodSec"] + (df["Per"] - 1) * 60 * 20
    # )
    # Safer dtypes
    df['gameType']        = pd.to_numeric(df['gameType'], errors='coerce').astype('Int8')   # small is fine
    df['Per']             = pd.to_numeric(df['Per'], errors='coerce').astype('Int16')       # or 'Int64'
    df['timeInPeriodSec'] = pd.to_numeric(df['timeInPeriodSec'], errors='coerce').astype('Int16')

    # Compute using int64 to avoid overflow
    per = df['Per'].astype('int64')
    tip = df['timeInPeriodSec'].astype('int64')

    # Non-playoff, non-SO periods
    df.loc[(df['gameType'] != 3) & (df['Per'] != 5), 'elapsedTime'] = tip + (per - 1) * 1200

    # Playoffs (20:00 OT)
    df.loc[df['gameType'] == 3, 'elapsedTime'] = tip + (per - 1) * 1200
        
    # # If some elapsedTime are negative raise error
    # if (df["elapsedTime"] < 0).any():
    #     print(df.loc[df["elapsedTime"] < 0] )
    #     raise ValueError("Negative elapsedTime found")

    # # If some elapsedTime are still NaN, raise error
    # if df["elapsedTime"].isna().any():
    #     print(df.loc[df["elapsedTime"].isna()])
    #     raise ValueError("NaN elapsedTime found")
    
    df['elapsedTime'] = df['elapsedTime'].fillna(0)  # Use nullable int for elapsedTime

    # Drop original list columns if you don't need them
    # df = df.drop(columns=list_columns)
    
    if include_rosters:
        return df, rosters_df
    else:
        return df

    

def map_number_to_key(list_of_lists, rosters_df, key):
    """
    Maps sweater numbers in a list of lists to a specified key from rosters_df.
    
    Args:
        list_of_lists (list): List containing sublists of sweater numbers.
        rosters_df (pd.DataFrame): DataFrame containing roster data with 'sweaterNumber' and key columns.
        key (str): Column name in rosters_df to map sweater numbers to.
    
    Returns:
        list: New list of lists with mapped values or original numbers if no mapping exists.
    """
    # Input validation
    if not isinstance(list_of_lists, list):
        print(f"⚠️ Expected list_of_lists to be a list, got {type(list_of_lists)}")
        return list_of_lists
    
    if rosters_df.empty:
        print("⚠️ rosters_df is empty, returning original list")
        return list_of_lists
    
    # Check if required columns exist
    if 'sweaterNumber' not in rosters_df.columns:
        print(f"⚠️ 'sweaterNumber' column not found in rosters_df. Available columns: {list(rosters_df.columns)}")
        return list_of_lists
    
    if key not in rosters_df.columns:
        print(f"⚠️ '{key}' column not found in rosters_df. Available columns: {list(rosters_df.columns)}")
        return list_of_lists
    
    try:
        # Create mapping with type conversion to handle both string and int numbers
        # Convert sweaterNumber to string for consistent lookup
        rosters_copy = rosters_df.copy()
        rosters_copy['sweaterNumber'] = rosters_copy['sweaterNumber'].astype(str)
        
        mapping = rosters_copy.set_index('sweaterNumber')[key].to_dict()
        
        # Map values using dictionary lookup with fallback to original item
        new_list = []
        for sublist in list_of_lists:
            if isinstance(sublist, list):
                mapped_sublist = []
                for item in sublist:
                    # Convert item to string for consistent lookup
                    item_str = str(item) if item is not None else ''
                    mapped_value = mapping.get(item_str, item)  # Fallback to original item
                    mapped_sublist.append(mapped_value)
                new_list.append(mapped_sublist)
            else:
                # Handle case where sublist is not actually a list
                print(f"⚠️ Expected sublist to be a list, got {type(sublist)}: {sublist}")
                new_list.append(sublist)
        
        return new_list
        
    except Exception as e:
        print(f"❌ Error in map_number_to_key: {e}")
        print(f"   rosters_df shape: {rosters_df.shape}")
        print(f"   list_of_lists type: {type(list_of_lists)}")
        if isinstance(list_of_lists, list) and len(list_of_lists) > 0:
            print(f"   first sublist: {list_of_lists[0]}")
        return list_of_lists
    

async def scrape_shifts(game_id):
    
    data = await scrapeHTMLShifts_async(game_id)
    data_parsed = parse_html_shifts(data['home'], data['away'])
    
    # 2) API PBP
    data_api = scrapeGameAPI(game=game_id)

    home_abbrev = data_api.get("homeTeam", {}).get("abbrev", "")
    away_abbrev = data_api.get("awayTeam", {}).get("abbrev", "")

    # Flatten API plays
    rosters_df = pd.json_normalize(data_api.get("rosterSpots", []), sep=".")
    home_shifts = pd.json_normalize(data_parsed['home']["shifts"])
    away_shifts = pd.json_normalize(data_parsed['away']["shifts"])
    shifts = pd.concat([home_shifts, away_shifts], )
    shifts = shifts.reset_index(drop=True)
    home_id = data_api.get("homeTeam", {}).get("id")
    rosters_df["isHome"] = (rosters_df["teamId"] == home_id).astype(int)
    rosters_df['fullName'] = rosters_df['firstName.default'] + ' ' + rosters_df['lastName.default']
    shifts['isHome'] = (shifts["team_type"] == 'Home').astype(int)
    
    shifts = shifts.merge(
        rosters_df,
        left_on=["jersey_number", "isHome"],
        right_on=["sweaterNumber", "isHome"],
        how="left"
    )
    # 1. Convert timeStrings to seconds
    for col in ['start_time_in_period', 'start_time_remaining', 'end_time_in_period', 'end_time_remaining']:
        shifts[f'{col}_seconds'] = shifts[col].apply(lambda x: time_str_to_seconds(x) if isinstance(x, str) else x)

    if data_api["gameType"] != 3:
        shifts['elapsed_time_start'] = np.where(
            shifts['period_number'] != 5,
            shifts['start_time_in_period_seconds'] + (shifts['period_number'] - 1) * 20 * 60,
            np.nan
        )
        shifts['elapsed_time_end'] = np.where(
            shifts['period_number'] != 5,
            shifts['end_time_in_period_seconds'] + (shifts['period_number'] - 1) * 20 * 60,
            np.nan
        )

    shifts["gameId"] = game_id

    else:
        shifts['elapsed_time_start'] = shifts['start_time_in_period_seconds'] + (shifts['period_number'] - 1) * 20 * 60
        shifts['elapsed_time_end'] = shifts['end_time_in_period_seconds'] + (shifts['period_number'] - 1) * 20 * 60

    return shifts

async def scrape_game_(game_id, include_shifts=False):
    
    pbp, shifts = await asyncio.gather(scrape_game(game_id=game_id), scrape_shifts(game_id=game_id))
    
    # # Build a lookup dictionary for all unique playerIds
    # unique_ids = shifts["playerId"].unique()
    # player_info_map = {pid: scrapePlayer(pid) for pid in unique_ids}

    # # Assign the shootsCatches column using the lookup
    # shifts = shifts.assign(
    #     shootsCatches=lambda x: x["playerId"].map(lambda pid: player_info_map[pid]["shootsCatches"])
    # )
    
    home_abbrev = pbp.query("isHome == 1")['eventTeam'].iloc[0]
    away_abbrev = pbp.query("isHome == 0")['eventTeam'].iloc[0]

  
    _shifts_events = shifts.pipe(build_shifts_events)
    
    _data = pd.concat([pbp, _shifts_events], ignore_index=True)

    #PBP manipulations
    sort_dict = {
        "PGSTR": 1, "PGEND": 2, "ANTHEM": 3, "EGT": 3, "CHL": 3, "DELPEN": 3,
        "BLOCK": 3, "GIVE": 3, "HIT": 3, "MISS": 3, "SHOT": 3, "TAKE": 3,
        "GOAL": 5, "STOP": 6, "PENL": 7, "PBOX": 7, "PSTR": 7, "ON": 8, "OFF": 8,
        "EISTR": 9, "EIEND": 10, "FAC": 12, "PEND": 13, "SOC": 14, "GEND": 15, "GOFF": 16
    }

    _data['Priority'] = _data['Event'].map(sort_dict).fillna(99).astype(int)
    # numeric jersey number (NaN for ON/OFF etc.)
    _data['num'] = pd.to_numeric(_data['#'], errors='coerce')

    # True if has jersey number
    _data['has_num'] = _data['num'].notna()

    _data['priority_for_sort'] = np.where(_data['has_num'], 0, _data['Priority'])

    _data = _data.sort_values(
        by=['elapsedTime',  'Priority', 'Str',],
        ascending=[True,  True,      True,   ],
        kind='mergesort'   # stable, preserves upstream order for perfect ties
    )

    _data = _data.drop(columns=['Priority', 'num', 'has_num', 'priority_for_sort'])


    # Shift 
    # 1) Build faceoff context from FAC rows
    fac_cols = ['elapsedTime', 'zoneCode', 'isHome', 'x_normalized', 'y_normalized']  # adjust casing if needed
    fac = _data[_data['Event'] == 'FAC'][fac_cols].rename(columns={
        'zoneCode': 'fac_zone', 'isHome': 'fac_isHome', 'x_normalized': 'fac_x', 'y_normalized': 'fac_y'
    }).sort_values('elapsedTime').drop_duplicates(['elapsedTime'], keep='first').assign(Event='ON')

    # 5) Merge onto ON rows at the same time/period
    _data = _data.merge(fac, on=['elapsedTime', 'Event'], how='left')

    _data['zoneStartType'] = pd.Series(index=_data.index, dtype='string')

    _data.loc[(_data['fac_zone'].isna() & _data['Event'].eq('ON')), "zoneStartType"] = 'OTF'
    # # optional: init dtype

    mask_base = _data['fac_zone'].notna() & _data['Event'].eq('ON')
    # (optional) only tag ON rows:
    # mask_base &= _data['Event'].eq('ON')
    same_team_off = _data['fac_isHome'].eq(_data['isHome']) & _data['fac_zone'].eq('O') 
    opp_team_def  = _data['fac_isHome'].ne(_data['isHome']) & _data['fac_zone'].eq('D') 

    _data.loc[mask_base & (same_team_off | opp_team_def), 'zoneStartType'] = 'OZS'

    same_team_off_DZ = _data['fac_isHome'].eq(_data['isHome']) & _data['fac_zone'].eq('D') 
    opp_team_def_DZ  = _data['fac_isHome'].ne(_data['isHome']) & _data['fac_zone'].eq('O')
    _data.loc[mask_base & (same_team_off_DZ | opp_team_def_DZ), 'zoneStartType'] = 'DZS'

    _data.loc[mask_base & _data['fac_zone'].eq('N'), 'zoneStartType'] = 'NZS'

    # Zone start mask base
    zs_mask_base = _data['zoneStartType'].isin(['OZS', 'DZS', 'NZS'])

    flip_coords_mask = _data['fac_isHome'].ne(_data['isHome']) & _data['zoneStartType'].isin(['OZS', 'DZS'])
    _data.loc[flip_coords_mask, ['fac_x', 'fac_y']] *= -1

    def faceoff_dot_name_vec(fac_x, fac_y):
        center_mask = (fac_x == 0) & (fac_y == 0)
        oz_mask = fac_x > 60
        dz_mask = fac_x < -60
        side = np.where(fac_y > 0, "L", "R")
        
        zone = np.select(
            [center_mask, oz_mask, dz_mask],
            ["Center", "OZ-" + side, "DZ-" + side],
            default="NZ-" + side
        )
        return zone
    # Apply faceoff dot naming to zone start rows
    _data.loc[zs_mask_base, "dot_name"] = faceoff_dot_name_vec(
    _data.loc[zs_mask_base, "fac_x"], 
    _data.loc[zs_mask_base, "fac_y"]
    )

    _data.loc[zs_mask_base, 'x_normalized'] = _data.loc[zs_mask_base, 'fac_x']
    _data.loc[zs_mask_base, 'y_normalized'] = _data.loc[zs_mask_base, 'fac_y']

    _data = _data.drop(columns=['fac_x', 'fac_y', 'fac_zone', 'fac_isHome', 'merge_idx'])

    fill_cols = ['gameId', 'venue', 'venueLocation', 'scrapedOn', 'source', 'gameDate', 
             'gameType', 'startTimeUTC', 'easternUTCOffset', 'venueUTCOffset', 
             'maxRegulationPeriods', 'awayScore', 'homeScore', 'awaySOG', 'homeSOG', 'Str']
    _data[fill_cols] = _data[fill_cols].bfill()

    _data.loc[_data['isHome'] == 1, 'eventTeam'] = home_abbrev
    _data.loc[_data['isHome'] == 0, 'eventTeam'] = away_abbrev
    
    _data['homeTeam'] = home_abbrev
    _data['awayTeam'] = away_abbrev
    
    _data = _data.merge(
        shifts.rename(columns={'playerId': 'player1Id'}).assign(
            isGoalie = shifts['positionCode'].eq('G')
        )[['player1Id', 'isGoalie']],
        on='player1Id',
        how='left'
    )
    _data = (_data
             .drop_duplicates(subset=['player1Id', 'player1Name', 'isHome', 'eventOwnerTeamId', 'eventTeam', 'elapsedTime', 'Event', 'isGoalie'])
             .drop(columns=['period'])
             .rename(columns={
                 'eventOwnerTeamId': 'teamId',
                 'Per': 'period',
                 'Str': 'strength',
                 'api_event' : 'event_api'
             }))

    if include_shifts:
        return _data, shifts

    else:
        return _data

  # Shifts manipulations
def build_shifts_events(shifts):
    names_cols = [name for name in shifts.columns if name.startswith('firstName.') or name.startswith('lastName.')]
    shifts = shifts.drop(columns=['start_time_elapsed_game', 'end_time_elapsed_game'] + names_cols)
    
    on_cols = {
        # 'start_time_in_period': 'Time',
        'start_time_in_period_seconds': 'timeInPeriodSec',
        'start_time_remaining_seconds': 'timeRemainingSec',
        'start_time_remaining': 'timeRemaining',
        'start_time_in_period': 'timeInPeriod',
        'elapsed_time_start': 'elapsedTime'
    }
    off_cols = {
        # 'end_time_in_period': 'Time',
        'end_time_in_period_seconds': 'timeInPeriodSec',
        'end_time_remaining_seconds': 'timeRemainingSec',
        'end_time_remaining' : 'timeRemaining',
        'end_time_in_period': 'timeInPeriod',
        'elapsed_time_end': 'elapsedTime'
    }

    # ON events
    on_df = shifts.rename(columns=on_cols).assign(Event='ON')
    on_df['Time'] = on_df['timeInPeriod']
    
    # OFF events
    off_df = shifts.rename(columns=off_cols).assign(Event='OFF')
    off_df['Time'] = off_df['timeInPeriod']

    # Shared renames
    shared = {
        'period_number': 'Per',
        'teamId': 'eventOwnerTeamId',
        'playerId': 'player1Id',
        'fullName': 'player1Name'
    }
    df = pd.concat([on_df, off_df], ignore_index=True).rename(columns=shared)
    df = df.drop(columns=['start_time_remaining', 'end_time_in_period', 'end_time_remaining',
                        'end_time_in_period_seconds', 'end_time_remaining_seconds', 'elapsed_time_end',
                        'start_time_in_period_seconds', 'start_time_remaining_seconds',
                        'elapsed_time_start', 'start_time_in_period'])
    
    ## PROBLEM IS THAT THE ON CAN BE AT THE SAME TIME AS THE OFF
    return df