def estimate_probability(structure, cisd_events, orderflow, session):
    # Basic heuristic combining signals to produce 0..1 probability
    score = 0.5
    if structure.get('bias') == 'BULLISH': score += 0.1
    if len(cisd_events) > 0: score += 0.12
    if orderflow.get('vol_z',0) > 1.0: score += 0.08
    if session == 'London': score += 0.03
    # clamp
    if score > 0.99: score = 0.99
    if score < 0.01: score = 0.01
    return round(score,4)
