import sqlite3

con = sqlite3.connect("sqlite3.db")
cur = con.cursor()

cur.execute("CREATE TABLE user(user_id, lang_code)")
