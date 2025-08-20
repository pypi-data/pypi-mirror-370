import numpy as np
import pandas as pd

from itertools import combinations
from collections import defaultdict, Counter


# ============================================================
# 0) Build the on-ice matrix (keep as you had, with tiny fixes)
# ============================================================
def seconds_matrix(df: pd.DataFrame, shifts: pd.DataFrame) -> pd.DataFrame:
    """
    Boolean on-ice matrix by second.
    Index (MultiIndex): player1Id, player1Name, isHome, teamId, eventTeam, isGoalie, positionCode
    Columns: 0..max_sec-1 (seconds)
    """
    # ensure ints
    game_length = int(pd.to_numeric(df["elapsedTime"], errors="coerce").max())
    base = (
        df.query("Event in ['ON','OFF']")[[
            "player1Id","player1Name","isHome","teamId","eventTeam","elapsedTime","Event","isGoalie","period"
        ]]
        .assign(elapsedTime=lambda x: pd.to_numeric(x["elapsedTime"], errors="coerce").astype("Int32"))
        .sort_values(["player1Id","elapsedTime","period"])
    )

    intervals = (
        base.assign(
            endTime=lambda x: x.groupby(
                ["player1Id","player1Name","isHome","teamId","eventTeam","isGoalie"]
            )["elapsedTime"].transform(lambda s: s.shift(-1).fillna(game_length))
        )
        .query("Event == 'ON'")
        .merge(
            shifts[["playerId","positionCode"]].drop_duplicates().rename(columns={"playerId":"player1Id"}),
            on="player1Id", how="left"
        )
    )

    # index
    idx_cols = ["player1Id","player1Name","isHome","teamId","eventTeam","isGoalie","positionCode"]
    player_index = (
        intervals[idx_cols].drop_duplicates().set_index(idx_cols).sort_index().index
    )
    max_sec = int(intervals["endTime"].max())

    mat = pd.DataFrame(False, index=player_index, columns=range(max_sec), dtype=bool)

    # fill
    for _ , r in intervals.iterrows():
        row_key = (r["player1Id"], r["player1Name"], r["isHome"], r["teamId"], r["eventTeam"], r["isGoalie"], r["positionCode"])
        start = int(r["elapsedTime"])
        end   = int(r["endTime"])
        if end > start:
            mat.loc[row_key, start:end-1] = True
    return mat


# ============================================================
# 1) Strengths per second (SKATERS ONLY counts + separate goalie counts)
# ============================================================
def strengths_by_second(matrix_df: pd.DataFrame, sep: str = "v", star: str = "*") -> pd.DataFrame:
    """
    Returns per-second table with the exact fields you asked for:
      home_sktrs_count, away_sktrs_count,
      home_goalies_count, away_goalies_count,
      home_strength, away_strength,
      team_str_home, team_str_away
    """
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool)
    is_goalie = matrix_df.index.get_level_values("isGoalie").astype(bool)

    # skater counts (exclude goalies)
    home_sktrs_count = matrix_df[~is_goalie & is_home].sum(axis=0).astype("Int16")
    away_sktrs_count = matrix_df[~is_goalie & ~is_home].sum(axis=0).astype("Int16")

    # goalie counts
    home_goalies_count = matrix_df[is_goalie & is_home].sum(axis=0).astype("Int8")
    away_goalies_count = matrix_df[is_goalie & ~is_home].sum(axis=0).astype("Int8")

    # side strings: skater count + '*' if that side has 0 goalies
    home_strength = home_sktrs_count.astype(str).mask(home_goalies_count.eq(0), home_sktrs_count.astype(str) + star)
    away_strength = away_sktrs_count.astype(str).mask(away_goalies_count.eq(0), away_sktrs_count.astype(str) + star)

    # team-oriented strings
    team_str_home = home_strength.str.cat(away_strength, sep=sep)  # for HOME players
    team_str_away = away_strength.str.cat(home_strength, sep=sep)  # for AWAY players

    out = pd.DataFrame({
        "home_sktrs_count": home_sktrs_count,
        "away_sktrs_count": away_sktrs_count,
        "home_goalies_count": home_goalies_count,
        "away_goalies_count": away_goalies_count,
        "home_strength": home_strength,
        "away_strength": away_strength,
        "team_str_home": team_str_home,
        "team_str_away": team_str_away,
    })
    out.index.name = "second"
    return out


