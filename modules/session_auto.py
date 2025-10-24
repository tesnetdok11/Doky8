from datetime import datetime
def get_session(dt=None):
    dt = dt or datetime.utcnow()
    h = dt.hour
    if 0 <= h < 8: return 'Asia'
    if 8 <= h < 15: return 'London'
    return 'NewYork'
