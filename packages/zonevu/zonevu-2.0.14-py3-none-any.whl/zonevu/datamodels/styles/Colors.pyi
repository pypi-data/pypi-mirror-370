from strenum import StrEnum

class RgbType(StrEnum):
    Rgb1 = 'Rgb1'
    Rgb255 = 'Rgb255'

def decode_html_color(color: str, rgb_type: RgbType) -> str | tuple[float, float, float]: ...
