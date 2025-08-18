from datetime import datetime, timedelta


def calc_delta(time: datetime) -> timedelta:
    """
    Calculate how much time has passed since the time
    """
    return datetime.now()-(
        datetime
        .fromtimestamp(time.timestamp())
    )
