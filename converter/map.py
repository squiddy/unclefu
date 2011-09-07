import os
from collections import namedtuple
from struct import calcsize

from converter import serialize, unpack_file


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
        self.nav_data_size = unpack_file('IBBHIIIII', f)

        self._read_grid(f)
        self._read_block_table(f, self.block_size)
        self._read_object_positions(f, self.object_pos_size)
        self._read_navigation_data(f, self.nav_data_size)

    def _read_grid(self, f):
        grid_columns = unpack_file('I' * 256 * 256, f)
        column_iter = iter(unpack_file('H' * (self.column_size / 2), f))

        cube_stack_table = {}
        pos = 0
        try:
            while True:
                d = column_iter.next()
                cubes = 6 - d

                cube_stack_table[pos] = [column_iter.next() for i in range(cubes)]
                pos += 2 * (1 + cubes)
        except StopIteration:
            pass

        self.grid = []
        for column in grid_columns:
            stack = cube_stack_table[column]
            self.grid.append(stack)

    def _read_block_table(self, f, size):
        block_struct = 'HBBBBBB'

        self.block_table = []
        for i in range(size / calcsize(block_struct)):
            block = Block(*unpack_file(block_struct, f))
            self.block_table.append(block)

    def _read_navigation_data(self, f, size):
        nav_struct = 'BBBBB30s'
        self.districts = []

        f.seek(-size, os.SEEK_END)
        for i in range(size / calcsize(nav_struct)):
            data = unpack_file(nav_struct, f)
            self.districts.append(District(*data))

    def _read_object_positions(self, f, size):
        object_pos_struct = 'HHHBBHHH'
        block_size = calcsize(object_pos_struct)

        self.object_pos = []
        for i in range(size / block_size):
            data = unpack_file(object_pos_struct, f)
            self.object_pos.append(ObjectPos(*data))

    def export(self):
        serialize('_build/map.json', self.grid)
        serialize('_build/blocks.json', [x.data() for x in self.block_table])
        serialize('_build/object_pos.json', [(o.x, o.y, o.z, o.type, o.remap >= 128, o.rotation / 1024.0 * 360) for o in self.object_pos])
