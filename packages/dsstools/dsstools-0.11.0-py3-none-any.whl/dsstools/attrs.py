# Copyright (C) 2025 dssTools Developers
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Interaction between nx.NodeDataViews and imported attributes."""
import sys
from enum import auto
from typing import NamedTuple

# This is obsolete in 3.11 and can be replaced wit StrEnum
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from strenum import LowercaseStrEnum as StrEnum

class Category(StrEnum):
    """Enum providing for categorizing internal codes.

    The following values are accepted:
    TEXT: Used for terms in text. This code is representative of a term found in
    a node text.
    MANUAL: Used for manually created codes in dssCode (or other sources).
    """
    TEXT = auto()
    MANUAL = auto()


class Code(NamedTuple):
    """Helper tuple class for passing complex arguments as node attributes."""
    term: str
    category: Category

    def __str__(self):
        # NOTE If we bump the condition for Python up to 3.11 we can replace
        # this whole module with a basic StrEnum implementation.
        return f"{self.category}:{self.term}"

    def to_str(self):
        """Convert the code to string."""
        return str(self)
