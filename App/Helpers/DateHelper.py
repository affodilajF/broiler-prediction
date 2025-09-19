
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