from .base_processor import BaseProcessor
import re
from pptx.enum.text import MSO_AUTO_SIZE

class ForeignObjectProcessor(BaseProcessor):
    """
    Processes <foreignObject> elements containing rich HTML text content.
    """
    def process(self):
        text_runs = self.element_data.get('text_runs')
        if not text_runs:
            return

        params = self.get_shape_params()
        if not params:
            return

        left, top, width, height = params
        textbox = self.slide.shapes.add_textbox(left, top, width, height)
        tf = textbox.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        tf.clear() # Clear default paragraph

        current_paragraph = None

        for i, run_data in enumerate(text_runs):
            text = run_data.get('text')
            tag_name = run_data.get('tagName')
            style = run_data.get('style', {})

            if not text:
                continue

            # Create a new paragraph for each list item or if it's the first run
            if tag_name == 'li' or current_paragraph is None:
                current_paragraph = tf.add_paragraph()
                # Add bullet point for list items
                if tag_name == 'li':
                    # Heuristic to determine bullet type based on content
                    bullet = "• " if ":" not in text else "» "
                    run = current_paragraph.add_run()
                    run.text = bullet
                    self._apply_run_styles(run, style, is_bullet=True)
            
            run = current_paragraph.add_run()
            run.text = text
            self._apply_run_styles(run, style)

    def _apply_run_styles(self, run, style, is_bullet=False):
        font = run.font
        self._set_font_family(font, style)

        # Apply font size from the main <foreignObject> style
        main_style = self.element_data.get('style', {})
        if main_style.get('fontSize'):
            try:
                font_size_px = float(re.sub(r'px$', '', main_style['fontSize']))
                scaled_font_size_px = font_size_px * self.converter.scale_y
                font.size = self.converter.px_to_pt(scaled_font_size_px)
            except (ValueError, TypeError):
                pass

        # Apply color
        color_str = style.get('color')
        # Special handling for bullet points to match example
        if is_bullet:
            color_str = "#64ffda" 
        
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
            # Fallback to the main foreignObject's font family if the run has none
            main_style = self.element_data.get('style', {})
            font_family_str = main_style.get('fontFamily')

        if not font_family_str:
            font.name = 'Calibri'
            return
        
        preferred_font = font_family_str.split(',')[0].strip().replace('"', '').replace("'", "")
        
        if preferred_font.lower() in ['sans-serif', 'system-ui']:
            font.name = 'Calibri'
        else:
            font.name = preferred_font
