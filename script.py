import cv2
import pytesseract
import re
import database_manager
from PIL import Image

# Set the path to the Tesseract executable if needed
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Adjust if necessary


def extract_text_from_image(image_path, rarity):
    names =  []
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
            newPrice = re.sub(r'[^0-9,]', '', price)
            prices.append(newPrice)
    
    # Create a list of dictionaries to hold the item data
    items = []
    for item, price in zip(names, prices):
        gold_cost = int(price.replace(",", "")) if price else None  # Handle empty price gracefully
        items.append({
            'Item Name': item.strip(),
            'Rarity': rarity,
            'Gold Cost': gold_cost
        })

    # Print or return the items
    for item in items:
        print(f"Item: {item['Item Name']}, Price: {item['Gold Cost']}")

    return items  

    

            
    

def extract_data(image_path, rarity, target):

    # Open the PNG image
    png_image = Image.open(image_path)

    if target == 'name':
        # Crop the image to the item name dimensions 
        crop_box = (100, 275, 265, 830)  # (left, upper, right, lower)
    elif target == 'cost':
        # Crop the image to the gold cost dimensions 
        crop_box = (1220, 275, 1300, 830)  # (left, upper, right, lower)
    
    cropped_image = png_image.crop(crop_box)

    # Convert the image to RGB (JPEG does not support transparency)
    rgb_image = cropped_image.convert('RGB')

    # Save the image as JPEG with high quality
    rgb_image.save('market-images/image-processing/item-names/Screenshot_12_names.jpg', quality=100)
    
    
    # Load the image
    img = cv2.imread('market-images/image-processing/item-names/Screenshot_12_names.jpg')

    # Check if the image was loaded successfully
    if img is None:
        print(f"Error: Unable to load image at {image_path}. Please check the path.")
        return ""

    if (rarity == 'rare'):
        # Adjust brightness and contrast
        alpha = 2.4  # Contrast control
        beta = -90 # Brightness control
        img_adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    elif (rarity == 'epic'):
        alpha = 2  # Contrast control
        beta = -80 # Brightness control
        img_adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    

    # Save the processed image as a temporary file
    if(target == 'name'):   
        temp_image_path = '/Users/iainshand/Documents/Projects/DnD-marketbot/image-check/test1.jpg'
        cv2.imwrite(temp_image_path, img_adjusted)
    elif(target == 'cost'):
        temp_image_path = '/Users/iainshand/Documents/Projects/DnD-marketbot/image-check/test2.jpg'
        cv2.imwrite(temp_image_path, img_adjusted)

    # Use Tesseract to extract text
    text = pytesseract.image_to_string(img_adjusted, config='--psm 6')
    return text


    







def parse_extracted_text(raw_text):
    items = []
    # Define possible rarities
    rarities = ['Poor', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Unique']

    # Split the raw text into lines
    lines = raw_text.splitlines()

    for line in lines:
        line = line.strip()  # Remove leading or trailing whitespace
        line = re.sub(r'[^a-zA-Z0-9, ]', '', line)  # Remove all special characters except commas
        words = line.split()  # Split the line into words

        item_name = []
        rarity = None
        gold_cost = None
        
        skip_count = 0  # To track how many words to skip after finding rarity
        
        # Loop through words to determine item name and rarity
        for word in words:
            if rarity is None and word in rarities:
                rarity = word  # Set rarity when found
                skip_count = 3  # Start skipping the next three words (for expiration date)
                continue
            
            if skip_count > 0:
                skip_count -= 1
                continue
            
            if re.match(r'^\d+[,]?\d*$', word):
                gold_cost = int(word.replace(",", ""))
                if gold_cost >= 15:
                    break
            
            if rarity is None:
                item_name.append(word)

        if rarity and gold_cost:
            items.append({
                'Item Name': ' '.join(item_name),
                'Rarity': rarity,
                'Gold Cost': gold_cost,
            })

    return items

def save_parsed_items_to_db(conn, items):
    database_manager.save_to_db(items, conn)




def main():
    conn = database_manager.create_connection()
    database_manager.create_master_table(conn)
    
    image_path = '/Users/iainshand/Documents/Projects/DnD-marketbot/market-images/Screenshot_12.png'
    extracted_data = extract_text_from_image(image_path, 'rare')

    save_parsed_items_to_db(conn, extracted_data)

    print("\nCurrent Database:")
    items = database_manager.fetch_all_items(conn)
    for item in items:
        print(f"ID: {item[0]}, Item Name: {item[1]}, Rarity: {item[2]}, Gold Cost: {item[3]}, Total Entries: {item[4]}")

    conn.close()

if __name__ == "__main__":
    main()
 

