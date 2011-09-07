#!/usr/bin/env python

"""
Parse the NYC map and its corresponding style file. Converted data is stored
in the _build directory.
"""

from converter.map import Map


m = Map()
m.load_from_file(open('data/NYC.CMP'))
m.export()
