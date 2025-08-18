import os
import requests
import zipfile
import glob
import pandas as pd
import subprocess
import contextlib
import shutil
import time
import tempfile
import tarfile

# the code in this file was originally inspired by similar code for R
# https://github.com/beanumber/abdwr3edata/blob/main/R/parse_retrosheet_pbp.R
# TODO: add gamelog functionality that mirrors events? (allstar, postseason, use helper functions)
# TODO: add cwevent_dir to all load functions (and pass to download functions)?


@contextlib.contextmanager
def _pushd(new_dir):
    prev_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(prev_dir)


@contextlib.contextmanager
def prepend_path(dir):
    abs_dir = os.path.abspath(dir)
    cwd_dir = os.getcwd()
    old_path = os.environ.get("PATH", "")
    new_path = os.pathsep.join([abs_dir, cwd_dir, "/usr/local/bin", old_path])
    os.environ["PATH"] = new_path
    try:
        yield
    finally:
        os.environ["PATH"] = old_path


# define header for gamelogs (column names for data frame)
# names originally from:
# https://github.com/maxtoki/baseball_R/blob/master/data/game_log_header.csv
# changed HomeRunsScore to HomeRunsScored which seems to have been a typo
gamelogs_header = [
    "Date",
    "DoubleHeader",
    "DayOfWeek",
    "VisitingTeam",
    "VisitingTeamLeague",
    "VisitingTeamGameNumber",
    "HomeTeam",
    "HomeTeamLeague",
    "HomeTeamGameNumber",
    "VisitorRunsScored",
    "HomeRunsScored",  # modified from Score to Scored for consistency
    "LengthInOuts",
    "DayNight",
    "CompletionInfo",
    "ForfeitInfo",
    "ProtestInfo",
    "ParkID",
    "Attendance",
    "Duration",
    "VisitorLineScore",
    "HomeLineScore",
    "VisitorAB",
    "VisitorH",
    "VisitorD",
    "VisitorT",
    "VisitorHR",
    "VisitorRBI",
    "VisitorSH",
    "VisitorSF",
    "VisitorHBP",
    "VisitorBB",
    "VisitorIBB",
    "VisitorK",
    "VisitorSB",
    "VisitorCS",
    "VisitorGDP",
    "VisitorCI",
    "VisitorLOB",
    "VisitorPitchers",
    "VisitorER",
    "VisitorTER",
    "VisitorWP",
    "VisitorBalks",
    "VisitorPO",
    "VisitorA",
    "VisitorE",
    "VisitorPassed",
    "VisitorDB",
    "VisitorTP",
    "HomeAB",
    "HomeH",
    "HomeD",
    "HomeT",
    "HomeHR",
    "HomeRBI",
    "HomeSH",
    "HomeSF",
    "HomeHBP",
    "HomeBB",
    "HomeIBB",
    "HomeK",
    "HomeSB",
    "HomeCS",
    "HomeGDP",
    "HomeCI",
    "HomeLOB",
    "HomePitchers",
    "HomeER",
    "HomeTER",
    "HomeWP",
    "HomeBalks",
    "HomePO",
    "HomeA",
    "HomeE",
    "HomePassed",
    "HomeDB",
    "HomeTP",
    "UmpireHID",
    "UmpireHName",
    "Umpire1BID",
    "Umpire1BName",
    "Umpire2BID",
    "Umpire2BName",
    "Umpire3BID",
    "Umpire3BName",
    "UmpireLFID",
    "UmpireLFName",
    "UmpireRFID",
    "UmpireRFName",
    "VisitorManagerID",
    "VisitorManagerName",
    "HomeManagerID",
    "HomeManagerName",
    "WinningPitcherID",
    "WinningPitcherName",
    "LosingPitcherID",
    "LosingPitcherNAme",
    "SavingPitcherID",
    "SavingPitcherName",
    "GameWinningRBIID",
    "GameWinningRBIName",
    "VisitorStartingPitcherID",
    "VisitorStartingPitcherName",
    "HomeStartingPitcherID",
    "HomeStartingPitcherName",
    "VisitorBatting1PlayerID",
    "VisitorBatting1Name",
    "VisitorBatting1Position",
    "VisitorBatting2PlayerID",
    "VisitorBatting2Name",
    "VisitorBatting2Position",
    "VisitorBatting3PlayerID",
    "VisitorBatting3Name",
    "VisitorBatting3Position",
    "VisitorBatting4PlayerID",
    "VisitorBatting4Name",
    "VisitorBatting4Position",
    "VisitorBatting5PlayerID",
    "VisitorBatting5Name",
    "VisitorBatting5Position",
    "VisitorBatting6PlayerID",
    "VisitorBatting6Name",
    "VisitorBatting6Position",
    "VisitorBatting7PlayerID",
    "VisitorBatting7Name",
    "VisitorBatting7Position",
    "VisitorBatting8PlayerID",
    "VisitorBatting8Name",
    "VisitorBatting8Position",
    "VisitorBatting9PlayerID",
    "VisitorBatting9Name",
    "VisitorBatting9Position",
    "HomeBatting1PlayerID",
    "HomeBatting1Name",
    "HomeBatting1Position",
    "HomeBatting2PlayerID",
    "HomeBatting2Name",
    "HomeBatting2Position",
    "HomeBatting3PlayerID",
    "HomeBatting3Name",
    "HomeBatting3Position",
    "HomeBatting4PlayerID",
    "HomeBatting4Name",
    "HomeBatting4Position",
    "HomeBatting5PlayerID",
    "HomeBatting5Name",
    "HomeBatting5Position",
    "HomeBatting6PlayerID",
    "HomeBatting6Name",
    "HomeBatting6Position",
    "HomeBatting7PlayerID",
    "HomeBatting7Name",
    "HomeBatting7Position",
    "HomeBatting8PlayerID",
    "HomeBatting8Name",
    "HomeBatting8Position",
    "HomeBatting9PlayerID",
    "HomeBatting9Name",
    "HomeBatting9Position",
    "AdditionalInfo",
    "AcquisitionInfo",
]

