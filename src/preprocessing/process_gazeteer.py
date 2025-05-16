import json
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

from settings import DATA_FOLDER, TRADE_GAZETEER_RAW, WORLD_COUNTRIES_FILE

def extract_single_point(geometry):
    """
    Extract a single point from GeometryCollection or MultiPoint.
    If it's already a Point, return as is.
    """
    if geometry['type'] == 'Point':
        return Point(geometry['coordinates'])
    elif geometry['type'] == 'MultiPoint':
        # Take the first point
        return Point(geometry['coordinates'][0])
    elif geometry['type'] == 'GeometryCollection':
        # Find the first Point or MultiPoint in the collection
        for geom in geometry['geometries']:
            if geom['type'] == 'Point':
                return Point(geom['coordinates'])
            elif geom['type'] == 'MultiPoint':
                return Point(geom['coordinates'][0])
    return None
def extract_date_from_when(when_obj):
    """
    Extract date information from the 'when' object.
    Returns a string representation of the date/period.
    Handles multiple formats including timespans with nested 'in' values.
    """
    if not when_obj:  # Empty object
        return None
    
    # Handle timespans format (array of timespan objects)
    if 'timespans' in when_obj and when_obj['timespans']:
        timespans = when_obj['timespans']
        date_ranges = []
        
        for timespan in timespans:
            start_year = None
            end_year = None
            
            # Extract start year
            if 'start' in timespan and 'in' in timespan['start']:
                start_year = timespan['start']['in']
            
            # Extract end year
            if 'end' in timespan and 'in' in timespan['end']:
                end_year = timespan['end']['in']
            
            # Format the range
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
    
    # Handle original formats for backward compatibility
    
    # Check for start and end dates (original format)
    if 'start' in when_obj and 'end' in when_obj:
        return f"{when_obj['start']}-{when_obj['end']}"
    
    # Check for single date
    if 'date' in when_obj:
        return str(when_obj['date'])
    
    # Check for date-parts (array format like [[2023, 7, 5]])
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
    
    # Check for various other date representations
    if 'year' in when_obj:
        return str(when_obj['year'])
    
    # If we can't parse it, return the string representation
    return str(when_obj)


def check_time_filter(when_obj):
    """
    Check if the feature should be included based on the 'when' object.
    Include if:
    1. 'when' is empty ({})
    2. 'when' contains time period between 1600 and 1800
    """
    if not when_obj:  # Empty object
        return True
    
    # Handle timespans format (array of timespan objects)
    if 'timespans' in when_obj and when_obj['timespans']:
        timespans = when_obj['timespans']
        
        # Check if any timespan overlaps with 1600-1800
        for timespan in timespans:
            start_year = None
            end_year = None
            
            # Extract start year
            if 'start' in timespan and 'in' in timespan['start']:
                start_year = timespan['start']['in']
            
            # Extract end year
            if 'end' in timespan and 'in' in timespan['end']:
                end_year = timespan['end']['in']
            
            # Check if this timespan overlaps with 1600-1800
            if start_year is not None and end_year is not None:
                # Two ranges overlap if: max(start1, start2) <= min(end1, end2)
                # Range 1: start_year to end_year
                # Range 2: 1600 to 1800
                if max(start_year, 1600) <= min(end_year, 1800):
                    return True
            elif start_year is not None:
                # Only start year, check if it's in range
                if 1600 <= start_year <= 1800:
                    return True
            elif end_year is not None:
                # Only end year, check if it's in range
                if 1600 <= end_year <= 1800:
                    return True
        
        # If no timespan overlaps with 1600-1800, exclude this feature
        return False
    
    # Handle original formats for backward compatibility
    
    # Check for start and end dates (original format)
    if 'start' in when_obj and 'end' in when_obj:
        start_year = when_obj.get('start', 0)
        end_year = when_obj.get('end', 9999)
        # Check if the range overlaps with 1600-1800
        return max(start_year, 1600) <= min(end_year, 1800)
    
    # If there's a single date
    if 'date' in when_obj:
        date_year = when_obj.get('date', 0)
        return 1600 <= date_year <= 1800
    
    # Check for year
    if 'year' in when_obj:
        year = when_obj.get('year', 0)
        return 1600 <= year <= 1800
    
    # Add more time parsing logic as needed
    return True  # Default to include if time structure is unclear


def load_country_boundaries():
    """
    Load modern country boundaries from a source.
    """
    try:
        countries = gpd.read_file(WORLD_COUNTRIES_FILE)
        return countries
    except Exception as e:
        print(f"Error loading country boundaries: {e}")
        print("Please ensure you have a countries dataset available")
        return None

