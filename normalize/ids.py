from base import XWingDataNormalizer
import requests


class AddModelIds(XWingDataNormalizer):
    """Adds ids to models if missing"""
    memory_url = None

    def __init__(self):
        self.max_id = 0
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

    def analise(self):
        ids = [model.get('id', 0) for model in self.data]
        ids.extend(self.memory.values())
        self.max_id = max(*ids)
        print('Memory', self.memory)
        print('Memory length', len(self.memory))
        print('Max id', self.max_id)
        print('Without id', len([model for model in self.data if 'id' not in model]))
        print('Qty', len(self.data))

    def normalize(self):
        auto_increment_value = self.max_id
        for model in self.data:
            if 'id' not in model:
                if model['name'] in self.memory:
                    model['id'] = self.memory[model['name']]
                else:
                    auto_increment_value += 1
                    model['id'] = auto_increment_value


class AddShipsIds(AddModelIds):
    source_key = 'ships'
    memory_url = 'https://raw.githubusercontent.com/lvisintini/xwing-data/master/data/ships.js'


if __name__ == '__main__':
    print('AddShipsIds')
    AddShipsIds()
