import json
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set, Union, cast
from pathlib import Path

from settings import DATA_FOLDER, TRADE_GAZETEER_RAW, WORLD_COUNTRIES_FILE

def extract_single_point(geometry: Dict[str, Any]) -> Optional[Point]:
    if geometry['type'] == 'Point':
        return Point(geometry['coordinates'])
    elif geometry['type'] == 'MultiPoint':
        return Point(geometry['coordinates'][0])
    elif geometry['type'] == 'GeometryCollection':
        for geom in geometry['geometries']:
            if geom['type'] == 'Point':
                return Point(geom['coordinates'])
            elif geom['type'] == 'MultiPoint':
                return Point(geom['coordinates'][0])
    return None

def extract_date_from_when(when_obj: Optional[Dict[str, Any]]) -> Optional[str]:
    if not when_obj:
        return None
    
    if 'timespans' in when_obj and when_obj['timespans']:
        timespans: List[Dict[str, Any]] = when_obj['timespans']
        date_ranges: List[str] = []
        
        for timespan in timespans:
            start_year: Optional[int] = None
            end_year: Optional[int] = None
            
            if 'start' in timespan and 'in' in timespan['start']:
                start_year = timespan['start']['in']
            
            if 'end' in timespan and 'in' in timespan['end']:
                end_year = timespan['end']['in']
            
            if start_year is not None and end_year is not None:
                if start_year == end_year:
                    date_ranges.append(str(start_year))
                else:
                    date_ranges.append(f"{start_year}-{end_year}")
            elif start_year is not None:
                date_ranges.append(f"{start_year}-")
            elif end_year is not None:
                date_ranges.append(f"-{end_year}")
        
        return "; ".join(date_ranges) if date_ranges else None
    
    if 'start' in when_obj and 'end' in when_obj:
        return f"{when_obj['start']}-{when_obj['end']}"
    
    if 'date' in when_obj:
        return str(when_obj['date'])
    
    if 'date-parts' in when_obj and when_obj['date-parts']:
        date_part = when_obj['date-parts'][0]
        if isinstance(date_part, list) and len(date_part) > 0:
            year = date_part[0]
            if len(date_part) > 1:
                month = date_part[1]
                if len(date_part) > 2:
                    day = date_part[2]
                    return f"{year}-{month:02d}-{day:02d}"
                else:
                    return f"{year}-{month:02d}"
            else:
                return str(year)
    
    if 'year' in when_obj:
        return str(when_obj['year'])
    
    return str(when_obj)


def check_time_filter(when_obj: Optional[Dict[str, Any]]) -> bool:
    if not when_obj:
        return True
    
    if 'timespans' in when_obj and when_obj['timespans']:
        timespans: List[Dict[str, Any]] = when_obj['timespans']
        
        for timespan in timespans:
            start_year: Optional[int] = None
            end_year: Optional[int] = None
            
            if 'start' in timespan and 'in' in timespan['start']:
                start_year = timespan['start']['in']
            
            if 'end' in timespan and 'in' in timespan['end']:
                end_year = timespan['end']['in']
            
            if start_year is not None and end_year is not None:
                if max(int(start_year), 1600) <= min(int(end_year), 1800):
                    return True
            elif start_year is not None:
                if 1600 <= int(start_year) <= 1800:
                    return True
            elif end_year is not None:
                if 1600 <= int(end_year) <= 1800:
                    return True
        
        return False
    
    if 'start' in when_obj and 'end' in when_obj:
        start_year: int = when_obj.get('start', 0)
        end_year: int = when_obj.get('end', 9999)
        return max(start_year, 1600) <= min(end_year, 1800)
    
    if 'date' in when_obj:
        date_year: int = when_obj.get('date', 0)
        return 1600 <= date_year <= 1800
    
    if 'year' in when_obj:
        year: int = when_obj.get('year', 0)
        return 1600 <= year <= 1800
    
    return True


def load_country_boundaries() -> Optional[gpd.GeoDataFrame]:
    try:
        countries: gpd.GeoDataFrame = gpd.read_file(WORLD_COUNTRIES_FILE)
        return countries
    except Exception as e:
        print(f"Error loading country boundaries: {e}")
        print("Please ensure you have a countries dataset available")
        return None

def get_country_centroids(countries_gdf: gpd.GeoDataFrame, countries_list: List[str], country_column: str = 'NAME') -> List[Dict[str, Any]]:
    target_countries: gpd.GeoDataFrame = countries_gdf[countries_gdf[country_column].isin(countries_list)].copy()
    
    target_countries['geometry'] = target_countries.geometry.centroid
    
    country_features: List[Dict[str, Any]] = []
    for _, row in target_countries.iterrows():
        feature_data: Dict[str, Any] = {
            'name': f"{row[country_column]}",
            'country': row[country_column],
            'date': None,  # Countries don't have dates
            'geometry': row['geometry']
        }
        country_features.append(feature_data)
    
    return country_features

