import os
import pyodbc, psycopg2
from datetime import timedelta
from decouple import config
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class Config:
    SECRET_KEY = config('SECRET_KEY')
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=480)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=480)
    SQLALCHEMY_TRACK_MODIFICATIONS = config('SQLALCHEMY_TRACK_MODIFICATIONS', cast=bool)

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, 'database.db')
    DEBUG = True
    SQLALCHEMY_ECHO = True

class SQLConfig(Config):
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};' \
                       'SERVER=;' \
                       'DATABASE=;' \
                       'charset=utf8;collation=Arabic_CI_AS;' \
                       'UID=;' \
                       'PWD=' 
                       

    @staticmethod
    def test_connection():
        try:
            conn = pyodbc.connect(SQLConfig.conn_str)
            conn.close()
            return "Successfully connected to SQL Server."
        except Exception as e:
            return "Failed to connect to SQL Server."

    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(conn_str))
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc:///?odbc_connect={}'.format(conn_str)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    DEBUG = True
    SQLALCHEMY_ECHO = True



class PostgreConfig(Config):

    # Example with a specific host and port:
    conn_str = 'postgresql://interface:interface@100:5432/interface'


    @staticmethod
    def test_connection():
        try:
            conn = psycopg2.connect(PostgreConfig.conn_str)
            conn.close()
            return "Successfully connected to PostgreSQL."
        except Exception as e:
            return "Failed to connect to PostgreSQL."

    # Use the connection string in SQLAlchemy configurations
    SQLALCHEMY_DATABASE_URI = conn_str
    engine = create_engine(conn_str)

    DEBUG = True
    SQLALCHEMY_ECHO = True



class ProdConfig(Config):
    pass

class TestConfig(Config):
    pass
