import numpy as np
from datetime import datetime
def now_iso(): return datetime.utcnow().isoformat()

def analyze_structure(dfs):
    # simple multi-TF slope based structure detection
    counts = {'up':0,'down':0}
    for tf, df in dfs.items():
        try:
            last = df['close'].astype(float).iloc[-60:]
            slope = (last.iloc[-1]-last.iloc[0])/(last.iloc[0]+1e-9)
            if slope>0: counts['up'] += 1
            else: counts['down'] += 1
        except Exception:
            pass
    bias = 'BULLISH' if counts['up']>=counts['down'] else 'BEARISH'
    return {'bias': bias, 'counts': counts, 'time': now_iso()}
