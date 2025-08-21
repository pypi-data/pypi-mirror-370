import pandas as pd

from jtools import consts as C


def get_trading_dates(market, startdate: str, enddate: str):
    """获取交易日"""
    exdates = C.HOLIDAYS.get(market, 'SH')
    if startdate < "20241231":
        all_hisdates = pd.read_csv(f'data/trddt_{market}.csv', header=None, dtype=str)
    else:
        all_hisdates = []
    all_bdates = pd.bdate_range(start=max(startdate, "20241231"), end=enddate).strftime("%Y%m%d").tolist()
    all_trddts = list(sorted(set(all_hisdates + all_bdates) - set(exdates)))
    return all_trddts

