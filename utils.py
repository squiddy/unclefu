from converter.style import Style


def extract_car_sprites(s, color):
    for index, car_info in enumerate(s.car_infos):
        vtype_name = {
            0: 'bus',
            3: 'bike',
            4: 'car',
            8: 'train'
        }.get(car_info.vtype, 'car')

        sprite_offset = s.sprite_offset[vtype_name]
        sprite = s.sprites.sprites[car_info.sprite_num + sprite_offset]

        x = sprite.x 
        y = sprite.page * 256 + sprite.y

        sprite_img = color.crop((x, y, x + sprite.width, y + sprite.height)).copy()
        sprite_img.save('/tmp/cars/%03d.png' % index, 'png')


def extract_object_sprites(s, color):
    sprite_offset = s.sprite_offset['object']
    count = s.sprite_numbers.object

    for index, sprite in enumerate(s.sprites.sprites[sprite_offset:sprite_offset+count]):
        x = sprite.x
        y = sprite.page * 256 + sprite.y

        sprite_img = color.crop((x, y, x + sprite.width, y + sprite.height)).copy()
        sprite_img.save('/tmp/object/%03d.png' % index, 'png')


def extract_ped_sprites(s, color):
    sprite_offset = s.sprite_offset['ped']
    count = s.sprite_numbers.ped

    for index, sprite in enumerate(s.sprites.sprites[sprite_offset:sprite_offset+count]):
        x = sprite.x
        y = sprite.page * 256 + sprite.y

        sprite_img = color.crop((x, y, x + sprite.width, y + sprite.height)).copy()
        sprite_img.save('/tmp/ped/%03d.png' % index, 'png')


if __name__ == '__main__':
    s = Style()
    s.load_from_file(open('gtadata/STYLE001.G24', 'r'))
    color = s.sprites.colorize()

    extract_car_sprites(s, color)
    extract_object_sprites(s, color)
    extract_ped_sprites(s, color)
