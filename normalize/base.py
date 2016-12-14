import json
from collections import OrderedDict

import requests


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

    def analise(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError


class MultipleXWingDataNormalizer:
    source_keys = []
    root = '/home/lvisintini/src/xwing-data/data'

    def __init__(self):
        self.data = {}
        for sk in self.source_keys:
            self.load_data(sk)
        print('BEFORE --------')
        self.analise()
        self.normalize()
        print('\nAFTER ---------')
        self.analise()
        for sk in self.source_keys:
            self.save_data(sk)


    def load_data(self, source_key):
        with open('{}/{}.js'.format(self.root, source_key), 'r') as file_object:
            self.data[source_key] = json.load(file_object, object_pairs_hook=OrderedDict)

    def save_data(self, source_key):
        with open('{}/{}.js'.format(self.root, source_key), 'w') as file_object:
            json.dump(self.data[source_key], file_object, indent=2)

    def analise(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError


class MemoryLoader:
    memory_url = None

    def __init__(self):
        self.memory = {}
        self.load_memory()
        super().__init__()

    def load_memory(self):
        if self.memory_url:
            print('Loading Memory...')
            response = requests.get(self.memory_url)
            for m in response.json():
                if 'id' in m:
                    self.memory[m['name']] = m['id']
            print('Loading Memory...Done!')