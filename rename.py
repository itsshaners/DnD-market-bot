import os

# Define the directory containing the screenshots
directory = 'market-images'  # Change this to your actual directory

# Define the range of screenshots to rename
old_start = 11
old_end = 20
new_start = 9

# Loop through the range of old screenshots
for old_number in range(old_start, old_end + 1):
    old_filename = f'Screenshot_{old_number}.png'
    new_filename = f'Screenshot_{new_start}.png'
    
    # Build the full path for the old and new filenames
    old_filepath = os.path.join(directory, old_filename)
    new_filepath = os.path.join(directory, new_filename)

    # Rename the file if it exists
    if os.path.exists(old_filepath):
        os.rename(old_filepath, new_filepath)
        print(f'Renamed: {old_filepath} to {new_filepath}')
        
    # Increment the new number for the next file
    new_start += 1

print("Renaming complete.")