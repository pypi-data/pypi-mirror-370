import socket

import pytest
from dcscope.gui import update


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect(("www.python.org", 80))
        NET_AVAILABLE = True
    except socket.gaierror:
        # no internet
        NET_AVAILABLE = False


@pytest.mark.skipif(not NET_AVAILABLE, reason="No network connection!")
def test_update_basic():
    mdict = update.check_release(ghrepo="DC-analysis/DCscope",
                                 version="2.0.0a1")
    assert mdict["errors"] is None
    assert mdict["update available"]
    mdict = update.check_release(ghrepo="DC-analysis/DCscope",
                                 version="8472.0.0")
    assert mdict["errors"] is None
    assert not mdict["update available"]