# ============================================================
# 2) Player TOI by (player-perspective) strength
# ============================================================
def toi_by_strength_all(matrix_df: pd.DataFrame, strengths_df: pd.DataFrame, in_seconds: bool = False) -> pd.DataFrame:
    """
    For every player: total TOI by the strength string from THEIR team perspective.
    Output columns: [player-index-levels...], Strength, time_on_ice
    """
    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()

    # choose proper per-second label for each side
    # (map columns 'team_str_home' or 'team_str_away' onto seconds)
    sec_label_home = strengths_df["team_str_home"]
    sec_label_away = strengths_df["team_str_away"]

    results = []
    for (i, row) in enumerate(matrix_df.itertuples(index=True, name=None)):
        idx = row[0]                 # MultiIndex key
        on  = np.asarray(row[1:], dtype=bool)  # boolean seconds for this player

        # decide side
        player_is_home = is_home[i]
        labels = sec_label_home if player_is_home else sec_label_away

        counts = pd.Series(labels[on]).value_counts()
        counts.name = idx
        results.append(counts)

    out = pd.DataFrame(results).fillna(0)
    if not in_seconds:
        out = out / 60.0
    out.index.names = idx_names
    out = out.reset_index().melt(
        id_vars=idx_names, var_name="Strength", value_name="time_on_ice"
    )
    return out


# ============================================================
# 3) Pairwise TOI helpers (stack-safe)
# ============================================================
def _stack_all_columns_to_series(df: pd.DataFrame) -> pd.Series:
    try:
        return df.stack(df.columns.names, future_stack=True)
    except TypeError:
        return df.stack(list(range(df.columns.nlevels)))

def _square_to_long(co: np.ndarray, idx: pd.MultiIndex, right_prefix: str) -> pd.DataFrame:
    co_df = pd.DataFrame(co, index=idx, columns=idx)
    ser = _stack_all_columns_to_series(co_df)
    ser = ser[ser > 0]
    if ser.empty:
        return pd.DataFrame(columns=list(idx.names) + [f"{right_prefix}_{n}" for n in idx.names] + ["TOI_sec"])
    ser.index = ser.index.set_names(list(idx.names) + [f"{right_prefix}_{n}" for n in idx.names])
    return ser.rename("TOI_sec").reset_index()

def _rect_to_long(cross: np.ndarray, left_idx: pd.MultiIndex, right_idx: pd.MultiIndex, right_prefix: str) -> pd.DataFrame:
    df = pd.DataFrame(cross, index=left_idx, columns=right_idx)
    ser = _stack_all_columns_to_series(df)
    ser = ser[ser > 0]
    if ser.empty:
        return pd.DataFrame(columns=list(left_idx.names) + [f"{right_prefix}_{n}" for n in right_idx.names] + ["TOI_sec"])
    ser.index = ser.index.set_names(list(left_idx.names) + [f"{right_prefix}_{n}" for n in right_idx.names])
    return ser.rename("TOI_sec").reset_index()


# ============================================================
# 4) Shared TOI — Teammates (one Strength column from player side)
# ============================================================
def shared_toi_teammates_by_strength(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    *,
    in_seconds: bool = False,
) -> pd.DataFrame:
    """
    Output columns: [player-index...], [tm_* index...], Strength, TOI
    Strength is team-oriented:
      - Home players use strengths_df['team_str_home']
      - Away players use strengths_df['team_str_away']
    Goalies ARE included in pairs and seconds.
    """
    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()
    all_rows  = np.ones(len(matrix_df), dtype=bool)

    pieces = []

    # HOME players → group seconds by team_str_home
    rows = all_rows & is_home
    if np.any(rows):
        r_idx = matrix_df.index[rows]
        groups = strengths_df["team_str_home"].dropna().groupby(strengths_df["team_str_home"]).groups
        for s, sec_idx in groups.items():
            secs = list(sec_idx)
            if not secs: continue
            M = matrix_df.loc[rows, secs].to_numpy(dtype=np.uint8)
            co = M @ M.T
            np.fill_diagonal(co, 0)
            if co.sum() == 0: continue
            long = _square_to_long(co, r_idx, right_prefix="tm")
            long["Strength"] = s
            pieces.append(long)

    # AWAY players → group seconds by team_str_away
    rows = all_rows & (~is_home)
    if np.any(rows):
        r_idx = matrix_df.index[rows]
        groups = strengths_df["team_str_away"].dropna().groupby(strengths_df["team_str_away"]).groups
        for s, sec_idx in groups.items():
            secs = list(sec_idx)
            if not secs: continue
            M = matrix_df.loc[rows, secs].to_numpy(dtype=np.uint8)
            co = M @ M.T
            np.fill_diagonal(co, 0)
            if co.sum() == 0: continue
            long = _square_to_long(co, r_idx, right_prefix="tm")
            long["Strength"] = s
            pieces.append(long)

    if not pieces:
        cols = idx_names + [f"tm_{n}" for n in idx_names] + ["Strength","TOI"]
        return pd.DataFrame(columns=cols)

    res = pd.concat(pieces, ignore_index=True)
    res["TOI"] = res.pop("TOI_sec") if in_seconds else (res.pop("TOI_sec")/60.0)
    order = idx_names + [f"tm_{n}" for n in idx_names] + ["Strength","TOI"]
    for nm in order:
        if nm not in res.columns: res[nm] = pd.Series(dtype="object")
    return res[order]


