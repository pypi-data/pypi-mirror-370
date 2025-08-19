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
3D coordinate (x, y, z)
"""

from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
import math
from vectormath import Vector3


@dataclass
class Coordinate(DataClassJsonMixin):
    """3D coordinate with optional rotation and vector helpers."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    x: float = 0
    y: float = 0
    z: float = 0

    @property
    def tuple(self) -> (float, float):
        return self.x, self.y

    @property
    def vector(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    def rotate(self, angle: float) -> 'Coordinate':
        """
        Rotates this point around the origin by an angle on the 2-dimensional plane
        @param angle: angle from x-axis in radians
        @return: the rotated point
        """
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Coordinate(x, y)

    def __add__(self, other: 'Coordinate') -> 'Coordinate':
        return Coordinate(self.x + other.x, self.y + other.y, self.z + other.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        if isinstance(other, Coordinate):
            return (self.x, self.y, self.z) == (other.x, other.y, other.z)
        return False

    @staticmethod
    def distance(c1: 'Coordinate', c2: 'Coordinate') -> float:
        dx = c1.x - c2.x
        dy = c1.y - c2.y
        dz = c1.z - c2.z
        dd = dx * dx + dy * dy + dz * dz
        d = math.sqrt(dd)
        return d

    @staticmethod
    def within(c: 'Coordinate', c1: 'Coordinate', c2: 'Coordinate') -> bool:
        # Test if c is within the rectangular region defined by c1 and c2, where c2 > c1.
        is_within = c1.x <= c.x <= c2.x and c1.y <= c.y <= c2.y
        return is_within


