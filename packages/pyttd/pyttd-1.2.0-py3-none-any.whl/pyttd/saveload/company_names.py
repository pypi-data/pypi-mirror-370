"""
Company Name Generation
"""

# String constants - from strings_type.h
SPECSTR_COMPANY_NAME_START = 0x70EA
SPECSTR_SILLY_NAME = 0x70E5
SPECSTR_ANDCO_NAME = 0x70E6
SPECSTR_PRESIDENT_NAME = 0x70E7

# Company name generation data - from strings.cpp
_silly_company_names = [
    "Bloggs Brothers",
    "Tiny Transport",
    "Express Travel",
    "Comfy-Coach & Co.",
    "Crush & Bump Ltd.",
    "Broken & Co.",
    "José's Car Lot",
    "Weekend Wanderers",
    "Hearse'R'Us",
    "Corpse Haulage",
    "Grim Reapers",
    "Crash & Burn Inc.",
    "Speedy Pete",
    "Railway Runners",
    "Highway Hawks",
    "Skyway Express",
    "Lightning Logistics",
    "Thunder Transport",
    "Storm Shipping",
    "Rain Rail",
    "Snow Speedway",
    "Freeze Freight",
    "Ice Transport",
    "Sleet & Sons",
    "Hail Holdings",
    "Drizzle Delivery",
    "Mist Motors",
    "Fog Freight",
    "Sunshine Shipping",
    "Cloud Nine",
    "Wind & Wings",
    "Storm & Stress Ltd.",
]

# President surname lists - from strings.cpp
_surname_list = [
    "Adams",
    "Allan",
    "Baker",
    "Bigwig",
    "Black",
    "Bloggs",
    "Brown",
    "Campbell",
    "Gordon",
    "Hamilton",
    "Hawthorn",
    "Higgins",
    "Green",
    "Gribble",
    "Jones",
    "McAlpine",
    "MacDonald",
    "McIntosh",
    "Muir",
    "Murphy",
    "Nelson",
    "O'Donnell",
    "Parker",
    "Phillips",
    "Pilkington",
    "Quigley",
    "Sharkey",
    "Thomson",
    "Watkins",
]


_initial_name_letters = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "R",
    "S",
    "T",
    "W",
]

# Color names - from company_base.h and table/palettes.h
_company_colors = [
    "Dark Blue",
    "Pale Green",
    "Pink",
    "Yellow",
    "Red",
    "Light Blue",
    "Green",
    "Dark Green",
    "Blue",
    "Cream",
    "Mauve",
    "Purple",
    "Orange",
    "Brown",
    "Grey",
    "White",
]


def generate_company_name(name_1: int, name_2: int) -> str:
    """Generate company name from name_1 and name_2"""
    if name_1 == SPECSTR_SILLY_NAME:
        # Silly company names
        index = min(name_2 & 0xFFFF, len(_silly_company_names) - 1)
        return _silly_company_names[index]
    elif name_1 == SPECSTR_ANDCO_NAME:
        # "& Co" company names
        return generate_andco_name(name_2)
    elif name_1 == SPECSTR_PRESIDENT_NAME:
        # President name as company name
        return generate_president_name(name_2)
    elif name_1 >= SPECSTR_COMPANY_NAME_START:
        # Town-based transport company names
        return generate_town_transport_name(name_1, name_2)
    else:
        return f"Company #{name_1}"


def generate_president_name(seed: int) -> str:
    """Generate president name from seed"""
    # Generate initial (first letter) - GB(x, 0, 8)
    initial_index = (len(_initial_name_letters) * ((seed >> 0) & 0xFF)) >> 8
    initial = _initial_name_letters[initial_index]

    # Generate surname - GB(x, 16, 8)
    surname_index = (len(_surname_list) * ((seed >> 16) & 0xFF)) >> 8
    surname = _surname_list[surname_index]

    return f"{initial}. {surname}"


def generate_andco_name(seed: int) -> str:
    """Generate 'Foobar & Co' company name"""
    # Use surname from bits 16-23 - GB(arg, 16, 8)
    surname_index = (len(_surname_list) * ((seed >> 16) & 0xFF)) >> 8
    surname = _surname_list[surname_index]
    return f"{surname} & Co."


def generate_town_transport_name(name_1: int, name_2: int) -> str:
    """Generate town-based transport company name
    A simplified implementation for now (only english). Future reference: townname.cpp"""

    town_type = name_1 - SPECSTR_COMPANY_NAME_START
    seed = name_2

    prefixes = ["", "Great ", "Little ", "New ", "Old ", "Upper ", "Lower "]
    roots = [
        "Amber",
        "Ash",
        "Aven",
        "Beck",
        "Bourne",
        "Brad",
        "Brent",
        "Bridge",
        "Brook",
        "Burn",
        "Burton",
        "Cam",
        "Carl",
        "Chester",
        "Church",
        "Clay",
        "Clear",
        "Cliff",
        "Comb",
        "Dale",
        "Dart",
        "Dun",
        "Eden",
        "Field",
        "Ford",
        "Glen",
        "Green",
        "Hamp",
        "Hill",
        "Holt",
        "Kel",
        "Ken",
        "King",
        "Lake",
        "Land",
        "Law",
        "Lee",
        "Lime",
        "Lin",
        "Mal",
        "Mel",
        "Mer",
        "Mill",
        "Moor",
        "Moss",
        "Nant",
        "New",
        "North",
        "Oak",
        "Over",
    ]
    suffixes = [
        "bridge",
        "brook",
        "burg",
        "burn",
        "bury",
        "by",
        "chester",
        "church",
        "cliff",
        "comb",
        "combe",
        "cross",
        "dale",
        "den",
        "dike",
        "don",
        "down",
        "field",
        "ford",
        "gate",
        "ham",
        "haven",
        "hill",
        "holt",
        "hope",
        "hurst",
        "ing",
        "ington",
        "ley",
        "ling",
        "low",
        "lyn",
        "marsh",
        "mead",
        "mill",
        "minster",
        "moor",
        "mouth",
        "ness",
        "ning",
        "over",
        "ridge",
        "shaw",
        "shire",
        "side",
        "stead",
        "stoke",
        "stone",
        "stow",
        "thorpe",
        "thwaite",
        "ton",
        "tree",
        "vale",
        "ville",
        "wall",
        "water",
        "well",
        "wick",
        "worth",
    ]

    # Generate town name from seed
    prefix = prefixes[(seed >> 24) % len(prefixes)]
    root = roots[(seed >> 16) & 0xFF % len(roots)]
    suffix = suffixes[(seed >> 8) & 0xFF % len(suffixes)]

    town_name = prefix + root + suffix
    return town_name + " Transport"


def get_color_name(color_index: int) -> str:
    """Convert color index to color name"""
    if 0 <= color_index < len(_company_colors):
        return _company_colors[color_index]
    return f"Color #{color_index}"