# ============================================================
# 5) Shared TOI — Opponents (playerStrength + oppStrength)
# ============================================================
def shared_toi_opponents_by_strength(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    *,
    in_seconds: bool = False,
) -> pd.DataFrame:
    """
    Output columns: [player-index...], [opp_* index...], playerStrength, oppStrength, TOI
    Goalies included.
    """
    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()
    all_rows  = np.ones(len(matrix_df), dtype=bool)

    # pair both team strings per second
    pair_series = pd.Series(
        list(zip(strengths_df["team_str_home"], strengths_df["team_str_away"])),
        index=strengths_df.index
    )
    groups = {k: idxs for k, idxs in pair_series.groupby(pair_series).groups.items()
              if pd.notna(k[0]) and pd.notna(k[1])}

    pieces = []
    rows_home = all_rows & is_home
    rows_away = all_rows & (~is_home)

    for (home_label, away_label), sec_idx in groups.items():
        secs = list(sec_idx)
        if not secs or not (np.any(rows_home) and np.any(rows_away)):
            continue
        Mh = matrix_df.loc[rows_home, secs].to_numpy(dtype=np.uint8)
        Ma = matrix_df.loc[rows_away, secs].to_numpy(dtype=np.uint8)
        cross = Mh @ Ma.T
        if cross.sum() == 0:
            continue

        # Home perspective
        long1 = _rect_to_long(cross, matrix_df.index[rows_home], matrix_df.index[rows_away], right_prefix="opp")
        long1["playerStrength"] = home_label
        long1["oppStrength"]    = away_label
        pieces.append(long1)

        # Away perspective
        long2 = _rect_to_long(cross.T, matrix_df.index[rows_away], matrix_df.index[rows_home], right_prefix="opp")
        long2["playerStrength"] = away_label
        long2["oppStrength"]    = home_label
        pieces.append(long2)

    if not pieces:
        cols = idx_names + [f"opp_{n}" for n in idx_names] + ["playerStrength","oppStrength","TOI"]
        return pd.DataFrame(columns=cols)

    res = pd.concat(pieces, ignore_index=True)
    res["TOI"] = res.pop("TOI_sec") if in_seconds else (res.pop("TOI_sec")/60.0)
    order = idx_names + [f"opp_{n}" for n in idx_names] + ["playerStrength","oppStrength","TOI"]
    for nm in order:
        if nm not in res.columns: res[nm] = pd.Series(dtype="object")
    return res[order]

# --- small utilities ---------------------------------------------------------
def _expand_mi_tuple(mi_tuple, names, prefix):
    """Expand a MultiIndex tuple -> dict of {f'{prefix}_{name}': value}."""
    return {f"{prefix}_{n}": v for n, v in zip(names, mi_tuple)}

def _mk_rows_df(keys, counts, idx_names, member_prefix="p"):
    """
    keys: list of (Strength, (rowpos1,rowpos2,...)) ; counts: seconds
    returns long dataframe with p1_*, p2_*, ... + Strength + TOI
    """
    rows = []
    for (strength, combo_pos), sec in zip(keys, counts):
        row = {"Strength": strength, "TOI_sec": sec}
        for k, pos in enumerate(combo_pos, start=1):
            row.update(_expand_mi_tuple(pos, idx_names, f"{member_prefix}{k}"))
        rows.append(row)
    return pd.DataFrame(rows)

