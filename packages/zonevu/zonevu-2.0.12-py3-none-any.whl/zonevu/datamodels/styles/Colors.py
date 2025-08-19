"""
Color related utilities
"""

#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#

from typing import Union, Tuple
from strenum import StrEnum


class RgbType(StrEnum):
    """RGB value range variant: 0-1 or 0-255."""
    Rgb1 = 'Rgb1'
    Rgb255 = 'Rgb255'


def decode_html_color(color: str, rgb_type: RgbType) -> Union[str, Tuple[float, float, float]]:
    """
    Convert HTML color string to a typical python style color. Html rgb values are in range [0, 255]
    @param rgb_type: range of rgb values
    @param color: and html color string that is either a well known HTML color string or a html rgb string
    @return: a python compatible color
    """
    if color.startswith('rgb'):
        r: int
        g: int
        b: int
        r, g, b = map(int, color[color.index('(') + 1:color.index(')')].split(','))
        divisor = 1 if rgb_type == RgbType.Rgb255 else 255
        output = (r / divisor, g / divisor, b / divisor)
        return output
    else:
        return color

