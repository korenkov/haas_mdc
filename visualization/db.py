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
            id         integer primary key autoincrement,
            machine_id text,
            title      text,
            type       integer
        )
        """)
        conn.commit()
    except sqlite3.OperationalError as e:
        print(e)


if __name__ == '__main__':
    create_schema(CHARTS_DB)