def filter_by_countries(gdf: gpd.GeoDataFrame, countries_list: List[str]) -> Tuple[gpd.GeoDataFrame, List[Dict[str, Any]]]:
    world: Optional[gpd.GeoDataFrame] = load_country_boundaries()
    
    if world is None:
        print("Could not load country boundaries. Skipping country filter.")
        return gdf, []
    
    world = world.to_crs(gdf.crs)
    
    country_column: str = 'NAME'
    
    target_countries: gpd.GeoDataFrame = world[world[country_column].isin(countries_list)].copy()
    
    if len(target_countries) == 0:
        print(f"No countries found matching: {countries_list}")
        print(f"Available countries sample: {world[country_column].head().tolist()}")
        return gdf, []
    
    country_centroids: List[Dict[str, Any]] = get_country_centroids(world, countries_list, country_column)
    
    points_with_countries: gpd.GeoDataFrame = gpd.sjoin(gdf, target_countries, how='inner', predicate='within')
    
    points_with_countries['country'] = points_with_countries[country_column]
    
    result_columns: List[str] = ['name', 'country', 'date', 'geometry']
    points_with_countries = points_with_countries[result_columns]
    
    print(f"Filtered from {len(gdf)} to {len(points_with_countries)} points within target countries")
    print(f"Adding {len(country_centroids)} country centroid points")
    
    return points_with_countries, country_centroids

def process_geojson_to_gpkg(input_files: List[Union[str, Path]], output_file: Union[str, Path], filter_countries: bool = True) -> int:
    target_countries: List[str] = ['Sierra Leone', 'Gambia', 'Ghana', 'Nigeria', 'India', 'Sri Lanka', 'Malaysia',
    "United States of America",
    "Canada",
    "Bahamas",
    "Barbados",
    "Jamaica",
    "Saint Kitts and Nevis",
    "Antigua and Barbuda",
    "Saint Vincent and the Grenadines",
    "Saint Lucia",
    "Dominica",
    "Grenada",
    "Trinidad and Tobago",
    "Belize",
    "Guyana",
    "Haiti",
    "Dominican Republic",
    "Honduras",
    "Nicaragua",
    "Costa Rica",
    "Panama",
    "France", # we add two control countries
    "Japan"]
    
    features: List[Dict[str, Any]] = []
    for input_file in input_files:
        with open(input_file, 'r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)
            features.extend(data['features'])
    
    features_data: List[Dict[str, Any]] = []
    
    for feature in features:
        properties: Dict[str, Any] = feature.get('properties', {})
        if len(properties.get('title', '')) < 4:
            continue
        when_obj: Optional[Dict[str, Any]] = feature.get('when', {})
        if not check_time_filter(when_obj):
            continue
        
        geometry: Dict[str, Any] = feature.get('geometry', {})
        point: Optional[Point] = extract_single_point(geometry)
        
        if point is None:
            continue
        
        date_value: Optional[str] = extract_date_from_when(when_obj)
        
        feature_data: Dict[str, Any] = {
            'name': properties.get('title', ''),
            'date': date_value,
            'geometry': point
        }
        
        features_data.append(feature_data)
    
    gdf: Optional[gpd.GeoDataFrame] = None
    if features_data:
        gdf = gpd.GeoDataFrame(features_data, crs='EPSG:4326')
        
        if filter_countries and gdf is not None:
            gdf, country_centroids = filter_by_countries(gdf, target_countries)
            
            if country_centroids and gdf is not None:
                country_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(country_centroids, crs=gdf.crs)
                gdf = pd.concat([gdf, country_gdf], ignore_index=True)
        
        if gdf is not None:
            gdf['name'] = gdf['name'].str.lower()
            gdf.to_file(output_file, driver='GPKG')
            print(f"Successfully saved {len(gdf)} features to {output_file}")
            print(f"Columns in output: {list(gdf.columns)}")
            
            if 'country' in gdf.columns:
                print("\nPoints per country:")
                print(gdf['country'].value_counts())
                
            if 'date' in gdf.columns:
                print(f"\nDates found: {gdf['date'].notna().sum()} out of {len(gdf)} features")
                print("Sample dates:")
                print(gdf['date'].dropna().head())
    else:
        print("No features matched the criteria.")
    
    return len(gdf) if isinstance(gdf, gpd.GeoDataFrame) else 0

if __name__ == "__main__":
    output_file: Path = DATA_FOLDER / "filtered_places.gpkg"
    world_gazeteer: str = "/home/cedric/repos/early-modern-global/data/1298_black_20250515_174218.json"
    
    count: int = process_geojson_to_gpkg([TRADE_GAZETEER_RAW, world_gazeteer], output_file)
    print(f"Processed {count} features total.")