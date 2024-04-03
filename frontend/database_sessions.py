from pathlib import Path
from sqlalchemy import create_engine, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database.postgres_sql_connect import config
import logging

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG
logging.debug("This is a debug message!")
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

  # Print the colored text
  print(f"{color_codes[color.lower()]}{text}{reset_code}")


params = config(filename="frontend/database.ini")

logging.debug(f"port is {params['port']}")
SQLALCHEMY_DATABASE_URL = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
logging.debug(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# from database import  db_models
Base.metadata.create_all(bind=engine)