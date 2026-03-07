import base64
from pathlib import Path


def image_to_base64(relative_path: str) -> str:
    image_path = Path(relative_path)
    return base64.b64encode(image_path.read_bytes()).decode()
