import qrcode
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Flowable
from .common import capture_details

class QRCodeFlowable(Flowable):
    def __init__(self, data, size):
        super().__init__()
        self.data = data
        self.size = size
        self.qr_x = 0
        self.qr_y = 0
        self.width = size
        self.height = size

    def wrap(self, width, height):
        return self.width, self.height

    def wrapOn(self, canv, width, height):
        return self.wrap(width,height)

    def drawOn(self, canvas, x, y, _sW=0):

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color='black', back_color='white')

        # Convert to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Draw QR code image directly on canvas using passed coordinates
        qr_image = ImageReader(buffer)
        canvas.drawImage(qr_image, x + self.qr_x, y + self.qr_y, self.size, self.size, mask='auto')
        
        # Add debug rectangle if needed
        canvas.setStrokeColorRGB(1, 0, 0)  # Red border for debugging
        canvas.rect(x + self.qr_x, y + self.qr_y, self.size, self.size, stroke=1, fill=0)
        
        capture_details(self, x, y)   