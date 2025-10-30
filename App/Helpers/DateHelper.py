
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


def get_today_utc():
    """
    Mengembalikan datetime saat ini (YYYY-MM-DD HH:MM:SS) dalam UTC
    """
    now_utc = datetime.now(timezone.utc)
    return now_utc


def get_today_range_for_wib():
    today_date_utc = datetime.now(timezone.utc).date()
    WIB_OFFSET = timedelta(hours=7)
    start_wib = datetime.combine(today_date_utc, datetime.min.time()) - WIB_OFFSET
    end_wib = datetime.combine(today_date_utc, datetime.max.time()) - WIB_OFFSET
    return start_wib.replace(tzinfo=timezone.utc), end_wib.replace(tzinfo=timezone.utc)


def get_today_range_utc(offset_str: str):
    # Parse offset string, misal "070" -> 7
    hours = int(offset_str[:3])
    local_tz = timezone(timedelta(hours=hours))

    # sekarang UTC
    now_utc = datetime.now(timezone.utc)

    # sekarang di zona lokal
    now_local = now_utc.astimezone(local_tz)

    # ambil tanggal hari ini di lokal
    today_local = now_local.date()

    # mulai & akhir hari lokal
    start_of_day_local = datetime.combine(today_local, datetime.min.time(), tzinfo=local_tz)
    end_of_day_local   = datetime.combine(today_local, datetime.max.time(), tzinfo=local_tz)

    # konversi ke UTC
    start_utc = start_of_day_local.astimezone(timezone.utc)
    end_utc   = end_of_day_local.astimezone(timezone.utc)

    return start_utc, end_utc



