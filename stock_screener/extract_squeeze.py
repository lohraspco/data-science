
import os
import sys
import psycopg2
import pandas as pd
import pandas_ta as ta
sys.path.append("..")
sys.path.append("/home/lohrasp/lohrasp/analyticsoptim")
# os.chdir("..")
print(os.getcwd())
from stock_screener.watchlist import Watchlist
from database.postgres_sql_connect import get_engine
from database.database_helper import config
print("config file exists in the path",
      os.path.isfile("stock_screener/database.ini"))


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


params = config("stock_screener/database.ini")
conn = psycopg2.connect(**params)
symbs = pd.read_sql_query(
    """ select * from saffron."security" where sp500=True""", conn)


def convert_currency_to_float(a):
    if a is None:
        return a
    else:
        b = a.translate(str.maketrans({'$': '', ',': ''}))
        return float(b)


symbs["marketcap"] = symbs["marketcap"].apply(convert_currency_to_float)
selected_symbs = tuple(symbs.query('marketcap>100000')["symbol"].to_list())
ss = 'BYND'  # df_symb.symbol.to_list()[1]
# df = pd.read_sql_query(f""" select * from saffron.daily_price where symbol='{ss}' """, conn)
# df.set_index("date", inplace=True)
# df= df.sort_index()
momo_bands_sma_ta = [
    {"kind": "sma", "length": 50},
    {"kind": "sma", "length": 200},
    {"kind": "bbands", "length": 20},
    {'kind': 'squeeze'},
    {"kind": "macd"},
    {"kind": "rsi"},
    {"kind": "log_return", "cumulative": True},
    {"kind": "sma", "close": "CUMLOGRET_1", "length": 5, "suffix": "CUMLOGRET"},
]
momo_bands_sma_strategy = ta.Strategy(
    "Momo, Bands and SMAs and Cumulative Log Returns",  # name
    momo_bands_sma_ta,  # ta
    "MACD and RSI Momo with BBANDS and SMAs 50 & 200 and Cumulative Log Returns"  # description
)


def yprint(content):
    print(bcolors.WARNING)
    print(content)
    print(bcolors.ENDC)
def rprint(content):
    print(bcolors.HEADER)
    print(content)
    print(bcolors.ENDC)

engine = get_engine()
ss = 'VZ'
watch = Watchlist(tickers=[ss], ds=engine)
watch.set_strategy(momo_bands_sma_strategy)

fb = watch.load(ss)
fb.ta.constants(True, [0, 30, 70])
sss = fb.tail()['SQZ_ON'].sum()
if sss > 0:
    yprint(ss)
# for ss in selected_symbs:
#     try:
#         watch = Watchlist(tickers=[ss], ds=engine)
#         watch.set_strategy(momo_bands_sma_strategy)

#         fb = watch.load(ss)
#         fb.ta.constants(True, [0, 30, 70])
#         sss = fb.tail(2)['SQZ_ON'].sum()
#         if sss > 0:
#             yprint(ss)
#         else:
#             rprint(ss)
#     except:
#         print("there was a problem with ", ss)
# cur = conn.cursor()
# cur.execute(""" select * from saffron."security" where sp500=True""")
# symbs = cur.fetchall()
