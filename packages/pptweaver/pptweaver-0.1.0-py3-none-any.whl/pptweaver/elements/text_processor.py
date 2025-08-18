import re
from pptx.util import Pt
from pptx.enum.text import MSO_AUTO_SIZE
from .base_processor import BaseProcessor

class TextProcessor(BaseProcessor):
    """
    Processes SVG <text> elements.
    For rich HTML content inside <foreignObject>, see ForeignObjectProcessor.
    """
    def process(self):
        self.text = self.element_data.get('text')
        if not self.text:
            return
            
        params = self.get_shape_params()
        if not params:
            return

        self.left, self.top, self.width, self.height = params
        textbox = self.slide.shapes.add_textbox(self.left, self.top, self.width, self.height)
        tf = textbox.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = self.text

        self._apply_font_styles(run)

    def _apply_font_styles(self, run):
        """Applies font styles to a text run."""
        style = self.element_data.get('style', {})
        font = run.font
        
        # Set font name
        self._set_font_family(font, style)

        if style.get('fontSize'):
            try:
                font_size_px = float(re.sub(r'px$', '', style['fontSize']))
                scaled_font_size_px = font_size_px * self.converter.scale_y
                font.size = self.converter.px_to_pt(scaled_font_size_px)
            except (ValueError, TypeError):
                pass

        # For SVG <text>, color is specified by the 'fill' attribute.
        color_str = style.get('fill')
        rgb_color, _ = self.converter.parse_color(color_str)
        if rgb_color:
            font.color.rgb = rgb_color

        # Apply bold
        font_weight = style.get('fontWeight', '400')
        try:
            is_bold = int(font_weight) > 400 or font_weight in ['bold', 'bolder']
            font.bold = is_bold
        except ValueError:
            font.bold = font_weight in ['bold', 'bolder']

    def _set_font_family(self, font, style):
        """Sets the font family, selecting the first available font from the CSS list."""
        font_family_str = style.get('fontFamily')
        if not font_family_str:
            font.name = 'Calibri'
            return
        
        # CSS font-family can be a comma-separated list. We take the first one.
        # Removing quotes around font names.
        preferred_font = font_family_str.split(',')[0].strip().replace('"', '').replace("'", "")
        
        # A basic mapping for common sans-serif fonts. Can be expanded.
        if preferred_font.lower() in ['sans-serif', 'system-ui']:
            font.name = 'Calibri'
        else:
            font.name = preferred_font
