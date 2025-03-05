import json
import uvicorn

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
from sqlalchemy import create_engine
from .dashfigs import *
from .patterns import patterns

import logging
from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)

# Set logging level and formatter with colors
colored_formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
    datefmt=None
)
handler = logging.StreamHandler()
handler.setFormatter(colored_formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.debug("This is a debug message (blue)")
logger.info("This is an info message (green)")
logger.warning("This is a warning message (yellow)")
logger.error("This is an error message (red)")

def colorful_print(text, color):
  """
  Prints text to the console in a specified color.

  Args:
      text: The text to be printed.
      color: The color code for the text (e.g., "red", "green", "blue").
  """
  # Escape codes for common colors
  color_codes = {
      "red": "\033[31m",
      "green": "\033[32m",
      "blue": "\033[34m",
      "yellow": "\033[33m",
      "magenta": "\033[35m",
      "cyan": "\033[36m",
      "white": "\033[37m",
  }
  reset_code = "\033[0m"  # Reset color to default

  # Check if the provided color is valid
  if color.lower() not in color_codes:
    print(f"Invalid color: {color}. Using default color (white).")
    color = "white"

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
    # cursor.execute("""
    #   SELECT table_name
    #   FROM information_schema.tables
    #   WHERE table_schema = 'saffron';  -- Modify for your schema name if needed
    # """)
    # logger.error(cursor.fetchall())
    # logger.warning(f"read config {engineurl} (red)")
    # cursor.execute("SELECT distinct symbol FROM saffron.magnificent7")
    symbols = ["spy", "nvda"]
    symbols = [symbol[0] for symbol in symbols]

    print('\033[92m')
    print(   '\033[93m')
    
    last=datetime.now().strftime("%Y-%m-%d")
    is_potential = ["Ha", "na"]
    # for symb in symbols[20:30]:
    #     df =dbh.get_stock_data_from_db(last, symbs=symb)
    #     _, _is_potential = dbh.add_bands(df)
    #     if _is_potential:
    #         is_potential.append(symb)
    # df = dbh.get_stock_data_from_db("2024-02-01", "spy")
    engine = create_engine(f"postgresql+psycopg2://admin:lohraspco@localhost:5432/postgres")
    df = pd.read_sql_query("SELECT * FROM stocks", engine)
    print(df)
    df.reset_index(inplace=True)
    df["date"] = df["date"].astype(str)
    print('\033[0m')

    return templates.TemplateResponse("home.html", {"request": request,
                                                    "patterns": patterns,
                                                    "symbols":symbols,
                                                    "is_potential": is_potential,
                                                    "stockdata": df.drop(['data_vendor_id','ticker_id'],axis=1,errors='ignore').tail()})

if __name__ == "__main__":
    uvicorn.run("frontend.app:app", host="0.0.0.0", port=8000, reload=True)