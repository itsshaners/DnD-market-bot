import os
import sqlite3
import re
from datetime import datetime
import cv2
import pytesseract
import re
from PIL import Image
import numpy as np

# Set the path to the Tesseract executable if needed
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Adjust if necessary

# Create the path for the database file
db_path = os.path.join(os.path.dirname(__file__), 'master-market-database.db')

def create_connection():
    """Create a database connection."""
    conn = sqlite3.connect(db_path)
    return conn

def create_master_table(conn):
    """Create the master table to track all item-specific tables."""
    cursor = conn.cursor()
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

def insert_item_into_master(conn, item_name, rarity, gold_cost):
    """Insert an item into the master table."""
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO master_item_history (item_name, rarity, gold_cost, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (item_name, rarity, gold_cost, timestamp))
    conn.commit()

def save_parsed_items_to_db(conn, items):
    for item in items:
        item_name = item['Item Name']
        rarity = item['Rarity']
        gold_cost = item['Gold Cost']

        insert_item_into_master(conn, item_name, rarity, gold_cost)

def extract_data_old(image_path, target):
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

    # Enlarge the image to help improve OCR accuracy
    scale_percent = 150  # Scale up by 150%
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)

    # Apply mild brightness and contrast adjustments
    alpha = 1  # Slight contrast increase
    beta = 0    # Mild brightness increase
    img_adjusted = cv2.convertScaleAbs(resized_img, alpha=alpha, beta=beta)

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
    text = pytesseract.image_to_string(yellow_extracted, config='--psm 6 -c tessedit_char_whitelist=0123456789')
    return text




def extract_cost_data(image_path):
    # Open the PNG image
    png_image = Image.open(image_path)

    # Create a list to store crop box coordinates
    crop_boxes = [
        (1220, 275, 1300, 323),
        (1220, 330, 1300, 375),
        (1220, 383, 1300, 430),
        (1220, 435, 1300, 485),
        (1220, 490, 1300, 540),
        (1220, 545, 1300, 600),
        (1220, 600, 1300, 650),
        (1220, 650, 1300, 700),
        (1220, 705, 1300, 755),
        (1220, 755, 1300, 810)
    ]

    # Initialize a list to store all the extracted costs
    cost_list = []

    # Loop through each crop box and extract text
    for i, crop_box in enumerate(crop_boxes):
        # Crop the image for the current cost position
        cropped_image = png_image.crop(crop_box)

        # Convert cropped image to RGB for Tesseract
        rgb_image = cropped_image.convert('RGB')

        # Save the cropped image for debugging
        cropped_image_path = f'market-images/image-processing/cropped_cost_{i + 1}.jpg'
        rgb_image.save(cropped_image_path, quality=100)

        # Load the cropped image using OpenCV for processing
        img = cv2.imread(cropped_image_path)

        if img is None:
            print(f"Error: Unable to load cropped image at {cropped_image_path}. Please check the path.")
            continue

        # Apply mild brightness and contrast adjustments
        alpha = 1  # Slight contrast increase
        beta = 0  # Mild brightness increase
        img_adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # Convert to HSV color space
        hsv_image = cv2.cvtColor(img_adjusted, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds for yellow color
        lower_yellow = np.array([24, 5, 95])  # Adjusted for better saturation
        upper_yellow = np.array([30, 255, 255])  # Keep the upper bound the same

        # Create a mask for yellow
        yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

        # Apply the mask to get the yellow parts
        yellow_extracted = cv2.bitwise_and(img_adjusted, img_adjusted, mask=yellow_mask)

        # Save the extracted yellow parts to check the output
        yellow_extracted_path = f'market-images/image-processing/yellow_extracted_{i + 1}.jpg'
        cv2.imwrite(yellow_extracted_path, yellow_extracted)

        # Use Tesseract to extract text
        text = pytesseract.image_to_string(yellow_extracted, config='--psm 6 -c tessedit_char_whitelist=0123456789')
        
        # Clean up the text and add to the list if it's not empty
        cost = text.strip()
        if cost:
            cost_list.append(cost)
        else:
            cost_list.append('error')  # Append 'error' if no cost was extracted

    print("Here is the cost list returned from extract_cost_data")
    print(cost_list)    

    return cost_list


def extraction_test():
    image_path = f'/Users/iainshand/Documents/Projects/DnD-marketbot/market-images/Screenshot_5.png'
    text = extract_cost_data(image_path)
    return text

if __name__ == "__main__":
    print(extraction_test())

        
