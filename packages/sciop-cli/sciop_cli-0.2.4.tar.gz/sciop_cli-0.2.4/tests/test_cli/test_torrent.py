import bencode_rs
import pytest
from click.testing import CliRunner

from sciop_cli.cli import torrent
from sciop_cli.data import get_default_trackers
from sciop_cli.exceptions import NoTrackersWarning

from ..conftest import DATA_DIR


@pytest.mark.parametrize("version", ["hybrid", "v2"])
def test_create_torrent(tmp_path, version):
    trackers = ["udp://example.com:6969", "http://example.com/announce.php"]
    webseeds = ["https://example.com/files"]
    output = tmp_path / "basic.torrent"
    args = [
        "-p",
        str(DATA_DIR / "basic"),
        "-o",
        str(output),
        "--creator",
        "sciop-tests",
        "--comment",
        "test",
        "-s",
        16 * (2**10),
    ]
    for tracker in trackers:
        args.extend(["--tracker", tracker])
    for webseed in webseeds:
        args.extend(["--webseed", webseed])
    if version == "v2":
        args.append("--v2")

    runner = CliRunner()
    result = runner.invoke(torrent.create, args)
    assert result.exit_code == 0
    expected = bencode_rs.bdecode((DATA_DIR / f"basic_{version}.torrent").read_bytes())
    created = bencode_rs.bdecode(output.read_bytes())

    # remove creation_date, which can't be set from python libtorrent
    del created[b"creation date"]
    if b"creation date" in expected:
        del expected[b"creation date"]

    # qbittorrent assigns trackers to the same tier by default,
    # while we assign each to a different tier.
    expected[b"announce-list"] = [[t] for t in expected[b"announce-list"][0]]

    assert bencode_rs.bencode(expected) == bencode_rs.bencode(created)


@pytest.mark.parametrize(
    "tracker",
    [
        ["udp://otherexample.com/:6969"],
        ["udp://otherexample.com/:6969", "udp://thirdexample.com/:6969"],
        None,
    ],
)
@pytest.mark.parametrize("default_trackers", [True, False, None])
def test_create_torrent_with_default_trackers(tmp_path, tracker, default_trackers, capsys):
    """
    - If we aren't given any trackers, and we don't specify default trackers, we add them
    - If we aren't given any trackers, and we specify no default trackers,
      we don't and emit a warning
    - If we are given trackers, and we don't specify default trackers, we don't add them
    - If we are given trackers, and we specify default trackers, we add them.
    """
    output = tmp_path / "basic.torrent"
    args = [
        "-p",
        str(DATA_DIR / "basic"),
        "-o",
        str(output),
    ]
    if tracker:
        for t in tracker:
            args.extend(["--tracker", t])

    if default_trackers:
        args.append("--default-trackers")
    elif default_trackers is False:
        # aka it's False
        args.append("--no-default-trackers")

    runner = CliRunner()
    if default_trackers is False and not tracker:
        # ensure we warn when creating torrents with no trackers
        with pytest.warns(NoTrackersWarning):
            result = runner.invoke(torrent.create, args)
    else:
        result = runner.invoke(torrent.create, args)

    assert result.exit_code == 0

    created = bencode_rs.bdecode(output.read_bytes())

    # if creating a torrent with no trackers, return early
    if default_trackers is False and not tracker:
        assert b"announce" not in created
        assert b"announce-list" not in created
        return
    # otherwise if we have a single tracker and no defaults, there isn't an announce list
    elif (tracker and len(tracker) == 1) and (
        default_trackers is None or default_trackers is False
    ):
        assert created[b"announce"] == tracker[0].encode("utf-8")
        assert b"announce-list" not in created
        return

    default_tracker_list = get_default_trackers()
    flat_tracker_list = []
    for tier in created[b"announce-list"]:
        flat_tracker_list.extend([t.decode("utf-8") for t in tier])

    # check if we have default trackers (if we should)
    if default_trackers or (not tracker and default_trackers is None):
        assert all([t in flat_tracker_list for t in default_tracker_list])
    else:
        assert not any([t in flat_tracker_list for t in default_tracker_list])

    # if we supplied a tracker, it should be included and it should be first
    if tracker:
        assert flat_tracker_list[0] == tracker[0]
