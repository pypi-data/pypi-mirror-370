from time import sleep

from pydantic import AnyUrl, TypeAdapter

from sciop_cli.data import DEFAULT_TRACKERS, get_default_trackers


def test_get_default_trackers():
    """
    We should be able to get default trackers,
    and only get them once if they already exist
    """
    DEFAULT_TRACKERS.unlink(missing_ok=True)
    trackers = get_default_trackers()
    assert DEFAULT_TRACKERS.exists()
    # we got some trackers
    assert len(trackers) > 0
    # they are all URIs
    validator = TypeAdapter(AnyUrl)
    assert all([validator.validate_python(t) for t in trackers])

    # ensure we don't get it twice
    first_mtime = DEFAULT_TRACKERS.stat().st_mtime_ns
    sleep(0.001)
    trackers2 = get_default_trackers()
    assert DEFAULT_TRACKERS.stat().st_mtime_ns == first_mtime
