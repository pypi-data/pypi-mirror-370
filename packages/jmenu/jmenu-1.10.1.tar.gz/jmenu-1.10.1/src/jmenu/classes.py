"""
Contains dataclasses jmenu uses to manage data.

The following collections are use-case specific to the University of Oulu:

    * MARKERS
    * RESTAURANTS
    * SKIPPED_ITEMS
"""

from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import NamedTuple

import requests


class MenuItem(NamedTuple):
    """Dataclass for single menu items and their properties

    Attributes:
        name (str):
            name of the dish
        diets ([str]):
            list of allergen markers

    Methods:
        diets_to_string: returns the list of diets as a joined string.
    """

    name: str
    diets: Iterable[str]

    def diets_to_string(self) -> str:
        """Returns the diets associated with this MenuItem as spaced string."""
        return " ".join(self.diets)

    def __eq__(self, other):
        """Compare two MenuItems with each other. Only considers name.

        Args:
            other (MenuItem): MenuItem to compare with

        Returns:
            MenuItem: MenuItem to compare with
        """
        return self.name == other.name


class Restaurant:
    name: str

    def __init__(self, name: str):
        self.name = name


class MealdooRestaurant(Restaurant):
    """API representation and utility class for Mealdoo restaurants.

    Attributes:
        menu_name (str): string identifier of the menu
        organization (str): string identifier of the restaurant organization
    """

    menu_name: str
    organization: str

    def __init__(self, name: str, menu_name: str, organization: str):
        self.menu_name = menu_name
        self.organization = organization
        Restaurant.__init__(self, name)


class JamixRestaurant(Restaurant):
    """Dataclass for relevant restaurant information

    Attributes:
        name (str):
            name of the restaurant
        client_id (int):
            internal jamix identifier used for restaurant providers
        kitchen_id (int):
            internal jamix identifier used to assign menu content
        menu_type (int):
            internal jamix identifier used to classify menus based on content
        relevant_menus ([str]):
            menu names used for filtering out desserts etc.
    """

    client_id: int
    kitchen_id: int
    menu_type: int
    relevant_menus: Iterable[str]

    def __init__(self, name, client_id, kitchen_id, menu_type, relevant_menus):
        Restaurant.__init__(self, name)
        self.client_id = client_id
        self.menu_type = menu_type
        self.kitchen_id = kitchen_id
        self.relevant_menus = relevant_menus


class SodexoRestaurant(Restaurant):
    """API representation and utility class

    Attributes:
        client_id (int): numerical representation of the client id
    """

    client_id: int

    def __init__(self, name, client_id: int):
        super().__init__(name)
        self.client_id = client_id


class Marker(NamedTuple):
    """Dataclass for allergen information markings

    Attributes:
        letters (str):
            allergen markings
        explanation (dict):
            extended information about the marker, in lang_code: explanation pairs.


    Methods:
        get_explanation(lang: str): returns the explanation string for this Marker. Defaults to english.
    """

    letters: str
    explanation: Mapping

    def get_explanation(self, lang_code: str = "en"):
        "Returns the explanation in the language specified by lang_code. Defaults to english."
        exp = self.explanation.get(lang_code)
        return exp if exp is not None else f"No explanation available for '{lang_code}'"


# TODO: Remove extra space when the API response is fixed
SKIPPED_ITEMS = [
    "proteiinilisäke",
    "Täysjyväriisi",
    "Täyshyväriisiä",
    "Lämmin kasvislisäke",
    "Höyryperunat",
    "Keitetyt perunat",
    "Tumma pasta",
    "Meillä tehty perunamuusi",
    "Mashed Potatoes",
    "Dark Pasta",
    "Whole Grain Rice",
    "Hot Vegetable  Side",  # note the extra space
]

