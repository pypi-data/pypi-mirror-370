# pylint: disable=missing-function-docstring
from unittest.mock import patch, Mock
import pytest

from skill_markII_audio_receiver.systemd import (
    get_service_status,
    normalize_service_name,
)

# Unit Tests


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("bluetooth", "bluetooth.service"),
        ("bluetooth.service", "bluetooth.service"),
        ("bluetooth.serv", "bluetooth.serv.service"),
        ("raspotify", "raspotify.service"),
        ("raspotify.service", "raspotify.service"),
        ("raspotify.serv", "raspotify.serv.service"),
        ("uxplay", "uxplay.service"),
        ("uxplay.service", "uxplay.service"),
        ("uxplay.serv", "uxplay.serv.service"),
    ],
)
def test_normalize_service_name(name, expected):
    assert normalize_service_name(name) == expected


def test_status():
    mock_output = "bluetooth.service - Bluetooth service"
    with patch("subprocess.run", return_value=Mock(returncode=0, stdout=mock_output.encode("utf-8"))):
        status = get_service_status("bluetooth")
        assert isinstance(status, bool)
        assert status is True
