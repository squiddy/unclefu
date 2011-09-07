import json
from struct import unpack, calcsize


def serialize(filename, data):
    with open(filename, 'w') as f:
        f.write(json.dumps(data, separators=(',', ':')))


unpack_file = lambda c, f: unpack(c, f.read(calcsize(c)))
