import datetime
from XwingDataDevTools.normalize.base import MultipleXWingDataNormalizer, XWingDataNormalizer
from pprint import pprint


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


class AddMissingSlots(XWingDataNormalizer):
    source_key = 'upgrades'

    memory = {
        294: 'Modification',
    }

    def __init__(self):
        self.slots = []
        super().__init__()

    def analise(self):
        for model in self.data:
            if model.get('slot'):
                self.slots.append(model['slot'])
        self.slots = list(set(self.slots))

    def normalize(self):
        for model in self.data:
            if 'slot' not in model:
                if model.get('id') in self.memory:
                    model['slot'] = self.memory[model.get('id')]
                print('\n' + model['name'])
                pprint()
                options = '\n\t'.join(
                    ['{} - {}'.format(i, self.slots[i]) for i in range(len(self.slots))]
                )
                modification = None
                while modification not in range(len(self.slots)):
                    if modification is not None:
                        print('No. That value is not right!. Try again...')
                    modification = input('Which slot should it have?\n\t'+ options + '\nResponse:')
                    if modification.isdigit():
                        modification = int(modification)
                model['slot'] = self.slots[int(modification)]
        print('Done!!')


class AddMissingReleaseDate(XWingDataNormalizer):
    source_key = 'sources'

    memory = {
    }

    def __init__(self):
        self.slots = []
        super().__init__()

    def analise(self):
        pprint(self.memory)

    def normalize(self):
        for model in self.data:
            if 'release_date' not in model:
                if model.get('id') in self.memory:
                    model['release_date'] = self.memory[model.get('id')]
                print()
                pprint(model)
                new_data = None
                while not isinstance(new_data, datetime.date):
                    if new_data is not None:
                        print('No. That value is not right!. Try again...')
                    new_data = input('Which release_date should it have?\nResponse: ')

                    try:
                        new_data = datetime.datetime.strptime(new_data, '%B %d, %Y').date()
                    except ValueError:
                        pass
                model['release_date'] = new_data.isoformat()
        print('Done!!')


class AddMissingAnnouncedDate(XWingDataNormalizer):
    source_key = 'sources'

    memory = {
    }

    def __init__(self):
        self.slots = []
        super().__init__()

    def analise(self):
        pprint(self.memory)

    def normalize(self):
        for model in self.data:
            if 'announced_date' not in model:
                if model.get('id') in self.memory:
                    model['announced_date'] = self.memory[model.get('id')]
                print()
                pprint(model)
                new_data = None
                while not isinstance(new_data, datetime.date):
                    if new_data is not None:
                        print('No. That value is not right!. Try again...')
                    new_data = input('Which announced_date should it have?\nResponse: ')

                    try:
                        new_data = datetime.datetime.strptime(new_data, '%B %d, %Y').date()
                    except ValueError:
                        pass
                model['announced_date'] = new_data.isoformat()
        print('Done!!')


if __name__ == '__main__':
    #print('RangeToString')
    #RangeToString()

    #print('Attack')
    #AttackToInt()

    #print('EnergyToInt')
    #EnergyToInt()

    #print('AddMissingSlots')
    #AddMissingSlots()

    print('AddMissingReleaseDate')
    AddMissingReleaseDate()
