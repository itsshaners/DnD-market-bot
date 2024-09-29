# database_manager.py
import os
import sqlite3
import re


# Create the database directory if it doesn't exist
db_directory = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_directory, exist_ok=True)

# Create the path for the database file
db_path = os.path.join(db_directory, 'master-market-database.db')

def create_connection():
    """Create a database connection."""
    conn = sqlite3.connect(db_path)
    return conn

def create_master_table(conn):
    """Create the master table to track all item-specific tables."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            rarity TEXT,
            gold_cost INTEGER,
            total_entries INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

def create_item_table(conn, item_name):
    """Create a unique table for the specific item."""
    cursor = conn.cursor()
    
    # Sanitize the item name to create a valid table name
    item_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', item_name.replace(" ", "_").lower())
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {item_table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rarity TEXT NOT NULL,
            gold_cost INTEGER NOT NULL
        )
    ''')
    conn.commit()

def insert_item_into_master(conn, item_name, rarity, gold_cost):
    """Insert or update item details in the items_master table."""
    cursor = conn.cursor()
    # If item already exists in items_master, update total_entries and gold_cost, else insert
    cursor.execute('''
        INSERT INTO items_master (item_name, rarity, gold_cost, total_entries)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(item_name) DO UPDATE SET 
            total_entries = total_entries + 1,
            gold_cost = excluded.gold_cost
    ''', (item_name, rarity, gold_cost))
    conn.commit()

def insert_into_item_table(conn, item_name, rarity, gold_cost):
    """Insert an entry into the item's specific table."""
    item_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', item_name.replace(" ", "_").lower())
    cursor = conn.cursor()
    
    # Skip insertion if gold_cost is None
    if gold_cost is not None:
        cursor.execute(f'''
            INSERT INTO {item_table_name} (rarity, gold_cost)
            VALUES (?, ?)
        ''', (rarity, gold_cost))
    else:
        print(f"Skipping insert for {item_name} due to None gold cost.")
    
    conn.commit()

def fetch_all_items(conn):
    """Fetch all items from the master table."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items_master")
    return cursor.fetchall()

# Save parsed items to both items_master and their respective item-specific tables
def save_to_db(items, conn):
    for item in items:
        item_name = item['Item Name']
        rarity = item['Rarity']
        gold_cost = item['Gold Cost']

        # Insert into the items_master
        insert_item_into_master(conn, item_name, rarity, gold_cost)

        # Create the item-specific table if it doesn't exist
        create_item_table(conn, item_name)

        # Insert the details into the item-specific table
        insert_into_item_table(conn, item_name, rarity, gold_cost)
