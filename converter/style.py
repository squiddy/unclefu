import itertools
import StringIO
import struct
from collections import namedtuple
from struct import unpack, unpack_from, calcsize

from PIL import Image

from converter import serialize, unpack_file


class PaletteIndex(object):
    """
    Contains all palettes (and mappings) for tiles and sprites. 
    """

    def __init__(self, tile_index_size):
        self.tile_index_size = tile_index_size

    def read_palettes(self, data, size):
        data = StringIO.StringIO(data)

        palette_count = size / 1024
        self.palettes = [[] for i in range(palette_count)]

        for k in range(palette_count / 64):
            for j in range(256):
                for i in range(64):
                    b, g, r, x = unpack_file('BBBB', data)
                    self.palettes[k*64+i].extend((r, g, b))

        k = palette_count / 64
        for j in range(256):
            for i in range(palette_count % 64):
                b, g, r, x = unpack_file('BBBB', data)
                self.palettes[k*64 + i].extend((r, g, b))

    def read_index(self, data, size):
        self.index = unpack_from('H' * (size / 2), data)

    def lookup_for_tile(self, tile):
        return self.palettes[self.index[4 * tile]]

    def lookup_for_sprite(self, sprite):
        return self.palettes[self.index[self.tile_index_size + sprite]]


class Sprite(object):

    def __init__(self, info_data, graphics_data, p):
        self.graphics_data = graphics_data
        self.sprites = []
        self.p = p

        self.width = 256
        self.height = len(self.graphics_data) / 256

        self._read_info(info_data)

    def _read_info(self, data):
        SpriteInfo = namedtuple('SpriteInfo', 'width height delta_count scaling_flag size clut x y page')

        try:
            while True:
                s = SpriteInfo(*unpack_from('BBBBHHBBH', data.read(12)))
                for i in range(s.delta_count):
                    data.read(6)

                self.sprites.append(s)
        except struct.error:
            # TODO handle end of data better
            pass

        print "sprites:", len(self.sprites)

    def colorize(self):
        original = Image.fromstring('P', (self.width, self.height), self.graphics_data)

        # Palette index 0 should be transparent, track the locations so we can
        # make them transparent at the end
        transparent = []
        pix = original.load()
        for x, y in itertools.product(range(self.width), range(self.height)):
            if pix[x, y] == 0:
                transparent.append((x, y))

        img = Image.new('RGB', original.size)
        img = img.convert('RGBA')
        for i, sprite in enumerate(self.sprites):
            x = sprite.x 
            y = sprite.page * self.width + sprite.y

            sprite_img = original.crop((x, y, x + sprite.width, y + sprite.height)).copy()
            sprite_img.putpalette(self.p.lookup_for_sprite(sprite.clut))
            img.paste(sprite_img, (x, y, x + sprite.width, y + sprite.height))

        pix = img.load()
        for x,y in transparent:
            pix[x,y] = (0, 0, 0, 0)

        img.save('_build/sprites.png', 'png')
        return img