RESTAURANTS = [
    JamixRestaurant("Foobar", 93077, 69, 84, ["Foobar Salad and soup", "Foobar Rohee"]),
    JamixRestaurant("Kerttu", 93077, 70, 118, ["Kerttu lounas"]),
    JamixRestaurant("Mara", 93077, 49, 111, ["Salad and soup", "Ravintola Mara"]),
    SodexoRestaurant("Mustikka & Hilla", 3305493),
    JamixRestaurant("Voltti", 93077, 70, 119, ["Voltti lounas"]),
]

MARKERS = [
    Marker("G", {"fi": "Gluteeniton", "en": "Gluten-free"}),
    Marker("M", {"fi": "Maidoton", "en": "Milk-free"}),
    Marker("L", {"fi": "Laktoositon", "en": "Lactose-free"}),
    Marker("SO", {"fi": "Sisältää soijaa", "en": "Contains soy"}),
    Marker("SE", {"fi": "Sisältää selleriä", "en": "Includes cellery"}),
    Marker("MU", {"fi": "Munaton", "en": "Egg-free"}),
    Marker(
        "[S], *",
        {
            "fi": "Kelan korkeakouluruokailunsuosituksen mukainen",
            "en": "Matches recommendation standards provided by KELA",
        },
    ),
    Marker("SIN", {"fi": "Sisältää sinappia", "en": "Contains mustard"}),
    Marker("<3", {"fi": "Sydänmerkki", "en": "Better choice indicator"}),
    Marker("VEG", {"fi": "Vegaani", "en": "Vegan"}),
]


class ApiEndpoint:
    """Base class for API endpoints."""

    baseUrl: str

    def create_url_for_restaurant(restaurant: Restaurant):
        pass

    def parse_items() -> list[MenuItem]:
        pass


class SodexoApi(ApiEndpoint):
    baseUrl = "https://www.sodexo.fi/ruokalistat/output/weekly_json"

    def create_url_for_restaurant(
        self,
        restaurant,
    ):
        return f"{self.baseUrl}/{restaurant.client_id}"

    def parse_items(self, data: dict, date: datetime, lang_code: str = "en"):
        items = []

        courses = data["mealdates"][(date.weekday())]["courses"]
        for course in courses.values():
            try:
                name = course[f"title_{lang_code}"]
                # disregard cafe puolukka
                if "puolukka" in name.lower():
                    continue
                diets = course.get("dietcodes")
                if diets:
                    diets = diets.replace(" ", "").split(",")
                else:
                    diets = []
                items.append(MenuItem(name, diets))
            except Exception:
                pass
        return items


class MealdooApi(ApiEndpoint):
    """Utility class for parsing Mealdoo API responses."""

    baseUrl = "https://api.fi.poweresta.com/publicmenu/dates"

    def create_url_for_restaurant(self, res: MealdooRestaurant, date: datetime) -> str:
        """Generate a URL with appropriate parameters for given [Restaurant].

        Args:
            res (MealdooRestaurant): Restaurant with appropriate metadata.
            date (datetime): Menu date.

        Returns:
            str: URL with formatted parameters.
        """
        return f"{self.baseUrl}/{res.organization}/{res.name.lower()}/?menu={res.menu_name}&dates={date.strftime('%Y-%m-%d')}"

    def parse_items(self, data: list[dict], lang_code: str) -> list[MenuItem]:
        """Create [MenuItems] based on response JSON.

        Args:
            data (list[dict]): Response JSON data.
            lang_code (str): Language code. Either "fi" or "en".

        Returns:
            list[MenuItem]: List of [MenuItems]
        """
        items = []
        for result in data:
            try:
                options = result["data"]["mealOptions"]
                for opt in options:
                    for row in opt["rows"]:
                        title = "???"
                        diets = []
                        for name in row["names"]:
                            if name["language"] == lang_code and name["name"]:
                                # title, *extra_diets = name["name"].split(",")
                                parts = name["name"].split(" ")
                                extra_diets = parts[-1].split(",")
                                if len(extra_diets) == 1 and len(extra_diets[0]) > 1:
                                    title = name["name"]
                                else:
                                    diets.extend(extra_diets)
                                    title = " ".join(parts[:-1])

                        for diet in row["diets"]:
                            if diet["language"] == lang_code and diet["dietShorts"]:
                                diets.extend(diet["dietShorts"])
                        diets = set([diet.strip() for diet in diets])
                        items.append(MenuItem(title if title else "???", diets))
            except Exception:
                pass

        return items


