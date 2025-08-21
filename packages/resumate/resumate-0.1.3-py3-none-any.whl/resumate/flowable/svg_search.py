import os
import sys
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from io import BytesIO
from .svg_flatener import flaten_svg


def get_icon_base_paths():
    """Get the base paths for icons depending on environment."""
    paths = []
    
    # Check if we're in development (submodules exist)
    if os.path.exists("submodules"):
        paths.extend([
            "submodules/devicons/icons",
            "submodules/logos/logos",
            "submodules/simple-icons/icons",
            "submodules/fontawesome/svgs",
            "submodules/fluentui-system-icons/assets"
        ])
    
    # Check for installed package icons
    try:
        import resumate
        package_dir = os.path.dirname(resumate.__file__)
        icons_dir = os.path.join(package_dir, 'icons')
        
        if os.path.exists(icons_dir):
            paths.extend([
                os.path.join(icons_dir, 'devicons'),
                os.path.join(icons_dir, 'logos'),
                os.path.join(icons_dir, 'simple-icons'),
                os.path.join(icons_dir, 'fontawesome'),
                os.path.join(icons_dir, 'fluentui')
            ])
    except ImportError:
        pass
    
    return paths

def search_svg(technology):
    """Search for SVG icons in both development and installed environments."""
    
    # If it's an actual file path, use it directly
    if technology and os.path.exists(technology):
        return technology
    
    if not technology:
        print(f"Warning: Empty technology name provided")
        return None
    
    # Get base paths for icon directories
    base_paths = get_icon_base_paths()
    
    if not base_paths:
        print("Warning: No icon directories found (neither submodules nor installed)")
        return None
    
    # Clean technology name
    clean_name = technology.lower().replace(' ', '').replace('#', 'sharp').replace('+', 'plus').replace('/', '')
    
    svg_files = []
    
    # Search in all base paths
    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
            
        # For devicons style (directory per technology)
        if 'devicons' in base_path:
            tech_dir = os.path.join(base_path, clean_name)
            if os.path.exists(tech_dir):
                files = [os.path.join(tech_dir, f) for f in os.listdir(tech_dir) if f.endswith(".svg")]
                svg_files.extend(files)
        
        # For single file icons (logos, simple-icons, etc)
        else:
            # Try direct match
            direct_path = os.path.join(base_path, f"{clean_name}.svg")
            if os.path.exists(direct_path):
                svg_files.append(direct_path)
            
            # Try with dash
            dash_path = os.path.join(base_path, f"{technology.replace(' ', '-').lower()}.svg")
            if os.path.exists(dash_path):
                svg_files.append(dash_path)
            
            # For fontawesome, check subdirectories
            if 'fontawesome' in base_path:
                for subdir in ['solid', 'brands', 'regular']:
                    fa_path = os.path.join(base_path, subdir, f"{clean_name}.svg")
                    if os.path.exists(fa_path):
                        svg_files.append(fa_path)
    
    # Sort with priority
    def custom_sort(item):
        if "original" in item and "wordmark" not in item:
            return 0
        elif "original" in item:
            return 1
        return 2
    
    svg_files = sorted(set(svg_files), key=custom_sort)
    
    # Test each SVG file
    for svg_file in svg_files:
        try:
            drawing = svg2rlg(svg_file)
            buffer = BytesIO()
            renderPDF.drawToFile(drawing, buffer)
            buffer.close()
            return svg_file
        except Exception as e:
            # Try flattening
            try:
                output = svg_file.replace('.svg', '_flatten.svg')
                print(f"Flattening SVG: {svg_file} -> {output}")
                flaten_svg(svg_file, output)
                
                drawing = svg2rlg(output)
                buffer = BytesIO()
                renderPDF.drawToFile(drawing, buffer)
                buffer.close()
                return output
            except Exception as flatten_error:
                print(f"Error processing {svg_file}: {e}")
                continue
    
    print(f"Warning: No SVG found for technology '{technology}'")
    return None