# --- 1) TEAMMATE COMBOS (same side) -----------------------------------------
def combos_teammates_by_strength(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,           # from strengths_by_second(...)
    *,
    N: int = 3,
    include_goalies: bool = False,        # combos are usually skaters; set True to allow goalies in combos
    in_seconds: bool = False,
    min_seconds: int = 1,                 # drop combos with less TOI than this (in seconds)
) -> pd.DataFrame:
    """
    Returns one row per N-player same-side combo per team-strength:
      p1_*, p2_*, ... pN_* (player bio from matrix index), Strength, TOI

    Strength is **from that team's perspective**:
      - home seconds use strengths_df['team_str_home']
      - away seconds use strengths_df['team_str_away']
    """
    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()
    is_goalie = matrix_df.index.get_level_values("isGoalie").astype(bool).to_numpy()

    # choose rows to consider for combos
    row_mask_home = (is_home)   & (include_goalies | (~is_goalie))
    row_mask_away = (~is_home)  & (include_goalies | (~is_goalie))

    out_keys, out_counts = [], []

    # --- HOME side
    if row_mask_home.any():
        M  = matrix_df.loc[row_mask_home]            # players x secs
        Mi = matrix_df.index[row_mask_home]
        sec_groups = strengths_df["team_str_home"].dropna().groupby(strengths_df["team_str_home"]).groups
        # precompute boolean numpy for speed
        M_np = M.to_numpy(dtype=bool)
        for label, secs_idx in sec_groups.items():
            secs = np.fromiter(secs_idx, dtype=int)
            if secs.size == 0: 
                continue
            sub = M_np[:, secs]                       # P x T'
            # iterate seconds: build combos from active players
            counts = {}
            for t in range(sub.shape[1]):
                on = np.flatnonzero(sub[:, t])
                if on.size < N: 
                    continue
                for combo in combinations(on.tolist(), N):
                    # represent combo as tuple of MultiIndex tuples (for stable identity)
                    combo_key = tuple(Mi[i] for i in combo)
                    counts[combo_key] = counts.get(combo_key, 0) + 1
            # push to output
            for combo_key, sec in counts.items():
                if sec >= min_seconds:
                    out_keys.append((label, combo_key))
                    out_counts.append(sec)

    # --- AWAY side
    if row_mask_away.any():
        M  = matrix_df.loc[row_mask_away]
        Mi = matrix_df.index[row_mask_away]
        M_np = M.to_numpy(dtype=bool)
        sec_groups = strengths_df["team_str_away"].dropna().groupby(strengths_df["team_str_away"]).groups
        for label, secs_idx in sec_groups.items():
            secs = np.fromiter(secs_idx, dtype=int)
            if secs.size == 0:
                continue
            sub = M_np[:, secs]
            counts = {}
            for t in range(sub.shape[1]):
                on = np.flatnonzero(sub[:, t])
                if on.size < N:
                    continue
                for combo in combinations(on.tolist(), N):
                    combo_key = tuple(Mi[i] for i in combo)
                    counts[combo_key] = counts.get(combo_key, 0) + 1
            for combo_key, sec in counts.items():
                if sec >= min_seconds:
                    out_keys.append((label, combo_key))
                    out_counts.append(sec)

    if not out_keys:
        # build empty frame with the expected columns
        cols = []
        for k in range(1, N+1):
            cols += [f"p{k}_{n}" for n in idx_names]
        cols += ["Strength", "TOI"]
        return pd.DataFrame(columns=cols)

    df = _mk_rows_df(out_keys, out_counts, idx_names, member_prefix="p")
    df["TOI"] = df.pop("TOI_sec") if in_seconds else (df.pop("TOI_sec")/60.0)
    # column order
    ordered = []
    for k in range(1, N+1):
        ordered += [f"p{k}_{n}" for n in idx_names]
    ordered += ["Strength", "TOI"]
    return df[ordered].sort_values(["Strength","TOI"], ascending=[True, False]).reset_index(drop=True)