class JamixApi(ApiEndpoint):
    """Utility class for parsing Jamix API responses."""

    baseUrl = "https://fi.jamix.cloud/apps/menuservice/rest/haku/menu"

    def create_url_for_restaurant(
        self,
        res: JamixRestaurant,
        date: datetime,
        lang_code="en",
    ) -> str:
        """Returns the formatted URL with given restaurant metadata as parameters.

        Args:
            res (JamixRestaurant): Restaurant metadata.
            date (datetime): Menu date.
            lang_code (str, optional): Language. Defaults to "en".

        Returns:
            str: Formatted URL string.
        """
        return f"{self.baseUrl}/{res.client_id}/{res.kitchen_id}?lang={lang_code}&date={date.strftime('%Y%m%d')}"

    def parse_items(
        self, data: list[dict], relevant_menus: list[str]
    ) -> list[MenuItem]:
        """Returns a list of [MenuItems] parsed from JSON data

        Parameters:
            data (list[dict]):
                parsed JSON response from the jamix API, see api._fetch_restaurant
            relevant_menus (list[str]):
                list of menu names to filter when parsing
                defaults to all menus

        Returns:
            (list[MenuItem]):
                list of restaurant menu items
        """
        menus = []
        for kitchen in data:
            for m_type in kitchen["menuTypes"]:
                if len(relevant_menus) == 0 or m_type["menuTypeName"] in relevant_menus:
                    menus.extend(m_type["menus"])
        if len(menus) == 0:
            return []
        items = []
        for menu in menus:
            day = menu["days"][0]
            mealopts = day["mealoptions"]
            sorted(mealopts, key=lambda x: x["orderNumber"])
            for opt in mealopts:
                for item in opt["menuItems"]:
                    if item["name"] not in SKIPPED_ITEMS and len(item["name"]) > 0:
                        item = MenuItem(item["name"], item["diets"].split(","))
                        if item not in items:
                            items.append(item)
        return items


class MenuItemFactory:
    """Factory function for creating and parsing requests to all restaurant APIs."""

    jamix = JamixApi()
    mealdoo = MealdooApi()
    sodexo = SodexoApi()

    def get_menu_items(
        self,
        restaurant: JamixRestaurant | MealdooRestaurant,
        date: datetime,
        lang_code="en",
    ) -> list[MenuItem]:
        """Fetch and create menu items for given [Restaurant].

        Args:
            restaurant (JamixRestaurant | MealdooRestaurant | SodexoRestaurant): Restaurant metadata.
            date (datetime): Menu date.
            lang_code (str, optional): Result language. Defaults to "en".

        Returns:
            list[MenuItem]: List of [MenuItems].
        """
        if type(restaurant) is JamixRestaurant:
            url = self.jamix.create_url_for_restaurant(restaurant, date, lang_code)
            data = requests.get(url, timeout=5).json()
            return self.jamix.parse_items(data, restaurant.relevant_menus)

        elif type(restaurant) is MealdooRestaurant:
            url = self.mealdoo.create_url_for_restaurant(restaurant, date)
            data = requests.get(url, timeout=5).json()
            return self.mealdoo.parse_items(data, lang_code)
        elif type(restaurant) is SodexoRestaurant:
            url = self.sodexo.create_url_for_restaurant(restaurant)
            data = requests.get(url, timeout=5).json()
            return self.sodexo.parse_items(data, date, lang_code)
