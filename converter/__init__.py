import json


def serialize(filename, data):
    with open(filename, 'w') as f:
        f.write(json.dumps(data, separators=(',', ':')))
