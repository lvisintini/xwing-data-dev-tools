from base import MultipleXWingDataNormalizer


class RangeToString(MultipleXWingDataNormalizer):
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


class AttackToInt(MultipleXWingDataNormalizer):
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


class EnergyToInt(MultipleXWingDataNormalizer):
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


if __name__ == '__main__':
    print('RangeToString')
    RangeToString()

    print('Attack')
    AttackToInt()

    print('EnergyToInt')
    EnergyToInt()