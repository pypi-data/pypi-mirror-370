from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml import parse_xml
from .base_processor import BaseProcessor

class LineProcessor(BaseProcessor):
    """
    Processes <line> SVG elements.
    """
    def process(self):
        attributes = self.element_data.get('attributes', {})
        
        try:
            x1 = self.converter.px_to_emu(float(attributes.get('x1', 0)) * self.converter.scale_x)
            y1 = self.converter.px_to_emu(float(attributes.get('y1', 0)) * self.converter.scale_y)
            x2 = self.converter.px_to_emu(float(attributes.get('x2', 0)) * self.converter.scale_x)
            y2 = self.converter.px_to_emu(float(attributes.get('y2', 0)) * self.converter.scale_y)
        except (ValueError, TypeError):
            return

        shape = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
        
        self.apply_styles(shape)

        style = self.element_data.get('style', {})
        if style.get('markerEnd') and style.get('markerEnd') != 'none':
            # python-pptx lacks a direct API for arrowheads on connectors.
            # We must manipulate the underlying XML.
            line_elem = shape.line._get_or_add_ln()
            
            # The XML for a standard triangle arrowhead at the end of the line.
            # `type="triangle"` is a more explicit synonym for `type="arrow"`.
            arrow_xml = '<a:headEnd type="triangle" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>'
            line_elem.append(parse_xml(arrow_xml))
