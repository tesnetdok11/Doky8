import os, pandas as pd
from pathlib import Path
DS = Path('storage/dataset.csv')
def log_signal(rec):
    DS.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([rec])
    if DS.exists():
        df.to_csv(DS, mode='a', header=False, index=False)
    else:
        df.to_csv(DS, index=False)
    print('Logged signal:', rec)
