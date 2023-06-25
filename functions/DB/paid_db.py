import datetime
import sqlite3

from functions.DB.cart import data_invoice_creating as data_parse


def current_order_id():
    db = sqlite3.connect('DB/paid_data.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS paid_data(
               № INT,
               ID TEXT,
               Название TEXT,
               Размер TEXT,
               Сироп TEXT,
               Цена INT,
               Время TIME
               )""")
    rows_average = list(sql.execute(f"SELECT COUNT (№) FROM paid_data").fetchall()[0])[0]
    return rows_average


def add_info_to_paid_data(user_id):
    db = sqlite3.connect('DB/paid_data.db')
    sql = db.cursor()

    now = datetime.datetime.now()

    sql.execute("""CREATE TABLE IF NOT EXISTS paid_data(
           № INT,
           ID TEXT,
           Название TEXT,
           Размер TEXT,
           Сироп TEXT,
           Цена INT,
           Время TIME
           )""")
    sql.execute("""CREATE TABLE IF NOT EXISTS all_data(
               № INT,
               ID TEXT,
               Название TEXT,
               Размер TEXT,
               Сироп TEXT,
               Цена INT,
               Время TIME
               )""")

    for i in data_parse(user_id):
        order_num = current_order_id() + 1
        title = list(i)[2]
        size = list(i)[3]
        syrup = list(i)[4]
        price = list(i)[5]
        time = now.strftime("%H:%M")

        sql.execute(f"INSERT INTO paid_data VALUES (?,?,?,?,?,?,?)",
                    (order_num, user_id, title, size, syrup, price, time))
        sql.execute(f"INSERT INTO all_data VALUES (?,?,?,?,?,?,?)",
                    (order_num, user_id, title, size, syrup, price, time))
        db.commit()


async def clear_all_db():

    db_names = ["paid_data", "current_orders", "cart_data", "orders_done"]

    try:
        for i in db_names:
            db = sqlite3.connect(f'DB/{i}.db')
            sql = db.cursor()

            sql.execute(f"DELETE FROM {i}")
            db.commit()
    except Exception:
        pass