# --- 2) OPPONENT COMBOS (vs each player) ------------------------------------
def combos_opponents_by_strength(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,           # from strengths_by_second(...)
    *,
    N: int = 2,
    include_goalies: bool = False,        # usually False (opponent skater combos)
    in_seconds: bool = False,
    min_seconds: int = 1,
) -> pd.DataFrame:
    """
    For every player, returns the TOI he shared with **N opponents at once** per strength.
    Columns:
      player_* (bio), opp1_* … oppN_* (bio), Strength, TOI

    Strength is from the **player's team perspective**:
      - home player → strengths_df['team_str_home']
      - away player → strengths_df['team_str_away']
    """
    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()
    is_goalie = matrix_df.index.get_level_values("isGoalie").astype(bool).to_numpy()

    # masks
    player_rows_home = is_home
    player_rows_away = ~is_home

    opp_rows_home = (~is_home) & (include_goalies | (~is_goalie))   # opponents for HOME players are AWAY rows
    opp_rows_away = ( is_home) & (include_goalies | (~is_goalie))   # opponents for AWAY players are HOME rows

    # numpy views
    M_all   = matrix_df.to_numpy(dtype=bool)
    idx_all = matrix_df.index

    out_rows = []

    # Helper to process one side
    def _process_side(player_mask, opp_mask, label_series):
        P_idx = np.flatnonzero(player_mask)
        O_idx = np.flatnonzero(opp_mask)
        if P_idx.size == 0 or O_idx.size == 0:
            return
        # split matrices
        M_players = M_all[P_idx, :]    # P x T
        M_opps    = M_all[O_idx, :]    # O x T

        # group seconds by strength label
        groups = label_series.dropna().groupby(label_series).groups
        for label, secs_idx in groups.items():
            secs = np.fromiter(secs_idx, dtype=int)
            if secs.size == 0:
                continue
            P_sub = M_players[:, secs]            # P x T'
            O_sub = M_opps[:, secs]               # O x T'
            # precompute opponent presence per second → combinations once per second,
            # then attribute those seconds to every present player.
            for t in range(P_sub.shape[1]):
                opp_on = np.flatnonzero(O_sub[:, t])
                if opp_on.size < N:
                    continue
                opp_combos = list(combinations(opp_on.tolist(), N))
                if not opp_combos:
                    continue
                ply_on = np.flatnonzero(P_sub[:, t])
                if ply_on.size == 0:
                    continue
                for p in ply_on:
                    p_key  = idx_all[P_idx[p]]
                    for comb in opp_combos:
                        opp_keys = tuple(idx_all[O_idx[c]] for c in comb)
                        out_rows.append((label, p_key, opp_keys))

    # home and away perspectives
    _process_side(player_rows_home, opp_rows_home, strengths_df["team_str_home"])
    _process_side(player_rows_away, opp_rows_away, strengths_df["team_str_away"])

    if not out_rows:
        cols = [f"player_{n}" for n in idx_names]
        for k in range(1, N+1):
            cols += [f"opp{k}_{n}" for n in idx_names]
        cols += ["Strength", "TOI"]
        return pd.DataFrame(columns=cols)

    # aggregate seconds
    # key: (Strength, player_mi_tuple, opp_combo_mi_tuple)
    c = Counter(out_rows)  # each occurrence is 1 second
    keys, secs = zip(*c.items())

    # build rows
    records = []
    for (label, player_mi, opp_combo_mi), sec in zip(keys, secs):
        row = {"Strength": label, "TOI_sec": sec}
        row.update(_expand_mi_tuple(player_mi, idx_names, "player"))
        for k, mi in enumerate(opp_combo_mi, start=1):
            row.update(_expand_mi_tuple(mi, idx_names, f"opp{k}"))
        records.append(row)

    df = pd.DataFrame.from_records(records)
    # units / order
    df["TOI"] = df.pop("TOI_sec") if in_seconds else (df.pop("TOI_sec")/60.0)
    ordered = [f"player_{n}" for n in idx_names]
    for k in range(1, N+1):
        ordered += [f"opp{k}_{n}" for n in idx_names]
    ordered += ["Strength", "TOI"]
    # filter by min_seconds
    if not in_seconds and min_seconds > 1:
        df = df[df["TOI"]*60 >= min_seconds]
    elif in_seconds and min_seconds > 1:
        df = df[df["TOI"] >= min_seconds]
    return df[ordered].sort_values(["Strength","TOI"], ascending=[True, False]).reset_index(drop=True)


# --- small helpers -----------------------------------------------------------
def _expand_mi_tuple(mi_tuple, names, prefix):
    return {f"{prefix}_{n}": v for n, v in zip(names, mi_tuple)}

def _build_empty_cols(idx_names, n_team, m_opp):
    cols = [f"p{k}_{n}" for k in range(1, n_team+1) for n in idx_names]
    cols += [f"opp{k}_{n}" for k in range(1, m_opp+1) for n in idx_names]
    cols += ["Strength", "TOI"]
    return cols

