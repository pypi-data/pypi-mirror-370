import yaml
import subprocess
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.lib import fonts
from reportlab.pdfbase import pdfmetrics




def find_font_file(font_name, font_style="Regular"):
    try:
        command = ["fc-list"]
        if font_name:
            command.extend(["|", "grep", font_name, "-i"])
        if font_style:
            command.extend(["|", "grep", font_style, "-i"])
        command.extend(["|", "cut", "-d", ":", "-f", "1"])
        
        #print(" ".join(command))
        output = subprocess.check_output(" ".join(command), shell=True).decode("utf-8").strip()
        return output
    except subprocess.CalledProcessError:
        print(f"Error: Unable to find font file for '{font_name}'")
        return None    


# Mapping for text alignment to be used in style conversion
alignment_mapping = {
    'TA_LEFT': TA_LEFT,
    'TA_CENTER': TA_CENTER,
    'TA_RIGHT': TA_RIGHT,
    'TA_JUSTIFY': TA_JUSTIFY
}
def create_styles(style_data):
    default_styles = getSampleStyleSheet()  # This gets the default styles
    custom_styles = {}
    
    for style_name, style_attrs in style_data.items():
        # If there's a parent style specified, try to find it in custom styles first
        if 'parent' in style_attrs:
            parent_style_name = style_attrs.pop('parent')  # Remove the parent from attrs
            parent_style = custom_styles.get(parent_style_name)
            if parent_style is None:
                parent_style = default_styles.get(parent_style_name)
            if parent_style is None:
                raise ValueError(f"Parent style '{parent_style_name}' not found in stylesheet")
        else:
            parent_style = None

        # Convert alignment value to ReportLab enum
        if 'alignment' in style_attrs:

            if isinstance(style_attrs['alignment'], str):
                alignment = style_attrs['alignment'].upper()
                if alignment in alignment_mapping:
                    style_attrs['alignment'] = alignment_mapping[alignment]
                else:
                    raise ValueError(f"Invalid alignment value '{alignment}'")
            else:
                alignment = style_attrs['alignment']



        # Check if font name is provided in the style attributes
        if 'fontName' in style_attrs:
            font_name = style_attrs['fontName']
            font_style= style_attrs['fontStyle']
            font_file = style_attrs.get('fontFile')  # Check if font file is provided
            #if font_file==None:
            #    font_file=find_font_file(font_name,font_style)
            #if font_file:
            #    print ("Font:",font_name,font_file)
                # Register font using pdfmetrics
                #pdfmetrics.registerTypeFace(pdfmetrics.EmbeddedType1Face(font_file, font_file))
                #pdfmetrics.registerFont(pdfmetrics.Font(font_name, faceName, 'WinAnsiEncoding'))
         
        # Create the custom style, ensuring that 'parent' is an actual ParagraphStyle object
        custom_styles[style_name] = ParagraphStyle(name=style_name, parent=parent_style, **style_attrs)
        bold=None
        if 'bold' in style_attrs and style_attrs['bold']:
            bold=True
        custom_styles[style_name].bold=bold

    return custom_styles