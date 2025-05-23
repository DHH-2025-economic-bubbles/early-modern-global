import json
import os
from typing import List
import pandas as pd
import geopandas as gpd
from datetime import datetime
import random
from shapely.geometry import Point


from modelling.utils import create_yearly_heatmap_images
from preprocessing.utils import read_gpkg_to_dict
from settings import DATA_FOLDER, DECADE_HEATMAP, FINDINGS_FOLDER



gpkg_path = DATA_FOLDER / "filtered_places.gpkg" 
places_data = read_gpkg_to_dict(gpkg_path)
places_names = list(places_data.keys())

words_of_interest: List[str] = [
    "tobacco",
    #"rice",
    "indigo",
    "sugar",
    "molasses",
    "negroes",
    #"silk",
    "peltry",
    "slave"
]

OUTPUT_FOLDER = FINDINGS_FOLDER/"year_heatmap_goods"
if DECADE_HEATMAP:
    OUTPUT_FOLDER = OUTPUT_FOLDER / "_decade"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

FILES_LOG = OUTPUT_FOLDER / "json_list"

def process_json_files(list_data: List[dict]):
    data_list = []
    if FILES_LOG.exists():
        FILES_LOG.unlink()
    FILES_LOG.touch()
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
                article_data['decade'] = (year // 10) * 10

                paragraph_words = article_data.get("found_words")
                

                for paragraph_words in paragraph_words:
                    matching_places = [word for word in places_names if word in paragraph_words]
                    if words_of_interest:
                        matching_words = [word for word in paragraph_words if word in words_of_interest]
                    
                    # Choose a random matching word if there are any
                    chosen_word = max(matching_words, key=matching_words.count) if matching_words else None
                    article_data['interest_word'] = chosen_word

                    if matching_places and matching_words:
                        with open(FILES_LOG, 'a') as file:
                            file.write(article_data["file_name"] + f" {year}" +  f" {chosen_word}"'\n')


                        for place in matching_places:
                            place_entry = article_data.copy()
                            coords = places_data[place]
                            if not coords:
                                print(f"{place} is not in the geo data")
                                continue
                            place_entry['geometry_point'] = Point(coords)
                            place_entry['longitude'] = coords[0]
                            place_entry['latitude'] = coords[1]
                            place_entry["place"] = place
                            data_list.append(place_entry)

            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error processing {article_data.get('file_name')}: {e}")
            continue
    
    df = pd.DataFrame(data_list)
    
    if not df.empty and 'geometry_point' in df.columns:
        gdf = gpd.GeoDataFrame(df, geometry='geometry_point')
        
        # Handle decade grouping if requested
        if DECADE_HEATMAP:
            # Group by decade and place
            # Get unique places per decade
            decade_places = gdf.groupby(['decade', 'place']).size().reset_index(name='count')
            
            # Find most mentioned interest_word per place per decade
            word_counts = gdf.groupby(['decade', 'place', 'interest_word']).size().reset_index(name='word_count')
            top_words = word_counts.sort_values('word_count', ascending=False).groupby(['decade', 'place']).first()
            
            # Create a new dataframe with one entry per place per decade
            decade_df = decade_places.merge(
                top_words[['interest_word']], 
                on=['decade', 'place'],
                how='left'
            )
            
            # Get representative point coordinates (using the first occurrence)
            coords = gdf.groupby(['decade', 'place']).first()[['longitude', 'latitude', 'geometry_point']]
            decade_df = decade_df.merge(coords, on=['decade', 'place'])
            
            # Create a new GeoDataFrame with decade grouping
            decade_gdf = gpd.GeoDataFrame(decade_df, geometry='geometry_point')
            return decade_gdf
        
        return gdf
    else:
        print("No valid data found or geometry issues")
        return None

def main():

    detected_words_file = DATA_FOLDER / "detect_words.jsonl"

    print("Loading detected words...")
    with open(detected_words_file, 'r', encoding='utf-8') as f:
        detected_words_data = [json.loads(line) for line in f]

    print("Processing JSON file...")
    gdf = process_json_files(detected_words_data)
    
    if gdf is not None:
        print(f"Successfully processed {len(gdf)} records")
        
        # Create yearly heatmap images
        print("\nCreating yearly heatmap images...")
        create_yearly_heatmap_images(gdf, output_folder=OUTPUT_FOLDER)
        
    else:
        print("Failed to process JSON files. Please check your data and paths.")

if __name__ == "__main__":
    main()