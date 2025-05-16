from pathlib import Path

DATA_FOLDER = Path(__file__).parents[1] / ("data")
FOLDER_ARTICLES = DATA_FOLDER / "json_res/scratch/project_2005072/keshu/octavo-newspapers-downloader/data/work/json_res"

FINDINGS_FOLDER = Path(__file__).parents[1] / ("findings")

ADS_FOLDER = DATA_FOLDER / "ads"

FILE_POLITICAL_AFFILIATIONS = DATA_FOLDER / "burney-titles-political.csv"

TRADE_GAZETEER_RAW = DATA_FOLDER / "1300_owtrad_20250515_115842.json"

WORLD_COUNTRIES_FILE = DATA_FOLDER/"ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"

BRITISH_COLONIAL_TRADE_PLACES_EAST = DATA_FOLDER / "filtered_trade_places.gpkg"