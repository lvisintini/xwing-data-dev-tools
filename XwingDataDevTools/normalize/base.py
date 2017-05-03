import json
import datetime
from collections import OrderedDict
from pprint import pprint


class XWingDataBaseMixin:
    root = '/home/lvisintini/src/xwing-data/data'


class ToolBase:
    def __init__(self):
        self.print_name()

    def print_name(self):
        print('\n{} {}'.format(self.__class__.__name__, '=' * (100 - len(self.__class__.__name__))))


class SingleDataLoaderMixin:
    source_key = ''
    root = None
    data = []

    def load_data(self):
        with open('{}/{}.js'.format(self.root, self.source_key), 'r') as file_object:
            self.data.extend(json.load(file_object, object_pairs_hook=OrderedDict))


class SingleDataSaverMixin:
    source_key = ''
    root = None
    data = []

    def save_data(self):
        with open('{}/{}.js'.format(self.root, self.source_key), 'w') as file_object:
            json.dump(self.data, file_object, indent=2, ensure_ascii=False)


class MultipleDataLoaderMixin:
    source_keys = []
    root = None
    data = []

    def load_all_data(self):
        for sk in self.source_keys:
            self.load_data(sk)

    def load_data(self, source_key):
        with open('{}/{}.js'.format(self.root, source_key), 'r') as file_object:
            self.data[source_key] = json.load(file_object, object_pairs_hook=OrderedDict)


class MultipleDataSaverMixin:
    source_keys = []
    root = None
    data = []

    def save_all_data(self):
        for sk in self.source_keys:
            self.save_data(sk)

    def save_data(self, source_key):
        with open('{}/{}.js'.format(self.root, source_key), 'w') as file_object:
            json.dump(self.data[source_key], file_object, indent=2, ensure_ascii=False)


class PathFinderMixin:
    field_name = None

    def get_field(self, model):
        if isinstance(self.field_name, list):
            data = model
            for path in self.field_name:
                data = data.get(path)
                if data is None:
                    break
            return data
        return model[self.field_name]

    def set_field(self, model, new_data):
        data = model
        for path in self.field_name[:-1]:
            if path not in data:
                data[path] = OrderedDict()
            data = data[path]
        data[self.field_name[-1]] = new_data


class SingleDataAnalyzer(SingleDataLoaderMixin, XWingDataBaseMixin, ToolBase):
    def __init__(self):
        super().__init__()
        self.data = []
        self.load_data()
        self.analise()

    def analise(self):
        raise NotImplementedError


class SingleDataNormalizer(
    SingleDataSaverMixin, SingleDataLoaderMixin, XWingDataBaseMixin, ToolBase
):
    def __init__(self):
        super().__init__()
        self.data = []
        self.load_data()
        self.normalize()
        self.save_data()

    def normalize(self):
        raise NotImplementedError


class SingleDataAnalyticalNormalizer(
    SingleDataSaverMixin, SingleDataLoaderMixin, XWingDataBaseMixin, ToolBase
):
    def __init__(self):
        super().__init__()
        self.data = []
        self.load_data()
        print('BEFORE --------')
        self.analise()
        self.normalize()
        print('\nAFTER ---------')
        self.analise()
        self.save_data()

    def analise(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError


class MultipleDataAnalyzer(MultipleDataLoaderMixin, XWingDataBaseMixin, ToolBase):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.load_all_data()
        self.analise()

    def analise(self):
        raise NotImplementedError


class MultipleDataNormalizer(
    MultipleDataSaverMixin, MultipleDataLoaderMixin, XWingDataBaseMixin, ToolBase
):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.load_all_data()
        self.normalize()
        self.save_all_data()

    def normalize(self):
        raise NotImplementedError


class MultipleDataAnalyticalNormalizer(
    MultipleDataSaverMixin, MultipleDataLoaderMixin, XWingDataBaseMixin, ToolBase
):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.load_all_data()
        print('BEFORE --------')
        self.analise()
        self.normalize()
        print('\nAFTER ---------')
        self.analise()
        self.save_all_data()

    def analise(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError


class SingleDataCollector(
    SingleDataSaverMixin, SingleDataLoaderMixin, XWingDataBaseMixin, ToolBase
):

    field_name = None
    memory = {}

    def __init__(self):
        super().__init__()
        self.data = []
        self.load_data()
        print('BEFORE --------')
        self.analise()
        self.gather()
        print('\nAFTER ---------')
        self.analise()
        self.save_data()

    def analise(self):
        pprint(self.memory)

    @staticmethod
    def print_model(model):
        print('\n' + model['name'])

    def input_text(self):
        return 'Which {} should it have?\nResponse (leave empty to skip): '.format(self.field_name)

    def clean_input(self, new_data):
        raise NotImplementedError

    def validate_input(self, new_data):
        raise NotImplementedError

    def gather(self):
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


class DateDataCollector(SingleDataCollector):
    input_format = None
    output_format = None

    def clean_input(self, new_data):
        try:
            new_data = datetime.datetime.strptime(new_data, self.input_format).date().isoformat()
        except ValueError:
            pass
        else:
            return new_data
        return new_data

    def validate_input(self, new_data):
        try:
            datetime.datetime.strptime(new_data, self.output_format).date()
        except ValueError:
            pass
        else:
            return True
        return False
