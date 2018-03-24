import os
import sqlite3
from threading import local

_active = local()

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
CHARTS_DB = 'charts.db'


def get_cursor(db=CHARTS_DB):
    conn = getattr(_active, '_conn', None)
    curr = getattr(_active, '_curr', None)

    if conn and curr: return conn, curr

    conn = sqlite3.connect(os.path.join(PROJECT_DIR, db))

    setattr(_active, '_conn', conn)
    setattr(_active, '_curr', curr)

    return conn, conn.cursor()


def create_schema(db=CHARTS_DB):
    conn, c = get_cursor(db)
    try:
        c.execute("""
        create table if not exists chart (
            id           integer primary key autoincrement,
            machine_id   varchar(256),
            chart_type   varchar(256),
            chart_params varchar(2000),
            data_provider BLOB
        )
        """)
        conn.commit()
    except sqlite3.OperationalError as e:
        print(e)


def select_param_with_time(from_date, to_date, param_code, machine_id):
    conn, c = get_cursor(db='data.db')
    for row in c.execute("""
    SELECT 
        log_date,
        param_val
    FROM params_data 
    WHERE (log_date BETWEEN ? and ?) and param_code = ? and machine_id = ?
    """, [from_date, to_date, param_code, machine_id]):
        yield row


def select_param_data(from_date, to_date, param_code, machine_id):
    conn, c = get_cursor(db='data.db')
    for row in c.execute("""
        SELECT 
            param_val
        FROM params_data 
        WHERE (log_date BETWEEN ? and ?) and param_code = ? and machine_id = ?
        """, [from_date, to_date, param_code, machine_id]):
        yield row


if __name__ == '__main__':
    create_schema(CHARTS_DB)