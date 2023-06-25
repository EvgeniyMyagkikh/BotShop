import sqlite3


def add_new_user(user_id):
    db = sqlite3.connect('DB/users_data.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS users_data(
        ID INT UNIQUE, 
        Баланс INT
        )""")

    sql.execute("INSERT OR IGNORE INTO users_data VALUES (?,?)", (user_id, 0))
    db.commit()


def insert_bonus(user_id, bonus):
    db = sqlite3.connect('DB/users_data.db')
    sql = db.cursor()

    sql.execute("UPDATE users_data SET Баланс = Баланс + (?) WHERE ID = (?)", (bonus, user_id))
    db.commit()


def bonuses_amount(user_id):
    db = sqlite3.connect('DB/users_data.db')
    sql = db.cursor()

    bonus = sql.execute("SELECT * FROM users_data WHERE ID = (?)", (user_id,)).fetchall()[0][1]
    db.commit()
    return bonus
