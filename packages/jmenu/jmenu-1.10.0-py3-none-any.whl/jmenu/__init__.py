"""
jmenu is a tool and python library for fetching University of Oulu restaurant menus from
the Jamix API.

jmenu can be invoked from the command line as is:

```shell
jmenu [-h] [-v] [-e] [-t] [-l {fi,en}] [-a markers [G, VEG ...]]
```

Additional flags and parameters described below

| Argument        | Example | Description                             |
| :-------------- | :------ | :-------------------------------------- |
| -a, --allergens | g veg   | Highlights appropriately marked results |

| Flag           | Description                         |
| :------------- | :---------------------------------- |
| -h, --help     | Display usage information           |
| -v, --version  | Display version information         |
| -e, --explain  | Display allergen marker information |
| -t, --tomorrow | Fetch menu results for tomorrow     |
| -l, --language | Result language, opts: {fi, en}     |

jmenu can also be imported as a library:

```python
from jmenu import main

main.run()
```

Documentation for the library can be found in the [project pages](https://jkerola.github.io/jmenu)
"""

from .classes import (
    JamixApi,
    JamixRestaurant,
    Marker,
    MealdooApi,
    MealdooRestaurant,
    MenuItem,
    MenuItemFactory,
    Restaurant,
)

__all__ = [
    "Restaurant",
    "MealdooRestaurant",
    "JamixRestaurant",
    "ApiEndpoint",
    "JamixApi",
    "MealdooApi",
    "Marker",
    "MenuItem",
    "MenuItemFactory",
]
