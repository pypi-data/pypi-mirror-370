from reportlab.platypus import Flowable
from reportlab.lib import colors
from .common import capture_details

class LineDrawer(Flowable):
    def __init__(self, height=0, color=colors.black, frame=None):
        super().__init__()
        self.width = 1
        self.height = height
        self.color = color
        self._frame = frame
        self._width_override = None  # Add this to handle width when frame is not available

    def drawOn(self, canvas, x, y, _sW=0):
        Flowable.drawOn(self, canvas, x, y, _sW)

    def draw(self):
        self.canv.setStrokeColor(self.color)
        
        # Get width from frame if available, otherwise use the width set during wrap
        if self._frame and hasattr(self._frame, '_width'):
            width = self._frame._width
        elif self._width_override:
            width = self._width_override
        else:
            width = self.width  # Fallback to default
        
        self.canv.line(0, self.height, width, self.height)
        
        # Only capture details if we have a frame
        if self._frame:
            frame_height = self._frame._height if self._frame else self.height
            frame_y_position = self._frame._y if self._frame else 0
            line_height = frame_y_position - self.height
            capture_details(self, 0, line_height)

    def wrap(self, availWidth, availHeight):
        if self._frame:
            return self._frame._width,1
        else :
            return availWidth,1


    def wrapOn(self, canvas, availWidth, availHeight):
        if self._frame:
            return self._frame._width,1
        else :
            return availWidth,1
