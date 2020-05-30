# -*- coding: utf-8 -*-
"""
.utils
========================
App common tool function.
"""

import os
import time
import codecs
from datetime import datetime


def unit_size(size):
    """ Convert Byte size to KB/MB/GB/TB.
    """
    units = ['KB', 'MB', 'GB', 'TB']
    i = 0
    size = size / 1024
    while size >= 1024 and i<(len(units)-1):
        i = i + 1
        size = size / 1024
    return '%.2f %s'%(size, units[i])

def standard_timestr(localtime):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(localtime))

_TEXT_BOMS = (
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
    codecs.BOM_UTF8,
)

def is_binary_file(filepath):
    with open(filepath, 'rb') as file:
        initial_bytes = file.read(8192)
        file.close()
    return not any(initial_bytes.startswith(bom) for bom in _TEXT_BOMS) and b'\0' in initial_bytes
