import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate, FrameBreak, PageBreak, PageTemplate, Frame

from .pdf_metadata import load_page_template_metadata, create_combined_template, calculate_objects
from .flowable import clear_rendered_details, get_rendered_details
from .section import add_section
from .styles import create_styles

def generate_pdf(resume_data, pdf_file, metadata_file):
    """
    Generate a PDF file from resume data using the specified page template metadata.
    """
    # Load page template metadata
    metadata = load_page_template_metadata(metadata_file)
    metadata['resume'] = resume_data

    # Calculate objects for both page types
    metadata['objects_page1'] = calculate_objects(
        metadata['frames_page1'],
        metadata['shapes_page1'],
        metadata.get('picture')
    )

    metadata['objects_continuation'] = calculate_objects(
        metadata['frames_continuation'],
        metadata['shapes_continuation']
    )

    # Create styles
    styles = create_styles(metadata['styles'])

    margin = 0

    # Process columns and build content
    column_index = 0
    all_pages = {}

    for column_name in sorted(metadata['template']['columns'], key=lambda x: metadata['template']['columns'][x]['order']):
        clear_rendered_details()  # Clear state for this column
        all_pages[column_name] = []
        flowables = []

        # Create in-memory buffer for this column
        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer,
                            pagesize=letter,
                            rightMargin=margin, leftMargin=margin,
                            topMargin=margin, bottomMargin=margin,
                            showBoundary=False)

        # Get the frame from already calculated objects
        if column_index == 0:  # wide column
            frame_obj = metadata['objects_page1']['wide_column']
        else:  # small column
            frame_obj = metadata['objects_page1']['small_column']

        # Use the pre-calculated frame dimensions
        frame = Frame(frame_obj.left, frame_obj.top, frame_obj.width, frame_obj.height)
        template = PageTemplate(id=column_name, frames=[frame])
        doc.addPageTemplates(template)

        column_index += 1

        base = metadata['template']['global']
        column = metadata['template']['columns'][column_name]

        try:
            for section_name in sorted(column['sections'], key=lambda x: column['sections'][x]['order']):
                section = column['sections'][section_name]
                section['name'] = section_name
                data = {section_name: metadata['resume'][section_name]}
                flowables.extend(add_section(base, section, data, styles,frame_height=frame_obj.height))
        except Exception as ex:
            print("Error: ", ex)

        # Build this column
        doc.build(flowables)
        buffer.close()
        
        # Get the captured details after building
        rendered_details = get_rendered_details()
        
        # Process rendered details into pages (with debug info)
        if len(rendered_details) > 0:
            column = []
            previous_y = rendered_details[0]['y']

            for idx, item in enumerate(rendered_details):
                y = item['y']

                # detect new page
                if y > previous_y:
                    all_pages[column_name].append(column)
                    column = []

                previous_y = y
                column.append(item['flowable'])

            # commit last page
            if len(column) > 0:
                all_pages[column_name].append(column)


    # Merge all pages
    merged_pages = []
    max_length = max(len(all_pages[columns]) for columns in all_pages) if all_pages else 0

    for i in range(max_length):
        page = {}
        for column_name in all_pages:
            column = all_pages[column_name]
            page[column_name] = column[i] if i < len(column) else []
        merged_pages.append(page)

    # Build the final PDF
    metadata['pages'] = len(merged_pages)
    pdf_build(pdf_file, margin, merged_pages, metadata)

def pdf_build(pdf_file, margin, merged_pages, metadata):
    """Build PDF with two-template system"""
    # Create PDF document
    doc = BaseDocTemplate(pdf_file,
                         pagesize=letter,
                         rightMargin=margin, leftMargin=margin,
                         topMargin=margin, bottomMargin=margin,
                         showBoundary=False)

    elements = []
    page_index = 0

    for page in merged_pages:
        for column in page:
            for item in page[column]:
                elements.append(item)
            elements.append(FrameBreak())
        page_index += 1

    # Create both page templates
    page_template1, page_template_continuation = create_combined_template(metadata)

    # Add both templates to document
    doc.addPageTemplates([page_template1, page_template_continuation])

    doc.build(elements)