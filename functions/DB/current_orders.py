import datetime
import sqlite3

import googleapiclient.discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

from disp import bot
from disp import cred_file
from sheets import get_data_from_sheet

credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_file,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)


def current_id():
    db = sqlite3.connect('DB/current_orders.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS current_orders(
                № INT,
                ID TEXT,
                Название TEXT,
                Размер TEXT,
                Сироп TEXT,
                Время TIME,
                Готовность BOOLEAN
                )""")

    rows_average = list(sql.execute(f"SELECT COUNT (№) FROM current_orders").fetchall()[0])[0]

    return rows_average


def current_order_number(user_id):
    db = sqlite3.connect('DB/current_orders.db')
    sql = db.cursor()

    data = list(
        sql.execute(f"SELECT № FROM current_orders WHERE ID = (?) AND Готовность = 0", [user_id]))
    numbers = [str(i).lstrip("(").rstrip(")").strip(",") for i in data]
    numbers = ", ".join(numbers)

    return numbers


async def add_info_to_current_orders_from_sheet():
    sheet_data = get_data_from_sheet()

    db = sqlite3.connect('DB/current_orders.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS current_orders(
                        № INT,
                        ID TEXT,
                        Название TEXT,
                        Размер TEXT,
                        Сироп TEXT,
                        Время TIME,
                        Готовность BOOLEAN
                        )""")

    sql.execute("""DELETE FROM current_orders""")

    for i in sheet_data:
        order_num = i[0]
        user_id = i[1]
        title = i[2]
        size = i[3]
        syrup = i[4]
        time = i[5]
        is_ready = i[6]
        sql.execute("INSERT INTO current_orders VALUES (?,?,?,?,?,?,?)",
                    (order_num, user_id, title, size, syrup, time, is_ready))
        db.commit()

    data = orders_done_amount()

    now = datetime.datetime.now()
    date = now.strftime('%d/%m/%y')

    for i in data:
        if in_done_db(i) == 0:
            try:
                await bot.send_message(i[1], f"Заказ № {i[0]} готов\n{date}")
                add_info_to_orders_done(i)
            except Exception:
                pass


def orders_done_amount():
    db = sqlite3.connect('DB/current_orders.db')
    sql = db.cursor()
    raw_data = list(
        sql.execute(f"SELECT №, ID FROM current_orders WHERE Готовность = 1"))
    data = [list(i) for i in raw_data]

    return data


def orders_in_work_amount():
    db = sqlite3.connect('DB/current_orders.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS current_orders(
                                № INT,
                                ID TEXT,
                                Название TEXT,
                                Размер TEXT,
                                Сироп TEXT,
                                Время TIME,
                                Готовность BOOLEAN
                                )""")
    amount_in_work = sql.execute(f"SELECT COUNT (*) FROM current_orders WHERE Готовность = 0").fetchall()[0][0]

    return amount_in_work


def add_info_to_orders_done(i):
    db = sqlite3.connect('DB/orders_done.db')
    sql = db.cursor()

    sql.execute("INSERT INTO orders_done VALUES (?,?)", (i[0], i[1]))
    db.commit()


def in_done_db(i):
    db = sqlite3.connect('DB/orders_done.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS orders_done(
                        № INT,
                        ID TEXT
                        )""")
    amount = sql.execute("SELECT COUNT (*) FROM orders_done WHERE № = (?)", (i[0],)).fetchall()[0][0]
    return amount
