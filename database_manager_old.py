
import os
import sqlite3

# Create the database directory if it doesn't exist
db_directory = os.path.join(os.path.dirname(__file__), 'database')  # Adjust this path as necessary
os.makedirs(db_directory, exist_ok=True)

# Create the path for the database file
db_path = os.path.join(db_directory, 'master-market-database.db')

def create_connection():
    conn = sqlite3.connect(db_path)
    return conn


def create_master_table(conn):
    """ Create the master table if it doesn't exist. """
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_db (
            id INTEGER PRIMARY KEY,
            item_name TEXT,
            rarity TEXT,
            gold_cost INTEGER
        )
    ''')
    conn.commit()

    

def create_item_table(conn):
    """ Create the items table in the database if it doesn't exist. """
    try:
        sql_create_items_table = """ 
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            gold_cost INTEGER NOT NULL
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_items_table)
    except Exception as e:
        print(f"An error occurred while creating the items table: {e}")

def insert_item(conn, item_name, rarity, gold_cost):
    """ Insert a new item into the items table. """
    sql = ''' INSERT INTO items(item_name, rarity, gold_cost)
              VALUES(?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (item_name, rarity, gold_cost))
        conn.commit()  # Commit the transaction
    except Exception as e:
        print(f"An error occurred while inserting the item: {e}")

def fetch_all_items(conn):
    """ Fetch all items from the items table. """
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    return rows

def check_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    return tables

# Save extracted items to master database
def save_to_master_db(items, conn):
    """ Save parsed items to the master database. """
    cursor = conn.cursor()
    for item in items:
        # Assuming item is a tuple (name, rarity, gold_cost)
        cursor.execute("INSERT INTO master_db (item_name, rarity, gold_cost) VALUES (?, ?, ?)", item)
    conn.commit()  # Commit changes to the database

# Save each unique item to a corresponding database
def save_to_item_db(item, conn):
    print("Do we even make it here !!!!!!!!!!!!!!!!!!!!!")
    # Create a directory for unique item databases if it doesn't exist
    item_db_directory = db_directory  # Use the same directory as the master database
    os.makedirs(item_db_directory, exist_ok=True)

    # Prepare the database filename based on the item name
    item_name = item['Item Name'].replace(" ", "_").replace("/", "_")  # Replace problematic characters
    item_db_path = os.path.join(item_db_directory, f"{item_name}.db")
    
    # Create or connect to the unique item database
    item_conn = sqlite3.connect(item_db_path)
    item_cursor = item_conn.cursor()

    # Create a table for the item if it doesn't exist
    item_cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_details (
            rarity TEXT,
            gold_cost INTEGER
        )
    ''')

    # Insert item details into the unique item database
    item_cursor.execute("INSERT INTO item_details (rarity, gold_cost) VALUES (?, ?)", 
                        (item['Rarity'], item['Gold Cost']))
    
    item_conn.commit()  # Commit the transaction
    item_conn.close()   # Close the connection for this item database

# Save items to database and master database
def save_to_db(items, text, conn):
    for item in items:
        # Insert into the main items database
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (item_name, rarity, gold_cost) VALUES (?, ?, ?)",
                       (item['Item Name'], item['Rarity'], item['Gold Cost']))
        
        # Save the entire extracted text to the master database
        save_to_master_db(items, conn)
        
        # Save to individual item database
        save_to_item_db(item, conn)

    conn.commit()  # Commit the transaction

# Main function to demonstrate usage
def main():
    # Create database connection
    conn = create_connection()
    create_master_table(conn)  # Create master table
    create_item_table(conn)  # Create items table

    # Example list of items (replace with your actual extracted items)
    items = [
        {'Item Name': 'Phoenix Choker', 'Rarity': 'Uncommon', 'Gold Cost': '35'},
        {'Item Name': 'Copper Ore', 'Rarity': 'Uncommon', 'Gold Cost': '385'},
        {'Item Name': 'Surgicalkit', 'Rarity': 'Uncommon', 'Gold Cost': '4'},
        {'Item Name': 'Tongbow', 'Rarity': 'Epic', 'Gold Cost': '154'},
        {'Item Name': 'GoldenTeeth', 'Rarity': 'Rare', 'Gold Cost': '30'},
        {'Item Name': 'GoCoinPurse', 'Rarity': 'Unique', 'Gold Cost': '39'},
        {'Item Name': 'Potion of Protection', 'Rarity': 'Rare', 'Gold Cost': '225'},
        {'Item Name': 'Ringof Resolve', 'Rarity': 'Epic', 'Gold Cost': '348'},
    ]
    
    # Save items to the database and corresponding files
    #save_items_to_db(items, conn)
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()

