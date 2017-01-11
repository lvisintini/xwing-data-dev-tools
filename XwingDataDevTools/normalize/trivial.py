import datetime
import re
from pprint import pprint

from XwingDataDevTools.normalize.base import (
    MultipleDataAnalyticalNormalizer, MultipleDataAnalyzer, SingleDataAnalyzer
)


class RangeToString(MultipleDataAnalyticalNormalizer):
    source_keys = ['upgrades', 'ships']

    def analise(self):
        strings = set()
        integers = set()
        other = set()

        for key in self.data.keys():
            for m in self.data[key]:
                a = m.get('range')
                if isinstance(a, int):
                    integers.add(a)
                elif isinstance(a, str):
                    strings.add(a)
                else:
                    other.add(a)

        print('strings:', strings)
        print('integers:', integers)
        print('other:', other)

    def normalize(self):
        for key in self.data.keys():
            for model in self.data[key]:
                if isinstance(model.get('range'), int):
                    model['range'] = str(model['range'])


class AttackToInt(MultipleDataAnalyticalNormalizer):
    source_keys = ['upgrades', 'ships', 'pilots']

    def analise(self):
        strings = set()
        integers = set()
        other = set()

        for key in self.data.keys():
            for m in self.data[key]:
                if key == 'pilots':
                    a = m.get('ship_override', {}).get('attack')
                else:
                    a = m.get('attack')
                if isinstance(a, int):
                    integers.add(a)
                elif isinstance(a, str):
                    strings.add(a)
                else:
                    other.add(a)

        print('strings:', strings)
        print('integers:', integers)
        print('other:', other)

    def normalize(self):
        for key in self.data.keys():
            for model in self.data[key]:
                if key == 'pilots':
                    if isinstance(model.get('ship_override', {}).get('attack'), str):
                        model['ship_override']['attack'] = int(model['ship_override']['attack'])
                else:
                    if isinstance(model.get('attack'), str):
                        model['attack'] = int(model['attack'])


class EnergyToInt(MultipleDataAnalyticalNormalizer):
    source_keys = ['upgrades', 'ships']

    def analise(self):
        strings = set()
        integers = set()
        other = set()

        for key in self.data.keys():
            for m in self.data[key]:
                a = m.get('energy')
                if isinstance(a, int):
                    integers.add(a)
                elif isinstance(a, str):
                    strings.add(a)
                else:
                    other.add(a)

        print('strings:', strings)
        print('integers:', integers)
        print('other:', other)

    def normalize(self):
        for key in self.data.keys():
            for model in self.data[key]:
                if isinstance(model.get('energy'), str):
                    model['energy'] = int(model['energy'])


class IconList(MultipleDataAnalyzer):
    source_keys = [
        'upgrades', 'ships', 'pilots', 'conditions', 'damage-deck-core', 'damage-deck-core-tfa',
    ]

    def analise(self):
        icons = []
        reg = re.compile(r'\[.*?\]')
        for key in self.data.keys():
            for model in self.data[key]:
                for t in ['text', 'effect']:
                    icons.extend(reg.findall(model.get(t, '')))
        print(set(icons))


class ShipNames(SingleDataAnalyzer):
    source_key = 'ships'

    def analise(self):
        names = []
        for model in self.data:
            names.append(model.get('name'))
        pprint(names)


class ShipsByReleaseDate(SingleDataAnalyzer):
    source_key = 'sources'

    def analise(self):
        today = datetime.date.today().isoformat()
        self.data = sorted(
            self.data,
            key=lambda s: (s.get('release_date', today), s.get('sku', 'SWX999'))
        )
        ships_by_release_date = []
        for model in self.data:
            for ship in model.get('contents', {}).get('ships', []):
                if isinstance(ship, dict):
                    ship_name = ship['name']
                else:
                    ship_name = ship

                if ship not in ships_by_release_date:
                    ships_by_release_date.append(ship_name)

        pprint(ships_by_release_date)


if __name__ == '__main__':
    pass
    RangeToString()
    AttackToInt()
    EnergyToInt()
    IconList()
    ShipNames()
    ShipsByReleaseDate()

