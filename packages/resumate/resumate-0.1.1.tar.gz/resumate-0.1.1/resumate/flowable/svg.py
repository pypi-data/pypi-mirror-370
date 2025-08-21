import os
from reportlab.platypus import Flowable
from reportlab.lib import colors
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from .common import capture_details
from .svg_flatener import flaten_svg
from .svg_search import search_svg

class SVGFlowableD(Flowable):
    def __init__(self, svg_file, text=None, style=None, placement="bottom", size=0,padding=5,color=None,debug=None):
        super().__init__()

        args={}
        if color!=None:
            if isinstance(color,str):
                color = int(color[1:], 16)
            args['color_converter']= lambda x:colors.HexColor(color)

        self.svg_file = search_svg(svg_file)
        
        # Handle missing SVG gracefully
        if self.svg_file is None:
            self.drawing = None
            print(f"Warning: Using text-only fallback for missing SVG: {svg_file}")
        else:
            try:
                self.drawing = svg2rlg(self.svg_file, **args)
            except Exception as e:
                print(f"Error loading SVG {self.svg_file}: {e}")
                self.drawing = None
                
        self.text = text
        self.style = style
        self.svg_x = 0
        self.svg_y = 0
        self.svg_width = size if self.drawing else 0
        self.svg_height = size if self.drawing else 0
        self.text_x = 0
        self.text_y = 0
        self.text_width = 0
        self.text_height = 0
        self.padding = padding
        self.placement = placement
        self.debug = debug
        self.calculate_bounds()

    def calculate_bounds(self):
        if self.text:
            self.text_width = stringWidth(self.text, self.style.fontName, self.style.fontSize)
            self.text_height = self.style.leading
            
        if self.drawing:
            # Calculate scaling factors based on desired width and height
            if self.svg_width and self.svg_height:
                scaling_x = self.svg_width / self.drawing.minWidth()
                scaling_y = self.svg_height / self.drawing.height
            elif self.svg_width:
                scaling_x = scaling_y = self.svg_width / self.drawing.width
            elif self.svg_height:
                scaling_x = scaling_y = self.svg_height / self.drawing.height
            else:
                print("Either width or height must be provided.")
                return
            self.drawing.width = self.drawing.minWidth() * scaling_x
            self.drawing.height = self.drawing.height * scaling_y
            self.svg_width = self.drawing.width
            self.svg_height = self.drawing.height
            self.drawing.scale(scaling_x, scaling_y)

        # Layout calculations - handle missing SVG case
        if self.placement == "bottom":
            self.width = max(self.svg_width, self.text_width) + self.padding * 2
            self.height = self.svg_height + self.text_height + self.padding * 3

            self.text_x = (self.width - self.text_width) / 2
            self.text_y = self.padding
            self.svg_x = (self.width - self.svg_width) / 2
            self.svg_y = self.padding * 2 + self.text_height

        elif self.placement == "top":
            self.width = max(self.svg_width, self.text_width) + self.padding * 2
            self.height = self.svg_height + self.text_height + self.padding * 3

            self.text_x = (self.width - self.text_width) / 2
            self.text_y = self.padding * 2 + self.svg_height
            self.svg_x = (self.width - self.svg_width) / 2
            self.svg_y = self.padding

        elif self.placement == "left":
            self.width = self.svg_width + self.text_width + self.padding * 2
            self.height = max(self.svg_height, self.text_height) + self.padding * 2

            self.text_x = self.padding
            self.text_y = (self.height - self.text_height) / 2
            self.svg_x = self.padding * 2 + self.text_width
            self.svg_y = self.padding

        elif self.placement == "right":
            self.width = self.svg_width + self.text_width + self.padding * 2
            self.height = max(self.svg_height, self.text_height) + self.padding * 2

            self.text_x = self.padding * 2 + self.svg_width
            self.text_y = (self.height - self.text_height) / 2
            self.svg_x = self.padding
            self.svg_y = self.padding

        # If no SVG, just use text dimensions
        if not self.drawing:
            self.width = self.text_width + self.padding * 2
            self.height = self.text_height + self.padding * 2
            self.text_x = self.padding
            self.text_y = self.padding

    def wrap(self, width, height):
        return self.width, self.height

    def wrapOn(self, canv, width, height):
        return self.width, self.height

    def drawOn(self, canvas, x, y, _sW=0):
        # Draw SVG if available
        if self.drawing:
            renderPDF.draw(self.drawing, canvas, x + self.svg_x, y + self.svg_y)
            if self.debug:
                canvas.setStrokeColorRGB(0, 0, 0)
                canvas.rect(x + self.svg_x, y + self.svg_y, self.svg_width, self.svg_height, stroke=1, fill=0)

        # Draw text
        if self.text:
            canvas.setFont(self.style.fontName, self.style.fontSize)
            canvas.setFillColor(self.style.textColor)
            canvas.drawString(x + self.text_x, y + self.text_y, self.text)
            if self.debug:
                canvas.setStrokeColorRGB(0, 0, 0)
                canvas.rect(x + self.text_x, y + self.text_y, self.text_width, self.text_height, stroke=1, fill=0)

        capture_details(self, x, y)



class SVGRRowD(Flowable):
    def __init__(self, contents=[], **kwargs):
        super().__init__(**kwargs)
        
        self.width=0
        self.height=0
        for item in contents:
            item.parent=self

        self.contents = contents

    def calc_dimentions(self,width,height):
        mx=0
        my=0
        height=0
        width=width

        for item in self.contents:
            w,h=item.wrap(width,height)
            
            if mx+w>width:
                mx=0
                my+=height
                height=0
                
            if h>height: 
                height=h

            mx+=w
        my+=height

        self.width=mx
        self.height=my    

    def wrap(self, availWidth, availHeight):
        #super().wrap(availWidth,availHeight)
        self.calc_dimentions(availWidth,availHeight)
        return self.width, self.height

    
    def wrapOn(self,canv, width, height):
        #super().wrapOn(canv, width, height)
        self.calc_dimentions(width,height)
        return self.width, self.height


    def drawOn(self, canvas, x, y, _sW):
        #super().drawOn(canvas, x, y, _sW)
        mx=0
        my=0
        height=0
        width=self._frame.width
        for item in self.contents:
            w,h=item.wrap(width,height)
            
            if mx+w>width:
                mx=0
                my-=height
                height=0
                
            if h>height: 
                height=h

            item.drawOn(canvas, x+mx, y-my)
            mx+=w
        my-=height
            #canvas.setStrokeColorRGB(0, 0, 0)  # Black color for the rectangle
            #canvas.rect(x+mx,y+my,flowable.width, flowable.height, stroke=1, fill=0)
        capture_details(self,  x, y)


