import yaml

from .shapes import shape_circle, shape_picture, shape_rectangle, shape_qrcode, frame
import pprint


class global_settings:
    def __init__(self, bold, upper, debug):
        self.bold = bold
        self.upper = upper
        self.debug = debug


class column:
    def __init__(self, name, keep_together, column_type):
        self.name = name
        self.keep_together = keep_together
        self.column_type = column_type
        self.data = []
        self.format = []


class template:
    def __init__(self, template_file):
        self.template_file = template_file
        self.metadata = {}
        self.styles = {}
        self.template = {}
        self.column_wide = {}
        self.column_small = {}
        self.footer_dark = False
        self.header_dark = True
        self.even_column_dark = False
        self.odd_column_dark = False
        self.icons = {
            'Home': 'submodules/fluentui-system-icons/assets/Home/SVG/ic_fluent_home_16_filled.svg',
            'Location': 'submodules/fluentui-system-icons/assets/Location/SVG/ic_fluent_location_16_filled.svg',
            'Calendar': 'submodules/fluentui-system-icons/assets/Calendar/ic_fluent_calendar_16_filled.svg',
            'Mail': 'submodules/fluentui-system-icons/assets/Mail/SVG/ic_fluent_mail_16_filled.svg',
            'Person': 'submodules/fluentui-system-icons/assets/Person/SVG/ic_fluent_person_16_filled.svg',
            'Building': 'submodules/fluentui-system-icons/assets/Building/SVG/ic_fluent_building_16_filled.svg',
            'Phone': 'submodules/fluentui-system-icons/assets/Phone/SVG/ic_fluent_phone_16_filled.svg',
            'Position': 'submodules/fluentui-system-icons/assets/Trophy/SVG/ic_fluent_trophy_16_filled.svg',
            'Briefcase': 'submodules/fluentui-system-icons/assets/Briefcase/SVG/ic_fluent_briefcase_16_filled.svg',
            'Certificate': 'submodules/fluentui-system-icons/assets/Certificate/SVG/ic_fluent_certificate_16_filled.svg',
            'Graduation': 'submodules/fluentui-system-icons/assets/Hat Graduation Sparkle/SVG/ic_fluent_hat_graduation_sparkle_16_filled.svg',
            'Code': 'submodules/fluentui-system-icons/assets/Code/SVG/ic_fluent_code_16_filled.svg',
            'Cog': 'submodules/fluentui-system-icons/assets/Settings Cog Multiple/SVG/ic_fluent_settings_cog_multiple_20_filled.svg',
            'Trophy': 'submodules/fluentui-system-icons/assets/Trophy/SVG/ic_fluent_trophy_16_filled.svg',
            'Access': 'submodules/fluentui-system-icons/assets/Accessibility/SVG/ic_fluent_accessibility_16_filled.svg',
            'Fingerprint': 'submodules/fluentui-system-icons/assets/Fingerprint/SVG/ic_fluent_fingerprint_16_filled.svg',
        }

        self.theme = {
            'text_light': '#545454',
            'text_dark': '#FFFFFF',
            'bg_light': '#FFFFFF',
            'bg_dark': '#545454'
        }

        fonts = [
            'Courier',
            'Courier-Bold',
            'Courier-Oblique',
            'Courier-BoldOblique',
            'Helvetica',
            'Helvetica-Bold',
            'Helvetica-Oblique',
            'Helvetica-BoldOblique',
            'Times-Roman',
            'Times-Bold',
            'Times-Italic',
            'Times-BoldItalic',
            'Symbol',
            'ZapfDingbats',
        ]

        self.base_template = {
            'fontName': 'Helvetica',
            'fontSize': 12,
            'fontStyle': 'Light',
            'leading': 14,
            'alignment': 'TA_LEFT',
            'spaceAfter': 4,
            'bulletIndent': 6,
        }

        self.heading_templates = {
            'Title': {'fontSize': 20, 'leading': 20, 'spaceAfter': 10, 'bold': True, 'upper': True},
            'Heading1': {'fontSize': 13, 'leading': 13, 'spaceAfter': 5, 'bold': True, 'upper': True},
            'Heading2': {'fontSize': 10, 'leading': 10, 'spaceAfter': 3, 'bold': True, 'upper': True, 'textColor': '#00AAAA'},
            'Heading3': {'fontSize': 10, 'leading': 10, 'spaceAfter': 3, 'bold': True, 'upper': True},
            'Heading1_Right': {'fontSize': 13, 'leading': 0, 'spaceAfter': 0, 'bold': True, 'upper': True, 'alignment': 'TA_RIGHT'},
            'Heading2_Right': {'fontSize': 10, 'leading': 0, 'spaceAfter': 0, 'bold': True, 'upper': True, 'alignment': 'TA_RIGHT'},
            'Heading3_Right': {'fontSize': 10, 'leading': 0, 'spaceAfter': 0, 'bold': True, 'upper': True, 'alignment': 'TA_RIGHT'},
            'Text': {'fontSize': 10, 'leading': 12,},
            'Text2': {'fontSize': 10, 'leading': 12, 'textColor': '#000000', 'fontName': 'Helvetica-Oblique'},
            'Left': {'alignment': 'TA_LEFT'},
            'Right': {'alignment': 'TA_RIGHT', 'spaceAfter': 0, 'leading': 0}
        }

    def generate_columns(self):
        self.column_wide['summary'] = {
            'order': 1,
            'svg': self.icons['Fingerprint'],
            'keep_together': True, 
            'type': 'text', 
            'data': 'text',
            'format': [
                {'data': 'text', 'type': 'string', 'style': 'Text'},
            ]
        }
        
        self.column_wide['experiences'] = {
            'order': 2,
            'keep_together': False,
            'svg': self.icons['Briefcase'],
            'type': 'array',
            'data': ['role', 'company', 'start', 'end', 'curently_working', 'feature_comment', 'success', 'skills'],
            'format': [
                {'data': 'role', 'type': 'string', 'style': 'Heading2'},
                {'data': '{start:%b %Y} - {end:%b %Y}', 'type': 'format', 'style': 'Heading3_Right'},
                {'data': 'company', 'type': 'string', 'style': 'Heading3'},
                {'data': 'feature_comment', 'type': 'string', 'style': 'Text2'},
                {'data': 'achievements', 'type': 'list', 'style': 'Text'},
                {'data': 'spacer', 'type': 'spacer', 'width': 10, 'height': 15, 'style': 'Text'}
            ]
        }
        
        self.column_wide['education'] = {
            'order': 3,
            'svg': self.icons['Graduation'],
            'keep_together': True, 
            'type': 'array', 
            'data': [{'school': ['school', 'course', 'start', 'end']}],
            'format': [
                {'data': 'school', 'type': 'string', 'style': 'Heading3'},
                {'data': '{start:%b %Y} - {end:%b %Y}', 'type': 'format', 'style': 'Heading3_Right'},
                {'data': 'course', 'type': 'string', 'style': 'Heading2'},
            ]
        }

        self.column_wide['certificates'] = {
            'order': 4,
            'svg': self.icons['Certificate'],
            'keep_together': True, 
            'type': 'array', 
            'data': ['name', 'date'], 
            'format': [
                {'data': '{date:%b %Y}', 'type': 'format', 'style': 'Heading2_Right'},
                {'data': 'name', 'type': 'string', 'style': 'Heading2'}
            ]
        }
        
        self.column_wide['references'] = {
            'order': 5,
            'svg': self.icons['Person'],
            'keep_together': True, 
            'type': 'array',
            'data': [{'reference': ['name', 'phone', 'email', 'relationship']}],
            'format': [
                {'data': '{name},{relationship}', 'type': 'format', 'style': 'Heading2'},
                {'data': 'phone', 'svg': self.icons['Phone'], 'padding': 2, 'type': 'svg', 'placement': 'right', 'size': '.15 inch', 'style': 'Text'},
                {'data': 'email', 'svg': self.icons['Mail'], 'padding': 2, 'type': 'svg', 'placement': 'right', 'size': '.15 inch', 'style': 'Text'},
                {'data': 'spacer', 'type': 'spacer', 'width': 10, 'height': 12, 'style': 'Text'}
            ]
        }
        
        self.column_small['screener'] = {
            'order': 1,
            'svg': self.icons['Cog'],
            'keep_together': True, 
            'type': 'object', 
            'data': ['veteran', 'disability', 'us_citizen', 'over_18', 'willing_to_travel', 'remote', 'hybrid', 'office', 'start_date'], 
            'format': [
                {'data': 'Veteran: {veteran} ', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Disabled: {disability} ', 'type': 'format', 'style': 'Text'}, 
                {'data': 'US Citizen: {us_citizen}', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Over 18: {over_18}', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Travel: {willing_to_travel}', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Remote: {remote}', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Hybrid: {hybrid}', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Office: {office}', 'type': 'format', 'style': 'Text'}, 
                {'data': 'Start Date: {start_date}', 'type': 'format', 'style': 'Text'}
            ]
        }
        
        self.column_small['strengths'] = {
            'order': 2,
            'svg': self.icons['Access'],
            'keep_together': True, 
            'type': 'array', 
            'data': ['strengths'], 
            'format': [
                {'data': 'strengths', 'type': 'list', 'style': 'Text'}
            ]
        }
        
        self.column_small['achievements'] = {
            'order': 3,
            'svg': self.icons['Trophy'],
            'keep_together': True, 
            'type': 'array', 
            'data': ['achievements'], 
            'format': [
                {'data': 'achievements', 'type': 'list', 'style': 'Text'}
            ]
        }
        
        self.column_small['skills'] = {
            'order': 4,
            'svg': self.icons['Code'],
            'keep_together': True, 
            'type': 'array',
            'data': ['skills'],
            'format': [
                {'data': 'skills', 'type': 'svgrow', 'svg_size': '.25 inch', 'placement': 'right', 'style': 'Text'},
            ]
        }

        self.column_small['passions'] = {
            'order': 5,
            'svg': self.icons['Person'],
            'keep_together': True, 
            'type': 'array', 
            'data': ['passions'], 
            'format': [
                {'data': 'passions', 'type': 'list', 'style': 'Text'}
            ]
        }

    def generate_template(self):
        self.template = {
            'global': {'heading': {'bold': True, 'upper': True}, 'list': {'bullet_style': '•'}},
            'header': {
                'name': 'header', 
                'frame': 'header', 
                'type': 'text', 
                'all_pages': False,
                'data': ['name', 'address', 'location', 'phone', 'email', 'position', 'github', 'linkedin', 'picture'],
                'format': [
                    {'data': 'name', 'type': 'string', 'style': 'Title'},
                    {'data': 'position', 'svg': 'submodules/fluentui-system-icons/assets/Trophy/SVG/ic_fluent_trophy_16_filled.svg', 'type': 'svg', 'color': '#FFFFFF', 'placement': 'right', 'size': '.15 inch', 'style': 'Heading2'},
                    {'data': 'email', 'svg': 'submodules/fluentui-system-icons/assets/Mail/SVG/ic_fluent_mail_16_filled.svg', 'type': 'svg', 'color': '#FFFFFF', 'placement': 'right', 'size': '.15 inch', 'style': 'Text'},
                    {'data': 'phone', 'svg': 'submodules/fluentui-system-icons/assets/Phone/SVG/ic_fluent_phone_16_filled.svg', 'type': 'svg', 'color': '#FFFFFF', 'placement': 'right', 'size': '.15 inch', 'style': 'Text'},
                    {'data': 'location', 'svg': 'submodules/fluentui-system-icons/assets/Location/SVG/ic_fluent_location_16_filled.svg', 'type': 'svg', 'color': '#FFFFFF', 'placement': 'right', 'size': '.15 inch', 'style': 'Text'},
                ]
            },
            'continuation_header': {
                'name': 'continuation_header',
                'type': 'text',
                'data': ['name', 'phone', 'email'],
                'format': [
                    {'data': 'name', 'type': 'string', 'style': 'Heading1'},
                    {'data': 'phone', 'type': 'string', 'style': 'Text'},
                    {'data': 'email', 'type': 'string', 'style': 'Text'},
                ]
            },
            'footer': {
                'name': 'footer', 
                'frame': 'footer', 
                'type': 'text', 
                'data': ['page', 'page_total'], 
                'format': [
                    {'data': 'Page {page} of {page_total}', 'type': 'format', 'style': 'Text'}
                ]
            },
            'columns': {
                'wide': {'sections': self.column_wide, 'order': 1},
                'small': {'sections': self.column_small, 'order': 2}
            }
        }

    def generate_stylesheet(self):
        column_index = 0
        for column in self.template['columns']:
            dark = self.even_column_dark if column_index % 2 == 0 else self.odd_column_dark
            for section in self.template['columns'][column]['sections']:
                self.style(section, "Heading1", dark)
                section_obj = self.template['columns'][column]['sections'][section]
                for item in section_obj['format']:
                    self.style(section, item['style'], dark)
        column_index += 1

        section = 'header'
        self.style(section, "Heading1", self.header_dark)
        for item in self.template['header']['format']:
            self.style(section, item['style'], self.header_dark)

        # Add styles for continuation header
        section = 'continuation_header'
        self.style(section, "Heading1", False)  # Light theme for continuation
        for item in self.template['continuation_header']['format']:
            self.style(section, item['style'], False)

        section = 'footer'
        self.style(section, "Heading1", self.footer_dark)
        for item in self.template['footer']['format']:
            self.style(section, item['style'], self.footer_dark)

    def style(self, section, style_type, dark):
        template = {
            'textColor': self.theme['text_dark'] if dark else self.theme['text_light'],
            'bgColor': self.theme['bg_dark'] if dark else self.theme['bg_light']
        }

        style_name = f"{section}_{style_type}"
        self.styles[style_name] = {**self.base_template, **template, **self.heading_templates.get(style_type, {})}

    def add_qr_code(self, qr_id, left, top, size, data, bg_color='#FFFFFF', fg_color='#000000', depth=5):
        """Add a QR code to the template"""
        qr_shape = shape_qrcode(qr_id, left, top, size, data, bg_color, fg_color, depth)
        return qr_shape

    def build(self):
        self.header_frame = frame('header', '0.5 inch', 'page_height-1.5 inch-.5 inch', 'page_width - 1 inch', '1.5 inch')
        self.footer_frame = frame('footer', '.25 inch', '0 inch', 'page_width - .25 inch', '.5 inch')
        self.wide_column_frame = frame('wide_column', '.25 inch', 'footer.height+footer.top+.25 inch', '(page_width - .75 inch) * 0.66', 'page_height-header.height-footer.height -1 inch')
        self.small_column_frame = frame('small_column',
                                        'wide_column.left+wide_column.width +0.25 inch',
                                        'footer.height+footer.top+.25 inch',
                                        'page_width - wide_column.width -.75 inch',
                                        'page_height-header.height-footer.height -1 inch')
        
        self.header_bg_rect = shape_rectangle('header_bg_rect', 0, 'page_height-2 inch', 'page_width', '2 inch', '#004455', depth=1)
        self.small_column_bg_rect = shape_rectangle('small_column_bg_rect',
                                                    'wide_column.left+wide_column.width +0.25 inch',
                                                    0,
                                                    'page_width - wide_column.width ',
                                                    'page_height-header.height-footer.height ',
                                                    '#F0F0F0', depth=2)
        self.edge_color_rect = shape_rectangle('edge_color_rect', 0, 0, '.125 inch', 'page_height', '#EE0000')
        self.header_bg_circle = shape_circle('header_bg_circle', 'page_width - 1.5 inch', 'page_height-1 inch', '.75 inch', '#222222', 1)
        self.picture = shape_picture('picture', 'header.left+header.width-1.70 inch', 'header.top + .35 inch', '1.4 inch', '1.4 inch', 'circle', '#000000')
        
        # Add QR codes
        self.linkedin_qr = self.add_qr_code('linkedin_qr', 'page_width - 1 inch', 'footer.top + 0.1 inch', '0.4 inch', 'https://linkedin.com/in/{linkedin}')
        self.contact_qr = self.add_qr_code('contact_vcard_qr', '0.1 inch', '1 inch', '0.8 inch', 'BEGIN:VCARD\\nVERSION:3.0\\nFN:{name}\\nTEL:{phone}\\nEMAIL:{email}\\nURL:https://linkedin.com/in/{linkedin}\\nEND:VCARD')
        self.portfolio_qr = self.add_qr_code('portfolio_qr', 'small_column.left + 0.1 inch', 'small_column.top + small_column.height - 1 inch', '0.6 inch', '{github}', '#F0F0F0')
        
        self.global_settings = global_settings(True, True, True)
        self.metadata['frames'] = [self.header_frame, self.footer_frame, self.wide_column_frame, self.small_column_frame]
        self.metadata['shapes'] = [self.header_bg_rect, self.small_column_bg_rect, self.edge_color_rect, self.header_bg_circle, self.linkedin_qr, self.contact_qr, self.portfolio_qr]
        self.metadata['picture'] = self.picture
        self.metadata['global'] = self.global_settings
        
        self.generate_columns()
        self.generate_template()
        self.generate_stylesheet()
        self.metadata['template'] = self.template
        self.metadata['styles'] = self.styles

    def load(self):
        """
        Load page template metadata from a YAML file.
        """
        with open(self.template_file, 'r') as file:
            self.metadata = yaml.safe_load(file)
        return self.metadata.get('page_template', {})

    def save(self):
        with open(self.template_file, 'w') as file:
            yaml.emitter.Emitter.prepare_tag = lambda self, tag: ''
            yaml.dump({'page_template': self.metadata}, file)