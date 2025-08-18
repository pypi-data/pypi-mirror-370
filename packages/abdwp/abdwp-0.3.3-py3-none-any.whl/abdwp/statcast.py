import os
import warnings
import pandas as pd
from pybaseball import statcast


def download_seasons(start_year, end_year=None, force_download=False, data_dir="statcast"):

    # define end_year if not provided by user, only download start year
    if end_year is None:
        end_year = start_year

    # check that years are provided as integers
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise ValueError("'start_year' and 'end_year' must be integers.")

    # check that years are properly ordered
    if start_year > end_year:
        raise ValueError("'start_year' must be less than or equal to 'end_year'.")

    # make statcast directory if it does not exist
    os.makedirs(data_dir, exist_ok=True)

    # process all years requested
    for year in range(start_year, end_year + 1):
        parquet_path = os.path.join(data_dir, f"sc-{year}.parquet")
        if os.path.exists(parquet_path) and not force_download:
            print(f"Data for {year} already exists, skipping.")
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                print(f"Downloading data for {year}.")
                df = statcast(start_dt=f"{year}-01-01", end_dt=f"{year}-12-31")
                df = df.convert_dtypes(dtype_backend="numpy_nullable")
                df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="zstd")


def load_season(year, force_download=False, regular_season=False, data_dir="statcast"):
    parquet_path = os.path.join(data_dir, f"sc-{year}.parquet")
    parquet_path_in_data = None
    if data_dir == "statcast":
        parquet_path_in_data = os.path.join("data", data_dir, f"sc-{year}.parquet")
    if force_download:
        download_seasons(year, year, force_download=force_download, data_dir=data_dir)
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path, engine="pyarrow")
    elif parquet_path_in_data and os.path.exists(parquet_path_in_data):
        df = pd.read_parquet(parquet_path_in_data, engine="pyarrow")
    else:
        download_seasons(year, year, data_dir=data_dir)
        df = pd.read_parquet(parquet_path, engine="pyarrow")
    if regular_season:
        df = filter_regular_season(df)
    return df


# all statcast features as of july 2025
statcast_features_default = [
    "pitch_type",
    "game_date",
    "release_speed",
    "release_pos_x",
    "release_pos_z",
    "player_name",
    "batter",
    "pitcher",
    "events",
    "description",
    "spin_dir",
    "spin_rate_deprecated",
    "break_angle_deprecated",
    "break_length_deprecated",
    "zone",
    "des",
    "game_type",
    "stand",
    "p_throws",
    "home_team",
    "away_team",
    "type",
    "hit_location",
    "bb_type",
    "balls",
    "strikes",
    "game_year",
    "pfx_x",
    "pfx_z",
    "plate_x",
    "plate_z",
    "on_3b",
    "on_2b",
    "on_1b",
    "outs_when_up",
    "inning",
    "inning_topbot",
    "hc_x",
    "hc_y",
    "tfs_deprecated",
    "tfs_zulu_deprecated",
    "umpire",
    "sv_id",
    "vx0",
    "vy0",
    "vz0",
    "ax",
    "ay",
    "az",
    "sz_top",
    "sz_bot",
    "hit_distance_sc",
    "launch_speed",
    "launch_angle",
    "effective_speed",
    "release_spin_rate",
    "release_extension",
    "game_pk",
    "fielder_2",
    "fielder_3",
    "fielder_4",
    "fielder_5",
    "fielder_6",
    "fielder_7",
    "fielder_8",
    "fielder_9",
    "release_pos_y",
    "estimated_ba_using_speedangle",
    "estimated_woba_using_speedangle",
    "woba_value",
    "woba_denom",
    "babip_value",
    "iso_value",
    "launch_speed_angle",
    "at_bat_number",
    "pitch_number",
    "pitch_name",
    "home_score",
    "away_score",
    "bat_score",
    "fld_score",
    "post_away_score",
    "post_home_score",
    "post_bat_score",
    "post_fld_score",
    "if_fielding_alignment",
    "of_fielding_alignment",
    "spin_axis",
    "delta_home_win_exp",
    "delta_run_exp",
    "bat_speed",
    "swing_length",
    "estimated_slg_using_speedangle",
    "delta_pitcher_run_exp",
    "hyper_speed",
    "home_score_diff",
    "bat_score_diff",
    "home_win_exp",
    "bat_win_exp",
    "age_pit_legacy",
    "age_bat_legacy",
    "age_pit",
    "age_bat",
    "n_thruorder_pitcher",
    "n_priorpa_thisgame_player_at_bat",
    "pitcher_days_since_prev_game",
    "batter_days_since_prev_game",
    "pitcher_days_until_next_game",
    "batter_days_until_next_game",
    "api_break_z_with_gravity",
    "api_break_x_arm",
    "api_break_x_batter_in",
    "arm_angle",
    "attack_angle",
    "attack_direction",
    "swing_path_tilt",
    "intercept_ball_minus_batter_pos_x_inches",
    "intercept_ball_minus_batter_pos_y_inches",
]


