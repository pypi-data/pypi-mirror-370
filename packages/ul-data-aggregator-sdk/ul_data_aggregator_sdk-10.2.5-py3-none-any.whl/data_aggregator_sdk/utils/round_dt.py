from datetime import datetime
from typing import Callable


def round_dt(dt: datetime, round_func: Callable[[datetime], datetime]) -> datetime:
    dt_timezone = dt.tzinfo
    dt = dt.replace(tzinfo=None)
    rounded_dt = round_func(dt)
    return rounded_dt.replace(tzinfo=dt_timezone)
