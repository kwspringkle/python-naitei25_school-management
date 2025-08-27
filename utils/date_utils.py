from datetime import date


def determine_semester(target_date: date) -> int:
    """Return default semester (1..3) based on month mapping.

    Rules (inclusive):
    - Semester 1: Sep–Dec and Jan (month 9,10,11,12,1)
    - Semester 2: Feb–Jun (month 2,3,4,5,6)
    - Semester 3: Jul–Aug (month 7,8)

    Note: At boundary months Feb and Jul belong to the later semesters (2 and 3).
    """
    m = target_date.month
    if m in (9, 10, 11, 12, 1):
        return 1
    if m in (2, 3, 4, 5, 6):
        return 2
    # months 7,8
    return 3


def determine_academic_year_start(target_date: date) -> str:
    """Return the starting year (YYYY) of the academic year for a given date.

    Convention: academic year starts in September. For months Sep–Dec,
    return the current year; for months Jan–Aug, return previous year.
    """
    y = target_date.year
    return str(y if target_date.month >= 9 else y - 1)


def get_semester_date_range(year: str, semester: int) -> tuple[date, date]:
    """
    Returns the start and end dates for a given semester in an academic year.
    Args:
        year: Academic year string (e.g., "2024-2025")
        semester: Semester number (1, 2, or 3)
    Returns:
        Tuple of (start_date, end_date)
    """
    try:
        year_start = int(year.split('-')[0])
        year_end = year_start + 1
    except (ValueError, IndexError):
        # Default to current year if invalid format
        from datetime import datetime
        year_start = datetime.now().year
        year_end = year_start + 1

    if semester == 1:
        # Kỳ 1: September to January
        return (
            date(year_start, 9, 1),  # Sept 1st
            date(year_end, 1, 31)    # Jan 31st
        )
    elif semester == 2:
        # Kỳ 2: February to June
        return (
            date(year_end, 2, 1),    # Feb 1st
            date(year_end, 6, 30)    # June 30th
        )
    elif semester == 3:
        # Kỳ 3: July to August
        return (
            date(year_end, 7, 1),    # July 1st
            date(year_end, 8, 31)    # Aug 31st
        )
    else:
        raise ValueError("Semester must be 1, 2, or 3")