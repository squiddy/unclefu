#!/usr/bin/env python

"""
Parse the NYC map and its corresponding style file. Converted data is stored
in the _build directory.
"""

from converter.map import Map
from converter.style import Style


print "parsing map ..."
m = Map()
m.load_from_file(open('data/NYC.CMP'))

print "parsing style ..."
s = Style()
s.load_from_file(open('data/STYLE00%d.G24' % m.style))

print "done"
