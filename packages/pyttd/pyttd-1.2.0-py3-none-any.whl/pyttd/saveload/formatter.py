"""
Functions for formatting and converting OpenTTD data to sane and human-readable formats.
"""

from typing import Dict, List, Any, Optional, Collection, Union
from .company_names import generate_company_name, generate_president_name, get_color_name

# Expense categories - from economy_type.h
_expense_categories = [
    "Construction",  # EXPENSES_CONSTRUCTION
    "New Vehicles",  # EXPENSES_NEW_VEHICLES
    "Train Running",  # EXPENSES_TRAIN_RUN
    "Road Vehicle Running",  # EXPENSES_ROADVEH_RUN
    "Aircraft Running",  # EXPENSES_AIRCRAFT_RUN
    "Ship Running",  # EXPENSES_SHIP_RUN
    "Property",  # EXPENSES_PROPERTY
    "Train Revenue",  # EXPENSES_TRAIN_REVENUE
    "Road Vehicle Revenue",  # EXPENSES_ROADVEH_REVENUE
    "Aircraft Revenue",  # EXPENSES_AIRCRAFT_REVENUE
    "Ship Revenue",  # EXPENSES_SHIP_REVENUE
    "Loan Interest",  # EXPENSES_LOAN_INTEREST
    "Other",  # EXPENSES_OTHER
]


def convert_date_to_year(date_value: int) -> int:
    """Convert date value to year"""
    # Constants from timer_game_common.h
    ORIGINAL_BASE_YEAR = 1920

    # Calculate DAYS_TILL_ORIGINAL_BASE_YEAR (days from Year 0 to 1920)
    year_as_int = ORIGINAL_BASE_YEAR
    number_of_leap_years = (
        (year_as_int - 1) // 4 - (year_as_int - 1) // 100 + (year_as_int - 1) // 400 + 1
    )
    DAYS_TILL_ORIGINAL_BASE_YEAR = (365 * year_as_int) + number_of_leap_years

    # Convert date to years since base year
    days_since_base_year = date_value - DAYS_TILL_ORIGINAL_BASE_YEAR
    # Leap years (365.25 average)
    years_since_base = days_since_base_year / 365.25

    return int(ORIGINAL_BASE_YEAR + years_since_base)


def convert_date_to_ymd(date_value: int) -> Dict[str, int]:
    """Convert date value to year, month, day"""
    # Constants from OpenTTD source
    ORIGINAL_BASE_YEAR = 1920
    DAYS_TILL_ORIGINAL_BASE_YEAR = 701265  # Pre-calculated

    # Calculate days since base year
    days_since_base = date_value - DAYS_TILL_ORIGINAL_BASE_YEAR

    # Calculate year (accounting for leap years)
    year = ORIGINAL_BASE_YEAR
    remaining_days = days_since_base

    # Handle negative dates (before 1920)
    if remaining_days < 0:
        while remaining_days < 0:
            year -= 1
            days_in_year = 366 if is_leap_year(year) else 365
            remaining_days += days_in_year
    else:
        # Handle positive dates (after 1920)
        while remaining_days >= (366 if is_leap_year(year) else 365):
            days_in_year = 366 if is_leap_year(year) else 365
            remaining_days -= days_in_year
            year += 1

    # Calculate month and day
    days_in_month = [
        31,
        29 if is_leap_year(year) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]

    month = 1
    day_of_year = remaining_days + 1  # 1-based

    for month_days in days_in_month:
        if day_of_year <= month_days:
            day = day_of_year
            break
        day_of_year -= month_days
        month += 1
    else:
        # Shouldn't happen, but why not
        month = 12
        day = 31

    return {
        "year": year,
        "month": month,
        "day": day,
        "date_value": date_value,
        "days_since_base": days_since_base,
    }


def is_leap_year(year: int) -> bool:
    """Check if year is leap year"""
    return (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))


def format_inflation_value(inflation_value: int) -> Dict[str, Any]:
    """Convert inflation to human-readable format"""
    # Inflation uses 16-bit fractional representation
    # Base value is 1 << 16 = 65536 (representing 1.0x multiplier)
    BASE_INFLATION = 65536

    # Calculate multiplier
    multiplier = inflation_value / BASE_INFLATION

    # Calculate percentage change from base
    percentage_change = (multiplier - 1.0) * 100

    return {
        "raw_value": inflation_value,
        "multiplier": round(multiplier, 6),
        "percentage_change": round(percentage_change, 2),
        "description": f"{multiplier:.2f}x multiplier"
        + (
            f" (+{percentage_change:.1f}%)"
            if percentage_change > 0
            else f" ({percentage_change:.1f}%)" if percentage_change < 0 else " (no change)"
        ),
    }


