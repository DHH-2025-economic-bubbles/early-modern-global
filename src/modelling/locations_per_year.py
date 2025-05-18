import json
from typing import List
import pandas as pd
import geopandas as gpd
from datetime import datetime
from shapely.geometry import Point


from modelling.utils import create_yearly_heatmap_images
from preprocessing.utils import read_gpkg_to_dict
from settings import DATA_FOLDER, FINDINGS_FOLDER

gpkg_path = DATA_FOLDER / "filtered_places.gpkg" 
places_data = read_gpkg_to_dict(gpkg_path)
places_names = list(places_data.keys())


def process_json_files(list_data: List[dict]):
    data_list = []
    
    for article_data in list_data:
        try:
            start_date = article_data.get('meta_issue_date_start')
            end_date = article_data.get('meta_issue_date_end')
            
            if start_date and end_date:
                if '-00' in start_date:
                    start_year = int(start_date.split('-')[0])
                else:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    start_year = start_dt.year
                    
                if '-00' in end_date:
                    end_year = int(end_date.split('-')[0])
                else:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_year = end_dt.year
                year = start_year + (end_year - start_year) // 2
                
                article_data['year'] = year

                found_words = article_data.get("found_words")
                
                matching_places = [place for place in places_names if place in found_words]
                
                if matching_places:
                    for place in matching_places:
                        place_entry = article_data.copy()
                        coords = places_data[place]
                        place_entry['geometry_point'] = Point(coords)
                        place_entry['longitude'] = coords[0]
                        place_entry['latitude'] = coords[1]
                        data_list.append(place_entry)
                else:
                    article_data['geometry_point'] = None
                    data_list.append(article_data)
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error processing {article_data.get('file_name')}: {e}")
            continue
    
    df = pd.DataFrame(data_list)
    
    if not df.empty and 'geometry_point' in df.columns:
        gdf = gpd.GeoDataFrame(df, geometry='geometry_point')
        return gdf
    else:
        print("No valid data found or geometry issues")
        return None

def main():

    detected_words_file = DATA_FOLDER / "detect_words.json"

    print("Loading detected words...")
    with open(detected_words_file, 'r', encoding='utf-8') as f:
        detected_words_data = json.load(f)

    print("Processing JSON file...")
    gdf = process_json_files(detected_words_data)
    
    if gdf is not None:
        print(f"Successfully processed {len(gdf)} records")
        print(f"Year range: {gdf['year'].min()} - {gdf['year'].max()}")
        
        # Create yearly heatmap images
        print("\nCreating yearly heatmap images...")
        create_yearly_heatmap_images(gdf, output_folder=FINDINGS_FOLDER/"year_heatmap")
        
    else:
        print("Failed to process JSON files. Please check your data and paths.")

if __name__ == "__main__":
    main()
