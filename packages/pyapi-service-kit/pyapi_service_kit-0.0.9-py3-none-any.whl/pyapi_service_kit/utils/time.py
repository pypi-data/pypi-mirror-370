from datetime import datetime
from dateutil.parser import isoparse
import pytz


def parse_zoned_iso(s: str) -> datetime:
    if "[" in s and s.endswith("]"):
        base, zone = s.split("[")
        zone = zone.strip("]")
    else:
        base = s
        zone = None

    dt = isoparse(base)
    if zone:
        try:
            tz = pytz.timezone(zone)
            dt = dt.astimezone(tz)
        except Exception:
            # Fallback: use the parsed offset
            pass
    return dt