def format_money(money: int, money_fraction: int = 0) -> int:
    """Format money as integer"""
    # OpenTTD money_fraction is additional cents/pence etc beyond the base money
    total_cents = money * 100 + money_fraction
    return round(total_cents / 100)


def format_coordinate(coord: int, map_size_x: int = 256) -> Optional[Dict[str, int]]:
    """Convert coordinate to x,y pair"""
    if coord == 0xFFFFFFFF:  # Invalid coordinate
        return None
    x = coord % map_size_x
    y = coord // map_size_x
    return {"x": x, "y": y}


def format_yearly_expenses(
    expenses: List[int], current_year: int = 1960
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Return per-year financial entries (expenses and revenues lists) for the last 3 years.

    - Expenses entries are shown as positive amounts
    - Revenue categories are stored as negative in OpenTTD; present as positive amounts
    """
    if len(expenses) != 39:
        return {"raw_data": expenses, "note": f"Unexpected length {len(expenses)}, expected 39"}

    years: List[Dict[str, Any]] = []

    # Process 3 years of data
    for year_idx in range(3):
        expenses_list: List[Dict[str, Any]] = []
        revenues_list: List[Dict[str, Any]] = []
        year_start = year_idx * 13
        actual_year = current_year - year_idx

        for cat_idx, category in enumerate(_expense_categories):
            raw_value = expenses[year_start + cat_idx]
            if "Revenue" in category:
                amount = format_money(abs(raw_value))
                revenues_list.append({"category": category, "amount": amount})
            else:
                amount = format_money(abs(raw_value))
                expenses_list.append({"category": category, "amount": amount})

        years.append({"year": actual_year, "expenses": expenses_list, "revenues": revenues_list})

    return years


def format_company_data(
    company: Dict[str, Any], current_year: Optional[int] = None, map_size_x: int = 256
) -> Dict[str, Any]:
    """Format company data for human-readable output"""
    formatted: Dict[str, Any] = {}

    name = company.get("name", "")
    name_1 = company.get("name_1", 0)
    name_2 = company.get("name_2", 0)

    if name and str(name).strip():
        formatted["name"] = str(name).strip()
    elif name_1 or name_2:
        formatted["name"] = generate_company_name(name_1, name_2)
    else:
        formatted["name"] = "Unknown Company"

    president_name = company.get("president_name", "")
    president_name_1 = company.get("president_name_1", 0)
    president_name_2 = company.get("president_name_2", 0)

    if president_name and str(president_name).strip():
        formatted["president_name"] = str(president_name).strip()
    elif president_name_1 or president_name_2:
        formatted["president_name"] = generate_president_name(president_name_2)
    else:
        formatted["president_name"] = "Unknown President"

    try:
        formatted["id"] = int(company.get("index", 0))
    except (ValueError, TypeError):
        formatted["id"] = 0

    try:
        formatted["money"] = int(company.get("money", 0))
    except (ValueError, TypeError):
        formatted["money"] = 0

    try:
        formatted["current_loan"] = int(company.get("current_loan", 0))
    except (ValueError, TypeError):
        formatted["current_loan"] = 0

    try:
        max_loan = int(company.get("max_loan", 0))
        # Check if max_loan is the default value (COMPANY_MAX_LOAN_DEFAULT)
        if max_loan == -9223372036854775808:
            formatted["max_loan"] = 300000  # TODO: Get this from settings
        else:
            formatted["max_loan"] = max_loan
    except (ValueError, TypeError):
        formatted["max_loan"] = 0

    try:
        formatted["is_ai"] = bool(int(company.get("is_ai", 0)))
    except (ValueError, TypeError):
        formatted["is_ai"] = False

    # Format color
    color_index = company.get("colour", 0)
    # Ensure color_index is an integer
    try:
        color_index = int(color_index)
    except (ValueError, TypeError):
        color_index = 0

    formatted["color"] = {"index": color_index, "name": get_color_name(color_index)}

    # Format coordinates - always include the key, even if None
    try:
        location = int(company.get("location_of_HQ", 0))
        if location != 0xFFFFFFFF:  # Valid coordinate
            # location_of_HQ is stored as a tile index, not separate x,y coordinates
            # Convert tile index to x,y coordinates using map_size_x
            # OpenTTD uses 0-based coordinates internally, but displays 1-based in UI
            log_x = (map_size_x - 1).bit_length()
            x_internal = location & ((1 << log_x) - 1)  # 0-based
            y_internal = location >> log_x  # 0-based
            x_display = x_internal + 1  # 1-based
            y_display = y_internal + 1  # 1-based
            formatted["headquarters"] = {"x": x_display, "y": y_display}
        else:
            formatted["headquarters"] = None
    except (ValueError, TypeError):
        formatted["headquarters"] = None

    try:
        last_build = int(company.get("last_build_coordinate", 0))
        if last_build != 0:
            # last_build_coordinate is stored as a tile index, not separate x,y coordinates
            # Convert tile index to x,y coordinates using map_size_x
            # OpenTTD uses 0-based coordinates internally, but displays 1-based in UI
            log_x = (map_size_x - 1).bit_length()
            x_internal = last_build & ((1 << log_x) - 1)  # 0-based
            y_internal = last_build >> log_x  # 0-based
            x_display = x_internal + 1  # 1-based
            y_display = y_internal + 1  # 1-based
            formatted["last_build"] = {"x": x_display, "y": y_display}
        else:
            formatted["last_build"] = None
    except (ValueError, TypeError):
        formatted["last_build"] = None

    # Format inauguration year
    try:
        inaugurated_year = int(company.get("inaugurated_year", 0))
        formatted["inaugurated_year"] = inaugurated_year
    except (ValueError, TypeError):
        formatted["inaugurated_year"] = 0

    # Format bankruptcy info
    try:
        formatted["months_of_bankruptcy"] = int(company.get("months_of_bankruptcy", 0))
    except (ValueError, TypeError):
        formatted["months_of_bankruptcy"] = 0

    try:
        formatted["bankrupt_timeout"] = int(company.get("bankrupt_timeout", 0))
    except (ValueError, TypeError):
        formatted["bankrupt_timeout"] = 0

    try:
        formatted["bankrupt_value"] = int(company.get("bankrupt_value", 0))
    except (ValueError, TypeError):
        formatted["bankrupt_value"] = 0

    # Format terraform/construction limits with proper units
    try:
        terraform_raw = int(company.get("terraform_limit", 0))
        terraform_actual = terraform_raw >> 16  # Remove the << 16 scaling
        formatted["terraform_limit"] = {
            "raw_value": terraform_raw,
            "tile_heights": terraform_actual,
            "description": f"{terraform_actual} tile heights",
        }
    except (ValueError, TypeError):
        formatted["terraform_limit"] = {
            "raw_value": 0,
            "tile_heights": 0,
            "description": "0 tile heights",
        }

    try:
        clear_raw = int(company.get("clear_limit", 0))
        clear_actual = clear_raw >> 16  # Remove the << 16 scaling
        formatted["clear_limit"] = {
            "raw_value": clear_raw,
            "tiles": clear_actual,
            "description": f"{clear_actual} tiles",
        }
    except (ValueError, TypeError):
        formatted["clear_limit"] = {"raw_value": 0, "tiles": 0, "description": "0 tiles"}

    try:
        tree_raw = int(company.get("tree_limit", 0))
        tree_actual = tree_raw >> 16  # Remove the << 16 scaling
        formatted["tree_limit"] = {
            "raw_value": tree_raw,
            "trees": tree_actual,
            "description": f"{tree_actual} trees",
        }
    except (ValueError, TypeError):
        formatted["tree_limit"] = {"raw_value": 0, "trees": 0, "description": "0 trees"}

    # Additional company fields
    try:
        formatted["money_fraction"] = int(company.get("money_fraction", 0))
    except (ValueError, TypeError):
        formatted["money_fraction"] = 0

    try:
        formatted["face"] = int(company.get("face", 0))
    except (ValueError, TypeError):
        formatted["face"] = 0

    try:
        formatted["block_preview"] = bool(int(company.get("block_preview", 0)))
    except (ValueError, TypeError):
        formatted["block_preview"] = False

    # Format yearly expenses if present
    yearly_expenses = company.get("yearly_expenses", [])
    if isinstance(yearly_expenses, list) and yearly_expenses:
        # Expose per-year data directly under a descriptive key
        formatted["yearly_financials"] = format_yearly_expenses(
            yearly_expenses, current_year or 1960
        )
    else:
        formatted["yearly_financials"] = []

    # Include raw data for debugging
    formatted["raw_data"] = company

    return formatted
