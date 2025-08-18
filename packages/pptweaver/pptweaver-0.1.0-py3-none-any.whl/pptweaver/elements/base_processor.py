from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """
    Abstract base class for all element processors.
    """
    def __init__(self, element_data, slide, converter):
        self.element_data = element_data
        self.slide = slide
        self.converter = converter # Provides access to scaling factors and utility functions

    @abstractmethod
    def process(self):
        """
        Processes the element data and adds the corresponding shape to the slide.
        This method must be implemented by all subclasses.
        """
        pass

    def get_shape_params(self):
        """
        Helper method to calculate the scaled position and dimensions.
        """
        rect = self.element_data.get('rect')
        if not rect or rect['width'] <= 0 or rect['height'] <= 0:
            return None

        left = self.converter.px_to_emu(rect['x'] * self.converter.scale_x)
        top = self.converter.px_to_emu(rect['y'] * self.converter.scale_y)
        width = self.converter.px_to_emu(rect['width'] * self.converter.scale_x)
        height = self.converter.px_to_emu(rect['height'] * self.converter.scale_y)
        
        return left, top, width, height

    def apply_styles(self, shape):
        """
        Applies fill and line styles to a given shape.
        """
        style = self.element_data.get('style', {})
        
        # Fill (only apply if the shape supports it)
        if hasattr(shape, 'fill'):
            fill_color_str = style.get('fill')
            self.fill_color, self.fill_alpha = self.converter.parse_color(fill_color_str)
            if self.fill_color:
                shape.fill.solid()
                shape.fill.fore_color.rgb = self.fill_color
                if self.fill_alpha is not None and self.fill_alpha < 1.0:
                    # Transparency is 1.0 (fully transparent) to 0.0 (fully opaque)
                    shape.fill.transparency = 1 - self.fill_alpha
            else:
                shape.fill.background()

        # Line (Stroke)
        if hasattr(shape, 'line'):
            line_color_str = style.get('stroke')
            line_color, line_alpha = self.converter.parse_color(line_color_str)
            if line_color:
                line = shape.line
                
                # Special handling for connectors (lines, arrows)
                # Their color is set via line.fill, not line.color
                if hasattr(line, 'fill'):
                    line.fill.solid()
                    line.fill.fore_color.rgb = line_color
                # Standard shapes use a different way to set line color
                elif hasattr(line, 'color'):
                     line.color.rgb = line_color
                
                stroke_width_str = style.get('strokeWidth', '1px').replace('px', '')
                try:
                    # Scale stroke width as well
                    stroke_width_px = float(stroke_width_str) * self.converter.scale_x
                    line.width = self.converter.px_to_emu(stroke_width_px)
                except (ValueError, TypeError):
                    line.width = self.converter.px_to_emu(1 * self.converter.scale_x)
