from reportlab.platypus import Flowable
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from .common import capture_details
from .svg import search_svg

class RatingFlowable(Flowable):
    def __init__(self, svg_file, text, rating, max_rating=5, style=None, 
                 icon_size=20, rating_style='bars', padding=10, 
                 filled_color=colors.black, empty_color=colors.lightgrey,
                 bar_width=15, bar_height=4, bar_spacing=3, 
                 layout='icon_rating_text', debug=False):
        """
        Create a rating flowable with icon, text, and rating visualization.
        
        Args:
            svg_file: Path to SVG icon or technology name
            text: Text label for the rating
            rating: Current rating value (e.g., 3 out of 5)
            max_rating: Maximum rating value (default 5)
            style: Text style for the label
            icon_size: Size of the SVG icon
            rating_style: 'bars', 'circles', 'stars', or 'dots'
            padding: Padding around elements (default 10)
            filled_color: Color for filled rating elements
            empty_color: Color for empty rating elements
            bar_width: Width of each rating bar
            bar_height: Height of rating bars
            bar_spacing: Space between rating elements
            layout: 'icon_rating_text' for vertical layout with icon on top
            debug: Show debug rectangles
        """
        super().__init__()
        
        self.svg_file = search_svg(svg_file)
        self.text = text
        self.rating = min(rating, max_rating)  # Ensure rating doesn't exceed max
        self.max_rating = max_rating
        self.style = style
        self.icon_size = icon_size
        self.rating_style = rating_style
        self.padding = padding
        self.filled_color = filled_color
        self.empty_color = empty_color
        self.bar_width = bar_width
        self.bar_height = bar_height
        self.bar_spacing = bar_spacing
        self.layout = layout
        self.debug = debug
        
        # Load SVG if available
        self.drawing = None
        if self.svg_file:
            try:
                self.drawing = svg2rlg(self.svg_file)
                # Scale the drawing to icon_size
                scaling = self.icon_size / max(self.drawing.width, self.drawing.height)
                self.drawing.width = self.drawing.width * scaling
                self.drawing.height = self.drawing.height * scaling
                self.drawing.scale(scaling, scaling)
            except Exception as e:
                print(f"Error loading SVG {self.svg_file}: {e}")
                self.drawing = None
        
        # Calculate component dimensions
        self.calculate_layout()
    
    def calculate_layout(self):
        """Calculate positions and dimensions of all components."""
        
        # Icon dimensions
        self.icon_width = self.icon_size if self.drawing else 0
        self.icon_height = self.icon_size if self.drawing else 0
        
        # Text dimensions
        if self.text and self.style:
            self.text_width = stringWidth(self.text, self.style.fontName, self.style.fontSize)
            self.text_height = self.style.leading
        else:
            self.text_width = 0
            self.text_height = 0
        
        # Rating visualization dimensions
        if self.rating_style == 'bars':
            self.rating_width = (self.bar_width * self.max_rating + 
                               self.bar_spacing * (self.max_rating - 1))
            self.rating_height = self.bar_height
        elif self.rating_style == 'circles':
            circle_size = self.bar_height * 2
            self.rating_width = (circle_size * self.max_rating + 
                               self.bar_spacing * (self.max_rating - 1))
            self.rating_height = circle_size
        elif self.rating_style == 'dots':
            dot_size = self.bar_height
            self.rating_width = (dot_size * self.max_rating + 
                               self.bar_spacing * (self.max_rating - 1))
            self.rating_height = dot_size
        else:  # default to bars
            self.rating_width = (self.bar_width * self.max_rating + 
                               self.bar_spacing * (self.max_rating - 1))
            self.rating_height = self.bar_height
        
        if self.layout == 'icon_rating_text':
            # Vertical layout: Icon on top, rating below, text at bottom
            # Width is the maximum of all components
            self.width = max(self.icon_width, self.rating_width, self.text_width) + self.padding * 2
            
            # Height is sum of all components plus padding between
            self.height = (self.padding * 2 +  # Top and bottom padding
                          self.icon_height + 
                          (self.padding if self.icon_height > 0 else 0) +  # Padding after icon
                          self.rating_height + 
                          (self.padding if self.text_height > 0 else 0) +  # Padding after rating
                          self.text_height)
            
            # Center all components horizontally
            self.icon_x = (self.width - self.icon_width) / 2
            self.icon_y = self.height - self.padding - self.icon_height  # Start from top
            
            self.rating_x = (self.width - self.rating_width) / 2
            self.rating_y = (self.icon_y - 
                           (self.padding if self.icon_height > 0 else 0) - 
                           self.rating_height)
            
            self.text_x = (self.width - self.text_width) / 2
            self.text_y = self.padding  # Text at bottom
            
        else:
            # Original horizontal layout
            self.icon_x = self.padding
            self.icon_y = self.padding
            
            self.text_x = self.icon_x + self.icon_width + (self.padding if self.icon_width > 0 else 0)
            self.text_y = self.padding + (self.icon_height - self.text_height) / 2
            
            self.rating_x = self.text_x + self.text_width + self.padding
            self.rating_y = self.padding + (self.icon_height - self.rating_height) / 2
            
            self.width = self.rating_x + self.rating_width + self.padding
            self.height = max(self.icon_height, self.text_height, self.rating_height) + self.padding * 2
    
    def wrap(self, avail_width, avail_height):
        return self.width, self.height
    
    def wrapOn(self, canv, avail_width, avail_height):
        return self.wrap(avail_width, avail_height)
    
    def draw_rating_bars(self, canvas, x, y):
        """Draw horizontal bars for rating."""
        for i in range(self.max_rating):
            bar_x = x + i * (self.bar_width + self.bar_spacing)
            
            if i < self.rating:
                canvas.setFillColor(self.filled_color)
            else:
                canvas.setFillColor(self.empty_color)
            
            canvas.rect(bar_x, y, self.bar_width, self.bar_height, stroke=0, fill=1)
    
    def draw_rating_circles(self, canvas, x, y):
        """Draw circles for rating."""
        circle_radius = self.bar_height
        for i in range(self.max_rating):
            circle_x = x + i * (circle_radius * 2 + self.bar_spacing) + circle_radius
            circle_y = y + circle_radius
            
            if i < self.rating:
                canvas.setFillColor(self.filled_color)
                canvas.circle(circle_x, circle_y, circle_radius, stroke=0, fill=1)
            else:
                canvas.setStrokeColor(self.empty_color)
                canvas.setFillColor(colors.white)
                canvas.circle(circle_x, circle_y, circle_radius, stroke=1, fill=1)
    
    def draw_rating_dots(self, canvas, x, y):
        """Draw small dots for rating."""
        dot_radius = self.bar_height / 2
        for i in range(self.max_rating):
            dot_x = x + i * (dot_radius * 2 + self.bar_spacing) + dot_radius
            dot_y = y + dot_radius
            
            if i < self.rating:
                canvas.setFillColor(self.filled_color)
            else:
                canvas.setFillColor(self.empty_color)
            
            canvas.circle(dot_x, dot_y, dot_radius, stroke=0, fill=1)
    
    def drawOn(self, canvas, x, y, _sW=0):
        """Draw the rating flowable on the canvas."""
        
        # Draw icon if available
        if self.drawing:
            renderPDF.draw(self.drawing, canvas, x + self.icon_x, y + self.icon_y)
            if self.debug:
                canvas.setStrokeColorRGB(0, 0, 1)  # Blue for icon
                canvas.rect(x + self.icon_x, y + self.icon_y, 
                          self.icon_width, self.icon_height, stroke=1, fill=0)
        
        # Draw text
        if self.text and self.style:
            canvas.setFont(self.style.fontName, self.style.fontSize)
            canvas.setFillColor(self.style.textColor)
            canvas.drawString(x + self.text_x, y + self.text_y, self.text)
            if self.debug:
                canvas.setStrokeColorRGB(0, 1, 0)  # Green for text
                canvas.rect(x + self.text_x, y + self.text_y, 
                          self.text_width, self.text_height, stroke=1, fill=0)
        
        # Draw rating visualization
        if self.rating_style == 'bars':
            self.draw_rating_bars(canvas, x + self.rating_x, y + self.rating_y)
        elif self.rating_style == 'circles':
            self.draw_rating_circles(canvas, x + self.rating_x, y + self.rating_y)
        elif self.rating_style == 'dots':
            self.draw_rating_dots(canvas, x + self.rating_x, y + self.rating_y)
        else:
            self.draw_rating_bars(canvas, x + self.rating_x, y + self.rating_y)
        
        if self.debug:
            canvas.setStrokeColorRGB(1, 0, 0)  # Red for rating area
            canvas.rect(x + self.rating_x, y + self.rating_y, 
                      self.rating_width, self.rating_height, stroke=1, fill=0)
            
            # Overall bounding box
            canvas.setStrokeColorRGB(0, 0, 0)  # Black for total area
            canvas.rect(x, y, self.width, self.height, stroke=1, fill=0)
        
        capture_details(self, x, y)