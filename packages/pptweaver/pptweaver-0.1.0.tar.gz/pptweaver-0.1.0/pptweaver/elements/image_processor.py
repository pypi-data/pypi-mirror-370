import requests
from io import BytesIO
import base64
from .base_processor import BaseProcessor

class ImageProcessor(BaseProcessor):
    """
    Processes <image> SVG elements.
    """
    def process(self):
        params = self.get_shape_params()
        if not params:
            return

        left, top, width, height = params
        
        href = self.element_data.get('attributes', {}).get('href')
        if not href:
            return

        try:
            image_stream = self._get_image_stream(href)
            if image_stream:
                self.slide.shapes.add_picture(image_stream, left, top, width, height)
        except Exception as e:
            print(f"Could not process image {href}: {e}") # Using print for visibility

    def _get_image_stream(self, href):
        """
        Fetches image data from a URL or decodes a Data URI.
        Returns a file-like object (BytesIO).
        """
        if href.startswith('data:image'):
            # Handle Data URI
            header, encoded = href.split(',', 1)
            image_data = base64.b64decode(encoded)
            return BytesIO(image_data)
        elif href.startswith(('http://', 'https://')):
            # Handle URL
            response = requests.get(href, stream=True)
            response.raise_for_status()
            # It's important to use a BytesIO stream
            image_stream = BytesIO()
            for chunk in response.iter_content(1024):
                image_stream.write(chunk)
            image_stream.seek(0)
            return image_stream
        else:
            # Handle local file paths if necessary in the future
            return None
