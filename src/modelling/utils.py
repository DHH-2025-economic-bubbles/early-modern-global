

import os
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from settings import  WORLD_COUNTRIES_FILE

from scipy.ndimage import gaussian_filter



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
    Create heatmap images for each year using matplotlib with normalization across all years
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
    
    # First pass: Calculate density grids and find global maximum density
    density_grids = {}
    global_max_density = 0
    
    for year in years:
        print(f"Calculating density for year {year}...")
        
        # Filter data for this year
        year_data = gdf[gdf['year'] == year]
        
        if len(year_data) == 0:
            continue
        
        # Get coordinates
        x_coords = year_data['longitude'].values
        y_coords = year_data['latitude'].values
        
        # Create density grid if we have enough points
        if len(year_data) > 1:
            # Create density grid
            xi, yi, density_grid = create_density_grid(x_coords, y_coords, 
                                                     grid_resolution=200, sigma=2.0)
            
            # Store for later use
            density_grids[year] = (xi, yi, density_grid)
            
            # Update global maximum
            year_max = np.max(density_grid)
            if year_max > global_max_density:
                global_max_density = year_max
    
    # Second pass: Create normalized heatmaps using the global maximum
    for year in years:
        print(f"Creating normalized heatmap for year {year}...")
        
        # Skip if no data or density grid for this year
        if year not in density_grids:
            continue
        
        # Get year data for point plotting
        year_data = gdf[gdf['year'] == year]
        
        # Get stored density grid
        xi, yi, density_grid = density_grids[year]
        
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
        
        # Plot heatmap
        X, Y = np.meshgrid(xi, yi)
        
        # Mask zero density areas
        density_grid_masked = np.ma.masked_where(density_grid <= 0.01, density_grid)
        
        # Plot the heatmap with normalized levels based on global maximum
        levels = np.linspace(0, global_max_density, 50)
        heatmap = ax.contourf(X, Y, density_grid_masked, levels=levels, 
                            cmap=cmap, alpha=0.7, extend='max')
        
        # Add individual points as well
        x_coords = year_data['longitude'].values
        y_coords = year_data['latitude'].values
        scatter = ax.scatter(x_coords, y_coords, c='red', s=30, alpha=0.8, 
                           edgecolors='darkred', linewidth=0.5, zorder=5)
        
        # Customize the plot
        ax.set_title(f'News Locations Heatmap - Year {year}', 
                    fontsize=28, fontweight='bold', pad=20)
        
        # Add info box with normalization note
        info_text = f'Year: {year}\nTotal Points: {len(year_data)}\nNormalized across all years'
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=16, 
               verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
               facecolor='white', alpha=0.9, edgecolor='black'))
        
        # Add colorbar
        cbar = plt.colorbar(heatmap, ax=ax, pad=0.01)
        cbar.set_label('Density (normalized across all years)', rotation=270, labelpad=20)
        
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
    
    print(f"Successfully created normalized heatmaps in {output_folder}")