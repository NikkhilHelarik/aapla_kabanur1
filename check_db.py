"""Run: python check_db.py - checks the SQLite database file and lists table row counts."""
import sqlite3, config
c = sqlite3.connect(config.DB_PATH)
print("DB file:", config.DB_PATH)
for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
    print(f"  {t}: {c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows")
