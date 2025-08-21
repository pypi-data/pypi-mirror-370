from datetime import datetime, timedelta

def current_time_iso():
    return datetime.now().isoformat()

def can_collect_daily(last_collected):
    if not last_collected:
        return True
    last_time = datetime.fromisoformat(last_collected)
    return datetime.now() - last_time >= timedelta(days=1)

def time_left(last_collected):
    if not last_collected:
        return "0:00:00"
    last_time = datetime.fromisoformat(last_collected)
    remaining = timedelta(days=1) - (datetime.now() - last_time)
    return str(remaining).split('.')[0]
