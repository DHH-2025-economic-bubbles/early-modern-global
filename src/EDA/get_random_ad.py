import json
import random
import polars as pl
from pathlib import Path

from settings import DATA_FOLDER

# Path to metadata CSV file
BL_NEWSPAPERS_META = Path("/home/cedric/repos/early-modern-global/data/bl_newspapers_meta.csv")
# Path to ads folder
ADS_FOLDER = DATA_FOLDER / "ads"

def get_random_ad():
    """
    Get a random entry from the ads folder and print it.
    Also display corresponding metadata from bl_newspapers_meta.csv.
    """
    answer = input("Do you want to print a random article? (input y if so): ")
    
    # Get all ad files
    ad_files = list(ADS_FOLDER.glob("*.json"))
    print(f"number of ads: {len(ad_files)}")
    
    while answer == "y":
        # Pick a random ad file
        random_file = random.choice(ad_files)
        
        # Load the random ad
        with open(random_file, 'r') as f:
            random_ad = json.load(f)
            
        print("\nRandom Advertisement:")
        print(json.dumps(random_ad, indent=2))
        
        answer = input("Do you want to print a random article? (input y if so): ")


if __name__ == "__main__":
    get_random_ad()