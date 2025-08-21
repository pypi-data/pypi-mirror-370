import xml.etree.ElementTree as ET
import argparse
import matplotlib.colors as mcolors
import numpy as np


def load_svg(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', 'http://www.w3.org/2000/svg')  # Register default namespace for writing
    return tree, root, namespace

def find_parent(element, tree):
    for parent in tree.iter():
        for child in parent:
            if child is element:
                return parent
    return None

def insert_after(target, new_element,tree):
    """Insert new_element after the target element."""
    parent = find_parent(target,tree)  # getparent() is not available in ET, this is just an illustration
    if parent is None:
        raise ValueError("Target must have a parent to insert after it")

    index = list(parent).index(target)  # Find the index of the target in parent
    parent.insert(index + 1, new_element)  # Insert new element after the target


def interpolate_color(start_color, end_color, percentage):
    """Interpolate between two colors."""
    start_rgb = mcolors.to_rgba(start_color)
    end_rgb = mcolors.to_rgba(end_color)
    interpolated_rgb = [(1 - percentage) * start_rgb[i] + percentage * end_rgb[i] for i in range(3)]
    return mcolors.to_hex(interpolated_rgb)

def get_color_from_gradient(gradient_stops, percentage):
    """Get color from gradient stops based on percentage."""
    for i in range(len(gradient_stops) - 1):
        start_offset, start_color = gradient_stops[i]
        end_offset, end_color = gradient_stops[i + 1]
        if percentage >= start_offset and percentage <= end_offset:
            segment_percentage = (percentage - start_offset) / (end_offset - start_offset)
            return interpolate_color(start_color, end_color, segment_percentage)
    return gradient_stops[-1][1]  # Return last color if percentage is outside the gradient range

import math

def create_gradient_slivers(root, rect, stops, num_slivers=20):
    x = int(rect.get('x', '0'))
    y = int(rect.get('y', '0'))
    width = int(rect.get('width'))
    height = int(rect.get('height'))
    sliver_width = int(width / num_slivers)
    parent = find_parent(rect, root)

    # Calculate angle of the gradient
    x1 = float(rect.get('x1', '0'))
    y1 = float(rect.get('y1', '0'))
    x2 = float(rect.get('x2', '1'))
    y2 = float(rect.get('y2', '0'))
    gradient_angle = math.atan2(y2 - y1, x2 - x1)


    current_color = stops[0][1]
    new_obj = rect
    for i in range(0, num_slivers):

        percentage = i / num_slivers
        current_color = get_color_from_gradient(stops, percentage)

        # Create sliver rectangle
        sliver_rect = ET.Element('rect', {
            'x': str(x),
            'y': str(y),
            'width': str(sliver_width+2),
            'height': str(height),
            'fill': current_color,
        })

        # Calculate rotation center
        cx = x + int(sliver_width / 2)
        cy = y + int(height / 2)

        # Rotate the sliver rectangle
        #sliver_rect.set('transform', f'rotate({math.degrees(gradient_angle)}, {cx}, {cy})')

        # Insert the sliver rectangle before the original rect
        insert_after(new_obj, sliver_rect, root)
        new_obj = sliver_rect

        # Update position for the next sliver
        x += int(sliver_width)

    # Remove the original rectangle after adding all slivers
    parent.remove(rect)

def replace_gradient_with_slivers(tree, root, namespace):
    rects = root.findall('.//svg:rect', namespace)
    for rect in rects:
        fill = rect.get('fill')
        if fill and fill.startswith('url(#'):
            gradient_id = fill[5:-1]  # Extract ID from url(#id)
            stops = get_gradient_stops(root, gradient_id, namespace)
            create_gradient_slivers(root, rect, stops)

    paths = root.findall('.//svg:path', namespace)
    for path in paths:
        fill = path.get('fill')
        if fill and fill.startswith('url(#'):
            gradient_id = fill[5:-1]  # Extract ID from url(#id)
            stops = get_gradient_stops(root, gradient_id, namespace)
            average_color = calculate_average_color([stop[1] for stop in stops])
            path.set('fill', average_color)

    gradients = root.findall('.//svg:linearGradient', namespace)
    for grad in gradients:
        try:
            root.remove(grad)
        except:
            pass
    gradients = root.findall('.//svg:radialGradient', namespace)
    for grad in gradients:
        try:
            root.remove(grad)
        except:
            pass

    return tree

def calculate_average_color(colors):
    """Calculate the average color from a list of colors."""
    rgb_colors = [mcolors.to_rgba(color) for color in colors]
    average_rgb = np.mean(rgb_colors, axis=0)
    return mcolors.to_hex(average_rgb)

def get_gradient_stops(root, gradient_id, namespace):
    gradient = root.find(f'.//svg:linearGradient[@id="{gradient_id}"]', namespace)
    if gradient==None:
        gradient = root.find(f'.//svg:radialGradient[@id="{gradient_id}"]', namespace)
        if gradient==None:
            #print ("NOPE")
            return []
    stops = gradient.findall('svg:stop', namespace)
    stop_details = []
    for stop in stops:
        offset = stop.get('offset')
        if offset is None:
            continue  # Skip stops without offset
        
        offset = offset.strip()
        if '%' in offset:
            offset = float(offset.strip('%')) / 100  # Convert percentage to a float representation
        else:
            offset = float(offset)  # Directly convert to float if not a percentage
        color = stop.get('stop-color')
        if color:  # Only add if color exists
            stop_details.append((offset, color))
    return stop_details

# Ensure you register the SVG namespace if not done already
ET.register_namespace('', 'http://www.w3.org/2000/svg')

# Ensure the rest of the script remains the same and includes any necessary error handling
def flaten_svg(input_file,output_file):
    tree, root, namespace = load_svg(input_file)
    new_tree = replace_gradient_with_slivers(tree, root, namespace)
    new_tree.write(output_file)


def main():
    parser = argparse.ArgumentParser(description="Convert SVG gradients to gradient slivers in SVG.")
    parser.add_argument('--input', type=str, help='Input SVG file path')
    parser.add_argument('--output', type=str, help='Output SVG file path')
    args = parser.parse_args()
    flaten_svg(args.input,args.output)

if __name__ == "__main__":
    main()