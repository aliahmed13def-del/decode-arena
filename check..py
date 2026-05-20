import sqlite3
conn = sqlite3.connect('hunt.db')
c = conn.cursor()
c.execute('SELECT team_name, trail, password FROM teams ORDER BY trail, team_name')
for row in c.fetchall():
    print(row[0], '|', row[1])
conn.close()