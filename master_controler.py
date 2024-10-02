import data_extraction
import database_manager
import re

def save_parsed_items_to_db(conn, items):
    database_manager.save_to_db(items, conn)

def process_item(item_name, rarity, image_path):
    items = []
    conn = database_manager.create_connection()
    database_manager.create_master_table(conn)
    
    # Extract the list of gold costs from the image
    gold_costs = data_extraction.extract_cost_data(image_path)

    # Iterate through the list of extracted gold costs
    for cost in gold_costs:
        # Remove any non-numeric characters and whitespace
        cleaned_price = re.sub(r'[^0-9]', '', cost).strip()

        if cleaned_price:  # If there is a valid cleaned price
            gold_cost = int(cleaned_price)  # Convert to integer
            items.append({'Item Name': item_name, 'Rarity': rarity, 'Gold Cost': gold_cost})

    # Save items to the database
    save_parsed_items_to_db(conn, items)

    # Debugging output for the extracted gold costs
    for item in items:
        print(f"Processed Item: {item['Item Name']}, Rarity: {item['Rarity']}, Gold Cost: {item['Gold Cost']}")

    print("\nCurrent Database:")
    all_items = database_manager.fetch_all_items(conn)
    for item in all_items:
        print(f"ID: {item[0]}, Item Name: {item[1]}, Rarity: {item[2]}, Gold Cost: {item[3]}")

    conn.close()

def process_image_range(start, stop):
    for i in range(start, stop+1):  # Range is inclusive of 1 and exclusive of 17
        image_path = f'/Users/iainshand/Documents/Projects/DnD-marketbot/market-images/Screenshot_{i}.png'
    
        if i == 1:
            process_item('adventurer tunic', 'rare', image_path)
        elif i == 2:
            process_item('adventurer tunic', 'epic', image_path)
        elif i == 3:
            process_item('adventurer tunic', 'legendary', image_path)
        elif i == 4:
            process_item('adventurer tunic', 'unique', image_path)
        elif i == 5:
            process_item('lightfoot boots', 'rare', image_path)
        elif i == 6:
            process_item('lightfoot boots', 'epic', image_path)
        elif i == 7:
            process_item('lightfoot boots', 'legendary', image_path)
        elif i == 8:
            process_item('lightfoot boots', 'unique', image_path)
        elif i == 9:
            process_item('mystic vestments', 'rare', image_path)
        elif i == 10:
            process_item('mystic vestments', 'epic', image_path)
        elif i == 11:
            process_item('mystic vestments', 'legendary', image_path)
        elif i == 12:
            process_item('mystic vestments', 'unique', image_path)
        elif i == 13:
            process_item('loose trousers', 'rare', image_path)
        elif i == 14:
            process_item('loose trousers', 'epic', image_path)
        elif i == 15:
            process_item('loose trousers', 'legendary', image_path)
        elif i == 16:
            process_item('loose trousers', 'unique', image_path)

if __name__ == "__main__":
    image_path = f'/Users/iainshand/Documents/Projects/DnD-marketbot/market-images/Screenshot_5.png' 
    process_image_range(1, 16)
    #process_item('adventurer tunic', 'rare', image_path)