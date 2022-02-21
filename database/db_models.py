import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper
from database.db_session import Base
from sqlalchemy.orm import relationship

# from frontend.database_sessions import Base

metadata = db.MetaData()

# stocks = db.Table("stocks", metadata,
#                   db.Column("id", db.Integer, primary_key=True, index=True),
#                   db.Column("symbol", db.String, unique=True, index=True),
#                   db.Column("price", db.Numeric(10, 4)),
#                   db.Column("forward_pe", db.Numeric(10, 4)),
#                   db.Column("forward_eps", db.Numeric(10,FvFF 4)),
#                   db.Column("dividend_yield", db.Numeric(10, 4)),
#                   db.Column("ma50", db.Numeric(10, 4)),
#                   db.Column("ma200", db.Numeric(10, 4)),
#                   schema="saffron")


class Stock(Base):
    __tablename__ = "stocks"
    schema = "saffron"
    id = db.Column(db.Integer, primary_key=True, index=True)
    symbol = db.Column(db.String, unique=True, index=True)
    price = db.Column(db.Numeric(10, 2))
    forward_pe = db.Column(db.Numeric(10, 2))
    forward_eps = db.Column(db.Numeric(10, 2))
    dividend_yield = db.Column(db.Numeric(10, 2))
    ma50 = db.Column(db.Numeric(10, 2))
    ma200 = db.Column(db.Numeric(10, 2))


# mapper(Stocks, stocks)


class Stocks(Base):
    __tablename__ = "saffron.stocks"
    id = db.Column(db.Integer, primary_key=True, index=True)
    symbol = db.Column(db.String, unique=True, index=True)
    price = db.Column(db.Numeric(10, 4))
    forward_pe = db.Column(db.Numeric(10, 4))
    forward_eps = db.Column(db.Numeric(10, 4))
    dividend_yield = db.Column(db.Numeric(10, 4))
    ma50 = db.Column(db.Numeric(10, 4))
    ma200 = db.Column(db.Numeric(10, 4))


class daily_price(Base):
    __tablename__ = "daily_price"
    id = db.Column(db.Integer, primary_key=True, index=True)
    Date = db.Column(db.Date)
    symbol = db.Column(db.String, unique=True, index=True)
    Open = db.Column(db.Numeric(10, 4))
    High = db.Column(db.Numeric(10, 4))
    Low = db.Column(db.Numeric(10, 4))
    Close = db.Column(db.Numeric(10, 4))
    Adj_Close = db.Column(db.Numeric(10, 4))
    Volume = db.Column(db.Numeric(10, 4))


class security(Base):
    __tablename__ = "security"
    id = db.Column(db.Integer, primary_key=True, index=True)
    symbol = db.Column(db.String, unique=True, index=True)
    name = db.Column(db.String)
    sp500 = db.Column(db.BOOLEAN)
