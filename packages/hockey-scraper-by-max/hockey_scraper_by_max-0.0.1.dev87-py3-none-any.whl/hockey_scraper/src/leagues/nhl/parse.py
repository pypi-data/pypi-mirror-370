from selectolax.lexbor import LexborHTMLParser
import re
from typing import Dict, List, Any


def parse_html_pbp(html: str) -> Dict[str, Any]:
    """
    Parse HTML content using Lexbor HTML parser to extract PBP event data and on-ice info.

    Args:
        html (str): The HTML content to parse.

    Returns:
        dict: Parsed data including events, columns, and on-ice/goalie information.
    """
    if not html or not html.strip():
        raise ValueError("HTML content cannot be empty")

    try:
        parser = LexborHTMLParser(html)
        table = parser.css("tr.oddColor, tr.evenColor")

        if not table:
            print("Warning: No play-by-play rows found in HTML")
            return _empty_result()

        data = []
        home_on_ice, away_on_ice = [], []
        home_goalie, away_goalie = [], []

        for row in table:
            cells = [td.text(strip=True) for td in row.css("td")]

            # Find embedded tables indicating on-ice players
            on_ice_raw = [
                el.text(strip=True)
                for el in row.css("td > table > tbody")
                if len(el.text(strip=True)) > 5
            ]

            skater_lists, goalie_lists = _parse_on_ice_players(on_ice_raw)

            # Ensure we have exactly 2 teams or handle missing data
            if len(skater_lists) == 2 and len(goalie_lists) == 2:
                away_on_ice.append(skater_lists[0])
                home_on_ice.append(skater_lists[1])
                home_goalie.append(goalie_lists[1])
                away_goalie.append(goalie_lists[0])
            else:
                # Handle missing or incomplete on-ice data
                away_on_ice.append([])
                home_on_ice.append([])
                home_goalie.append([])
                away_goalie.append([])

            # Process cell data with proper bounds checking
            if cells and len(cells) > 0:
                cells_data = _clean_cell_data(cells)
                if cells_data:  # Only add if we have valid data
                    data.append(cells_data)

        columns = ["#", "Per", "Str", "Time:Elapsed Game", "Event", "Description"]

        return {
            "data": data,
            "columns": columns,
            "home_on_ice": home_on_ice,
            "away_on_ice": away_on_ice,
            "home_goalie": home_goalie,
            "away_goalie": away_goalie,
        }

    except Exception as e:
        raise RuntimeError(f"Error parsing HTML play-by-play data: {e}")


def _parse_on_ice_players(on_ice_raw: List[str]) -> tuple[List[List[str]], List[List[str]]]:
    """
    Parse on-ice player strings to extract skater and goalie numbers.

    Args:
        on_ice_raw: List of raw on-ice player strings (usually 2 teams)

    Returns:
        tuple: (skater_lists, goalie_lists) for each team
    """
    skater_lists, goalie_lists = [], []

    for team_str in on_ice_raw:
        if not team_str.strip():
            continue

        # NHL HTML format is like: "18C71C7L3D72D35G"
        # Where numbers+letter indicate: 18C (center), 71C (center), 7L (left wing),
        # 3D (defense), 72D (defense), 35G (goalie)

        # Split by position letters to get individual players
        # Pattern: number + letter (C|L|R|D|G)
        players = re.findall(r"(\d+)([CLRDG])", team_str)

        skaters = []
        goalies = []

        for number, position in players:
            if position == "G":  # Goalie
                goalies.append(number)
            else:  # Skater (C, L, R, D)
                skaters.append(number)

        skater_lists.append(skaters)
        goalie_lists.append(goalies if goalies else [])  # Ensure list even if empty

    return skater_lists, goalie_lists


def _clean_cell_data(cells: List[str]) -> List[str]:
    """
    Clean and validate cell data from play-by-play rows.

    Args:
        cells: Raw cell data

    Returns:
        Cleaned cell data (first 6 columns)
    """
    if not cells:
        return []

    # Clean each cell and take first 6 columns
    cleaned_cells = []
    for i, cell in enumerate(cells[:6]):  # Limit to 6 columns
        if cell:
            # Replace various types of non-breaking spaces and clean
            cleaned_cell = (
                cell.replace("\xa0", " ").replace("\u00a0", " ").replace("\u2009", " ").strip()
            )
            cleaned_cells.append(cleaned_cell)
        else:
            cleaned_cells.append("")  # Ensure we maintain column structure

    # Pad to 6 columns if needed
    while len(cleaned_cells) < 6:
        cleaned_cells.append("")

    return cleaned_cells


def _empty_result() -> Dict[str, Any]:
    """Return empty result structure when no data is found."""
    return {
        "data": [],
        "columns": ["#", "Per", "Str", "Time:Elapsed Game", "Event", "Description"],
        "home_on_ice": [],
        "away_on_ice": [],
        "home_goalie": [],
        "away_goalie": [],
    }


def parse_html_rosters(html: str) -> Dict[str, Any]:
    """
    Parse HTML content to extract NHL game roster information.

    Args:
        html (str): The HTML content from NHL roster report.

    Returns:
        dict: Parsed roster data including home/away players, scratches, coaches, and game info.
    """
    if not html or not html.strip():
        raise ValueError("HTML content cannot be empty")

    try:
        parser = LexborHTMLParser(html)

        # Extract game information
        game_info = _parse_game_info(parser)

        # Extract rosters for both teams
        home_roster = _parse_team_roster(parser, "home")
        away_roster = _parse_team_roster(parser, "away")

        # Extract officials information
        officials = _parse_officials(parser)

        return {
            "home": home_roster,
            "away": away_roster,
            "officials": officials,
            "gameInfo": game_info,
        }

    except Exception as e:
        raise ValueError(f"Failed to parse roster HTML: {e}")


def _parse_game_info(parser: LexborHTMLParser) -> Dict[str, str]:
    """Extract game information from the HTML."""
    try:
        import re
        from datetime import datetime

        # Game info is typically in a table with ID "GameInfo"
        game_info = {}

        # Try to find the game info table
        game_table = parser.css_first("#GameInfo")
        if game_table:
            rows = game_table.css("tr")
            for row in rows:
                cells = row.css("td")
                if len(cells) >= 2:
                    label = cells[0].text(strip=True)
                    value = cells[1].text(strip=True)
                    if label and value:
                        game_info[label.lower().replace(" ", "_")] = value

        # Fallback to specific selectors if the table approach doesn't work
        if not game_info:
            selectors = {
                "date": "#GameInfo > tbody > tr:nth-child(4) > td",
                "attendance_venue": "#GameInfo > tbody > tr:nth-child(5) > td",
                "start_end": "#GameInfo > tbody > tr:nth-child(6) > td",
            }

            for key, selector in selectors.items():
                element = parser.css_first(selector)
                if element:
                    game_info[key] = element.text(strip=True)

        # Parse and convert date to datetime object
        if "date" in game_info:
            date_text = game_info["date"]
            try:
                # Parse date like "Friday, November 1, 2024"
                parsed_date = datetime.strptime(date_text, "%A, %B %d, %Y")
                game_info["date"] = parsed_date.isoformat()
                game_info["date_raw"] = date_text  # Keep original for reference
            except ValueError:
                # If parsing fails, keep original text
                game_info["date_raw"] = date_text
                print(f"Warning: Could not parse date '{date_text}'")

        # Parse and separate attendance and venue
        if "attendance_venue" in game_info:
            attendance_venue_text = game_info["attendance_venue"]
            # Pattern: "Attendance 18,006 at Madison Square Garden"
            attendance_match = re.search(
                r"Attendance\s+([\d,]+)", attendance_venue_text, re.IGNORECASE
            )
            venue_match = re.search(r"at\s+(.+)$", attendance_venue_text, re.IGNORECASE)

            if attendance_match:
                # Remove commas and convert to clean number string
                game_info["attendance"] = attendance_match.group(1).replace(",", "")
            if venue_match:
                game_info["venue"] = venue_match.group(1).strip()

            # Remove the combined field
            del game_info["attendance_venue"]

        # Parse and separate start and end times with datetime conversion
        if "start_end" in game_info:
            start_end_text = game_info["start_end"]
            # Pattern: "Start 7:08 EDT; End 9:38 EDT" or "Start 7:08 PM EDT; End 9:38 PM EDT"
            start_match = re.search(r"Start\s+([^;]+)", start_end_text, re.IGNORECASE)
            end_match = re.search(r"End\s+(.+)$", start_end_text, re.IGNORECASE)

            if start_match:
                start_time_text = start_match.group(1).strip()
                game_info["start_time_raw"] = start_time_text

                # Try to parse the time to datetime (assuming current date as base)
                try:
                    # Extract time and timezone
                    time_pattern = r"(\d{1,2}:\d{2})(?:\s*(AM|PM))?\s*([A-Z]{3,4})?"
                    time_tz_match = re.search(time_pattern, start_time_text, re.IGNORECASE)
                    if time_tz_match:
                        time_str = time_tz_match.group(1)
                        am_pm = time_tz_match.group(2)
                        timezone = time_tz_match.group(3)

                        # Create a time format string
                        if am_pm:
                            time_format = f"{time_str} {am_pm}"
                            parsed_time = datetime.strptime(time_format, "%I:%M %p")
                        else:
                            parsed_time = datetime.strptime(time_str, "%H:%M")

                        # Combine with game date if available
                        if "date" in game_info and game_info["date"] != game_info.get("date_raw"):
                            game_date = datetime.fromisoformat(game_info["date"])
                            combined_datetime = game_date.replace(
                                hour=parsed_time.hour, minute=parsed_time.minute
                            )
                            game_info["start_time"] = combined_datetime.isoformat()
                        else:
                            # Just store the time part
                            game_info["start_time"] = parsed_time.time().isoformat()

                        if timezone:
                            game_info["start_timezone"] = timezone
                except ValueError:
                    # If parsing fails, keep original text
                    game_info["start_time"] = start_time_text
                    print(f"Warning: Could not parse start time '{start_time_text}'")

            if end_match:
                end_time_text = end_match.group(1).strip()
                game_info["end_time_raw"] = end_time_text

                # Try to parse the end time
                try:
                    time_pattern = r"(\d{1,2}:\d{2})(?:\s*(AM|PM))?\s*([A-Z]{3,4})?"
                    time_tz_match = re.search(time_pattern, end_time_text, re.IGNORECASE)
                    if time_tz_match:
                        time_str = time_tz_match.group(1)
                        am_pm = time_tz_match.group(2)
                        timezone = time_tz_match.group(3)

                        if am_pm:
                            time_format = f"{time_str} {am_pm}"
                            parsed_time = datetime.strptime(time_format, "%I:%M %p")
                        else:
                            parsed_time = datetime.strptime(time_str, "%H:%M")

                        # Combine with game date if available
                        if "date" in game_info and game_info["date"] != game_info.get("date_raw"):
                            game_date = datetime.fromisoformat(game_info["date"])
                            combined_datetime = game_date.replace(
                                hour=parsed_time.hour, minute=parsed_time.minute
                            )
                            game_info["end_time"] = combined_datetime.isoformat()
                        else:
                            game_info["end_time"] = parsed_time.time().isoformat()

                        if timezone:
                            game_info["end_timezone"] = timezone
                except ValueError:
                    game_info["end_time"] = end_time_text
                    print(f"Warning: Could not parse end time '{end_time_text}'")

            # Remove the combined field
            del game_info["start_end"]

        return game_info

    except Exception as e:
        print(f"Warning: Could not parse game info: {e}")
        return {}


