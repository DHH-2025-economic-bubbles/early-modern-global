import os
import json
import re
import random
import shutil
import logging
from multiprocessing import Pool, cpu_count

from settings import DATA_FOLDER, ADS_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Compile regex once for case-insensitive search of the word "india"
TARGET_PATTERN = re.compile(r'\bindia\b', re.IGNORECASE)
FOLDER_TO_SAVE = DATA_FOLDER / "india_ads"

def file_contains_string(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "india" not in content.lower():  # Fast pre-check
                return None
            data = json.loads(content)
            # Deep search across all JSON text
            if TARGET_PATTERN.search(json.dumps(data)):
                return file_path
    except Exception:
        return None

def find_matching_jsons(directory):
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(file_contains_string, json_files)
    return [f for f in results if f]

if __name__ == "__main__":
    logger.info("Starting search for files containing 'india'")
    matches = find_matching_jsons(ADS_FOLDER)
    logger.info(f"Found {len(matches)} matching files.")
    
    # Create the destination folder if it doesn't exist
    os.makedirs(FOLDER_TO_SAVE, exist_ok=True)
    logger.info(f"Saving files to {FOLDER_TO_SAVE}")
    
    # Randomly select 10% of the matched files
    sample_size = max(1, int(len(matches) * 0.1))
    selected_files = random.sample(matches, sample_size)
    logger.info(f"Selected {sample_size} files ({(sample_size/len(matches)*100):.1f}% of total)")
    
    # Copy the selected files to the destination folder
    for i, file_path in enumerate(selected_files, 1):
        file_name = os.path.basename(file_path)
        destination = os.path.join(FOLDER_TO_SAVE, file_name)
        shutil.copy2(file_path, destination)
        if i % 10 == 0 or i == len(selected_files):
            logger.info(f"Progress: {i}/{len(selected_files)} files saved ({(i/len(selected_files)*100):.1f}%)")
    
    # Verify the number of saved files
    saved_files = os.listdir(FOLDER_TO_SAVE)
    logger.info(f"Successfully saved {len(saved_files)} files to {FOLDER_TO_SAVE}")
    logger.info(f"Sample percentage: {(len(saved_files)/len(matches)*100):.2f}% of total matches")
