import datetime
import sqlite3

import googleapiclient.discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

from functions.DB.cart import data_invoice_creating as data_parse
from disp import sheet_id, cred_file

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    cred_file,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)


def add_info_to_google_sheet(message):
    db = sqlite3.connect('DB/paid_data.db')
    sql = db.cursor()

    user_id = message.chat.id

    for i in data_parse(user_id):
        title = list(i)[2]
        size = list(i)[3]
        syrup = list(i)[4]
        now = datetime.datetime.now()
        time = now.strftime("%H:%M")
        order_number = sql.execute(
            f"SELECT № FROM paid_data WHERE ID = (?) AND Название = (?) AND Время = (?) AND Размер = (?)",
            (user_id, title, time, size)).fetchall()[0][0]

        body = {
            'values': [
                [order_number, user_id, title, size, syrup, time, 0]
            ]
        }

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            valueInputOption="USER_ENTERED",
            range="A1:E1",
            body=body
        ).execute()

        get_data_from_sheet()


def get_data_from_sheet():
    value = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Лист1',
        majorDimension='ROWS'
    ).execute()
    return value["values"][1::]
