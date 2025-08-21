class frame:
    def __init__(self, frame_id, left, top, width, height):
        self.id = frame_id
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class shape_rectangle:
    def __init__(self, id, left=0, top=0, width=0, height=0, background_color=None, depth=0):
        self.id = id
        self.depth = depth
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.background_color = background_color
        self.type = "rect"


class shape_circle:
    def __init__(self, id, left=0, top=0, diameter=0, background_color=None, depth=0):
        self.id = id
        self.depth = depth
        self.left = left
        self.top = top
        self.diameter = diameter
        self.background_color = background_color
        self.type = "circle"


class shape_picture:
    def __init__(self, id, left=0, top=0, max_width=0, max_height=0, mask=None, background_color=None, depth=0):
        self.id = id
        self.depth = depth
        self.left = left
        self.top = top
        self.width = None
        self.height = None
        self.max_width = max_width
        self.max_height = max_height
        self.background_color = background_color
        self.mask = mask
        self.type = "picture"


class shape_qrcode:
    def __init__(self, id, left=0, top=0, size=0, data=None, background_color=None, foreground_color=None, depth=0):
        self.id = id
        self.depth = depth
        self.left = left
        self.top = top
        self.size = size
        self.data = data
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.type = "qrcode"