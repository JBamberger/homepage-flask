import sqlite3

__connection = None


def open():
    global __connection
    __connection = sqlite3.connect("/tmp/fcm.sqlite")
    cursor = __connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS devices (fcm_id TEXT NOT NULL PRIMARY KEY)''')
    __connection.commit()


def insert_fcm_id(id):
    global __connection
    c = __connection.cursor()
    c.execute('''INSERT OR ABORT INTO devices VALUES (?)''', [id])
    __connection.commit()


def update_fcm_id(old_id, new_id):
    global __connection
    c = __connection.cursor()
    c.execute('''UPDATE devices SET fcm_id=? WHERE fcm_id LIKE ? ''', [new_id, old_id])
    __connection.commit()


def get_all_ids():
    global __connection
    c = __connection.cursor()
    c.execute('''SELECT * FROM devices''')
    return c.fetchall()



def close():
    global __connection
    __connection.close()