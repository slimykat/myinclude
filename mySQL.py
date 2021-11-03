#from numpy.core.einsumfunc import einsum
import mysql.connector
from mysql.connector import Error
import datetime
import numpy as np
import logging


def connect(host, database, user, password, port):
    try:
        # 連接 MySQL/MariaDB 資料庫
        connection = mysql.connector.connect(
            host=host,          # 主機名稱
            port = port,
            database=database, # 資料庫名稱
            user=user,        # 帳號
            password=password)  # 密碼
        if connection.is_connected():
            # 顯示資料庫版本
            db_Info = connection.get_server_info()
            logging.debug(f"資料庫版本： {db_Info}")
            # 顯示目前使用的資料庫
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            logging.debug(f"目前使用的資料庫： {record}")
    except Error as e:
        logging.error(f"資料庫連接失敗： {e}")
    return connection

def disconnect(connection):
    if (connection.is_connected()):
        connection.cursor().close()
        connection.close()
        print("資料庫連線已關閉")


if __name__ == "__main__":
    pass




