def detect_cisd_in_df(df, lookback=30):
    events = []
    lows = df['low'].astype(float)
    for i in range(lookback, len(lows)-2):
        low = lows.iat[i]
        if low < lows.iloc[i-lookback:i].min():
            events.append({'type':'bull_sweep','idx':i,'time':str(df.index[i])})
    return events
