#database_manager.py
import os
import sqlite3
import re
from datetime import datetime

# Create the path for the database file
db_path = os.path.join(os.path.dirname(__file__), 'master-market-database.db')


### Creation Functions ###
def create_connection():
    """Create a database connection."""
    conn = sqlite3.connect(db_path, timeout=60)  # Set timeout to 10 seconds
    return conn

def create_master_table(conn):
    """Create the master table to track all item-specific tables."""
    cursor = conn.cursor()

    # Create a new master_item_history table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_item_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            rarity TEXT,
            gold_cost INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def create_item_table(conn, item_name):
    """Create a unique table for the specific item."""
    cursor = conn.cursor()
    
    # Sanitize the item name to create a valid table name and append '_history'
    item_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', item_name.replace(" ", "_").lower()) + '_history'
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {item_table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rarity TEXT NOT NULL,
            gold_cost INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def create_item_data_table():
    """Create the item_data table if it does not exist."""
    conn = sqlite3.connect('master-market-database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            avg_price REAL NOT NULL,
            lowest_price REAL NOT NULL,
            price_gap REAL NOT NULL,
            UNIQUE(item_name, rarity)  -- Ensures unique entries for each item and rarity
        )
    """)
    conn.commit()
    conn.close()



### Insertion Functions ###
def insert_item_into_master(conn, item_name, rarity, gold_cost):
    """Insert an item into the master table."""
    cursor = conn.cursor()
    
    # Get the current timestamp formatted as 'YYYY-MM-DD HH:MM:SS'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert a new entry with a unique ID each time, including the current timestamp
    cursor.execute('''
        INSERT INTO master_item_history (item_name, rarity, gold_cost, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (item_name, rarity, gold_cost, timestamp))

    conn.commit()

def insert_into_item_table(conn, item_name, rarity, gold_cost):
    """Insert an entry into the item's specific table."""
    if gold_cost is None:
        print(f"Warning: Skipping insertion for item '{item_name}' due to missing gold cost.")
        return  # Skip insertion if gold_cost is None

    item_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', item_name.replace(" ", "_").lower()) + '_history'
    cursor = conn.cursor()
    
    # Get the current timestamp formatted as 'YYYY-MM-DD HH:MM:SS'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert a new entry with the current timestamp
    cursor.execute(f'''
        INSERT INTO {item_table_name} (rarity, gold_cost, timestamp)
        VALUES (?, ?, ?)
    ''', (rarity, gold_cost, timestamp))
    
    conn.commit()



### Fetching Functions ###
def fetch_all_items():
    conn = sqlite3.connect('master-market-database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT item_name, rarity FROM master_item_history")
    items = cursor.fetchall()
    conn.close()
    return items

def fetch_prices_for_item(item_name, rarity):
    conn = sqlite3.connect('master-market-database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT gold_cost FROM master_item_history WHERE item_name = ? AND rarity = ? ORDER BY gold_cost ASC", (item_name, rarity))
    prices = cursor.fetchall()
    conn.close()
    return [price[0] for price in prices]




### Saving functions ###
# Save parsed items to both master_item_history and their respective item-specific tables
def save_to_db(items, conn):
    for item in items:
        item_name = item['Item Name']
        rarity = item['Rarity']
        gold_cost = item['Gold Cost']

        # Insert into the master_item_history
        insert_item_into_master(conn, item_name, rarity, gold_cost)

        # Create the item-specific table if it doesn't exist
        create_item_table(conn, item_name)

        # Insert the details into the item-specific table
        insert_into_item_table(conn, item_name, rarity, gold_cost)

# Function to save parsed items to database
def save_parsed_items_to_db(conn, items):
    save_to_db(items, conn)

def save_item_data(item_name, rarity, avg_price, lowest_price, price_gap):
    conn = sqlite3.connect('master-market-database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO item_data (item_name, rarity, avg_price, lowest_price, price_gap)
        VALUES (?, ?, ?, ?, ?)
    """, (item_name, rarity, avg_price, lowest_price, price_gap))
    conn.commit()
    conn.close()
