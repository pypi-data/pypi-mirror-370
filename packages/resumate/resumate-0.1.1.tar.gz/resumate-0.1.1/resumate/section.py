from datetime import datetime
from .flowable import ParagraphD,LineDrawer,SpacerD, SVGRRowD,SVGFlowableD,SingleWordD,RatingFlowable
from reportlab.platypus import KeepTogether
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import copy

from .common import _eval_with_units
from .common import ucfirst, get_style




def calculate_section_height(flowables, available_width):
    """Calculate the total height of a section's flowables with more accurate measurements"""
    total_height = 0
    page_width, page_height = letter

    for flowable in flowables:
        try:
            # Wrap gives us width & height (already includes spacing if style exists)
            width, height = flowable.wrap(available_width, page_height)
            total_height += height
        except AttributeError:
            if hasattr(flowable, 'height'):
                total_height += flowable.height
            else:
                total_height += 8  # fallback estimate

    return total_height

def add_section(base, section, data, styles, frame_height=None):
    pdf_object = []
    name = section['name']

    if base['heading']['upper']:
        heading = section['name'].upper()
    else:
        heading = ucfirst(section['name'])

    style = get_style(name, 'Heading1', styles)
    header = []

    if 'svg' in section:
        pdf_object.append(SVGFlowableD(section['svg'], heading, style, placement="right", size=.25 * inch))
    else:
        pdf_object.append(ParagraphD(heading, style))

    pdf_object.append(LineDrawer(5, style.textColor))
    pdf_object.extend(add_items(base, section, data, styles,frame_height=500))

    ## Add the spacing gap at the end
    pdf_object.append(SpacerD(1, 20))

    # Use frame height directly for keep_together logic
    if 'keep_together' in section and section['keep_together'] == True:
        # Use the actual frame height if provided, otherwise fall back to reasonable default
        if frame_height:
            available_height = frame_height
        else:
            # Conservative fallback if frame height not available
            page_width, page_height = letter
            available_height = page_height * 0.7  # Conservative estimate
        
        # Calculate section height
        page_width, page_height = letter
        available_width = page_width * 0.66  # Assume wide column width  
        section_height = calculate_section_height(pdf_object, available_width)

        # Only use KeepTogether if section fits in 90% of frame height
        #if section_height <= available_height :
        #    
        return [KeepTogether(pdf_object)]
        #else:
         #   # Section is too large, let it flow naturally
         #   print(f"Section '{name}' too large for KeepTogether: {section_height:.1f}pt > {available_height * 0.9:.1f}pt")
          #  return pdf_object
    else:
        return pdf_object


