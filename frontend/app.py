import json
from datetime import datetime
import database.database_helper as dbh
import pandas as pd
from database.postgres_sql_connect import config
# from database.db_session import engine, sessionLocal
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
# from sqlalchemy.orm import Session
from starlette.middleware.wsgi import WSGIMiddleware

from frontend.router import (cherknevis, dash_graph, dashboard,
                             iris_classifier_router)

from .dashfigs import *
from .patterns import patterns

templates = Jinja2Templates(directory="template")

app = FastAPI()
# app.include_router(iris_classifier_router.router, prefix='/frontend')
app.include_router(dashboard.router)
app.include_router(cherknevis.router)
app.mount("/dash", WSGIMiddleware(dash_graph.dashapp.server))
app.mount("/static", StaticFiles(directory="static"), name="static")

class StockRequest(BaseModel):
    symbol: str

def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, symbols:str = "FB"):
    cursor= dbh.get_pg_cursur()
    engineurl = config()
    symbols = pd.read_sql(f"select ticker from saffron.security where sp500=true", con=cursor.connection)
    symbols = list (symbols.ticker.values)

    print('\033[92m')

    print(   '\033[93m')
    

    
    last=datetime.now().strftime("%Y-%m-%d")
    is_potential = ["Ha", "na"]
    for symb in symbols[20:30]:
        df =dbh.get_stock_data_from_db(last, symbs=symb)
        _, _is_potential = dbh.add_bands(df)
        if _is_potential:
            is_potential.append(symb)
    df = dbh.get_stock_data_from_db("2021-12-24", "MMC")
    df.reset_index(inplace=True)
    df["date"] = df["date"].astype(str)
    print('\033[0m')

    return templates.TemplateResponse("home.html", {"request": request,
                                                    "patterns": patterns,
                                                    "symbols":symbols,
                                                    "is_potential": is_potential,
                                                    "stockdata": df.drop(['data_vendor_id','ticker_id'],axis=1).tail()})
