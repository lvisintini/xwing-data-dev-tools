import _ctypes
import json
import re

from base import XWingDataNormalizer

# http://stackoverflow.com/questions/13249415/can-i-implement-custom-indentation-for-pretty-printing-in-python-s-json-module


def di(obj_id):
    # from http://stackoverflow.com/a/15012814/355230
    """ Reverse of id() function. """
    return _ctypes.PyObj_FromPtr(obj_id)


class NoIndent(object):
    def __init__(self, value):
        self.value = value

    def to_json(self):
        return json.dumps(self.value)


class NoIndentEncoder(json.JSONEncoder):
    FORMAT_SPEC = "@@{}@@"
    regex = re.compile(FORMAT_SPEC.format(r"(\d+)"))

    def default(self, obj):
        if not isinstance(obj, NoIndent):
            return super().default(obj)
        return self.FORMAT_SPEC.format(id(obj))

    def encode(self, obj):
        format_spec = self.FORMAT_SPEC  # local var to expedite access
        result = super().encode(obj)
        for match in self.regex.finditer(result):
            id = int(match.group(1))
            result = result.replace('"{}"'.format(format_spec.format(id)),
                                    di(int(id)).to_json())
        return result


class SameLineData(XWingDataNormalizer):
    @staticmethod
    def filter(model):
        raise True

    @staticmethod
    def analise():
        print('No data to show')

    def save_data(self):
        with open('{}/{}.js'.format(self.root, self.source_key), 'w') as file_object:
            file_object.write(json.dumps(self.data, indent=2, cls=NoIndentEncoder))


class SameLineManeuverNormalizer(XWingDataNormalizer):
    source_key = 'ships'

    def normalize(self):
        for model in self.data:
            model['maneuvers'] = [NoIndent(speed) for speed in model['maneuvers']]
            if 'maneuvers_energy' in model:
                model['maneuvers_energy'] = [
                    NoIndent(speed) for speed in model['maneuvers_energy']
                ]


class SameLineSourcesNormalizer(XWingDataNormalizer):
    source_key = 'sources'

    def normalize(self):
        for model in self.data:
            model['contents']['ships'] = [
                NoIndent(ship) for ship in model['contents']['ships']
            ]
            model['contents']['pilots'] = [
                NoIndent(pilot) for pilot in model['contents']['pilots']
            ]
            model['contents']['upgrades'] = [
                NoIndent(upgrade) for upgrade in model['contents']['upgrades']
            ]


if __name__ == '__main__':
    print('SameLineManeuverNormalizer')
    SameLineManeuverNormalizer()

    print('SameLineSourcesNormalizer')
    SameLineSourcesNormalizer()