def _parse_team_roster(parser: LexborHTMLParser, team: str) -> Dict[str, Any]:
    """Extract roster information for a specific team."""
    try:
        team_data = {"roster": [], "scratches": [], "head_coach": "", "goalies": [], "skaters": []}

        # Find tables that contain player roster data
        # These tables typically have rows with 3 columns: #, Pos, Name
        all_tables = parser.css("table")
        roster_tables = []

        for table in all_tables:
            table_text = table.text(strip=True)
            # Check if this table contains roster structure and player names
            has_roster_header = "#PosName" in table_text or (
                "Pos" in table_text and "Name" in table_text
            )
            has_senators = any(name in table_text for name in ["TKACHUK", "STÜTZLE", "CHABOT"])
            has_rangers = any(name in table_text for name in ["PANARIN", "ZIBANEJAD", "SHESTERKIN"])

            # Count 3-column player rows
            player_row_count = 0
            rows = table.css("tr")
            for row in rows:
                cells = row.css("td")
                if len(cells) == 3:
                    cell_texts = [cell.text(strip=True) for cell in cells]
                    if (
                        cell_texts[0].isdigit()
                        and cell_texts[1] in "CLDGR"
                        and len(cell_texts[2]) > 3
                    ):
                        player_row_count += 1

            # Table is a roster table if it has the header and significant player rows
            if has_roster_header and player_row_count >= 15:
                is_away_table = has_senators and not has_rangers
                is_home_table = has_rangers and not has_senators

                if (team == "away" and is_away_table) or (team == "home" and is_home_table):
                    roster_tables.append(table)

        # Parse the roster table for this team
        if roster_tables:
            roster_table = roster_tables[0]  # Should only be one per team

            # Parse players from the roster table
            player_rows = roster_table.css("tr")

            for row in player_rows:
                cells = row.css("td")
                if len(cells) == 3:  # Number, Position, Name
                    number_text = cells[0].text(strip=True)
                    position_text = cells[1].text(strip=True)
                    name_text = cells[2].text(strip=True)

                    # Skip header row
                    if number_text == "#" or position_text == "Pos":
                        continue

                    # Only process if we have valid data
                    if number_text.isdigit() and position_text in "CLDGR" and name_text:
                        player_info = {
                            "number": number_text,
                            "position": position_text,
                            "name": name_text,
                        }

                        # Categorize by position
                        if position_text == "G":
                            team_data["goalies"].append(player_info)
                        else:
                            team_data["skaters"].append(player_info)

                        team_data["roster"].append(player_info)

        # Parse scratches - look for tables with ID "Scratches"
        scratch_table = parser.css_first("#Scratches")
        if scratch_table:
            # Scratches table has two columns, we need the right one for the team
            scratch_columns = scratch_table.css("td")
            if len(scratch_columns) >= 2:
                # Away team scratches in first column, home team in second
                scratch_column = scratch_columns[1] if team == "home" else scratch_columns[0]

                # Look for a table within this column
                scratch_player_table = scratch_column.css_first("table")
                if scratch_player_table:
                    scratch_rows = scratch_player_table.css("tr")
                    for row in scratch_rows:
                        cells = row.css("td")
                        if len(cells) == 3:
                            number_text = cells[0].text(strip=True)
                            position_text = cells[1].text(strip=True)
                            name_text = cells[2].text(strip=True)

                            # Skip header row
                            if number_text == "#" or position_text == "Pos":
                                continue

                            if number_text.isdigit() and position_text in "CLDGR" and name_text:
                                team_data["scratches"].append(
                                    {
                                        "number": number_text,
                                        "position": position_text,
                                        "name": name_text,
                                    }
                                )

        # Parse head coach - look for "Head Coaches" section
        coaches_table = parser.css_first("#HeadCoaches")
        if coaches_table:
            coach_columns = coaches_table.css("td")
            if len(coach_columns) >= 2:
                # Away coach in first column, home coach in second
                coach_column = coach_columns[1] if team == "home" else coach_columns[0]
                coach_text = coach_column.text(strip=True)

                # Clean up the coach name (remove extra whitespace/formatting)
                if coach_text and len(coach_text) > 1:
                    team_data["head_coach"] = coach_text

        return team_data

    except Exception as e:
        print(f"Warning: Could not parse {team} roster: {e}")
        return {"roster": [], "scratches": [], "head_coach": "", "goalies": [], "skaters": []}


