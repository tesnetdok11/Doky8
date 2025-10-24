def choose_rr(prob):
    # returns (SL_pct, TP_pct) relative values or risk rules
    if prob >= 0.95: return (0.0025, 0.01)
    if prob >= 0.90: return (0.005, 0.02)
    if prob >= 0.85: return (0.0075, 0.02)
    if prob >= 0.75: return (0.01, 0.015)
    return (0.02, 0.02)
