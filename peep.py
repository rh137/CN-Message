import sqlite3 as sql
import os

db = 'UserInfo.db'

if not os.path.exists(db):
    print('database doesn\'t exist')
    exit()

conn = sql.connect(db)

c = conn.cursor()

c.execute('SELECT * FROM Users')
#print(c.fetchall())

count = 0
tmp = c.fetchone()
while tmp:
    print(tmp)
    tmp = c.fetchone()
    count = count + 1

if count == 0:
    print('the database is empty')

c.close()
