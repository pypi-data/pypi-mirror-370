from datetime import datetime
from unittest.mock import patch

from jmenu.classes import (
    MARKERS,
    RESTAURANTS,
    JamixApi,
    JamixRestaurant,
    Marker,
    MealdooRestaurant,
    MenuItem,
    MenuItemFactory,
)
from tests.conftest import mock_fetch_restaurant


def test_jamix_rest():
    rest = JamixRestaurant("test", 1, 2, 3, ["test"])
    assert rest is not None
    assert rest.name == "test"
    assert rest.client_id == 1
    assert rest.kitchen_id == 2
    assert rest.menu_type == 3
    assert rest.relevant_menus == ["test"]


def test_mealdoo_rest():
    rest = MealdooRestaurant("test", "menu", "org")
    assert rest is not None
    assert rest.name == "test"
    assert rest.menu_name == "menu"
    assert rest.organization == "org"


def test_marker():
    mark = Marker("t", "test")
    assert mark is not None
    assert mark.letters == "t"
    assert mark.explanation == "test"


def test_menu_item():
    item = MenuItem("test", "t")
    assert item is not None
    assert item.diets == "t"
    assert item.name == "test"


def test_restaurants():
    assert RESTAURANTS is not None
    assert len(RESTAURANTS) == 6
    for rest in RESTAURANTS:
        assert rest is not None
        assert rest.name is not None


def test_markers():
    assert MARKERS is not None
    assert len(MARKERS) == 10
    for mark in MARKERS:
        assert mark is not None
        assert mark.letters is not None


@patch("jmenu.classes.requests.get", side_effect=mock_fetch_restaurant)
def test_fetch_restaurant(self):
    rest = list(filter(lambda x: x.name == "Mara", RESTAURANTS)).pop()
    fac = MenuItemFactory()
    results = fac.get_menu_items(rest, datetime.now(), lang_code="fi")
    assert len(results) == 6
    names = [item.name for item in results]
    assert "Punajuurisosekeitto" in names


def test_jamix_parsing(mock_jamix):
    items = JamixApi().parse_items(mock_jamix, [])
    assert len(items) == 20
