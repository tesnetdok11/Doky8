def compute_orderflow(df):
    vol = df['volume'].astype(float).iloc[-30:]
    z = 0.0
    if vol.std() != 0:
        z = float((vol.iloc[-1]-vol.mean())/vol.std())
    return {'vol_z': z, 'last_vol': float(vol.iloc[-1])}
