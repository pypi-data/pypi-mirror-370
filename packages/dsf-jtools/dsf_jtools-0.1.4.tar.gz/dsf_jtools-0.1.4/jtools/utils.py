import pandas as pd
import os
from datetime import datetime, timedelta

from jtools import consts as C


def get_trading_dates(market, startdate: str, enddate: str):
    """获取交易日"""
    exdates = C.HOLIDAYS.get(market, 'SH')
    if startdate < "20241231":
        fp_his = os.path.join(os.path.dirname(__file__), f'data/trddt_{market}.csv')
        # fp_his = f'data/trddt_{market}.csv'
        all_hisdates = pd.read_csv(fp_his, header=None, dtype=str)
    else:
        all_hisdates = []
    all_bdates = pd.bdate_range(start=max(startdate, "20241231"), end=enddate).strftime("%Y%m%d").tolist()
    all_trddts = list(sorted(set(all_hisdates + all_bdates) - set(exdates)))
    return all_trddts


def get_last_trddt(market='SH') -> str:
    """获取：上一个成交日
    
    - 当日非交易日，默认返回前一个交易日
    - 当日交易日，返回当日
    :return: trddt in %Y%m%d format
    """
    _now = datetime.today()
    _stdate = (_now - timedelta(days=30)).strftime("%Y%m%d")
    _trddts = get_trading_dates(market, _stdate, _now.strftime("%Y%m%d"))
    return _trddts[-1]


def get_latest_trddt(market='SH') -> str:
    """获取：最近交易日

    - 当日交易日，返回当日
    - 当日非交易日，默认返回下一个交易日
    """
    _now = datetime.today()
    _eddate = (_now + timedelta(days=30)).strftime("%Y%m%d")
    _trddts = get_trading_dates(market, _now.strftime("%Y%m%d"), _eddate)
    return _trddts[0]
