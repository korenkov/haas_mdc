import sqlite3

conn = sqlite3.connect('data.db')

c = conn.cursor()

c.execute("""
create table params_data (
    param_code integer,
    param_val  real, 
    log_date   real,
    machine_id text
)
""")
