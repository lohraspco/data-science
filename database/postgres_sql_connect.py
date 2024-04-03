import psycopg2
from configparser import  ConfigParser
# conn = psycopg2.connect("dbname=suppliers user=postgres password=postgres")
import os
from sqlalchemy import create_engine

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

def config(filename='/frontend/database.ini', section='postgresql'):
    current_path = os.getcwd()
    parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if os.path.isfile(".." + filename):
        filename = ".." + filename
    elif  os.path.isfile(filename):
        pass
    else:
        filename = current_path +"/"+ filename
    colorful_print(filename, "red")

    print(filename, os.path.isfile(filename))

    # create a parser
    assert os.path.isfile(filename)
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


params = config()
def get_engine():
    SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:reallyStrongPwd123@{params['host']}:{params['port']}/postgres"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    print("here is the engine")
    return engine

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
        print(params)
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')






