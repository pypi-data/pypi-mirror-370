import io
import os
import re
import base64
from typing import Optional
from urllib.parse import urlparse
from PIL import Image as PILImage


class Utils:
    @staticmethod
    def to_data_url(image: PILImage.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:image/png;base64,{base64_string}"

    @staticmethod
    def unwrap(key: str, text: str) -> Optional[str]:
        pattern = f"<{key}>(.*?)</{key}>"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return None

    @staticmethod
    def get_extension(url: str) -> Optional[str]:
        parsed_url = urlparse(url)
        _, extension = os.path.splitext(parsed_url.path)
        if "." in extension:
            return extension[1:]
        else:
            return None