# --- the general combo function ---------------------------------------------
def combo_toi_by_strength(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    *,
    n_team: int = 2,                 # size of your-team combo
    m_opp: int  = 0,                 # size of opponent combo (0 = ignore opps)
    include_goalies_team: bool = False,
    include_goalies_opp: bool  = False,
    side: str = "both",              # "home", "away", or "both"
    in_seconds: bool = False,
    min_seconds: int = 1,
) -> pd.DataFrame:
    """
    Count seconds where an n_team-player combo (same side) was on-ice
    simultaneously with an m_opp-player combo (opposite side), grouped by
    the *team-perspective* strength label.

    Strength used:
      - For HOME combos -> strengths_df['team_str_home']
      - For AWAY  combos -> strengths_df['team_str_away']
    """
    assert side in {"home", "away", "both"}

    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()
    is_goalie = matrix_df.index.get_level_values("isGoalie").astype(bool).to_numpy()

    # team-side row masks
    team_home_mask = is_home & (include_goalies_team | (~is_goalie))
    team_away_mask = (~is_home) & (include_goalies_team | (~is_goalie))

    # opponent-side row masks
    opp_for_home_mask = (~is_home) & (include_goalies_opp | (~is_goalie))
    opp_for_away_mask = (is_home)  & (include_goalies_opp | (~is_goalie))

    # numpy views
    M_all   = matrix_df.to_numpy(dtype=bool)
    idx_all = matrix_df.index

    def _process(team_mask, opp_mask, label_series):
        keys = []
        # precompute indices
        T_idx = np.flatnonzero(team_mask)
        O_idx = np.flatnonzero(opp_mask)
        if T_idx.size == 0:
            return Counter()

        M_team = M_all[T_idx, :]                # T x S
        M_opp  = M_all[O_idx, :] if m_opp > 0 else None

        # seconds grouped by team-perspective strength
        groups = label_series.dropna().groupby(label_series).groups
        cnt = Counter()

        for label, sec_idx in groups.items():
            secs = np.fromiter(sec_idx, dtype=int)
            if secs.size == 0:
                continue

            T_sub = M_team[:, secs]             # T x S'
            O_sub = M_opp[:, secs] if m_opp > 0 else None

            # iterate seconds; make combos only from active players
            for t in range(T_sub.shape[1]):
                t_on = np.flatnonzero(T_sub[:, t])
                if t_on.size < n_team:
                    continue
                team_combos = list(combinations(t_on.tolist(), n_team))

                if m_opp == 0:
                    for tc in team_combos:
                        team_key = tuple(idx_all[T_idx[i]] for i in tc)
                        cnt[(label, team_key, tuple())] += 1
                else:
                    o_on = np.flatnonzero(O_sub[:, t])
                    if o_on.size < m_opp:
                        continue
                    opp_combos = list(combinations(o_on.tolist(), m_opp))
                    if not opp_combos:
                        continue
                    for tc in team_combos:
                        team_key = tuple(idx_all[T_idx[i]] for i in tc)
                        for oc in opp_combos:
                            opp_key = tuple(idx_all[O_idx[j]] for j in oc)
                            cnt[(label, team_key, opp_key)] += 1
        return cnt

    counts = Counter()

    if side in {"home", "both"}:
        counts.update(_process(team_home_mask, opp_for_home_mask, strengths_df["team_str_home"]))
    if side in {"away", "both"}:
        counts.update(_process(team_away_mask, opp_for_away_mask, strengths_df["team_str_away"]))

    if not counts:
        return pd.DataFrame(columns=_build_empty_cols(idx_names, n_team, m_opp))

    # materialize to rows
    records = []
    for (label, team_combo, opp_combo), secs in counts.items():
        if secs < min_seconds:
            continue
        row = {"Strength": label, "TOI_sec": secs}
        for k, mi in enumerate(team_combo, start=1):
            row.update(_expand_mi_tuple(mi, idx_names, f"p{k}"))
        for k, mi in enumerate(opp_combo, start=1):
            row.update(_expand_mi_tuple(mi, idx_names, f"opp{k}"))
        records.append(row)

    if not records:
        return pd.DataFrame(columns=_build_empty_cols(idx_names, n_team, m_opp))

    df = pd.DataFrame.from_records(records)

    # units + column order
    df["TOI"] = df.pop("TOI_sec") if in_seconds else (df.pop("TOI_sec")/60.0)

    order = []
    for k in range(1, n_team+1):
        order += [f"p{k}_{n}" for n in idx_names]
    for k in range(1, m_opp+1):
        order += [f"opp{k}_{n}" for n in idx_names]
    order += ["Strength", "TOI"]

    # ensure all expected columns exist (in case some positions never appear)
    for col in order:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")

    return df[order].sort_values(["Strength","TOI"], ascending=[True, False]).reset_index(drop=True)

import numpy as np
import pandas as pd
from itertools import combinations
from collections import defaultdict