def add_items(base, section, data, styles, frame_height=None):
    pdf_object = []
    name = section['name']

    # Check if this is a special case where data is passed directly (like continuation_header)
    # In this case, the data IS the content, not a wrapper
    if section['type'] == 'text':
        # If the section name exists as a key in data, use th
        # Otherwise, assume data itself contains the fields directly
        if name in data:
            pdf_object.extend(add_item(base, section, data[name], styles, name))
        else:
            # Data is passed directly (like for continuation_header)
            pdf_object.extend(add_item(base, section, data, styles, name))
    elif section['type'] == 'ratings':
        
        # Get rating configuration from section
        rating_config = section.get('rating_config', {})
        max_rating = rating_config.get('max_rating', 5)
        rating_style_type = rating_config.get('rating_style', 'bars')
        icon_size = _eval_with_units(rating_config.get('icon_size', '0.25 inch'))
        bar_width = rating_config.get('bar_width', 10)
        bar_height = rating_config.get('bar_height', 3)
        bar_spacing = rating_config.get('bar_spacing', 2)
        filled_color = rating_config.get('filled_color', '#007ACC')
        empty_color = rating_config.get('empty_color', '#E0E0E0')
        layout = rating_config.get('layout', 'icon_rating_text')  # New layout option
        
        # Convert colors if needed
        if isinstance(filled_color, str):
            filled_color = colors.HexColor(filled_color)
        if isinstance(empty_color, str):
            empty_color = colors.HexColor(empty_color)
        
        # Process each category of skills
        if name in data:
            for category_item in data[name]:
                # Add category header if it exists
                if 'category' in category_item:
                    category_style = get_style(name, 'Heading3', styles)
                    pdf_object.append(ParagraphD(category_item['category'], category_style))
                    pdf_object.append(SpacerD(1, 2))
                
                # Create rating row for skills in this category
                if 'skills' in category_item:
                    rating_array = []
                    for skill in category_item['skills']:
                        # Handle different skill formats
                        if isinstance(skill, dict):
                            skill_name = skill.get('name', '')
                            skill_rating = skill.get('rating', max_rating)
                            skill_svg = skill.get('svg', skill_name.lower().replace(' ', '').replace('#', 'sharp'))
                        elif isinstance(skill, str):
                            # Simple string format - use skill name for both text and svg lookup
                            skill_name = skill
                            skill_rating = max_rating  # Default to max rating
                            # Clean up the name for SVG lookup
                            skill_svg = skill.lower().replace(' ', '').replace('#', 'sharp').replace('+', 'plus').replace('/', '').replace('.', '')
                        else:
                            continue
                        
                        # Create rating flowable for each skill with vertical layout
                        rating_flowable = RatingFlowable(
                            svg_file=skill_svg,
                            text=skill_name,
                            rating=skill_rating,
                            max_rating=max_rating,
                            style=get_style(name, 'Text', styles),
                            icon_size=icon_size,
                            rating_style=rating_style_type,
                            padding=2,  # 10px padding as requested
                            filled_color=filled_color,
                            empty_color=empty_color,
                            bar_width=bar_width,
                            bar_height=bar_height,
                            bar_spacing=bar_spacing,
                            layout=layout,  # Use the vertical layout
                            debug=False
                        )
                        rating_array.append(rating_flowable)
                    
                    if rating_array:
                        rating_row = SVGRRowD(rating_array)
                        pdf_object.append(rating_row)
                        pdf_object.append(SpacerD(1, 5))

    elif section['type'] == 'array':
        block = []
        if name in data:
            for item in data[name]:
                # For array items, use frame height directly
                item_flowables = add_item(base, section, item, styles, name)

                # Use frame height if available, otherwise conservative fallback
                if frame_height:
                    available_height = frame_height
                else:
                    page_width, page_height = letter
                    available_height = page_height * 0.7

                # Calculate item height
                page_width, page_height = letter
                available_width = page_width * 0.66  # Assume wide column width
                item_height = calculate_section_height(item_flowables, available_width)

#                # Use 80% of frame height for individual items
#                if item_height <= (available_height * 0.8):
#                    pdf_object.extend([KeepTogether(item_flowables)])
#                else:
#                    # Let large items flow naturally
#                    print(f"Array item in '{name}' flowing naturally: {item_height:.1f}pt > {available_height * 0.8:.1f}pt")
                pdf_object.extend(item_flowables)
        else:
            # Handle case where data might be the array itself
            if isinstance(data, list):
                for item in data:
                    item_flowables = add_item(base, section, item, styles, name)

                    # Use frame height if available
                    if frame_height:
                        available_height = frame_height
                    else:
                        page_width, page_height = letter
                        available_height = page_height * 0.7

                    # Calculate item height
                    page_width, page_height = letter
                    available_width = page_width * 0.66
                    item_height = calculate_section_height(item_flowables, available_width)

                    pdf_object.extend(item_flowables)

    elif section['type'] == 'object':
        if name in data:
            pdf_object.extend(add_item(base, section, data[name], styles, name))
        else:
            # Data is passed directly
            pdf_object.extend(add_item(base, section, data, styles, name))

    return pdf_object

def convert_data(data):
    # Create a deep copy of the original data
    data_copy = copy.deepcopy(data)

    # Recursive function to traverse nested structures
    def _convert(item):
        if isinstance(item, dict):
            for key, value in item.items():
                item[key] = _convert(value)
            return item
        elif isinstance(item, list):
            for i, value in enumerate(item):
                item[i] = _convert(value)
            return item
        elif isinstance(item, str):
            try:
                datetime_obj = datetime.strptime(item, "%Y-%m-%d")
                return datetime_obj.date()
            except ValueError:
                return item
        else:
            return item

    # Call the recursive function on the copied data
    return _convert(data_copy)

