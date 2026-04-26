import sqlite3
import bcrypt
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT username, password_hash, role, created_at FROM users WHERE username = ?', ('emp@001',))
row = cur.fetchone()
print('row =', row)
if row:
    print('bcrypt check =', bcrypt.checkpw('221121'.encode('utf-8'), row['password_hash'].encode('utf-8')))
else:
    print('user not found')
conn.close()
