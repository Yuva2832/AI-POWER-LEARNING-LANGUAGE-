import sqlite3
from app import db, app

# Create tables within app context
with app.app_context():
    db.create_all()
    print("Tables created")

# Check what tables exist
conn = sqlite3.connect('language_learning.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables in database:', tables)
conn.close()