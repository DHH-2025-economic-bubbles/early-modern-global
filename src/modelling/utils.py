import os
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches

from settings import DECADE_HEATMAP, WORLD_COUNTRIES_FILE

def create_yearly_heatmap_images(gdf, output_folder):
    """
    Create heatmap images for each year using scipy.stats.gaussian_kde
    which is optimized and reliable for kernel density estimation
    Points are colored based on their interest_word value
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get unique years and sort them
    if DECADE_HEATMAP:
        years = sorted(gdf['decade'].unique())
    else:    
        years = sorted(gdf['year'].unique())
    
    # Set up the colormap for heatmap
    colors = ['#000080', '#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('heatmap', colors, N=n_bins)
    
    # Create world boundaries for better visualization
    try:
        world = gpd.read_file(WORLD_COUNTRIES_FILE)
    except Exception as e:
        print(f"Warning: Could not load world countries file: {e}")
        world = None
    
    # Setup grid for KDE evaluation
    grid_resolution = 100
    x_grid = np.linspace(-180, 180, grid_resolution)
    y_grid = np.linspace(-90, 90, grid_resolution)
    X, Y = np.meshgrid(x_grid, y_grid)
    positions = np.vstack([X.ravel(), Y.ravel()]).T
    
    # Define color map for interest_words
    # Create a distinctive color for each word of interest
    interest_word_colors = {
        "furs": "#e41a1c",      # red
        "peltry": "#e41a1c",    # red (same as furs)
        "tobacco": "#377eb8",   # blue
        "rice": "#4daf4a",      # green
        "indigo": "#984ea3",    # purple
        "sugar": "#ff7f00",     # orange
        "rum": "#ffff33",       # yellow
        "molasses": "#a65628",  # brown
        "negroes": "#f781bf",   # pink (same as slave)
        "slave": "#f781bf",     # pink 
        "silk": "#cab2d6"       # light purple (new color)
    }
    
    # Process each year
    for year in years:
        print(f"Processing year {year}...")
        
        # Filter data for this year
        if DECADE_HEATMAP:
            year_data = gdf[gdf['decade'] == year]
        else:
            year_data = gdf[gdf['year'] == year]
        
        if len(year_data) < 5:  # Need at least 5 points for reliable KDE
            print(f"Skipping year {year}: Not enough data points ({len(year_data)})")
            continue
        
        # Get coordinates
        x_coords = year_data['longitude'].values
        y_coords = year_data['latitude'].values
        interest_words = year_data['interest_word'].values
        
        # Handle NaN values
        mask = ~(np.isnan(x_coords) | np.isnan(y_coords))
        if np.sum(mask) < len(mask):
            print(f"Warning: Found {len(mask) - np.sum(mask)} NaN coordinates in year {year}")
            x_coords = x_coords[mask]
            y_coords = y_coords[mask]
            interest_words = interest_words[mask]
        
        if len(x_coords) < 5:
            print(f"Skipping year {year} after NaN removal: Not enough valid data points")
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
        
        try:
            # Create and evaluate KDE
            print(f"Calculating KDE for {len(x_coords)} points...")
            
            # Use scipy.stats.gaussian_kde which is optimized for this purpose
            coords = np.vstack([x_coords, y_coords])
            kde = gaussian_kde(coords, bw_method='scott')  # Automatic bandwidth selection
            
            # Reshape positions for evaluation
            Z = kde(np.vstack([X.ravel(), Y.ravel()]))
            Z = Z.reshape(X.shape)
            
            # Check for negative values (should be none with gaussian_kde)
            if np.any(Z < 0):
                print(f"Warning: Found {np.sum(Z < 0)} negative values in KDE result")
                Z = np.maximum(Z, 0)
                
            # Plot the KDE heatmap using pcolormesh
            heatmap = ax.pcolormesh(X, Y, Z, cmap=cmap, alpha=0.5)  # Reduced alpha for better point visibility
            
            # Add contour lines for better visualization
            contour = ax.contour(X, Y, Z, colors='black', alpha=0.2, linewidths=0.5)
            
            # Add colorbar
            cbar = plt.colorbar(heatmap, ax=ax, pad=0.01)
            cbar.set_label('Density Estimation', rotation=270, labelpad=20)
            
        except Exception as e:
            print(f"Error calculating KDE for year {year}: {e}")
            print("Falling back to simple scatter plot")
            heatmap = None  # No heatmap to display
        
        # Add scatter plot with different colors based on interest_word
        # Keep track of word appearances to create legend
        used_words = set()
        scatter_handles = []
        
        # Plot each point with its respective color based on interest_word
        for i, (x, y, word) in enumerate(zip(x_coords, y_coords, interest_words)):
            if pd.isna(word):
                # Handle points with no interest_word
                color = 'gray'
                label = 'No interest word'
            else:
                color = interest_word_colors.get(word, 'gray')  # Default to gray if word not in color map
                label = word
                
            scatter = ax.scatter(x, y, c=color, s=50, alpha=0.9,
                               edgecolors='black', linewidth=0.5, zorder=10)
            
            if label not in used_words:
                used_words.add(label)
                scatter_handles.append(mpatches.Patch(color=color, label=label))
        
        # Create legend with interest words that appear in this year
        if scatter_handles:
            legend = ax.legend(handles=scatter_handles, title="Words of Interest",
                            loc='upper right', fontsize=12, framealpha=0.9,
                            facecolor='white', edgecolor='black')
            legend.get_title().set_fontsize('14')
        
        # Customize the plot
        ax.set_title(f'News Locations Heatmap - Year {year}', 
                    fontsize=28, fontweight='bold', pad=20)
        
        # Add info box
        info_text = f'Year: {year}\nTotal Points: {len(x_coords)}'
        if heatmap is not None:
            info_text += '\nKDE Heatmap Visualization'
        else:
            info_text += '\nScatter Plot Only'
            
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
    
    print(f"Successfully created heatmaps in {output_folder}")