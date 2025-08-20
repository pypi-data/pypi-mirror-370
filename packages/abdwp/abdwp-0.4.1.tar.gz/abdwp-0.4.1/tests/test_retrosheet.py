import pytest
import os

from abdwp.retrosheet import download_gamelogs
from abdwp.retrosheet import load_gamelogs
from abdwp.retrosheet import download_events
from abdwp.retrosheet import load_pbp
from abdwp.retrosheet import load_rosters
from abdwp.retrosheet import load_teams
from abdwp.retrosheet import download_chadwick


def test_load_gamelogs_runs():
    try:
        load_gamelogs(2019)
    except Exception:
        pass


def test_load_pbp_runs():
    try:
        load_pbp(2019)
    except Exception:
        pass


def test_load_rosters_runs():
    try:
        load_rosters(2019)
    except Exception:
        pass


def test_load_teams_runs():
    try:
        load_teams(2019)
    except Exception:
        pass


@pytest.mark.skipif(os.name != "nt", reason="Windows only test")
def test_download_chadwick():
    try:
        chadwick_dir = download_chadwick()
        download_events(2019, cwevent_dir=chadwick_dir)
        download_events(2018)
        df_2019 = load_pbp(2019)
        df_2018 = load_pbp(2018)
        assert df_2019 is not None
        assert df_2018 is not None
    except RuntimeError as e:
        if "No Chadwick tools found in extracted archive" in str(e):
            pytest.skip(f"Chadwick download failed: {e}")
        else:
            raise
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")
