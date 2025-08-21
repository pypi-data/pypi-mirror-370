from reportlab.platypus import Flowable
from .common import capture_details


class SpacerD(Flowable):
    def __init__(self,width=0, height=0, thing=0):
        super().__init__()
        self.width = width
        self.height = height
    
    #def draw(self):
    #    frame_y_position = self._frame._y if self._frame else 0
    #    line_height = frame_y_position  - self.height  
    #    capture_details(self,  self._frame.width, line_height)
    def drawOn(self, canvas, x, y, _sW=0):
        self.canvas=canvas
        #width, height = self.wrap(canvas._doc.width, canvas._doc.height)
        self.x=x
        self.y=y
        capture_details(self,  self.width+x, y)


    def wrap(self,aW,Ah):
        return self.width,self.height

    def wrapOn(self,canvas, aW,Ah):
        return self.width,self.height