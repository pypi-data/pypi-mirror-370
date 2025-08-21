import logging

# Import all flowable classes
from .svg_flatener import flaten_svg
from .line import LineDrawer
from .spacer import SpacerD
from .svg import SVGFlowableD, SVGRRowD
from .paragraph import ParagraphD
from .qrcode import QRCodeFlowable
from .word import SingleWordD
from .rating import RatingFlowable

# Import state management functions
from .common import (
    capture_details,
    rendered_details,
    get_rendered_details,
    clear_rendered_details,
    set_rendered_details
)

# Set up warning handler for svglib
class WarningCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.warnings = []

    def emit(self, record):
        if record.levelno == logging.WARNING:
            raise Exception(f"Warning escalated to error: {record.getMessage()}")

logger = logging.getLogger('svglib')
logger.setLevel(logging.WARNING)
handler = WarningCaptureHandler()
logger.addHandler(handler)

# Define public API
__all__ = [
    # Flowable classes
    'LineDrawer',
    'SpacerD',
    'SVGFlowableD',
    'SVGRRowD',
    'ParagraphD',
    'QRCodeFlowable',
    'SingleWordD',
    'RatingFlowable',  

    # Utility functions
    'flaten_svg',
    
    # State management
    'capture_details',
    'get_rendered_details',
    'clear_rendered_details',
    'set_rendered_details',
    
    # Direct access to state (use with caution)
    'rendered_details'
]