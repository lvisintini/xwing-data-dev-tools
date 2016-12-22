from collections import OrderedDict

from XwingDataDevTools.normalize.base import MultipleXWingDataNormalizer


class FieldRenamer(MultipleXWingDataNormalizer):
    source_keys = ['ships', 'upgrades']

    mapping = {
        'ships': {
            'faction': 'factions',
        },
        'upgrades': {
            'size': 'sizes',
            'ship': 'ships',
        }
    }

    @staticmethod
    def analise():
        print('Nothing to print')

    def normalize(self):
        for sk in self.source_keys:
            for i in range(len(self.data[sk])):
                model_items = list(self.data[sk][i].items())

                for j in range(len(model_items)):
                    if model_items[j][0] in self.mapping[sk]:
                        model_items[j] = (self.mapping[sk][model_items[j][0]], model_items[j][1])

                self.data[sk][i] = OrderedDict(model_items)


if __name__ == '__main__':
    FieldRenamer()