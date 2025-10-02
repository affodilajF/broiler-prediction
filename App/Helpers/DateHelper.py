
from datetime import datetime, timezone, timedelta

def utc_to_offset_iso(dt, offset_str):
    # Convert UTC datetime to specified offset and return ISO format string
    if dt is None:
        return None
    hours = int(offset_str[:3])
    minutes = int(offset_str[4:])
    offset = timezone(timedelta(hours=hours, minutes=minutes))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(offset).isoformat()

def offset_to_utc(date_str, offset_str="+00:00"):
    # Convert date string with specified offset to UTC datetime
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    hours = int(offset_str[:3])
    minutes = int(offset_str[4:])
    offset = timezone(timedelta(hours=hours, minutes=minutes))
    date_with_tz = date_obj.replace(tzinfo=offset)
    date_utc = date_with_tz.astimezone(timezone.utc)
    return date_utc

from datetime import datetime, timedelta, timezone

def local_to_offset_iso(date_input, offset_str):
    """
    Terima date_input yang bisa string 'YYYY-MM-DD' atau datetime (naive),
    lalu convert ke datetime aware dengan timezone sesuai offset_str (misal '+07:00').

    Return datetime aware dengan offset timezone.
    """
    from datetime import datetime, timezone, timedelta

    # Step 1: Parse date_input ke datetime jika masih string
    if isinstance(date_input, str):
        date_dt = datetime.strptime(date_input, "%Y-%m-%d")
    elif isinstance(date_input, datetime):
        date_dt = date_input
    else:
        raise ValueError("date_input harus string 'YYYY-MM-DD' atau datetime object")

    # Step 2: Parse offset_str ke timezone offset
    sign = 1 if offset_str.startswith('+') else -1
    hours, minutes = map(int, offset_str[1:].split(':'))
    offset = timezone(sign * timedelta(hours=hours, minutes=minutes))

    # Step 3: Set timezone offset ke datetime lokal (aware)
    aware_local_dt = date_dt.replace(tzinfo=offset)

    # Jangan convert ke UTC, langsung return aware local datetime dengan offset
    return aware_local_dt


def now_with_offset_iso_dt(offset_str):
    """
    Return current datetime with given offset as timezone-aware datetime object.
    """
    sign = 1 if offset_str.startswith('+') else -1
    hours, minutes = map(int, offset_str[1:].split(':'))
    offset = timezone(sign * timedelta(hours=hours, minutes=minutes))

    now = datetime.now(offset)
    return now



