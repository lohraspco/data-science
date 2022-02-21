import psycopg2
from configparser import  ConfigParser
# conn = psycopg2.connect("dbname=suppliers user=postgres password=postgres")
import os
from sqlalchemy import create_engine

def config(filename='/frontend/database.ini', section='postgresql'):
    parent_path = os.getcwd()
    if filename.startswith("/"):
        filename = parent_path + filename
    else:
        filename = parent_path +"/"+ filename


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

def get_engine():
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:reallyStrongPwd123@192.168.0.108/postgres"
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






