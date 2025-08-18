import logging

from .base_processor import BaseProcessor

class PolygonProcessor(BaseProcessor):
    """
    Processes <polygon> and <polyline> SVG elements by creating a Freeform shape.
    """
    def process(self):
        attributes = self.element_data.get('attributes', {})
        points_str = attributes.get('points', '').strip()
        
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
            
            # The API is build_freeform(start_x, start_y).add_line_segments(points_list)
            # We need to collect all subsequent points into a list.
            point_list = [(
                self.converter.px_to_emu(float(p[0]) * self.converter.scale_x),
                self.converter.px_to_emu(float(p[1]) * self.converter.scale_y)
            ) for p in points[1:]]

            # For polygons, we must manually add the starting point to the end of the list
            # to close the shape.
            tag_name = self.element_data.get('tagName')
            if tag_name == 'polygon':
                point_list.append((start_x, start_y))

            shape_builder = self.slide.shapes.build_freeform(start_x, start_y)
            if point_list:
                shape_builder.add_line_segments(point_list)
            shape = shape_builder.convert_to_shape()
            
            self.apply_styles(shape)
            
        except (ValueError, TypeError, IndexError) as e:
            # Handle cases where points are not valid numbers
            logging.error(f"PolygonProcessor failed for points '{points_str}': {e}", exc_info=True)
            return
