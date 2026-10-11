# Path: import_db.py
import mysql.connector

try:
    from local_config import DB_PASSWORD
except ImportError:
    DB_PASSWORD = ""

# Aiven connection configuration
config = {
    'host': 'mantalaan-db-mantalaan-project.f.aivencloud.com',
    'port': 20885,
    'user': 'avnadmin',
    'password': DB_PASSWORD,
    'database': 'defaultdb',  # Connect to defaultdb first to create mantalaan_db
    'ssl_ca': 'ca.pem'
}

print("Connecting to Aiven database...")
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

print("Creating and selecting 'mantalaan_db'...")
cursor.execute("CREATE DATABASE IF NOT EXISTS mantalaan_db;")
cursor.execute("USE mantalaan_db;")

print("Disabling sql_require_primary_key for session...")
cursor.execute("SET SESSION sql_require_primary_key = 0;")

print("Reading SQL backup file ('mantalaan_db.sql')...")
with open('mantalaan_db.sql', 'r', encoding='utf-8', errors='ignore') as f:
    sql_content = f.read()
    
print("Executing SQL statements...")
statements = sql_content.split(';')
for statement in statements:
    if statement.strip():
        try:
            cursor.execute(statement)
        except Exception as e:
            print(f"Skipped/Error on statement: {e}")
            
conn.commit()
cursor.close()
conn.close()
print("Database import completed successfully!")