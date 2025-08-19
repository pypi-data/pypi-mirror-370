from jmenu.main import get_version, run
from importlib.metadata import version, PackageNotFoundError
from unittest.mock import patch
from conftest import mock_fetch_restaurant, mock_fetch_restaurant_fail


def test_version_system():
    try:
        comp = version("jmenu")
    except PackageNotFoundError:
        comp = "development build"
    assert get_version() == comp


@patch("jmenu.classes.requests.get", side_effect=mock_fetch_restaurant)
def test_run(self, capsys):
    exit_code = run()
    assert exit_code == 0
    out, _ = capsys.readouterr()
    assert "Creme" in out


@patch("jmenu.classes.requests.get", side_effect=mock_fetch_restaurant_fail)
def test_run_on_failed_fetch(self, capsys):
    exit_code = run()
    assert exit_code == 1
    out, _ = capsys.readouterr()
    assert "Creme" not in out
