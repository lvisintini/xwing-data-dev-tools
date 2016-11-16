import json
from collections import OrderedDict

from base import XWingDataNormalizer


class SourcesForeignKey(XWingDataNormalizer):
    source_key = 'sources'

    min_maneuvers_override = 10

    def __init__(self):
        self.ships = []
        with open('{}/{}.js'.format(self.root, 'ships'), 'r') as file_object:
            self.ships.extend(json.load(file_object, object_pairs_hook=OrderedDict))
        super().__init__()

    def analise(self):
        print(len(self.ships))
        print(max([s['id'] for s in self.ships if s.get('id')]))
        print([s['name'] for s in self.ships if s.get('id') is None])

    def normalize(self):
        for model in self.data:
            fks = {}
            for ship_name, qty in model['contents'].get('ships', {}).items():
                ship_id = next((ship['id'] for ship in self.ships if ship['name'] == ship_name))
                fks[ship_id] = qty
            model['contents']['ships'] = fks

if __name__ == '__main__':
    print('ShipsIds')
    SourcesForeignKey()
