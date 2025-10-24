import os, pandas as pd
from dotenv import load_dotenv
load_dotenv()
try:
    from binance.client import Client
except Exception:
    Client = None
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
def fetch_klines(pair='BTCUSDT', interval='1m', limit=500):
    if Client is None or not API_KEY:
        print('Binance client not available or API key missing.')
        return None
    client = Client(API_KEY, API_SECRET, {"timeout":10})
    try:
        kl = client.get_klines(symbol=pair, interval=interval, limit=limit)
        df = pd.DataFrame(kl, columns=['open_time','open','high','low','close','volume','close_time','qv','count','tbv','tbqv','ignore'])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df = df.set_index('open_time')
        for c in ['open','high','low','close','volume']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna()
        return df
    except Exception as e:
        print('Binance fetch error', e)
        return None

def resample_ohlc(df, target_tf='15m'):
    rule = target_tf.replace('m','T').replace('h','H')
    agg = {'open':'first','high':'max','low':'min','close':'last','volume':'sum'}
    df_res = df.resample(rule).agg(agg).dropna()
    return df_res