# define header for roster (column names for data frame)
roster_header = [
    "PlayerID",
    "LastName",
    "FirstName",
    "Bats",
    "Pitches",
    "Team",
    "Position",
]


def _download_and_unzip(url, zipped_file, extract_to, retries=3, delay=2):
    for attempt in range(retries):
        try:
            print(f"Downloading {url} to a temporary file")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(zipped_file, "wb") as f:
                f.write(r.content)
            print(f"Unzipping to {extract_to}")
            with zipfile.ZipFile(zipped_file, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            return  # success
        except (requests.RequestException, zipfile.BadZipFile) as e:
            print(f"Error during download or unzip: {e}")
            if os.path.exists(zipped_file):
                os.remove(zipped_file)
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise RuntimeError(
                    f"Failed to download and unzip after {retries} attempts: {url}"
                ) from e


# TODO: set a default for cwevent_dir? or if None, use working dir?
def download_events(
    start_year,
    end_year=None,
    postseason=False,
    allstar=False,
    data_dir="retrosheet",
    cwevent_dir="chadwick",
):

    if postseason and allstar:
        raise ValueError("Only one of 'postseason' or 'allstar' can be True.")

    season_type = "regular season"
    if postseason:
        season_type = "postseason"
    if allstar:
        season_type = "allstar game"

    # define end_year if not provided by user, only download start year
    if end_year is None:
        end_year = start_year

    # check that years are provided as integers
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise ValueError("'start_year' and 'end_year' must be integers.")

    # check that years are properly ordered
    if start_year > end_year:
        raise ValueError("'start_year' must be less than or equal to 'end_year'.")

    # make data directory if it does not exist
    os.makedirs(data_dir, exist_ok=True)

    # process events for each requested year
    for year in range(start_year, end_year + 1):

        # intro messaging
        print(f"Downloading and parsing {season_type} events for {year}.")
        print(f"")

        if postseason:
            url_suffix = "post"
            file_suffix = "-post"
        elif allstar:
            url_suffix = "as"
            file_suffix = "-allstar"
        else:  # regular season
            url_suffix = "eve"
            file_suffix = ""

        # setup url and file paths
        url = f"http://www.retrosheet.org/events/{year}{url_suffix}.zip"
        pbp_parquet = os.path.join(data_dir, f"pbp-{year}{file_suffix}.parquet")
        rosters_parquet = os.path.join(data_dir, f"rosters-{year}{file_suffix}.parquet")
        teams_parquet = os.path.join(data_dir, f"teams-{year}{file_suffix}.parquet")

        with tempfile.TemporaryDirectory() as temp_dir:
            zipped_file = os.path.join(temp_dir, f"{year}{url_suffix}.zip")
            pbp_csv = os.path.join(temp_dir, f"pbp-{year}{file_suffix}.csv")
            event_pattern = os.path.join(temp_dir, f"{year}*.EV*")

            # obtain zipped events from retrosheet website and decompress
            _download_and_unzip(url, zipped_file, temp_dir)

            # try to use current directory if no cwevent_dir supplied
            if cwevent_dir is None:
                cwevent_dir = os.getcwd()

            # allow user to specify directory containing cwevent and temporarily add it to PATH
            with prepend_path(cwevent_dir):

                # check that cwevent is installed
                cwevent_cmd = "cwevent.exe" if os.name == "nt" else "cwevent"
                if shutil.which(cwevent_cmd) is None:
                    raise RuntimeError(
                        "The 'cwevent' command-line tool is not installed or not in your PATH. "
                        "Installation instructions can be found at: https://github.com/chadwickbureau/chadwick/blob/master/INSTALL "
                        "Additional documentation: https://chadwick.sourceforge.net/doc/cwevent.html"
                    )

                # setup arguments to cwevent
                cwevent_args = [cwevent_cmd, "-n", "-y", str(year), "-f", "0-96"] + glob.glob(
                    event_pattern
                )

                # process event file with cwevent and write parsed pbp file
                with _pushd(temp_dir):
                    print(f"\nRunning: {' '.join(cwevent_args)} > {os.path.basename(pbp_csv)}")
                    with open(pbp_csv, "w", newline="") as out_f:
                        subprocess.run(cwevent_args, stdout=out_f, check=True, shell=False)

            # read processed csv files and write parquet files to parsed directory
            df = pd.read_csv(
                pbp_csv,
                dtype_backend="numpy_nullable",
                engine="pyarrow",
            )
            df.to_parquet(pbp_parquet, index=False, engine="pyarrow", compression="zstd")
            print(f"Play-by-play written to {pbp_parquet}")

            # create and write parsed roster file
            roster_file_pattern = os.path.join(temp_dir, f"*.ROS")
            roster_files = glob.glob(roster_file_pattern)
            roster_dfs = []
            for file in roster_files:
                df = pd.read_csv(
                    file,
                    header=None,
                    names=roster_header,
                    dtype_backend="numpy_nullable",
                    engine="pyarrow",
                )
                roster_dfs.append(df)
            if roster_dfs:
                roster_df = pd.concat(roster_dfs, ignore_index=True)
                roster_df.to_parquet(
                    rosters_parquet, index=False, engine="pyarrow", compression="zstd"
                )
                print(f"Roster written to {rosters_parquet}")

            # create and write teams file
            teams_file = os.path.join(temp_dir, f"TEAM{year}")
            teams_df = pd.read_csv(
                teams_file,
                header=None,
                names=["Abbreviation", "League", "City", "Team"],
                dtype=str,
                dtype_backend="pyarrow",
                engine="pyarrow",
            )
            teams_df.to_parquet(teams_parquet, index=False, engine="pyarrow", compression="zstd")
            print(f"Teams written to {teams_parquet}")


def _load_retrosheet_file(
    kind, year, data_dir="retrosheet", force_download=False, postseason=False, allstar=False
):
    """
    Helper to load a retrosheet file (pbp, rosters, teams) for a given year and type.
    """
    if postseason and allstar:
        raise ValueError("Only one of 'postseason' or 'allstar' can be True.")
    suffix = ""
    if postseason:
        suffix = "-post"
    elif allstar:
        suffix = "-allstar"
    filename = f"{kind}-{year}{suffix}.parquet"
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath) or force_download:
        download_events(year, postseason=postseason, allstar=allstar, data_dir=data_dir)
    return pd.read_parquet(filepath, engine="pyarrow")


