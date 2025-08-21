from reportlab.platypus import Paragraph, Frame, Image
from reportlab.lib.pagesizes import letter
from .shapes import shape_circle, shape_rectangle, shape_picture, shape_qrcode
from reportlab.lib.utils import ImageReader
from .flowable import LineDrawer, ParagraphD
from reportlab.lib.units import inch
import qrcode
from io import BytesIO

from .section import add_items


def generate_qr_code(data, size, bg_color='#FFFFFF', fg_color='#000000'):
    """Generate QR code and return as BytesIO buffer"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color=fg_color, back_color=bg_color)

    # Convert to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def substitute_template_variables(template_string, resume_data):
    """Replace template variables like {name}, {email} with actual data"""
    if not template_string or not isinstance(template_string, str):
        return template_string

    try:
        # Flatten resume data for easier access
        flat_data = {}
        if 'header' in resume_data:
            flat_data.update(resume_data['header'])

        # Add other common fields
        for key, value in resume_data.items():
            if isinstance(value, (str, int, float)):
                flat_data[key] = value

        return template_string.format(**flat_data)
    except (KeyError, ValueError) as e:
        # If substitution fails, return original string
        print(f"Template substitution error: {e}")
        return template_string


def draw_shapes_simple(objects, canvas, metadata):
    """Simple shape drawing from objects dict"""
    resume_data = metadata['resume']
    
    # Sort shapes by depth
    filtered_dict = {k: v for k, v in objects.items() 
                    if isinstance(v, (shape_rectangle, shape_circle, shape_picture, shape_qrcode))}
    sorted_shapes = sorted(filtered_dict.items(), key=lambda x: x[1].depth)
    
    for item_name, item in sorted_shapes:
        if item.type == 'rect':
            hex_color = item.background_color
            if hex_color is None:
                continue
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            canvas.setFillColorRGB(r/255, g/255, b/255)
            canvas.rect(item.left, item.top, item.width, item.height, stroke=0, fill=1)
            
        elif item.type == 'circle':
            hex_color = item.background_color
            if hex_color is None:
                continue
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            canvas.setFillColorRGB(r/255, g/255, b/255)
            canvas.circle(item.left, item.top, item.diameter, stroke=0, fill=1)
            
        elif item.type == 'qrcode':
            # Generate and draw QR code
            qr_data = substitute_template_variables(item.data, resume_data)
            qr_buffer = generate_qr_code(
                qr_data,
                item.size,
                item.background_color or '#FFFFFF',
                item.foreground_color or '#000000'
            )
            qr_image = ImageReader(qr_buffer)
            canvas.drawImage(qr_image, item.left, item.top, item.size, item.size, mask='auto')


def header_footer_page1(canvas, doc, metadata, styles):
    """Header/footer for first page"""
    # Draw shapes for page 1
    draw_shapes_simple(metadata['objects_page1'], canvas, metadata)
    
    # Set up objects for page 1
    metadata['objects'] = metadata['objects_page1']
    metadata['header'] = metadata['objects_page1']['header']
    metadata['footer'] = metadata['objects_page1']['footer']
    
    # Add full header
    add_header(canvas, doc, metadata, styles)
    
    # Add footer
    add_footer(canvas, doc, metadata, styles)
    
    # Switch to continuation template for next page
    if doc.page == 1:
        doc.handle_nextPageTemplate('ContinuationPage')


def header_footer_continuation(canvas, doc, metadata, styles):
    """Header/footer for continuation pages"""
    # Draw shapes for continuation pages
    draw_shapes_simple(metadata['objects_continuation'], canvas, metadata)
    
    # Set up objects for continuation
    metadata['objects'] = metadata['objects_continuation']
    metadata['header'] = metadata['objects_continuation'].get('header_cont')
    metadata['footer'] = metadata['objects_continuation'].get('footer_cont')
    
    # Add continuation header
    if 'continuation_header' in metadata['template']:
        add_continuation_header(canvas, doc, metadata, styles)
    
    # Add footer
    add_footer(canvas, doc, metadata, styles)


def add_header(canvas, doc, metadata, styles):
    """Add full header for page 1"""
    resume = metadata['resume']
    header = metadata['header']

    header_frame = Frame(header.left, header.top, header.width, header.height)

    # List of paragraphs (Flowable objects) for the header
    story = add_items(metadata['template']['global'], metadata['template']['header'], metadata['resume'], styles)

    # Calculate available width and starting height within the frame
    available_width = header_frame.width
    current_y = header_frame._y2
    
    # Draw each paragraph in the header frame on the canvas
    for flowable in story:
        flowable_width, flowable_height = flowable.wrap(header.width, header.height)
        flowable.drawOn(canvas, header_frame._x1, current_y)
        try:
            current_y -= flowable.style.leading + flowable.style.spaceAfter
        except:
            current_y -= flowable_height

    # Add profile picture if it exists
    if 'picture' in metadata['objects']:
        try:
            profile_image(metadata['objects']['picture'], resume['header']['picture'], canvas)
        except (KeyError, FileNotFoundError) as e:
            print(f"Could not load profile picture: {e}")

def add_continuation_header(canvas, doc, metadata, styles):
    """Add minimal header for continuation pages"""
    if 'continuation_header' not in metadata['template']:
        return  # No continuation header defined

    resume = metadata['resume']
    continuation_config = metadata['template']['continuation_header']

    # Use the continuation header frame
    if metadata.get('header'):
        header = metadata['header']
        header_frame = Frame(header.left, header.top, header.width, header.height)
    else:
        # Fallback frame if not defined
        header_frame = Frame(
            0.25 * inch,
            (11 - 0.75) * inch,
            (8.5 - 0.5) * inch,
            0.75 * inch
        )

    # Pass the header data directly to add_items
    # The key is that we're passing the actual data, not wrapped in another dict
    story = add_items(
        metadata['template']['global'],
        continuation_config,
        metadata['resume']['header'],  # Pass header data directly
        styles
    )

    # Draw continuation header elements
    current_y = header_frame._y2
    for flowable in story:
        flowable_width, flowable_height = flowable.wrap(header_frame.width, header_frame.height)
        flowable.drawOn(canvas, header_frame._x1, current_y)
        try:
            # Move down for next element
            current_y -= flowable.style.leading + flowable.style.spaceAfter
        except AttributeError:
            # For non-paragraph flowables (like LineDrawer)
            current_y -= flowable_height


def profile_image(object, image_path, c):
    """Draw profile image with optional circle mask"""
    try:
        image = ImageReader(image_path)
    except (IOError, FileNotFoundError) as e:
        print(f"Warning: Could not load profile image from {image_path}: {e}")
        return  # Gracefully handle missing image
    
    image_width, image_height = image.getSize()
    aspect_ratio = image_width / image_height
    new_width = object.max_width
    new_height = new_width / aspect_ratio

    # Determine the diameter of the circle to be the smaller of the new dimensions
    circle_diameter = min(new_width, new_height)

    # Position for the image
    xpos, ypos = object.left, object.top

    if object.mask == 'circle':
        # Draw a circle mask
        c.saveState()
        path = c.beginPath()
        # Position the circle to be centered over the image
        path.circle(xpos + new_width / 2, ypos + new_height / 2, circle_diameter / 2)
        c.clipPath(path, stroke=0, fill=0)
        c.drawImage(image, xpos, ypos, new_width, new_height, mask='auto')
        c.restoreState()
    else:
        c.drawImage(image, xpos, ypos, new_width, new_height, mask='auto')


def add_footer(canvas, doc, metadata, styles):
    """Add footer to any page"""
    resume = metadata['resume']
    footer = metadata['footer']
    
    if not footer:
        return  # No footer defined
    
    frame = Frame(footer.left, footer.top, footer.width, footer.height)

    hex_color = footer.background_color
    if hex_color == None:
        r = g = b = 0
    else:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
    
    # Convert to normalized RGB
    r_normalized = r / 255
    g_normalized = g / 255
    b_normalized = b / 255

    # List of paragraphs (Flowable objects) for the footer
    story = [
        LineDrawer(5, styles['footer_Heading1'].textColor, frame),
        Paragraph(f"Page {doc.page} of {metadata['pages']} ", styles['footer_Text']),
    ]

    # Calculate available width and starting height within the frame
    current_y = frame._y2
    
    # Draw each paragraph in the footer frame on the canvas
    for flowable in story:
        flowable_width, flowable_height = flowable.wrap(footer.width, footer.height)
        try:
            current_y -= flowable.style.leading + flowable.style.spaceAfter
        except:
            current_y -= flowable_height
        flowable.drawOn(canvas, frame._x1, current_y)


# Keep the old header_footer function for backward compatibility if needed
def header_footer(canvas, doc, metadata, styles):
    """Legacy header/footer function - redirects to appropriate page handler"""
    if doc.page == 1:
        header_footer_page1(canvas, doc, metadata, styles)
    else:
        header_footer_continuation(canvas, doc, metadata, styles)