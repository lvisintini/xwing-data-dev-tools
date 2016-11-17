import json
from collections import OrderedDict

from base import XWingDataNormalizer


class SourcesForeignKey(XWingDataNormalizer):
    source_key = 'sources'

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


class SourcesForeignKey2(XWingDataNormalizer):
    source_key = 'sources'

    @staticmethod
    def analise():
        print('No data to show')

    def normalize(self):
        for model in self.data:
            fks = []
            for ship_id, qty in model['contents'].get('ships', {}).items():
                fks.append(OrderedDict({'ship_id': int(ship_id), 'amount': qty}))
            model['contents']['ships'] = fks

            fks = []
            for pilot_id, qty in model['contents'].get('pilots', {}).items():
                fks.append(OrderedDict({'pilot_id': int(pilot_id), 'amount': qty}))
            model['contents']['pilots'] = fks

            fks = []
            for upgrade_id, qty in model['contents'].get('upgrades', {}).items():
                fks.append(OrderedDict({'upgrade_id': int(upgrade_id), 'amount': qty}))
            model['contents']['upgrades'] = fks


if __name__ == '__main__':
    print('SourcesForeignKey2')
    SourcesForeignKey2()
