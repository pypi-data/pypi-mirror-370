import pandas as pd
import os

from jtools import consts as C


def get_trading_dates(market, startdate: str, enddate: str):
    """获取交易日"""
    exdates = C.HOLIDAYS.get(market, 'SH')
    if startdate < "20241231":
        # fp_his = os.path.join(os.path.dirname(__file__), f'data/trddt_{market}.csv')
        fp_his = f'data/trddt_{market}.csv'
        all_hisdates = pd.read_csv(fp_his, header=None, dtype=str)
    else:
        all_hisdates = []
    all_bdates = pd.bdate_range(start=max(startdate, "20241231"), end=enddate).strftime("%Y%m%d").tolist()
    all_trddts = list(sorted(set(all_hisdates + all_bdates) - set(exdates)))
    return all_trddts

