from reportlab.platypus import Paragraph
from .common import capture_details

class ParagraphD(Paragraph):
    def __init__(self, text, style, debug=False, **kwargs):
        if getattr(style, "bold", False):
            text = f"<b>{text}</b>"
        super().__init__(text, style, **kwargs)
        self.debug = debug
        self.details = {}

    def wrap(self, availWidth, availHeight):
        # use ReportLab’s paragraph wrapping, but track values
        w, h = super().wrap(availWidth, availHeight)
        self.width, self.height = w, h
        return w, h

    def wrapOn(self, canv, availWidth, availHeight):
        # delegate to wrap, ReportLab calls this during layout
        return self.wrap(availWidth, availHeight)

    def drawOn(self, canvas, x, y, _sW=0):
        super().drawOn(canvas, x, y, _sW)
        #self.debug=True
        if self.debug:
            canvas.setStrokeColorRGB(1, 0, 0)  # red box
            canvas.rect(x, y, self.width, self.height, stroke=1, fill=0)

        capture_details(self, x, y)
