from reportlab.lib.pagesizes import letter
from reportlab.platypus import Frame, PageTemplate
from functools import partial

import yaml
from .template_loader import template_loader
from .header import header_footer_page1, header_footer_continuation
from .styles import create_styles
from .common import _eval_with_units

from .shapes import shape_circle, shape_rectangle, shape_picture, shape_qrcode


def load_page_template_metadata(template_identifier):
    """
    Load page template metadata from a template name or file path.
    
    Args:
        template_identifier: Template name (for built-in) or path to template file
        
    Returns:
        Template metadata dictionary
    """
    # Use the template loader to get template data
    metadata = template_loader.get_template(template_identifier)
    return metadata

def load_resume_from_yaml(yaml_file):
    """Load resume data from a YAML file."""
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def load_page_template_metadata(metadata_file):
    """Load page template metadata from a YAML file."""
    with open(metadata_file, 'r') as file:
        metadata = yaml.safe_load(file)
    return metadata.get('page_template', {})

def calculate_objects(frame_list, shape_list, picture_config=None):
    """Calculate objects for a specific page type"""
    objects = {}
    
    # Process frames
    for item in frame_list:
        x1 = _eval_with_units(item.get('left', '0'), objects)
        y1 = _eval_with_units(item.get('top', '0'), objects)
        width = _eval_with_units(item.get('width', '0'), objects)
        height = _eval_with_units(item.get('height', '0'), objects)
        item_id = item.get('id', '')
        bg_color = item.get('background_color', None)
        objects[item_id] = shape_rectangle(item_id, x1, y1, width, height, bg_color)
    
    # Process shapes
    for item in shape_list:
        item_id = item.get('id', '')
        item_type = item.get('type', '')

        if item_type == 'rect':
            x1 = _eval_with_units(item.get('left', '0'), objects)
            y1 = _eval_with_units(item.get('top', '0'), objects)
            width = _eval_with_units(item.get('width', '0'), objects)
            height = _eval_with_units(item.get('height', '0'), objects)
            bg_color = item.get('background_color', None)
            depth = item.get('depth', 0)
            objects[item_id] = shape_rectangle(item_id, x1, y1, width, height, bg_color, depth)

        elif item_type == 'circle':
            x1 = _eval_with_units(item.get('left', '0'), objects)
            y1 = _eval_with_units(item.get('top', '0'), objects)
            diameter = _eval_with_units(item.get('diameter', '0'), objects)
            bg_color = item.get('background_color', None)
            depth = item.get('depth', 0)
            objects[item_id] = shape_circle(item_id, x1, y1, diameter, bg_color, depth)

        elif item_type == 'qrcode':
            x1 = _eval_with_units(item.get('left', '0'), objects)
            y1 = _eval_with_units(item.get('top', '0'), objects)
            size = _eval_with_units(item.get('size', '0'), objects)
            data = item.get('data', '')
            bg_color = item.get('background_color', '#FFFFFF')
            fg_color = item.get('foreground_color', '#000000')
            depth = item.get('depth', 0)
            objects[item_id] = shape_qrcode(item_id, x1, y1, size, data, bg_color, fg_color, depth)
    
    # Process picture if provided
    if picture_config:
        item = picture_config
        x1 = _eval_with_units(item.get('left', '0'), objects)
        y1 = _eval_with_units(item.get('top', '0'), objects)
        max_width = _eval_with_units(item.get('max_width', '0'), objects)
        max_height = _eval_with_units(item.get('max_height', '0'), objects)
        mask = item.get('mask', 'circle')
        item_id = item.get('id', '')
        bg_color = item.get('background_color', None)
        depth = item.get('depth', 0)
        objects[item_id] = shape_picture(item_id, x1, y1, max_width, max_height, mask, bg_color, depth)
    
    return objects

def create_page_template(metadata):
    """Create page templates for both page types"""
    styles = create_styles(metadata['styles'])
    
    # Calculate objects for page 1
    objects_page1 = calculate_objects(
        metadata['frames_page1'],
        metadata['shapes_page1'],
        metadata.get('picture')
    )
    
    # Calculate objects for continuation pages
    objects_continuation = calculate_objects(
        metadata['frames_continuation'],
        metadata['shapes_continuation']
    )
    
    # Create frames for page 1
    frames = []
    page_templates = []
    
    for frame_data in metadata['frames_page1']:
        frame_id = frame_data.get('id', '')
        shape = objects_page1[frame_id]
        if frame_id in ['header', 'footer']:
            continue
        frame = Frame(shape.left, shape.top, shape.width, shape.height, id=shape.id)
        frames.append(frame)
        page_templates.append(PageTemplate(id=frame_id, frames=frame, pagesize=letter))
    
    metadata['header'] = objects_page1['header']
    metadata['footer'] = objects_page1['footer']
    metadata['objects_page1'] = objects_page1
    metadata['objects_continuation'] = objects_continuation
    
    return [objects_page1, page_templates, styles]

def create_combined_template(metadata):
    """Create combined template with separate page layouts"""
    styles = create_styles(metadata['styles'])

    # Calculate objects for both page types
    objects_page1 = calculate_objects(
        metadata['frames_page1'],
        metadata['shapes_page1'],
        metadata.get('picture')
    )

    objects_continuation = calculate_objects(
        metadata['frames_continuation'],
        metadata['shapes_continuation']
    )

    # Store objects in metadata for access by header/footer functions
    metadata['objects_page1'] = objects_page1
    metadata['objects_continuation'] = objects_continuation

    # Create frames for page 1 - order matters for flow!
    frames_page1 = []
    # Add wide column first
    wide_shape = objects_page1['wide_column']
    wide_frame = Frame(wide_shape.left, wide_shape.top, wide_shape.width, wide_shape.height, id='wide_column')
    frames_page1.append(wide_frame)
    
    # Add small column second
    small_shape = objects_page1['small_column']
    small_frame = Frame(small_shape.left, small_shape.top, small_shape.width, small_shape.height, id='small_column')
    frames_page1.append(small_frame)

    # Create frames for continuation pages - same order!
    frames_continuation = []
    # Add wide column first
    wide_cont_shape = objects_continuation['wide_column_cont']
    wide_cont_frame = Frame(wide_cont_shape.left, wide_cont_shape.top, wide_cont_shape.width, wide_cont_shape.height, id='wide_column_cont')
    frames_continuation.append(wide_cont_frame)
    
    # Add small column second
    small_cont_shape = objects_continuation['small_column_cont']
    small_cont_frame = Frame(small_cont_shape.left, small_cont_shape.top, small_cont_shape.width, small_cont_shape.height, id='small_column_cont')
    frames_continuation.append(small_cont_frame)

    # Create page templates with multiple frames
    page_template1 = PageTemplate(
        id='FirstPage',
        frames=frames_page1,  # Multiple frames in order
        pagesize=letter,
        onPage=partial(header_footer_page1, metadata=metadata, styles=styles)
    )

    page_template_continuation = PageTemplate(
        id='ContinuationPage',
        frames=frames_continuation,  # Multiple frames in order
        pagesize=letter,
        onPage=partial(header_footer_continuation, metadata=metadata, styles=styles)
    )

    return page_template1, page_template_continuation