class Style(object):

    def load_from_file(self, f):
        # Header
        self.version, self.side_size, self.lid_size, self.aux_size, \
        self.anim_size, self.clut_size, self.tileclut_size, self.spriteclut_size, \
        self.newcarclut_size, self.fontclut_size, self.palette_index_size, \
        self.object_info_size, self.car_size, self.sprite_info_size, \
        self.sprite_graphics_size, self.sprite_numbers_size = unpack_file('I' * 16, f)

        # Tiles
        size = self.side_size + self.lid_size + self.aux_size
        if size % (64 * 64 * 4):
            size += (64 * 64 * 4) - (size % (64 * 64 * 4))
        side_lid_aux = f.read(size)

        # Animations
        self._read_animations(f, self.anim_size)

        # Palette
        clut = f.read(self.clut_size)
        if self.clut_size % (64 * 1024):
            f.read(64*1024 - (self.clut_size % (64*1024)))

        palette_index_data = f.read(self.palette_index_size)
        self.palette_index = PaletteIndex(tile_index_size=self.tileclut_size / 1024)
        self.palette_index.read_palettes(clut, self.clut_size)
        self.palette_index.read_index(palette_index_data, self.palette_index_size)

        # Object infos
        self._read_object_info(f, self.object_info_size)

        # Car infos
        self._read_car_infos(f, self.car_size)

        # Sprites
        sprite_info = f.read(self.sprite_info_size)
        sprite_graphics = f.read(self.sprite_graphics_size)
        self._read_sprite_numbers(f, self.sprite_numbers_size)

        self.sprites = Sprite(StringIO.StringIO(sprite_info), sprite_graphics, self.palette_index)
        self.sprites.colorize()

        self.colorize_tiles(side_lid_aux, self.palette_index)

    def _create_sprite_texture_coordinates(self):
        groups = ('car', 'object', )
        result = {}
        width = 256.0
        height = 4442.0

        for g in groups:
            sprite_offset = self.sprite_offset[g]
            count = getattr(self.sprite_numbers, g)
            result[g] = []

            for index, sprite in enumerate(self.sprites.sprites[sprite_offset:sprite_offset+count]):
                x = sprite.x
                y = sprite.page * 256 + sprite.y

                coords = (sprite.width, sprite.height, x / width, y / height, (x + sprite.width) / width, (y + sprite.height) / height)
                result[g].append(coords)

        return result

    def _read_sprite_numbers(self, f, size):
        fields = 'arrow digits boat bux bus car object ped speedo tank ' \
                 'traffic_lights train trdoors bike tram wbus wcar ex ' \
                 'tumcar tumtruck ferry'

        SpriteNumbers = namedtuple('SpriteNumbers', fields)
        self.sprite_numbers = SpriteNumbers(*unpack_file('H' * (size / 2), f))
        self.sprite_offset = {}

        for i, field in enumerate(SpriteNumbers._fields):
            fields_before = SpriteNumbers._fields[:i]
            self.sprite_offset[field] = sum(getattr(self.sprite_numbers, f) for f in fields_before)

        print "sprite numbers: ", ', '.join(("%d %s" % (v, k) for (k, v) in self.sprite_numbers._asdict().items()))

    def _read_car_infos(self, f, size):
        fields = 'width height depth sprite_num weight max_speed min_speed acceleration braking grip handling ' \
                 'remap24 remap8 ' \
                 'vtype model turning damageable value mass_center_x mass_center_y moment ' \
                 'rbp_mass g1_thrust tyre_adhesion_x tyre_adhesion_y handbrake_friction footbrake_friction front_brake_bias ' \
                 'turn_ratio drive_wheel_offset ' \
                 'back_end_slide_value handbrake_slide_value ' \
                 'convertible engine radio horn sound_function fast_change_flag door_count doors'

        CarInfo = namedtuple('CarInfo', fields)

        hls_info_struct = 'hhh'
        door_info_struct = 'HHHH'

        fixed_to_float = lambda x: x * (1.0 / 2**16)

        start = f.tell()
        self.car_infos = []

        while f.tell() < start + size:
            data = list(unpack_file('hhhhhhhhhhh', f))
            data += [[unpack_file(hls_info_struct, f) for i in range(12)]]
            data += [unpack_file('B' * 12, f)]
            data += unpack_file('BBBB', f)
            data += [unpack_file('HHHH', f)]
            data += unpack_file('bb i', f)
            data += map(fixed_to_float, unpack_file('iiiiiii', f))
            data += unpack_file('hh', f)
            data += map(fixed_to_float, unpack_file('ii', f))
            data += unpack_file('BBBBBB', f)

            door_count, = unpack_file('h', f)
            doors = []
            for j in range(door_count):
                doors.append(unpack_file('hhhh', f))

            data += [door_count, doors]
            self.car_infos.append(CarInfo(*data))

        print "car infos:", len(self.car_infos)

    def _read_animations(self, f, size):
        Animation = namedtuple('Animation', 'block which speed frame_count frames')
        self.animations = []

        count, = unpack('B', f.read(1))
        for i in range(count):
            data = list(unpack('BBBB', f.read(4)))
            data.append(unpack('B' * data[3], f.read(data[3])))
            self.animations.append(Animation(*data))

        print "animations:", len(self.animations)

    def _read_object_info(self, f, size):
        ObjectInfo = namedtuple('ObjectInfo', 'width height depth sprite_num')

        object_info_struct = 'IIIHxxxxxx'
        block_size = calcsize(object_info_struct)

        self.object_infos = []
        for i in range(size / block_size):
            data = unpack_file('IIIHxxxxxx', f)
            self.object_infos.append(ObjectInfo(*data))

        print "object infos:", len(self.object_infos)

    def colorize_tiles(self, tiles, palette_index):
        width = 256
        height = len(tiles) / width
        tile_size = 64

        orig_tiles = Image.fromstring('P', (width, height), tiles)

        img = Image.new('RGBA', (2048, 2048))
        for tile in range(len(tiles) / tile_size**2):
            stx = tile % 4
            sty = tile / 4

            coords = ((stx * tile_size, sty * tile_size, (stx + 1) * tile_size, (sty + 1) * tile_size))
            tile_image = orig_tiles.crop(coords).copy()

            # Keep track of pixels that become transparent after applying
            # the palette
            transparent = []
            pix = tile_image.load()
            for x,y in itertools.product(range(tile_size), range(tile_size)):
                if pix[x, y] == 0:
                    transparent.append((x, y))

            tile_image.putpalette(palette_index.lookup_for_tile(tile))
            tile_image = tile_image.convert('RGBA')

            # Paste non-transparent version on final image
            dtx = tile % (2048 / 64)
            dty = tile / (2048 / 64)
            coords = ((dtx * tile_size, dty * tile_size, (dtx + 1) * tile_size, (dty + 1) * tile_size))
            img.paste(tile_image, coords)

            # Make pixels transparent
            pix = tile_image.load()
            for x, y in transparent:
                pix[x, y] = (0, 0, 0, 0)

            # Paste transparent version on final image
            tile += 384
            dtx = tile % (2048 / 64)
            dty = tile / (2048 / 64)
            coords = ((dtx * tile_size, dty * tile_size, (dtx + 1) * tile_size, (dty + 1) * tile_size))
            img.paste(tile_image, coords)

        img.save('_build/tiles.png', 'png')

    def export(self):
        serialize('_build/sprites.json', self._create_sprite_texture_coordinates())
        serialize('_build/car_info.json', [(c.sprite_num, ) for c in self.car_infos])
        serialize('_build/object_info.json', self.object_infos)