def load_pbp(year, data_dir="retrosheet", force_download=False, postseason=False, allstar=False):
    return _load_retrosheet_file("pbp", year, data_dir, force_download, postseason, allstar)


def load_rosters(
    year, data_dir="retrosheet", force_download=False, postseason=False, allstar=False
):
    return _load_retrosheet_file("rosters", year, data_dir, force_download, postseason, allstar)


def load_teams(year, data_dir="retrosheet", force_download=False, postseason=False, allstar=False):
    return _load_retrosheet_file("teams", year, data_dir, force_download, postseason, allstar)


def download_gamelogs(start_year, end_year=None, data_dir="retrosheet"):

    # define end_year if not provided by user, only download start year
    if end_year is None:
        end_year = start_year

    # check that years are provided as integers
    if not (isinstance(start_year, int) and isinstance(end_year, int)):
        raise ValueError("'start_year' and 'end_year' must be integers.")

    # check that years are properly ordered
    if start_year > end_year:
        raise ValueError("'start_year' must be less than or equal to 'end_year'.")

    # make data directory if it does not exist
    os.makedirs(data_dir, exist_ok=True)

    # process gamelogs for each requested year
    for year in range(start_year, end_year + 1):

        # intro messaging
        print(f"Downloading and parsing gamelogs for {year}.")

        # url for year's gamelogs
        url = f"http://www.retrosheet.org/gamelogs/gl{year}.zip"

        # setup files to be downloaded to created
        gamelogs_parquet = os.path.join(data_dir, f"gamelogs-{year}.parquet")

        with tempfile.TemporaryDirectory() as temp_dir:
            zipped_file = os.path.join(temp_dir, f"gl{year}.zip")
            gamelogs_txt = os.path.join(temp_dir, f"gl{year}.txt")

            # obtain zipped gamelogs from retrosheet website
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(zipped_file, "wb") as f:
                f.write(r.content)

            # decompress downloaded gamelogs
            with zipfile.ZipFile(zipped_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # parse the gamelogs
            df = pd.read_csv(
                gamelogs_txt,
                header=None,
                names=gamelogs_header,
                dtype_backend="numpy_nullable",
                engine="pyarrow",
            )

            # write parsed gamelogs to disk as parquet file
            df.to_parquet(gamelogs_parquet, index=False, engine="pyarrow", compression="zstd")
            print(f"Gamelogs written to {gamelogs_parquet}")

        # summary messaging
        print(f"Finished downloading and parsing gamelogs for {year}.")
        print(f"")


def load_gamelogs(year, data_dir="retrosheet", force_download=False):
    gamelogs_parquet = os.path.join(data_dir, f"gamelogs-{year}.parquet")
    if not os.path.exists(gamelogs_parquet) or force_download:
        download_gamelogs(year, data_dir=data_dir)
    return pd.read_parquet(gamelogs_parquet, engine="pyarrow")


def download_chadwick(install_dir="chadwick"):
    install_dir = os.path.join(os.getcwd(), install_dir)
    os.makedirs(install_dir, exist_ok=True)
    if os.name == "nt":
        url = "https://github.com/chadwickbureau/chadwick/releases/download/v0.10.0/chadwick-0.10.0-win.zip"
        filename = "chadwick-0.10.0-win.zip"
        print(f"Downloading Chadwick tools to {install_dir}")
    else:
        url = "https://github.com/chadwickbureau/chadwick/releases/download/v0.10.0/chadwick-0.10.0.tar.gz"
        filename = "chadwick-0.10.0.tar.gz"
        print(f"This function currently only supports Windows.")
        return None
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_file = os.path.join(temp_dir, filename)
        print(f"Downloading {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(archive_file, "wb") as f:
            f.write(r.content)
        print(f"Extracting to {temp_dir}")
        if filename.endswith(".zip"):
            with zipfile.ZipFile(archive_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        elif filename.endswith(".tar.gz"):
            with tarfile.open(archive_file, "r:gz") as tar_ref:
                tar_ref.extractall(temp_dir, filter="data")
        extracted_dirs = [
            d
            for d in os.listdir(temp_dir)
            if os.path.isdir(os.path.join(temp_dir, d)) and not d.startswith(".")
        ]
        if extracted_dirs:
            chadwick_dir = os.path.join(temp_dir, extracted_dirs[0])
        else:
            if os.name == "nt":
                exe_files = [f for f in os.listdir(temp_dir) if f.endswith(".exe")]
            else:
                exe_files = None
            if exe_files:
                chadwick_dir = temp_dir
            else:
                raise RuntimeError("No Chadwick tools found in extracted archive")
        for item in os.listdir(chadwick_dir):
            if item.endswith((".zip", ".tar.gz")) or item.startswith("."):
                continue
            src = os.path.join(chadwick_dir, item)
            dst = os.path.join(install_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    print(f"Chadwick tools installed to: {install_dir}")
    if os.name == "nt":
        print(f"You can now use cwevent_dir='{install_dir}' in download_events().")
    return install_dir