def combo_shot_metrics_by_strength(
    matrix_df: pd.DataFrame,
    strengths_df: pd.DataFrame,
    pbp_df: pd.DataFrame,
    *,
    n_team: int = 2,
    m_opp: int  = 0,
    include_goalies_team: bool = False,
    include_goalies_opp: bool  = False,
    side: str = "both",
    include_toi: bool = True,
    toi_in_seconds: bool = False,         # if True, TOI values are seconds; else minutes
    precomputed_toi: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    One row per combo (team N + optional opponent M) per strength:
      p1_*,...,pN_*, [opp1_*,...,oppM_*], Strength,
      ShotsFor, ShotsAgainst, FenwickFor, FenwickAgainst, CorsiFor, CorsiAgainst,
      [TOI, rates/60, shares]
    """

    assert side in {"home", "away", "both"}

    idx_names = list(matrix_df.index.names)
    is_home   = matrix_df.index.get_level_values("isHome").astype(bool).to_numpy()
    is_goalie = matrix_df.index.get_level_values("isGoalie").astype(bool).to_numpy()

    team_home_mask = is_home   & (include_goalies_team | (~is_goalie))
    team_away_mask = (~is_home) & (include_goalies_team | (~is_goalie))
    opp_for_home_mask = (~is_home) & (include_goalies_opp | (~is_goalie))
    opp_for_away_mask = ( is_home)  & (include_goalies_opp | (~is_goalie))

    M = matrix_df.to_numpy(dtype=bool)
    _, S = M.shape
    idx_all = matrix_df.index

    H_team_idx = np.flatnonzero(team_home_mask)
    A_team_idx = np.flatnonzero(team_away_mask)
    H_opp_idx  = np.flatnonzero(opp_for_away_mask)  # home as opponents for away team
    A_opp_idx  = np.flatnonzero(opp_for_home_mask)  # away as opponents for home team

    # --- PBP: filter to attempts ---
    events = pbp_df.loc[pbp_df["Event"].isin(["SHOT","GOAL","MISS","BLOCK"]),
                        ["Event","elapsedTime","isHome"]].copy()
    events["sec"] = pd.to_numeric(events["elapsedTime"], errors="coerce")
    events = events[events["sec"].notna()]
    events["sec"] = events["sec"].astype("Int32").clip(lower=0, upper=S-1)

    evt_is_home  = events["isHome"].astype(int).astype(bool).to_numpy()
    evt_is_block = events["Event"].eq("BLOCK").to_numpy()
    attempt_home = np.where(evt_is_block, ~evt_is_home, evt_is_home)

    is_shot = events["Event"].isin(["SHOT","GOAL"]).to_numpy()
    is_fen  = events["Event"].isin(["SHOT","GOAL","MISS"]).to_numpy()

    home_label = strengths_df["team_str_home"]
    away_label = strengths_df["team_str_away"]

    # SF, SA, FF, FA, CF, CA
    counts = defaultdict(lambda: np.zeros(6, dtype=int))

    # --- Attribute each event to relevant combos on that second ---
    for e_idx, r in events.reset_index(drop=True).iterrows():
        s = int(r["sec"])
        att_home = bool(attempt_home[e_idx])

        label_for = home_label.iloc[s] if att_home else away_label.iloc[s]
        label_def = away_label.iloc[s] if att_home else home_label.iloc[s]

        w_shot = int(is_shot[e_idx])
        w_fen  = int(is_fen[e_idx])
        w_cor  = 1

        # FOR side
        if (att_home and side in {"home","both"}) or ((not att_home) and side in {"away","both"}):
            T_idx = H_team_idx if att_home else A_team_idx
            O_idx = A_opp_idx  if att_home else H_opp_idx

            team_on = T_idx[np.flatnonzero(M[T_idx, s])]
            if team_on.size >= n_team:
                team_combos = combinations(sorted(team_on.tolist()), n_team)
                if m_opp > 0:
                    opp_on = O_idx[np.flatnonzero(M[O_idx, s])]
                    opp_combos = list(combinations(sorted(opp_on.tolist()), m_opp)) if opp_on.size >= m_opp else []
                else:
                    opp_combos = [()]

                for tc in team_combos:
                    tc_keys = tuple(idx_all[i] for i in tc)
                    if m_opp == 0:
                        key = (label_for, tc_keys, ())
                        counts[key][0] += w_shot; counts[key][2] += w_fen; counts[key][4] += w_cor
                    else:
                        for oc in opp_combos:
                            oc_keys = tuple(idx_all[j] for j in oc)
                            key = (label_for, tc_keys, oc_keys)
                            counts[key][0] += w_shot; counts[key][2] += w_fen; counts[key][4] += w_cor

        # AGAINST side
        if (att_home and side in {"away","both"}) or ((not att_home) and side in {"home","both"}):
            T_idx = A_team_idx if att_home else H_team_idx
            O_idx = H_opp_idx  if att_home else A_opp_idx

            team_on = T_idx[np.flatnonzero(M[T_idx, s])]
            if team_on.size >= n_team:
                team_combos = combinations(sorted(team_on.tolist()), n_team)
                if m_opp > 0:
                    opp_on = O_idx[np.flatnonzero(M[O_idx, s])]
                    opp_combos = list(combinations(sorted(opp_on.tolist()), m_opp)) if opp_on.size >= m_opp else []
                else:
                    opp_combos = [()]

                for tc in team_combos:
                    tc_keys = tuple(idx_all[i] for i in tc)
                    if m_opp == 0:
                        key = (label_def, tc_keys, ())
                        counts[key][1] += w_shot; counts[key][3] += w_fen; counts[key][5] += w_cor
                    else:
                        for oc in opp_combos:
                            oc_keys = tuple(idx_all[j] for j in oc)
                            key = (label_def, tc_keys, oc_keys)
                            counts[key][1] += w_shot; counts[key][3] += w_fen; counts[key][5] += w_cor

    # --- Build DataFrame ---
    rows = []
    for (label, team_keys, opp_keys), vec in counts.items():
        row = {"Strength": label,
               "ShotsFor": vec[0], "ShotsAgainst": vec[1],
               "FenwickFor": vec[2], "FenwickAgainst": vec[3],
               "CorsiFor": vec[4], "CorsiAgainst": vec[5]}
        for i, mi in enumerate(team_keys, start=1):
            for n, v in zip(idx_names, mi): row[f"p{i}_{n}"] = v
        for i, mi in enumerate(opp_keys, start=1):
            for n, v in zip(idx_names, mi): row[f"opp{i}_{n}"] = v
        rows.append(row)

    if not rows:
        base_cols = []
        for k in range(1, n_team+1): base_cols += [f"p{k}_{n}" for n in idx_names]
        for k in range(1, m_opp+1):  base_cols += [f"opp{k}_{n}" for n in idx_names]
        base_cols += ["Strength","ShotsFor","ShotsAgainst","FenwickFor","FenwickAgainst","CorsiFor","CorsiAgainst"]
        if include_toi: base_cols += ["TOI"]
        # include differentials / shares / per60 columns as empty too
        base_cols += ["ShotsDifferential","FenwickDifferential","CorsiDifferential",
                      "ShotsFor%","FenwickFor%","CorsiFor%"]
        if include_toi:
            for col in ["ShotsFor","ShotsAgainst","ShotsDifferential",
                        "FenwickFor","FenwickAgainst","FenwickDifferential",
                        "CorsiFor","CorsiAgainst","CorsiDifferential"]:
                base_cols.append(f"{col}/60")
        return pd.DataFrame(columns=base_cols)

    df = pd.DataFrame(rows)

    # Ensure combo columns exist (some MI fields may be missing if constant)
    for k in range(1, n_team+1):
        for n in idx_names:
            col = f"p{k}_{n}"
            if col not in df.columns: df[col] = pd.NA
    for k in range(1, m_opp+1):
        for n in idx_names:
            col = f"opp{k}_{n}"
            if col not in df.columns: df[col] = pd.NA

    # ----- Optional TOI attach -----
    if include_toi:
        key_cols = []
        for k in range(1, n_team+1): key_cols += [f"p{k}_{n}" for n in idx_names]
        for k in range(1, m_opp+1):  key_cols += [f"opp{k}_{n}" for n in idx_names]
        key_cols += ["Strength"]

        if precomputed_toi is None:
            toi_df = combo_toi_by_strength(
                matrix_df, strengths_df,
                n_team=n_team, m_opp=m_opp,
                include_goalies_team=include_goalies_team,
                include_goalies_opp=include_goalies_opp,
                side=side,
                in_seconds=toi_in_seconds,
            )
        else:
            toi_df = precomputed_toi.copy()

        df = df.merge(toi_df[key_cols + ["TOI"]], on=key_cols, how="left")

    # Add +/- and shares
    df["ShotsDifferential"]   = df["ShotsFor"]   - df["ShotsAgainst"]
    df["FenwickDifferential"] = df["FenwickFor"] - df["FenwickAgainst"]
    df["CorsiDifferential"]   = df["CorsiFor"]   - df["CorsiAgainst"]

    denom = (df["ShotsFor"]   + df["ShotsAgainst"]).replace(0, np.nan)
    df["ShotsFor%"]   = df["ShotsFor"]   / denom
    denom = (df["FenwickFor"] + df["FenwickAgainst"]).replace(0, np.nan)
    df["FenwickFor%"] = df["FenwickFor"] / denom
    denom = (df["CorsiFor"]   + df["CorsiAgainst"]).replace(0, np.nan)
    df["CorsiFor%"]   = df["CorsiFor"]   / denom

    # Per-60 (if TOI attached)
    ordered = []
    for k in range(1, n_team+1): ordered += [f"p{k}_{n}" for n in idx_names]
    for k in range(1, m_opp+1):  ordered += [f"opp{k}_{n}" for n in idx_names]
    ordered += ["Strength",
                "ShotsFor","ShotsAgainst","ShotsDifferential","ShotsFor%",
                "FenwickFor","FenwickAgainst","FenwickDifferential","FenwickFor%",
                "CorsiFor","CorsiAgainst","CorsiDifferential","CorsiFor%"]
    if include_toi:
        ordered += ["TOI"]
        # convert TOI to minutes for per-60 math if needed
        toi_minutes = df["TOI"] if not toi_in_seconds else (df["TOI"] / 60.0)
        toi_minutes = toi_minutes.replace(0, np.nan)
        for col in ["ShotsFor","ShotsAgainst","ShotsDifferential",
                    "FenwickFor","FenwickAgainst","FenwickDifferential",
                    "CorsiFor","CorsiAgainst","CorsiDifferential"]:
            df[f"{col}/60"] = df[col] * 60.0 / toi_minutes
        ordered += [f"{c}/60" for c in ["ShotsFor","ShotsAgainst","ShotsDifferential",
                                        "FenwickFor","FenwickAgainst","FenwickDifferential",
                                        "CorsiFor","CorsiAgainst","CorsiDifferential"]]
        

    # Guarantee all columns exist (edge cases)
    for col in ordered:
        if col not in df.columns: df[col] = pd.NA
        
        

    return df[ordered].sort_values(["Strength","CorsiFor","CorsiAgainst"], ascending=[True, False, False]).reset_index(drop=True)