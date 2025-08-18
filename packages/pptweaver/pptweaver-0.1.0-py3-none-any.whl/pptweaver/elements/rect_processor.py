from pptx.enum.shapes import MSO_SHAPE
from .base_processor import BaseProcessor

class RectProcessor(BaseProcessor):
    """
    Processes <rect> SVG elements.
    """
    def process(self):
        params = self.get_shape_params()
        if not params:
            return

        self.left, self.top, self.width, self.height = params
        
        shape = self.slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, self.left, self.top, self.width, self.height
        )
        
        # Parse fill and line styles
        self.apply_styles(shape)
