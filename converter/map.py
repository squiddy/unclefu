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

        grid_size = 256 * 256
        self.grid = unpack_file('I' * grid_size, f)

        column_iter = iter(unpack_file('H' * (self.column_size / 2), f))

        self.cube_stack_table = {}
        pos = 0
        try:
            while True:
                d = column_iter.next()
                cubes = 6 - d

                self.cube_stack_table[pos] = [column_iter.next() for i in range(cubes)]
                pos += 2 * (1 + cubes)
        except StopIteration:
            pass

        self.block_table = []
        for i in range(self.block_size / 8):
            self.block_table.append(Block(*unpack_file('HBBBBBB', f)))

        self._read_object_positions(f, self.object_pos_size)

        self.districts = []

        f.seek(-self.nav_data_size, os.SEEK_END)
        for i in range(self.nav_data_size / 35):
            data = unpack_file('BBBBB30s', f)
            self.districts.append(District(*data))

        a = []
        for i in range(grid_size):
            column = self.cube_stack_table[self.grid[i]]
            a.append(column)

        serialize('_build/map.json', a)
        serialize('_build/blocks.json', [x.data() for x in self.block_table])

    def _read_object_positions(self, f, size):
        object_pos_struct = 'HHHBBHHH'
        block_size = calcsize(object_pos_struct)

        object_pos = []
        for i in range(size / block_size):
            data = unpack_file(object_pos_struct, f)
            object_pos.append(ObjectPos(*data))

        serialize('_build/object_pos.json', [(o.x, o.y, o.z, o.type, o.remap >= 128, o.rotation / 1024.0 * 360) for o in object_pos])
