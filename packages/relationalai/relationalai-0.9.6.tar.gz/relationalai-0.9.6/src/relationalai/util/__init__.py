from datetime import datetime

def get_timestamp():
    return datetime.utcnow() # Would use `datetime.now(datetime.UTC)`, but it only works in 3.11.

