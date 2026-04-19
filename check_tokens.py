import sqlite3
import datetime

DB = r'c:\projects\v_python_project\backend\database.db'
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('SELECT token, email, expires_at FROM password_resets ORDER BY rowid DESC LIMIT 5')
rows = c.fetchall()
conn.close()

now = datetime.datetime.now()
fmt = '%Y-%m-%d %H:%M:%S'
print(f'Current time: {now.strftime(fmt)}')
print('-' * 80)
for r in rows:
    expires = datetime.datetime.strptime(r[2], fmt)
    valid = 'VALID  [OK]' if expires > now else 'EXPIRED [!!]'
    print(f'Status : {valid}')
    print(f'Email  : {r[1]}')
    print(f'Expires: {r[2]}')
    print(f'URL    : http://localhost:3000/reset-password/{r[0]}')
    print('-' * 80)
