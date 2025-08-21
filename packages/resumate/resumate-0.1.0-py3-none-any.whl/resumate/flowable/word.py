from reportlab.platypus import Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth
from .common import capture_details

class SingleWordD(Flowable):
    def __init__(self, text, style):
        super().__init__()
        self.text = text
        self.style=style
        

    def wrapOn(self, canvas, availWidth, availHeight):
        return self.wrap(self.width, self.height)
    def wrap(self, availWidth, availHeight):
        # Use stringWidth to calculate the width of the word
        self.width = stringWidth(self.text, self.style.fontName, self.style.fontSize)
        self.height = self.style.fontSize * 1.2  # Approximate height based on font size
        return self.width, self.height

    def draw(self):
        # Set the font and draw the word
        self.canvas.setFont(self.style.fontName, self.style.fontSize)
        self.canvas.setFillColor(self.style.textColor)
        self.canvas.drawString(self.x,self.y, self.text)

    def drawOn(self, canvas, x, y, _sW=0):
        self.canvas=canvas
        #width, height = self.wrap(canvas._doc.width, canvas._doc.height)
        self.x=x
        self.y=y
        self.draw()

        capture_details(self,  x, y)