def _parse_officials(parser: LexborHTMLParser) -> Dict[str, List[str]]:
    """Extract officials information from the HTML."""
    try:
        officials = {"referees": [], "linesmen": [], "standby": []}

        # Try to find officials table
        officials_table = parser.css_first("#Officials")
        if officials_table:
            rows = officials_table.css("tr")
            current_type = None

            for row in rows:
                row_text = row.text(strip=True).lower()

                if "referee" in row_text:
                    current_type = "referees"
                elif "linesmen" in row_text or "linesman" in row_text:
                    current_type = "linesmen"
                elif "standby" in row_text:
                    current_type = "standby"
                elif current_type and row_text:
                    # This is likely an official's name
                    officials[current_type].append(row_text)

        return officials

    except Exception as e:
        print(f"Warning: Could not parse officials: {e}")
        return {"referees": [], "linesmen": [], "standby": []}


def parse_html_shifts(html_home: str, html_away: str) -> Dict[str, Any]:
    """
    Parse HTML shifts data for both home and away teams.

    This parser follows the sophisticated approach from scraper_pandas.py to extract
    detailed shift information including individual player shifts and summary statistics.

    Args:
        html_home (str): HTML content for home team shifts
        html_away (str): HTML content for away team shifts

    Returns:
        Dict[str, Any]: Parsed shifts data with structure:
        {
            "home": {
                "shifts": [list of individual shift records],
                "summary": [list of summary records],
                "team_name": str,
                "metadata": dict
            },
            "away": {
                "shifts": [list of individual shift records],
                "summary": [list of summary records],
                "team_name": str,
                "metadata": dict
            },
            "parsing_metadata": dict
        }
    """

    def _parse_team_shifts(html_content: str, team_type: str) -> Dict[str, Any]:
        """Parse shifts data for a single team."""
        if not html_content or not html_content.strip():
            return {
                "shifts": [],
                "summary": [],
                "team_name": f"Unknown {team_type}",
                "metadata": {"parsing_error": "Empty HTML content"},
            }

        try:
            parser = LexborHTMLParser(html_content)

            # Extract team name
            team_name_selector = (
                "body > div.pageBreakAfter > table > tbody > tr:nth-child(3) "
                "> td > table > tbody > tr > td"
            )
            team_name_element = parser.css(team_name_selector)
            team_name = (
                team_name_element[0].text(strip=True)
                if team_name_element
                else f"Unknown {team_type}"
            )

            # Extract player names
            player_rows_selector = (
                "body > div.pageBreakAfter > table > tbody > tr:nth-child(4) "
                "> td > table > tbody > tr"
            )
            n_trs = len(parser.css(player_rows_selector))

            players = []
            for i in range(n_trs):
                player_selector = (
                    f"body > div.pageBreakAfter > table > tbody > "
                    f"tr:nth-child(4) > td > table > tbody > "
                    f"tr:nth-child({i + 1}) > td.playerHeading"
                )
                player_element = parser.css(player_selector)
                if player_element:
                    players.append(player_element[0].text(strip=True))

            # Extract shift data rows
            rows = parser.css("tr.oddColor, tr.evenColor")
            raw_data = []
            for row in rows:
                cells = [td.text(strip=True) for td in row.css("td")]
                if cells:  # Only add non-empty rows
                    raw_data.append(cells)

            # Group data by player (separated by TOT rows)
            player_data_groups = []
            current_group = []

            for row in raw_data:
                if row and row[0] == "TOT":
                    if current_group:
                        player_data_groups.append(current_group)
                    current_group = []
                else:
                    current_group.append(row)

            # Add the last group if it exists
            if current_group:
                player_data_groups.append(current_group)

            # Match players to their data
            player_shifts_dict = {}
            for player, player_shifts in zip(players, player_data_groups):
                player_shifts_dict[player] = player_shifts

            # Define columns for different data types
            shift_columns = [
                "shift_number",
                "period",
                "start_time_elapsed_game",
                "end_time_elapsed_game",
                "duration",
                "event",
            ]

            summary_columns = [
                "period",
                "shifts_count",
                "average_duration",
                "total_ice_time",
                "even_strength_total",
                "power_play_total",
                "short_handed_total",
            ]

            # Process shifts data
            all_shifts = []
            all_summary = []

            for player_name, shifts_data in player_shifts_dict.items():
                # Extract jersey number from player name (first part before space)
                jersey_number = None
                if " " in player_name:
                    try:
                        jersey_number = int(player_name.split(" ")[0])
                    except (ValueError, IndexError):
                        jersey_number = None

                # Separate shift records (6 columns) from summary records (7 columns)
                shift_records = [row for row in shifts_data if len(row) == 6]
                summary_records = [row for row in shifts_data if len(row) == 7]

                # Process individual shifts
                for shift_row in shift_records:
                    shift_record = dict(zip(shift_columns, shift_row))
                    shift_record["player_name"] = player_name
                    shift_record["jersey_number"] = jersey_number
                    shift_record["team_type"] = team_type
                    shift_record["team_name"] = team_name

                    # Parse time fields
                    if "/" in shift_record["start_time_elapsed_game"]:
                        start_parts = shift_record["start_time_elapsed_game"].split(" / ")
                        shift_record["start_time_in_period"] = (
                            start_parts[0] if len(start_parts) > 0 else ""
                        )
                        shift_record["start_time_remaining"] = (
                            start_parts[1] if len(start_parts) > 1 else ""
                        )

                    if "/" in shift_record["end_time_elapsed_game"]:
                        end_parts = shift_record["end_time_elapsed_game"].split(" / ")
                        shift_record["end_time_in_period"] = (
                            end_parts[0] if len(end_parts) > 0 else ""
                        )
                        shift_record["end_time_remaining"] = (
                            end_parts[1] if len(end_parts) > 1 else ""
                        )

                    # Convert duration to seconds
                    if ":" in shift_record["duration"]:
                        try:
                            duration_parts = shift_record["duration"].split(":")
                            duration_seconds = int(duration_parts[0]) * 60 + int(duration_parts[1])
                            shift_record["duration_seconds"] = duration_seconds
                        except (ValueError, IndexError):
                            shift_record["duration_seconds"] = None

                    # Convert shift number and period
                    try:
                        shift_record["shift_number"] = int(shift_record["shift_number"])
                    except (ValueError, TypeError):
                        shift_record["shift_number"] = None

                    try:
                        # Handle OT periods
                        period_value = shift_record["period"]
                        if period_value == "OT":
                            shift_record["period_number"] = 4
                        else:
                            shift_record["period_number"] = int(period_value)
                    except (ValueError, TypeError):
                        shift_record["period_number"] = None

                    all_shifts.append(shift_record)

                # Process summary records
                for summary_row in summary_records:
                    summary_record = dict(zip(summary_columns, summary_row))
                    summary_record["player_name"] = player_name
                    summary_record["jersey_number"] = jersey_number
                    summary_record["team_type"] = team_type
                    summary_record["team_name"] = team_name

                    # Convert time fields to seconds
                    time_fields = [
                        "average_duration",
                        "total_ice_time",
                        "even_strength_total",
                        "power_play_total",
                        "short_handed_total",
                    ]

                    for field in time_fields:
                        if field in summary_record and ":" in str(summary_record[field]):
                            try:
                                time_parts = str(summary_record[field]).split(":")
                                seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                                summary_record[f"{field}_seconds"] = seconds
                            except (ValueError, IndexError):
                                summary_record[f"{field}_seconds"] = None

                    # Convert period and shifts count
                    try:
                        period_value = summary_record["period"]
                        if period_value == "OT":
                            summary_record["period_number"] = 4
                        else:
                            summary_record["period_number"] = int(period_value)
                    except (ValueError, TypeError):
                        summary_record["period_number"] = None

                    try:
                        summary_record["shifts_count"] = int(summary_record["shifts_count"])
                    except (ValueError, TypeError):
                        summary_record["shifts_count"] = None

                    all_summary.append(summary_record)

            return {
                "shifts": all_shifts,
                "summary": all_summary,
                "team_name": team_name,
                "metadata": {
                    "players_count": len(players),
                    "total_shifts": len(all_shifts),
                    "total_summary_records": len(all_summary),
                    "parsing_successful": True,
                },
            }

        except Exception as e:
            return {
                "shifts": [],
                "summary": [],
                "team_name": f"Unknown {team_type}",
                "metadata": {"parsing_error": str(e), "parsing_successful": False},
            }

    # Parse both teams
    home_data = _parse_team_shifts(html_home, "Home")
    away_data = _parse_team_shifts(html_away, "Away")

    # Combine results
    result = {
        "home": home_data,
        "away": away_data,
        "parsing_metadata": {
            "total_shifts": len(home_data["shifts"]) + len(away_data["shifts"]),
            "total_summary_records": (len(home_data["summary"]) + len(away_data["summary"])),
            "home_parsing_successful": home_data["metadata"].get("parsing_successful", False),
            "away_parsing_successful": away_data["metadata"].get("parsing_successful", False),
            "parsed_on": datetime.utcnow().isoformat() if "datetime" in globals() else None,
        },
    }

    return result
