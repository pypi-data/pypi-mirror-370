def humanized_duration(ms: int) -> str:
    seconds = ms / 1000
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    display_days = int(days)
    display_hours = int(hours % 24)
    display_minutes = int(minutes % 60)
    display_seconds = seconds % 60

    parts = []
    if display_days > 0:
        parts.append(f"{display_days}d")
    if display_hours > 0:
        parts.append(f"{display_hours}h")
    if display_minutes > 0:
        parts.append(f"{display_minutes}m")
    if display_seconds > 0:
        parts.append(f"{display_seconds:,.1f}s")
    return " ".join(parts[:3])

def humanized_bytes(bytes: int) -> str:
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 ** 2:
        return f"{bytes / 1024:.1f} KB"
    elif bytes < 1024 ** 3:
        return f"{bytes / 1024 ** 2:.1f} MB"
    elif bytes < 1024 ** 4:
        return f"{bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{bytes / 1024 ** 4:.1f} TB"

def str_to_bool(s):
    # Adapted from snowflake's convert_str_to_bool
    if s is None:
        return None
    if s.lower() in ("true", "t", "yes", "y", "on", "1"):
        return True
    if s.lower() in ("false", "f", "no", "n", "off", "0"):
        return False
    raise ValueError(f"Invalid boolean value: {s}")

def default_serialize(obj):
    return '<skipped>'
