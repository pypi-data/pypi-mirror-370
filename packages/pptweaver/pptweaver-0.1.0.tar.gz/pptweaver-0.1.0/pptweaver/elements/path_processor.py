from .base_processor import BaseProcessor
import logging

class PathProcessor(BaseProcessor):
    """
    Processes <path> SVG elements by creating a Freeform shape
    based on linearized points calculated in the browser.
    """
    def process(self):
        attributes = self.element_data.get('attributes', {})
        # Use the pre-calculated linearized points instead of the 'd' attribute.
        points_str = attributes.get('linearized_points', '').strip()
        
        if not points_str:
            return

        try:
            points = [p.split(',') for p in points_str.split()]
            if len(points) < 2:
                return
        except Exception:
            return

        try:
            # Start the freeform shape builder
            start_x = self.converter.px_to_emu(float(points[0][0]) * self.converter.scale_x)
            start_y = self.converter.px_to_emu(float(points[0][1]) * self.converter.scale_y)

            point_list = [(
                self.converter.px_to_emu(float(p[0]) * self.converter.scale_x),
                self.converter.px_to_emu(float(p[1]) * self.converter.scale_y)
            ) for p in points[1:]]

            shape_builder = self.slide.shapes.build_freeform(start_x, start_y)
            if point_list:
                shape_builder.add_line_segments(point_list)
            
            # Note: We cannot reliably determine if a path should be closed ('Z' command)
            # without a full path parser. For now, we leave all paths open.
            # This can be enhanced later.

            shape = shape_builder.convert_to_shape()
            self.apply_styles(shape)
            
        except (ValueError, TypeError, IndexError) as e:
            logging.error(f"PathProcessor failed for linearized_points '{points_str}': {e}", exc_info=True)
            return
