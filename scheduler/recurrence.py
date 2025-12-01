import datetime

def next_run_time(rule, last_run):
    freq = rule["frequency"]

    if freq == "once":
        return datetime.datetime.fromisoformat(rule["time"])

    if freq == "daily":
        return last_run + datetime.timedelta(days=1)

    if freq == "hourly":
        return last_run + datetime.timedelta(hours=1)

    if freq == "weekly":
        return last_run + datetime.timedelta(weeks=1)

    if freq == "interval":
        return last_run + datetime.timedelta(seconds=rule["seconds"])

    raise ValueError("Unknown recurrence rule")