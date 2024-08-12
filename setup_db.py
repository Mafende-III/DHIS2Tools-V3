import sqlite3

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect('usage_stats.db')

# Create a cursor object to interact with the database
c = conn.cursor()

# Create a table to store extraction logs
c.execute('''
    CREATE TABLE IF NOT EXISTS extractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_name TEXT,
        extraction_date TEXT
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")
