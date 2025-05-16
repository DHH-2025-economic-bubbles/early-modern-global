import json
import os
import pandas as pd
import geopandas as gpd
from datetime import datetime
from shapely.geometry import Point
import folium
from folium.plugins import HeatMapWithTime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import pdist, squareform

from settings import FINDINGS_FOLDER, WORLD_COUNTRIES_FILE

def process_json_files(folder_path):
    """
    Process all JSON files in a folder and create a GeoDataFrame
    """
    data_list = []
    
    # Iterate through all JSON files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                    # Extract year from date fields
                    start_date = data.get('meta_issue_date_start')
                    end_date = data.get('meta_issue_date_end')
                    
                    if start_date and end_date:
                        # Parse dates and calculate middle year
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                        
                        # Calculate middle date and extract year
                        middle_date = start_dt + (end_dt - start_dt) / 2
                        year = middle_date.year
                        
                        # Add year to the data
                        data['year'] = year
                        
                        # Extract coordinates from geometry
                        if 'geometry' in data and 'coordinates' in data['geometry']:
                            coords = data['geometry']['coordinates']
                            data['longitude'] = coords[0]
                            data['latitude'] = coords[1]
                            
                            # Create Point geometry
                            data['geometry_point'] = Point(coords[0], coords[1])
                        
                        data_list.append(data)
                        
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Error processing {filename}: {e}")
                continue
    
    # Create DataFrame
    df = pd.DataFrame(data_list)
    
    # Create GeoDataFrame
    if not df.empty and 'geometry_point' in df.columns:
        gdf = gpd.GeoDataFrame(df, geometry='geometry_point')
        return gdf
    else:
        print("No valid data found or geometry issues")
        return None


def create_density_grid(x_coords, y_coords, grid_resolution=100, sigma=1.0):
    """
    Create a density grid from point coordinates
    """
    # Create grid
    x_min, x_max = -180, 180
    y_min, y_max = -90, 90
    
    xi = np.linspace(x_min, x_max, grid_resolution)
    yi = np.linspace(y_min, y_max, grid_resolution)
    
    # Create 2D grid
    density_grid = np.zeros((len(yi), len(xi)))
    
    # Calculate density for each grid point
    for i, x_grid in enumerate(xi):
        for j, y_grid in enumerate(yi):
            # Calculate distances to all points
            distances = np.sqrt((x_coords - x_grid)**2 + (y_coords - y_grid)**2)
            # Use gaussian kernel
            density = np.sum(np.exp(-distances**2 / (2 * sigma**2)))
            density_grid[j, i] = density
    
    # Apply gaussian filter for smoothing
    density_grid = gaussian_filter(density_grid, sigma=0.5)
    
    return xi, yi, density_grid

def create_yearly_heatmap_images(gdf, output_folder):
    """
    Create heatmap images for each year using matplotlib
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get unique years and sort them
    years = sorted(gdf['year'].unique())
    
    # Set up the colormap for heatmap (blue -> green -> red)
    colors = ['#000080', '#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('heatmap', colors, N=n_bins)
    
    # Create world boundaries for better visualization
    try:
        world = gpd.read_file(WORLD_COUNTRIES_FILE)
    except:
        world = None
    
    for year in years:
        print(f"Creating heatmap for year {year}...")
        
        # Filter data for this year
        year_data = gdf[gdf['year'] == year]
        
        if len(year_data) == 0:
            continue
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(20, 12), dpi=150)
        
        # Set world boundaries
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        
        # Add world map background if available
        if world is not None:
            world.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)
        else:
            ax.set_facecolor('lightgray')
        
        # Get coordinates
        x_coords = year_data['longitude'].values
        y_coords = year_data['latitude'].values
        
        # Create density heatmap if we have enough points
        if len(year_data) > 1:
            # Create density grid
            xi, yi, density_grid = create_density_grid(x_coords, y_coords, 
                                                     grid_resolution=200, sigma=2.0)
            
            # Plot heatmap
            X, Y = np.meshgrid(xi, yi)
            
            # Mask zero density areas
            density_grid_masked = np.ma.masked_where(density_grid <= 0.01, density_grid)
            
            # Plot the heatmap
            heatmap = ax.contourf(X, Y, density_grid_masked, levels=50, 
                                cmap=cmap, alpha=0.7, extend='max')
        
        # Add individual points as well
        scatter = ax.scatter(x_coords, y_coords, c='red', s=30, alpha=0.8, 
                           edgecolors='darkred', linewidth=0.5, zorder=5)
        
        # Customize the plot
        ax.set_title(f'News Locations Heatmap - Year {year}', 
                    fontsize=28, fontweight='bold', pad=20)
        
        # Add info box
        info_text = f'Year: {year}\nTotal Points: {len(year_data)}'
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=16, 
               verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
               facecolor='white', alpha=0.9, edgecolor='black'))
        
        # Remove axis labels and ticks for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        
        # Remove frame
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Save the plot
        png_path = os.path.join(output_folder, f'heatmap_{year}.png')
        plt.savefig(png_path, dpi=200, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.1)
        plt.close()
    
    print(f"Successfully created {len(years)} heatmap images in {output_folder}")

# Example usage
def main():
    # Set your folder path here
    folder_path = "/home/cedric/repos/early-modern-global/data/news_locations/individual_matches"
    
    print("Processing JSON files...")
    gdf = process_json_files(folder_path)
    
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
