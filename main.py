#!/usr/bin/env python3
"""Bot Doky v8.9 Core - Hybrid Crypto Focus (analysis only)"""
import os, time, json
from dotenv import load_dotenv
load_dotenv()

from modules import smc_ict_engine, orderflow_module, cisd_detector, session_auto, probability_matrix, risk_manager, telegram_bridge, binance_datafeed, autolearn

CFG = json.load(open('config.json'))
PAIRS = CFG.get('pairs', ['BTCUSDT'])
TFS = CFG.get('timeframes', ['1m','15m','1h'])
PROB_TH = CFG.get('prob_threshold', 0.85)

def build_multi_tf(pair):
    base='1m'
    df1 = binance_datafeed.fetch_klines(pair, interval=base, limit=1200)
    if df1 is None:
        return None
    out = {base: df1}
    for tf in TFS:
        if tf==base: continue
        out[tf] = binance_datafeed.resample_ohlc(df1, target_tf=tf)
    return out

def run_cycle():
    for p in PAIRS:
        dfs = build_multi_tf(p)
        if not dfs:
            print('No data for', p)
            continue
        sess = session_auto.get_session()
        structure = smc_ict_engine.analyze_structure(dfs)
        cisd = cisd_detector.detect_cisd_in_df(dfs['1m'])
        of = orderflow_module.compute_orderflow(dfs['1m'])
        prob = probability_matrix.estimate_probability(structure, cisd, of, sess)
        rr = risk_manager.choose_rr(prob)
        rec = {'pair':p, 'bias':structure.get('bias'), 'prob':prob, 'session':sess, 'rr':rr, 'time':structure.get('time')}
        print('[DO KY]', rec)
        autolearn.log_signal(rec)
        if CFG.get('telegram_enabled') and prob >= PROB_TH:
            txt = f"<b>{p}</b>\nBias: {structure.get('bias')}\nProb: {prob:.2f}\nSession: {sess}\nRR: {rr}"
            telegram_bridge.send_message(txt)

if __name__=='__main__':
    interval = 60
    while True:
        try:
            run_cycle()
        except Exception as e:
            print('Main loop error:', e)
        time.sleep(interval)
