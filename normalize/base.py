import json
from collections import OrderedDict


class XWingDataNormalizer:
    source_key = ''
    root = '/home/lvisintini/src/xwing-data/data'

    def __init__(self):
        self.data = []
        self.load_data()
        print('BEFORE --------')
        self.analise()
        self.normalize()
        print('\nAFTER ---------')
        self.analise()
        self.save_data()

    def load_data(self):
        with open('{}/{}.js'.format(self.root, self.source_key), 'r') as file_object:
            self.data.extend(json.load(file_object, object_pairs_hook=OrderedDict))

    def save_data(self):
        with open('{}/{}.js'.format(self.root, self.source_key), 'w') as file_object:
            json.dump(self.data, file_object, indent=2)

    def filter(self, model):
        raise NotImplementedError

    def analise(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError
