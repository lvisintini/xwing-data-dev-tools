import json
import datetime
from collections import OrderedDict
from pprint import pprint

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
            json.dump(self.data, file_object, indent=2, ensure_ascii=False)

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
            json.dump(self.data[source_key], file_object, indent=2, ensure_ascii=False)

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


class DataCollector(XWingDataNormalizer):
    memory = {}
    field_name = None

    def __init__(self):
        super().__init__()

    def analise(self):
        pprint(self.memory)

    @staticmethod
    def print_model(model):
        print('\n' + model['name'])

    def input_text(self):
        return 'Which {} should it have?\nResponse (leave empty to skip): '.format(self.field_name)

    def clean_input(self):
        raise NotImplementedError

    def validate_input(self):
        raise NotImplementedError

    def normalize(self):
        for model in self.data:
            if self.field_name not in model:
                if model.get('id') in self.memory:
                    model[self.field_name] = self.memory[model.get('id')]
                    continue

                self.print_model(model)
                new_data = None

                while not self.validate_input(new_data):
                    if new_data is not None:
                        print('No. That value is not right!. Try again...')
                    new_data = input(self.input_text())
                    if not new_data:
                        break

                    new_data = self.clean_input(new_data)

                else:
                    model[self.field_name] = new_data
                    self.memory[model['id']] = new_data
        print('Done!!')


class DateDataCollector(DataCollector):
    input_format = None
    output_format = None

    def clean_input(self, new_data):
        try:
            new_data = datetime.datetime.strptime(new_data, self.input_format).date().isoformat()
        except:
            pass
        else:
            return new_data
        return new_data

    def validate_input(self, new_data):
        try:
            datetime.datetime.strptime(new_data, self.output_format).date()
        except:
            pass
        else:
            return True
        return False
