import psycopg

# Connect to default 'postgres' database
conn = psycopg.connect("postgresql://postgres@localhost:5432/postgres")
conn.autocommit = True

cursor = conn.cursor()

# Check if database exists
cursor.execute("SELECT 1 FROM pg_database WHERE datname='school_network'")
exists = cursor.fetchone()

if not exists:
    cursor.execute("CREATE DATABASE school_network")
    print("Database 'school_network' created successfully!")
else:
    print("Database 'school_network' already exists.")

cursor.close()
conn.close()