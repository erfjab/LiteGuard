from datetime import datetime


def time_diff(target: datetime, now: datetime = datetime.now()) -> str:
    delta = target - now
    total_seconds = abs(int(delta.total_seconds()))
    is_future = delta.total_seconds() > 0

    units = [(86400, "day"), (3600, "hour"), (60, "minute"), (1, "second")]

    for seconds, name in units:
        if total_seconds >= seconds:
            value = total_seconds // seconds
            direction = "from now" if is_future else "ago"
            return f"{value} {name} {direction}"

    return "now"
