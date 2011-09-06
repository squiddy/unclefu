import itertools
import json
import os

from collections import namedtuple
from struct import unpack, calcsize

import numpy as np


ObjectPos = namedtuple('ObjectPos', 'x y z type remap rotation pitch roll')
District = namedtuple('District', 'x y width height index name')

class Block(namedtuple('Block', 'type_map type_map_ext left right top bottom lid')):

    @property
    def block_type(self):
        return (self.type_map >> 4) & 3

    @property
    def lid_rotation(self):
        return (self.type_map >> 14) & 3

    @property
    def flat(self):
        return self.type_map & 2**7

    @property
    def slope(self):
        return (self.type_map >> 8) & (2**6 - 1)

    def data(self):
        return [self.block_type, self.left, self.right, self.top,
                self.bottom, self.lid, self.lid_rotation, self.flat,
                self.slope]


class Map(object):

    def load_from_file(self, f):
        self.version, self.style, self.sample, _, self.route_size, \
        self.object_pos_size, self.column_size, self.block_size, \
        self.nav_data_size = unpack('IBBHIIIII', f.read(28))

        grid_size = 256 * 256;
        self.grid = np.fromstring(f.read(grid_size * 4), dtype=np.uint32).reshape((256, 256))

        table = iter(np.fromstring(f.read(self.column_size), dtype=np.int16))

        self.cube_stack_table = {}
        pos = 0
        try:
            while True:
                d = table.next()
                cubes = 6 - d

                self.cube_stack_table[pos] = [table.next() for i in range(cubes)]
                pos += 2 * (1 + cubes)
        except StopIteration:
            pass

        self.block_table = []
        for i in range(self.block_size / 8):
            self.block_table.append(Block(*unpack('HBBBBBB', f.read(8))))

        self._read_object_positions(f, self.object_pos_size)

        self.districts = []

        f.seek(-self.nav_data_size, os.SEEK_END)
        for i in range(self.nav_data_size / 35):
            data = unpack('BBBBB30s', f.read(35))
            self.districts.append(District(*data))

        a = []
        for (x, y) in itertools.product(range(256), range(256)):
            column = self.cube_stack_table[self.grid[x, y]]
            a.append(map(int, column))

        with open('_build/map.json', 'w') as f:
            f.write(json.dumps(a, separators=(',',':')))

        with open('_build/blocks.json', 'w') as f:
            f.write(json.dumps([x.data() for x in self.block_table], separators=(',',':')))

    def _read_object_positions(self, f, size):
        object_pos_struct = 'HHHBBHHH'
        block_size = calcsize(object_pos_struct)

        object_pos = []
        for i in range(size / block_size):
            data = unpack(object_pos_struct, f.read(block_size))
            object_pos.append(ObjectPos(*data))

        with open('_build/object_pos.json', 'w') as f:
            f.write(json.dumps([(o.x, o.y, o.z, o.type, o.remap >= 128, o.rotation / 1024.0 * 360) for o in object_pos], separators=(',',':')))