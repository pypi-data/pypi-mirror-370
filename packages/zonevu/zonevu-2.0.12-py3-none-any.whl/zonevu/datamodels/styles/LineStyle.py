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

"""
Line style definition.

Specifies color, width, and pattern for line features in visualizations.
"""

from dataclasses import dataclass
from typing import Union, Tuple
from dataclasses_json import dataclass_json, LetterCase
from ..styles.Colors import decode_html_color, RgbType


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class LineStyle:
    """Line styling: color, thickness, dash pattern, and visibility."""
    show: bool = True  # Master switch
    color: str = 'gray'  # Css color string
    thickness: float = 1  # Thickness of the line
    dashed: bool = False  # Whether the line is dashed

    @staticmethod
    def FromRGB(r: int, g: int, b: int) -> 'LineStyle':
        style = LineStyle()
        style.color = 'rgb(%s,%s,%s)' % (r, g, b)
        return style

    def get_color(self, rgb_type: RgbType) -> Union[str, Tuple[float, float, float]]:
        return decode_html_color(self.color, rgb_type)
