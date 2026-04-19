import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Show employees
c.execute('SELECT id, email, name, department FROM employees ORDER BY id')
rows = c.fetchall()
print("=== EMPLOYEES ===")
print(f"Total: {len(rows)}")
print(f"{'ID':<5} {'Email':<30} {'Name':<20} {'Department'}")
print("-" * 80)
for r in rows:
    print(f"{r[0]:<5} {r[1]:<30} {r[2]:<20} {r[3]}")

# Show managers
c.execute('SELECT id, email, name, department FROM managers ORDER BY id')
mgrs = c.fetchall()
print(f"\n=== MANAGERS ===")
print(f"Total: {len(mgrs)}")
for r in mgrs:
    print(f"{r[0]:<5} {r[1]:<30} {r[2]:<20} {r[3]}")

# Show record counts
c.execute('SELECT COUNT(*) FROM records')
total = c.fetchone()[0]
c.execute('SELECT DISTINCT employee_id FROM records')
unique = len(c.fetchall())
print(f"\n=== RECORDS ===")
print(f"Total records: {total}")
print(f"Unique employees with records: {unique}")

# Show sample records (last 5)
c.execute('''SELECT employee_name, burnout_score, burnout_level, fatigue, work_hours, submission_date 
             FROM records ORDER BY created_at DESC LIMIT 5''')
samples = c.fetchall()
print(f"\n=== LATEST 5 RECORDS ===")
print(f"{'Name':<20} {'Score':<8} {'Level':<10} {'Fatigue':<10} {'Hours':<8} {'Date'}")
print("-" * 75)
for r in samples:
    print(f"{r[0]:<20} {r[1]:<8} {r[2]:<10} {r[3]:<10} {r[4]:<8} {r[5]}")

conn.close()
