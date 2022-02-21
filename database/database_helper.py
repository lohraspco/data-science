import yfinance
from datetime import datetime
import psycopg2
# from database.postgres_sql_connect import config
import os
from itertools import chain
from database.postgres_sql_connect import config
import pandas as pd
import numpy as np

# from frontend.database_sessions import SessionLocal


def get_pg_cursur():
    conn = psycopg2.connect(
        host="192.168.0.108",
        database="postgres",
        user="postgres",
        password="reallyStrongPwd123")
    curs = conn.cursor()
    return curs


def get_time_and_symbols():
    curs = get_pg_cursur()
    curs.execute("""select ticker from saffron.security where sp500=true""")
    symb = curs.fetchall()
    symb = list(chain(*symb))
    curs.execute("""select max(date)  from saffron.daily_price """)
    db_last_date = curs.fetchone()[0]
    db_last_date_next = db_last_date + pd.Timedelta(days=1)
    current_date = datetime.today()
    return db_last_date_next, current_date, symb


def add_bands(df, bolling_coeff=2, keltner_coeff=1.5, ma_window=20):
    df = df.sort_index()
    df['20sma'] = df['close'].rolling(ma_window).mean()
    df['std'] = df['close'].rolling(ma_window).std()

    df["lowerbollinger"] = df["20sma"] - (bolling_coeff * df["std"])
    df["upperbollinger"] = df["20sma"] + (bolling_coeff * df["std"])

    df['TR'] = df['high'] - df['low']
    df['ATR'] = df['TR'].rolling(window=20).mean()
    df["lowerkeltner"] = df["20sma"] - (keltner_coeff * df["ATR"])
    df["upperkeltner"] = df["20sma"] + (keltner_coeff * df["ATR"])

    def in_sqeeze(df):
        return df['lowerbollinger'] > df['lowerkeltner'] and df['upperbollinger'] < df['upperkeltner']

    # print("\n\n\n\n\n\n\n\n\n dljfldkajf;afdkl;aj;ldsfjl;ajsdfljlksaf\n\n")
    # print(np.where((df['lowerbollinger'] > df['lowerkeltner'])
    #                & (df['upperbollinger'] < df['upperkeltner'])))
    df["sqeeze_on"] = (df['lowerbollinger'] > df['lowerkeltner']) & (df['upperbollinger'] < df['upperkeltner'])

    try:
        # print(df.iloc[-3]["sqeeze_on"],  not df.iloc[-3]["sqeeze_on"])
    # df['sqeeze_on'] = df.apply(in_sqeeze, axis=1)
        potential_high_move = df.iloc[-3]["sqeeze_on"] &  df.iloc[-3]["sqeeze_on"]
    except:
        print("be ga")
        potential_high_move = None
    return df, potential_high_move


def get_stock_data_from_db(end, symbs, weeks_back=20, as_dict=True):
    
    start = pd.to_datetime(end) - pd.Timedelta(weeks=weeks_back)
    curs = get_pg_cursur()
    query2 = ""
    if isinstance(symbs, str):
        query2 = f""" SELECT * from saffron."daily_price" where ticker='{symbs}' and date between '{start}' AND '{end}' """
    elif isinstance(symbs, list):
        if len(symbs) == 1:
            query2 = f""" SELECT * from saffron."daily_price" where ticker='{symbs[0]}' and date between '{start}' AND '{end}' """
        else:
            symbols = tuple(symbs)
            query2 = f""" SELECT * from saffron."daily_price" where ticker in {symbols} and date between '{start}' AND '{end}' """
    else:
        print("The symbols should be either a list or a string")
        return
    df = pd.read_sql_query(query2, con=curs.connection)
    print(symbs, df.shape)
    df_dict = {}
    df.set_index(["date", "ticker"], inplace=True)

    # df = df.unstack()
    return df


def fetch_stock_data_form_yfinance(id: int):
    SQLALCHEMY_DATABASE_URL = f"postgresql://{params['user']}:{params['password']}@{params['host']}/{params['database']}"
    from sqlalchemy import create_engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    _stock = db.query(Stocks).filter(Stocks.id == id).first()
    yahoo_daata = yfinance.Ticker(_stock.symbol)
    _stock.price = yahoo_daata.info['previousClose']
    _stock.forward_pe = yahoo_daata.info['forwardPE']
    _stock.forward_eps = yahoo_daata.info['forwardEps']
    if yahoo_daata.info['dividendYield'] is not None:
        _stock.dividend_yield = yahoo_daata.info['dividendYield'] * 100
    _stock.ma50 = yahoo_daata.info['fiftyDayAverage']
    _stock.ma200 = yahoo_daata.info['twoHundredDayAverage']
    print(_stock)
    db.add(_stock)
    db.commit()
