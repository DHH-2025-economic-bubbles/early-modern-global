import os
import re
from PIL import Image

def create_gif_from_yearly_pngs(input_folder='yearly_heatmaps', 
                                output_path='heatmap_animation.gif',
                                duration=1000,
                                loop=0,
                                optimize=True):
    """
    Create an animated GIF from yearly heatmap PNG images
    
    Args:
        input_folder: Folder containing the yearly PNG files
        output_path: Path for the output GIF file
        duration: Duration of each frame in milliseconds
        loop: Number of loops (0 = infinite loop)
        optimize: Whether to optimize the GIF file size
    """
    
    # Get all PNG files from the folder
    png_files = []
    pattern = re.compile(r'heatmap_(\d{4})\.png')
    
    # Find all heatmap PNG files and extract years
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            match = pattern.match(filename)
            if match:
                year = int(match.group(1))
                file_path = os.path.join(input_folder, filename)
                png_files.append((year, file_path))
    
    # Sort by year
    png_files.sort(key=lambda x: x[0])
    
    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return
    
    print(f"Found {len(png_files)} PNG files")
    print(f"Year range: {png_files[0][0]} to {png_files[-1][0]}")
    
    # Load images
    images = []
    for year, file_path in png_files:
        print(f"Loading image for year {year}...")
        img = Image.open(file_path)
        images.append(img)
    
    # Save as animated GIF
    print(f"Creating animated GIF: {output_path}")
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop,
        optimize=optimize
    )
    
    print(f"Successfully created {output_path}")
    print(f"GIF contains {len(images)} frames with {duration}ms per frame")

def create_gif_with_fade_transitions(input_folder='yearly_heatmaps',
                                   output_path='heatmap_fade_animation.gif',
                                   duration=800,
                                   fade_frames=3,
                                   loop=0):
    """
    Create an animated GIF with fade transitions between years
    
    Args:
        input_folder: Folder containing the yearly PNG files
        output_path: Path for the output GIF file
        duration: Duration of each main frame in milliseconds
        fade_frames: Number of intermediate frames for fade transition
        loop: Number of loops (0 = infinite loop)
    """
    
    # Get all PNG files
    png_files = []
    pattern = re.compile(r'heatmap_(\d{4})\.png')
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            match = pattern.match(filename)
            if match:
                year = int(match.group(1))
                file_path = os.path.join(input_folder, filename)
                png_files.append((year, file_path))
    
    png_files.sort(key=lambda x: x[0])
    
    if len(png_files) < 2:
        print("Need at least 2 images for fade transitions")
        return
    
    print(f"Creating GIF with fade transitions...")
    
    # Load images
    all_frames = []
    for i, (year, file_path) in enumerate(png_files):
        img = Image.open(file_path).convert('RGBA')
        
        # Add main frame
        all_frames.append(img)
        
        # Add fade transition frames (except for the last image)
        if i < len(png_files) - 1:
            next_img = Image.open(png_files[i + 1][1]).convert('RGBA')
            
            # Create fade transition frames
            for j in range(1, fade_frames + 1):
                alpha = j / (fade_frames + 1)
                
                # Create blended frame
                blended = Image.blend(img, next_img, alpha)
                all_frames.append(blended)
    
    # Create duration list (longer for main frames, shorter for transitions)
    durations = []
    for i in range(len(png_files)):
        durations.append(duration)  # Main frame
        if i < len(png_files) - 1:
            # Transition frames
            durations.extend([duration // 4] * fade_frames)
    
    # Save as animated GIF
    all_frames[0].save(
        output_path,
        save_all=True,
        append_images=all_frames[1:],
        duration=durations,
        loop=loop,
        optimize=True
    )
    
    print(f"Successfully created {output_path} with {len(all_frames)} frames")

# Main execution
if __name__ == "__main__":
    print("=== Creating GIF animations from yearly heatmaps ===\n")
    
    # Create basic GIF (1 second per frame)
    print("Creating basic animated GIF...")
    create_gif_from_yearly_pngs(
        input_folder='/home/cedric/repos/early-modern-global/findings/year_heatmap',
        output_path='/home/cedric/repos/early-modern-global/findings/heatmap_animation.gif',
        duration=500
    )
    
    print("Done! Created two GIF files:")
    print("- heatmap_animation.gif (basic animation)")
    print("- heatmap_fade_animation.gif (with smooth transitions)")