# h/t to scott powers
statcast_features_reorder = [
    # pitch identifiers
    "game_pk",
    "game_date",
    "game_type",
    "game_year",
    "at_bat_number",
    "pitch_number",
    # player and team identifiers
    "home_team",
    "away_team",
    "batter",
    "stand",
    "player_name",
    "pitcher",
    "p_throws",
    "on_1b",
    "on_2b",
    "on_3b",
    "fielder_2",
    "fielder_3",
    "fielder_4",
    "fielder_5",
    "fielder_6",
    "fielder_7",
    "fielder_8",
    "fielder_9",
    # context
    "inning",
    "inning_topbot",
    "outs_when_up",
    "balls",
    "strikes",
    "if_fielding_alignment",
    "of_fielding_alignment",
    # pitch tracking
    "pitch_type",
    "arm_angle",
    ## features needed to recreate the full quadratic trajectory of the pitch
    "ax",
    "ay",
    "az",
    "vx0",
    "vy0",
    "vz0",
    "release_pos_x",
    "release_pos_y",
    "release_pos_z",
    ## interpretable features that are functions of the quadratic trajectory
    "release_speed",
    "release_extension",
    "effective_speed",
    "pfx_x",
    "pfx_z",
    "plate_x",
    "plate_z",
    "zone",
    ## additional features not derived from the quadratic trajectory
    "release_spin_rate",
    "spin_axis",
    "sz_top",
    "sz_bot",
    # swing tracking
    "bat_speed",
    "swing_length",
    "attack_angle",
    "attack_direction",
    "swing_path_tilt",
    "intercept_ball_minus_batter_pos_x_inches",
    "intercept_ball_minus_batter_pos_y_inches",
    # batted ball tracking
    "launch_speed",
    "launch_angle",
    "estimated_woba_using_speedangle",
    "estimated_ba_using_speedangle",
    "estimated_slg_using_speedangle",
    "hc_x",
    "hc_y",
    "hit_distance_sc",
    "bb_type",
    "hit_location",
    # outcome
    "type",
    "description",
    "events",
    "woba_denom",
    "woba_value",
    "babip_value",
    "iso_value",
    "delta_run_exp",
    "delta_home_win_exp",
]


statcast_features_remove = [
    feature for feature in statcast_features_default if feature not in statcast_features_reorder
]

statcast_features_ordered = statcast_features_reorder + statcast_features_remove


def reorder_columns(df, keep_all=False):
    df = df.loc[:, statcast_features_ordered].copy()
    if not keep_all:
        df = df.drop(statcast_features_remove, axis=1, errors="ignore")
    return df


# currently defaulting to ascending=False to match pybaseball
def arrange_rows(df, keep_index=False, ascending=False):
    sort_columns = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
    missing = [col for col in sort_columns if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing required columns for sorting: {missing}")
    df = df.sort_values(by=sort_columns, ascending=ascending)
    if not keep_index:
        df = df.reset_index(drop=True)
    return df


def filter_regular_season(df):
    if "game_type" not in df.columns:
        raise ValueError("DataFrame must contain a 'game_type' column.")
    return df[df["game_type"] == "R"].copy()
