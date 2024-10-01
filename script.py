import os
import cv2
import pytesseract
import re
import database_manager
from PIL import Image
import numpy as np

# Set the path to the Tesseract executable if needed
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Adjust if necessary

def extract_text_from_image(image_path, rarity):
    names = []
    prices = []

    item_name_txt = extract_data(image_path, rarity, 'name')
    gold_price_txt = extract_data(image_path, rarity, 'cost')

    item_names = item_name_txt.splitlines()
    gold_prices = gold_price_txt.splitlines()

    for item in item_names:
        if item != '':
            names.append(item)

    for price in gold_prices:
        if price != '':
            new_price = re.sub(r'[^0-9,]', '', price)
            prices.append(new_price)

    # Create a list of dictionaries to hold the item data
    items = []
    for item, price in zip(names, prices):
        gold_cost = int(price.replace(",", "")) if price else None  # Handle empty price gracefully
        items.append({
            'Item Name': item.strip(),
            'Rarity': rarity,
            'Gold Cost': gold_cost
        })


    # Remove special characters from item names
    for item in items:
        item['Item Name'] = re.sub(r'[^a-zA-Z0-9\s]', '', item['Item Name'])

    # Print the items
    for item in items:
        print(f"Item: {item['Item Name']}, Price: {item['Gold Cost']}")

    return items



def extract_data(image_path, rarity, target):
    # Open the PNG image
    png_image = Image.open(image_path)

    if target == 'name':
        crop_box = (100, 275, 265, 830)  # Crop for item name
    elif target == 'cost':
        crop_box = (1220, 275, 1300, 810)  # Crop for gold cost

    cropped_image = png_image.crop(crop_box)
    rgb_image = cropped_image.convert('RGB')

    # Save the cropped image for debugging
    rgb_image.save('market-images/image-processing/cropped_image.jpg', quality=100)

    # Load the image using OpenCV
    img = cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)

    if img is None:
        print(f"Error: Unable to load image at {image_path}. Please check the path.")
        return ""

    # Apply mild brightness and contrast adjustments
    alpha = 1.2  # Slight contrast increase
    beta = 10    # Mild brightness increase
    img_adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    # Convert to HSV color space
    hsv_image = cv2.cvtColor(img_adjusted, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for yellow color
    lower_yellow = np.array([25, 50, 50])  # Adjusted for better saturation
    upper_yellow = np.array([30, 255, 255])  # Keep the upper bound the same

    # Create a mask for yellow
    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    # Apply the mask to get the yellow parts
    yellow_extracted = cv2.bitwise_and(img_adjusted, img_adjusted, mask=yellow_mask)

    # Save the extracted yellow parts to check the output
    cv2.imwrite('market-images/image-processing/yellow_extracted.jpg', yellow_extracted)

    # Use Tesseract to extract text
    text = pytesseract.image_to_string(yellow_extracted, config='--psm 6')
    return text






def save_parsed_items_to_db(conn, items):
    database_manager.save_to_db(items, conn)

def process_range():
    conn = database_manager.create_connection()
    database_manager.create_master_table(conn)

    # Loop through each screenshot from Screenshot_1.png to Screenshot_32.png
    for i in range(1, 20):  # Range is inclusive of 1 and exclusive of 33
        image_path = f'/Users/iainshand/Documents/Projects/DnD-marketbot/market-images/Screenshot_{i}.png'
        
        # Check if the image file exists before processing
        if os.path.exists(image_path):
            extracted_data = extract_text_from_image(image_path, 'rare')
            save_parsed_items_to_db(conn, extracted_data)

            print(f"\nProcessed: Screenshot_{i}.png")
        else:
            print(f"Warning: {image_path} does not exist.")

    print("\nCurrent Database:")
    items = database_manager.fetch_all_items(conn)
    for item in items:
        print(f"ID: {item[0]}, Item Name: {item[1]}, Rarity: {item[2]}, Gold Cost: {item[3]}")

    conn.close()


def process_item(item_name, rarity, image_path):
    items = []
    conn = database_manager.create_connection()
    database_manager.create_master_table(conn)
    
    # Extract the gold cost text from the image
    gold_cost_txt = extract_data(image_path, rarity, 'cost')

    # Split by lines and process each line
    for line in gold_cost_txt.splitlines():
        # Remove any non-numeric characters and whitespace
        cleaned_price = re.sub(r'[^0-9]', '', line).strip()
        
        if cleaned_price:  # If there is a valid cleaned price
            gold_cost = int(cleaned_price)  # Convert to integer
            items.append({'Item Name': item_name, 'Rarity': rarity, 'Gold Cost': gold_cost})

    # Save items to the database
    save_parsed_items_to_db(conn, items)

    # Debugging output for the extracted gold cost
    for item in items:
        print(f"Processed Item: {item['Item Name']}, Rarity: {item['Rarity']}, Gold Cost: {item['Gold Cost']}")

    print("\nCurrent Database:")
    all_items = database_manager.fetch_all_items(conn)
    for item in all_items:
        print(f"ID: {item[0]}, Item Name: {item[1]}, Rarity: {item[2]}, Gold Cost: {item[3]}")

    conn.close()


    

if __name__ == "__main__":
    
    for i in range(1, 17):  # Range is inclusive of 1 and exclusive of 17
        image_path = f'/Users/iainshand/Documents/Projects/DnD-marketbot/market-images/Screenshot_{i}.png'
    
        if i <= 4:
            process_item('adventurer tunic', 'rare', image_path)
        elif i <= 8:
            process_item('lightfoot boots', 'rare', image_path)
        elif i <= 12:
            process_item('mystic vestments', 'rare', image_path)
        elif i <= 16:
            process_item('loose trousers', 'rare', image_path)
        