def get_country_centroids(countries_gdf, countries_list, country_column='NAME'):
    """
    Get centroid points for each country in the list.
    """
    # Filter to target countries
    target_countries = countries_gdf[countries_gdf[country_column].isin(countries_list)].copy()
    
    # Calculate centroids
    target_countries['geometry'] = target_countries.geometry.centroid
    
    # Create feature data for country centroids
    country_features = []
    for _, row in target_countries.iterrows():
        feature_data = {
            'name': f"{row[country_column]}",
            'country': row[country_column],
            'date': None,  # Countries don't have dates
            'geometry': row['geometry']
        }
        country_features.append(feature_data)
    
    return country_features

def filter_by_countries(gdf, countries_list):
    """
    Filter GeoDataFrame to keep only points within specified countries.
    """
    # Load country boundaries
    world = load_country_boundaries()
    
    if world is None:
        print("Could not load country boundaries. Skipping country filter.")
        return gdf, []
    
    # Ensure both are in the same CRS
    world = world.to_crs(gdf.crs)
    
    # Filter world data to only include our target countries
    country_column = 'NAME'  # Adjust this based on your country data
    
    # Filter countries
    target_countries = world[world[country_column].isin(countries_list)].copy()
    
    if len(target_countries) == 0:
        print(f"No countries found matching: {countries_list}")
        print(f"Available countries sample: {world[country_column].head().tolist()}")
        return gdf, []
    
    # Get country centroids
    country_centroids = get_country_centroids(world, countries_list, country_column)
    
    # Perform spatial join to find points within countries
    points_with_countries = gpd.sjoin(gdf, target_countries, how='inner', predicate='within')
    
    # Add country name to the points
    points_with_countries['country'] = points_with_countries[country_column]
    
    # Clean up the result by selecting only our desired columns
    result_columns = ['name', 'country', 'date', 'geometry']
    points_with_countries = points_with_countries[result_columns]
    
    print(f"Filtered from {len(gdf)} to {len(points_with_countries)} points within target countries")
    print(f"Adding {len(country_centroids)} country centroid points")
    
    return points_with_countries, country_centroids

def process_geojson_to_gpkg(input_files, output_file, filter_countries=True):
    """
    Process GeoJSON file and convert to GPKG with filtering and geometry conversion.
    """
    # Define target countries
    target_countries = ['Sierra Leone', 'Gambia', 'Ghana', 'Nigeria', 'India', 'Sri Lanka', 'Malaysia',
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
    "Panama"]
    
    features = []
    # Read the JSON file
    for input_file in input_files:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            features.extend(data['features'])
    
    # Prepare lists for the GeoDataFrame
    features_data = []
    
    # Process each feature
    for feature in data['features']:
        properties = feature.get('properties', {})
        # we remove short names because they create too many false positives
        if len(properties.get('title')) < 4:
            continue
        # Check time filter
        when_obj = feature.get('when', {})
        if not check_time_filter(when_obj):
            continue
        
        # Extract geometry and convert to single point
        geometry = feature.get('geometry', {})
        point = extract_single_point(geometry)
        
        if point is None:
            continue
        
        # Extract properties we want to keep
        
        
        # Extract date from when object
        date_value = extract_date_from_when(when_obj)
        
        feature_data = {
            'name': properties.get('title'),
            'date': date_value,
            'geometry': point
        }
        
        features_data.append(feature_data)
    
    # Create GeoDataFrame
    if features_data:
        gdf = gpd.GeoDataFrame(features_data, crs='EPSG:4326')
        
        # Filter by countries and get country centroids if requested
        if filter_countries:
            gdf, country_centroids = filter_by_countries(gdf, target_countries)
            
            # Add country centroids to the main dataframe
            if country_centroids:
                country_gdf = gpd.GeoDataFrame(country_centroids, crs=gdf.crs)
                gdf = pd.concat([gdf, country_gdf], ignore_index=True)
        
        # Save to GPKG
        gdf.to_file(output_file, driver='GPKG')
        print(f"Successfully saved {len(gdf)} features to {output_file}")
        print(f"Columns in output: {list(gdf.columns)}")
        
        # Show country distribution
        if 'country' in gdf.columns:
            print("\nPoints per country:")
            print(gdf['country'].value_counts())
            
        # Show date distribution
        if 'date' in gdf.columns:
            print(f"\nDates found: {gdf['date'].notna().sum()} out of {len(gdf)} features")
            print("Sample dates:")
            print(gdf['date'].dropna().head())
    else:
        print("No features matched the criteria.")
    
    return len(gdf) if isinstance(gdf, gpd.GeoDataFrame) else 0

# Usage example
if __name__ == "__main__":
    output_file = DATA_FOLDER / "filtered_places.gpkg"
    world_gazeteer = "/home/cedric/repos/early-modern-global/data/1298_black_20250515_174218.json"
    
    # Run the conversion
    count = process_geojson_to_gpkg([TRADE_GAZETEER_RAW, world_gazeteer], output_file)
    print(f"Processed {count} features total.")