def add_item(base, section, data, styles, name):
    pdf_object = []
    object_type = ParagraphD

    data_copy = convert_data(data)

    for item in section['format']:
        style = get_style(name, item['style'], styles)
        bold = None
        color = None

        if 'padding' in item:
            padding = item['padding']
        else:
            padding = 2

        if 'color' in item:
            color = item['color']

        height = 0
        width = 0
        if 'width' in item:
            width = item['width']
        if 'height' in item:
            height = item['height']

        if item['type'] == "spacer":
            pdf_object.append(SpacerD(width, height))

        elif item['type'] == "line":
            line_height = item.get('data', 5)
            pdf_object.append(LineDrawer(line_height, style.textColor, frame=None))

        elif item['type'] == "qrcode":
            from .flowable import QRCodeFlowable
            qr_data = item['data']

            # Handle different data formats
            if isinstance(qr_data, str):
                # Check if it's a format string with template variables
                if '{' in qr_data and '}' in qr_data:
                    try:
                        # For format strings, substitute with available data
                        qr_data = qr_data.format(**data_copy)
                    except KeyError as e:
                        print(f"QR format key error: {e}")
                        # If format fails, check if it's a direct field reference
                        if qr_data in data_copy:
                            qr_data = str(data_copy[qr_data])
                        else:
                            print(f"Warning: Could not resolve QR data '{qr_data}'")
                # Check if it's a direct field reference (no brackets)
                elif qr_data in data_copy:
                    qr_data = str(data_copy[qr_data])

            qr_size = _eval_with_units(item.get('size', '0.75 inch'))
            pdf_object.append(QRCodeFlowable(qr_data, qr_size))

        elif item['type'] == "rating":
                    from reportlab.lib import colors
                    
                    # Get the rating data
                    rating_value = 0
                    rating_text = ""
                    svg_file = None
                    
                    # Handle different data configurations
                    if 'data' in item:
                        if isinstance(item['data'], dict):
                            # Complex rating with multiple fields
                            rating_field = item['data'].get('rating_field', 'rating')
                            text_field = item['data'].get('text_field', 'name')
                            svg_field = item['data'].get('svg_field', None)
                            
                            if rating_field in data_copy:
                                rating_value = data_copy[rating_field]
                            if text_field in data_copy:
                                rating_text = str(data_copy[text_field])
                            if svg_field and svg_field in data_copy:
                                svg_file = data_copy[svg_field]
                        elif isinstance(item['data'], str):
                            # Simple rating - data field contains the rating value
                            if item['data'] in data_copy:
                                # Check if it's a dict with rating info
                                if isinstance(data_copy[item['data']], dict):
                                    rating_value = data_copy[item['data']].get('rating', 0)
                                    rating_text = data_copy[item['data']].get('name', '')
                                    svg_file = data_copy[item['data']].get('svg', None)
                                else:
                                    rating_value = data_copy[item['data']]
                            # Use the field name as text if no text specified
                            rating_text = item.get('text', item['data'])
                    
                    # Override with explicit values if provided
                    if 'rating' in item:
                        rating_value = item['rating']
                    if 'text' in item:
                        rating_text = item['text']
                    if 'svg' in item:
                        svg_file = item['svg']
                    
                    # Get configuration options
                    max_rating = item.get('max_rating', 5)
                    rating_style_type = item.get('rating_style', 'bars')
                    icon_size = _eval_with_units(item.get('icon_size', '0.3 inch'))
                    bar_width = item.get('bar_width', 15)
                    bar_height = item.get('bar_height', 4)
                    bar_spacing = item.get('bar_spacing', 3)
                    debug = item.get('debug', False)
                    
                    # Handle colors
                    filled_color = colors.black
                    empty_color = colors.lightgrey
                    
                    if 'filled_color' in item:
                        if isinstance(item['filled_color'], str):
                            filled_color = colors.HexColor(item['filled_color'])
                        else:
                            filled_color = item['filled_color']
                    
                    if 'empty_color' in item:
                        if isinstance(item['empty_color'], str):
                            empty_color = colors.HexColor(item['empty_color'])
                        else:
                            empty_color = item['empty_color']
                    
                    # Create the rating flowable
                    rating_flowable = RatingFlowable(
                        svg_file=svg_file,
                        text=rating_text,
                        rating=rating_value,
                        max_rating=max_rating,
                        style=style,
                        icon_size=icon_size,
                        rating_style=rating_style_type,
                        padding=padding,
                        filled_color=filled_color,
                        empty_color=empty_color,
                        bar_width=bar_width,
                        bar_height=bar_height,
                        bar_spacing=bar_spacing,
                        debug=debug
                    )
                    
                    pdf_object.append(rating_flowable)

        elif item['type'] == "ratingrow":
            from .flowable import RatingFlowable
            from reportlab.lib import colors
            
            rating_array = []
            
            # Get configuration options with defaults
            max_rating = item.get('max_rating', 5)
            rating_style_type = item.get('rating_style', 'bars')
            icon_size = _eval_with_units(item.get('icon_size', '0.3 inch'))
            bar_width = item.get('bar_width', 15)
            bar_height = item.get('bar_height', 4)
            bar_spacing = item.get('bar_spacing', 3)
            debug = item.get('debug', False)
            
            # Handle colors
            filled_color = colors.black
            empty_color = colors.lightgrey
            
            if 'filled_color' in item:
                if isinstance(item['filled_color'], str):
                    filled_color = colors.HexColor(item['filled_color'])
            
            if 'empty_color' in item:
                if isinstance(item['empty_color'], str):
                    empty_color = colors.HexColor(item['empty_color'])
            
            # Get the list of ratings
            if item['data'] in data_copy and isinstance(data_copy[item['data']], list):
                ratings = data_copy[item['data']]
            else:
                ratings = []
            
            for rating_item in ratings:
                # Handle different rating item formats
                if isinstance(rating_item, dict):
                    svg_file = rating_item.get('svg', rating_item.get('name', ''))
                    text = rating_item.get('name', '')
                    rating_value = rating_item.get('rating', 0)
                else:
                    # Simple format: just the name, assume full rating
                    svg_file = rating_item
                    text = rating_item
                    rating_value = max_rating
                
                rating_flowable = RatingFlowable(
                    svg_file=svg_file,
                    text=text,
                    rating=rating_value,
                    max_rating=max_rating,
                    style=style,
                    icon_size=icon_size,
                    rating_style=rating_style_type,
                    padding=padding,
                    filled_color=filled_color,
                    empty_color=empty_color,
                    bar_width=bar_width,
                    bar_height=bar_height,
                    bar_spacing=bar_spacing,
                    debug=debug
                )
                
                rating_array.append(rating_flowable)
            
            if rating_array:  # Only add if we have items
                rating_row = SVGRRowD(rating_array)
                pdf_object.append(rating_row)

        elif item['type'] == "string":
            if item['data'] in data_copy:
                pdf_object.append(object_type(str(data_copy[item['data']]), style))
            else:
                print(f"Warning: Field '{item['data']}' not found in data for section '{name}'")

        elif item['type'] == "format":
            try:
                formatted_text = str(item['data'].format(**data_copy))
                pdf_object.append(object_type(formatted_text, style))
            except KeyError as e:
                print(f"Format error in {name}: Missing key {e} in template '{item['data']}'")
                pdf_object.append(object_type(item['data'], style))
            except Exception as e:
                print(f"Format error in {name}: {e}")
                pdf_object.append(object_type(item['data'], style))

        elif item['type'] == "list":
            style.leftIndent = style.fontSize * 2

            if isinstance(data_copy, str):
                pdf_object.append(object_type(data_copy, style, bulletText=base['list']['bullet_style']))
            elif item['data'] in data_copy and isinstance(data_copy[item['data']], list):
                for i, value in enumerate(data_copy[item['data']]):
                    if isinstance(value, dict):
                        try:
                            formatted_value = value.format(**data_copy)
                        except:
                            formatted_value = str(value)
                    else:
                        formatted_value = str(value)
                    pdf_object.append(object_type(formatted_value, style, bulletText=base['list']['bullet_style']))

        elif item['type'] == "svg":
            if item['data'] in data_copy:
                pdf_object.append(SVGFlowableD(
                    item['svg'],
                    str(data_copy[item['data']]),
                    style,
                    item['placement'],
                    _eval_with_units(item['size']),
                    color=color,
                    padding=padding,
                    debug=None
                ))

        elif item['type'] == "svgrow":
            svg_array = []
            svg_size = _eval_with_units(item['svg_size'])
            placement = item['placement']

            # Get the list of items for the SVG row
            if item['data'] in data_copy and isinstance(data_copy[item['data']], list):
                items = data_copy[item['data']]
            else:
                items = []

            for svg_item in items:
                svg_flowable = SVGFlowableD(svg_item, svg_item, style, placement, svg_size, padding)
                # Only add if the SVG was successfully created
                if svg_flowable.drawing is not None or svg_flowable.text:
                    svg_array.append(svg_flowable)
            
            if svg_array:  # Only add if we have items
                svgRow = SVGRRowD(svg_array)
                pdf_object.append(svgRow)

    return pdf_object