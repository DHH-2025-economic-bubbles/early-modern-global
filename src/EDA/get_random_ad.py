import json
import random
from pathlib import Path

from settings import FILTERED_ADS

def get_random_ad():
    """
    Get a random entry from filtered_ads.json and print it.
    """
    
    with open(FILTERED_ADS, 'r') as f:
        ads = json.load(f)
    
    random_ad = random.choice(ads)
    print(json.dumps(random_ad, indent=2))
    return random_ad

if __name__ == "__main__":
    get_random_ad()