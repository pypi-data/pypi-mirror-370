from pptx.enum.shapes import MSO_SHAPE
from .base_processor import BaseProcessor

class OvalProcessor(BaseProcessor):
    """
    Processes <circle> and <ellipse> SVG elements, as both map to an oval shape.
    """
    def process(self):
        params = self.get_shape_params()
        if not params:
            return

        left, top, width, height = params
        
        # In python-pptx, both circles and ellipses are created as OVAL shapes.
        # The bounding box (left, top, width, height) correctly defines the shape.
        shape = self.slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
        self.apply_styles(shape)
