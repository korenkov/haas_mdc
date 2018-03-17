import sqlite3

conn = sqlite3.connect('data.db')

c = conn.cursor()

c.execute("""
create table params_data (
    log_date integer, 
    param_code integer,
    param_val real, 
    machine_id text
)
""")
