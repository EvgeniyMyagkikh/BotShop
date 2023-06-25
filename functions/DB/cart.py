import sqlite3


def current_cart_id():
    db = sqlite3.connect('DB/cart_data.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS cart_data(
       № INT,
       ID TEXT,
       Название TEXT,
       Размер TEXT,
       Сироп TEXT,
       Цена INT
       )""")

    rows_average = list(sql.execute("SELECT COUNT (№) FROM cart_data").fetchall()[0])[0]
    return rows_average


def get_last_id(name):
    db = sqlite3.connect('DB/(?).db', name)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS cart_data(
           № INT,
           ID TEXT,
           Название TEXT,
           Размер TEXT,
           Сироп TEXT,
           Цена INT
           )""")

    rows_average = list(sql.execute("SELECT COUNT (№) FROM (?))", name).fetchall()[0])[0]
    return rows_average


def add_info_to_cart(user_id, order_num, title, size, syrup, price):
    db = sqlite3.connect('DB/cart_data.db')
    sql = db.cursor()

    sql.execute("INSERT INTO cart_data VALUES (?,?,?,?,?,?)", (order_num, user_id, title, size, syrup, price))
    db.commit()


def data_invoice_creating(user_id):
    db = sqlite3.connect('DB/cart_data.db')
    sql = db.cursor()

    data = sql.execute("SELECT *  FROM cart_data where ID = (?)", [user_id]).fetchall()
    db.commit()
    return data


def total_sum_counter(invoice_data):
    total = 0
    for i in invoice_data:
        total += i[5]
    return total


def clear_user_cart_data(user_id):
    db = sqlite3.connect('DB/cart_data.db')
    sql = db.cursor()

    try:
        sql.execute("DELETE FROM cart_data WHERE ID = (?)", [user_id])
        db.commit()
    except Exception:
        pass

    sql.close()
    db.close()
