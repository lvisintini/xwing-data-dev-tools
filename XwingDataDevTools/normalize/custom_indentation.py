import _ctypes
import json
import re

from XwingDataDevTools.normalize.base import SingleDataNormalizer

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


class SameLineData(SingleDataNormalizer):
    @staticmethod
    def filter(model):
        raise True

    def save_data(self):
        with open('{}/{}.js'.format(self.root, self.source_key), 'w') as file_object:
            file_object.write(
                json.dumps(self.data, indent=2, cls=NoIndentEncoder, ensure_ascii=False)
            )


class SameLineShipsNormalizer(SameLineData):
    source_key = 'ships'

    def normalize(self):
        for model in self.data:
            model['maneuvers'] = [NoIndent(speed) for speed in model['maneuvers']]
            if 'maneuvers_energy' in model:
                model['maneuvers_energy'] = [
                    NoIndent(speed) for speed in model['maneuvers_energy']
                ]


class SameLineSourcesNormalizer(SameLineData):
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

            if 'conditions' in model['contents']:
                model['contents']['conditions'] = [
                    NoIndent(condition) for condition in model['contents']['conditions']
                ]


class SameLinePilotsNormalizer(SameLineData):
    source_key = 'pilots'

    def normalize(self):
        for model in self.data:
            model['ship'] = NoIndent(model['ship'])
            if 'conditions' in model:
                model['conditions'] = [NoIndent(cond) for cond in model['conditions']]


class SameLineUpgradesNormalizer(SameLineData):
    source_key = 'upgrades'

    def normalize(self):
        for model in self.data:
            if 'conditions' in model:
                model['conditions'] = [NoIndent(cond) for cond in model['conditions']]
            if 'ship' in model:
                model['ship'] = [NoIndent(ship) for ship in model['ship']]
            if 'ships' in model:
                model['ships'] = [NoIndent(ship) for ship in model['ships']]
            if 'grants' in model:
                model['grants'] = [NoIndent(grant) for grant in model['grants']]


def same_line_indent():
    SameLineShipsNormalizer()
    SameLineSourcesNormalizer()
    SameLinePilotsNormalizer()
    SameLineUpgradesNormalizer()


if __name__ == '__main__':
    same_line_indent()
