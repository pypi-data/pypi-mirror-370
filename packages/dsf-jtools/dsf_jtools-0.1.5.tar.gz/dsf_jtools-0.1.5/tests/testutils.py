import sys
sys.path.append(r'F:\projects\jtools')

from jtools.utils import *

print(len(get_trading_dates('SH', '20240101', '20250821')))

trddts1 = ['20250102', '20250103', '20250106', '20250107', '20250108', '20250109', '20250110', '20250113', '20250114', '20250115', '20250116', '20250117', '20250120', '20250121', '20250122', '20250123', '20250124', '20250127']
assert trddts1 == get_trading_dates('SH', '20250101', '20250131')
assert trddts1 == get_trading_dates('DF', '20250101', '20250131')

trddts2 = ['20250428', '20250429', '20250430', '20250506', '20250507', '20250508', '20250509', '20250512', '20250513', '20250514', '20250515', '20250516']
assert trddts2 == get_trading_dates('SH', '20250428', '20250518')
assert trddts2 == get_trading_dates('DF', '20250428', '20250518')

lasttrddt = get_last_trddt()
assert lasttrddt == '20250821'

latesttrddt = get_latest_trddt()
assert lasttrddt == '20250821'
