"""
Utility functions for Glitch Lab.
"""

import os
import re


def get_frame_info(filename):
    """Wyciąga numer klatki i rozszerzenie z nazwy pliku."""
    name, ext = os.path.splitext(filename)
    if not ext:
        return None, None, None
    ext = ext[1:]
    match = re.search(r'^(.*?)(\d+)$', name)
    if match:
        prefix = match.group(1)
        frame_num = int(match.group(2))
        padding = len(match.group(2))
        return frame_num, ext, (prefix, padding)
    return None, None, None