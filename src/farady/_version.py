# Copyright (C) 2018-2026  Adam Ahmed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["__version__", "__version_tuple__", "version", "version_tuple"]

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Tuple
    from typing import Union

    VERSION_TUPLE = Tuple[Union[int, str], ...]
else:
    VERSION_TUPLE = object

version: str
__version__: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE

__version__ = version = "0.1.0.post1.dev0+g670ee68.d20260223"
__version_tuple__ = version_tuple = (0, 1, 0, "post1", "dev0", "g670ee68.d20260223")
