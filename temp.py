import database_manager

def fix_master_history():
    conn = database_manager.create_connection()
    cursor = conn.cursor()

    try:
        # Fetch all entries sorted by item_name and timestamp
        cursor.execute("SELECT id, item_name, gold_cost FROM master_item_history ORDER BY item_name, timestamp")
        rows = cursor.fetchall()

        if not rows:
            return

        prev_item = None
        prev_cost = None
        current_item_entries = []

        for row in rows:
            current_id, item_name, gold_cost = row

            # Check if we moved to a new item
            if prev_item != item_name:
                # Process the previous item entries
                if current_item_entries:
                    fix_item_entries(cursor, current_item_entries)

                # Reset tracking variables for the new item
                current_item_entries = []

            # Collect entries of the current item
            current_item_entries.append((current_id, gold_cost))

            prev_item = item_name

        # Fix the last batch of entries
        if current_item_entries:
            fix_item_entries(cursor, current_item_entries)

        conn.commit()

    except sqlite3.Error as e:
        print(f"Error while fixing master history: {e}")
    finally:
        conn.close()

def fix_item_entries(cursor, item_entries):
    """Fix item entries by checking for anomalies in prices."""
    for i in range(1, len(item_entries) - 1):
        prev_id, prev_cost = item_entries[i - 1]
        current_id, current_cost = item_entries[i]
        next_id, next_cost = item_entries[i + 1]

        if current_cost is None or not (prev_cost <= current_cost <= next_cost):
            cursor.execute("UPDATE master_item_history SET gold_cost = 0 WHERE id = ?", (current_id,))

def fix_item_history(item_name):
    conn = database_manager.create_connection()
    cursor = conn.cursor()

    try:
        # Fetch all entries for the specific item sorted by timestamp
        cursor.execute(f"SELECT id, gold_cost FROM {item_name}_history ORDER BY timestamp")
        rows = cursor.fetchall()

        if not rows:
            return

        for i in range(1, len(rows) - 1):
            prev_id, prev_cost = rows[i - 1]
            current_id, current_cost = rows[i]
            next_id, next_cost = rows[i + 1]

            if current_cost is None or not (prev_cost <= current_cost <= next_cost):
                cursor.execute(f"UPDATE {item_name}_history SET gold_cost = 0 WHERE id = ?", (current_id,))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Error while fixing item history for {item_name}: {e}")
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    fix_master_history()