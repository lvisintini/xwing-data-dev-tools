from collections import OrderedDict
from base import XWingDataNormalizer, MultipleXWingDataNormalizer, MemoryLoader


class AddModelIds(MemoryLoader, XWingDataNormalizer):
    """Adds 1-based ids to models if missing"""

    def __init__(self):
        self.max_id = None
        self.min_id = None
        super().__init__()

    def analise(self):
        ids = [model['id'] for model in self.data if 'id' in model]
        ids.extend(self.memory.values())
        self.max_id = max(*ids)
        self.min_id = min(*ids)
        print('Memory', self.memory)
        print('Memory length', len(self.memory))
        print('Max id', self.max_id)
        print('Min id', self.min_id)
        print('Without id', len([model for model in self.data if 'id' not in model]))
        print('Qty', len(self.data))

    def normalize(self):
        auto_increment_value = self.max_id
        if auto_increment_value is None:
            auto_increment_value = 0
        for model in self.data:
            if 'id' not in model:
                if model['name'] in self.memory:
                    model['id'] = self.memory[model['name']]
                else:
                    auto_increment_value += 1
                    model['id'] = auto_increment_value


class ConditionsOneBasedIds(MemoryLoader, MultipleXWingDataNormalizer):
    source_keys = ['conditions', 'sources', 'pilots']
    #memory_url = 'https://raw.githubusercontent.com/lvisintini/xwing-data/master/data/conditions.js'

    def analise(self):
        ids = [model['id'] for model in self.data['conditions'] if 'id' in model]
        self.max_id = max(*ids)
        self.min_id = min(*ids)
        print('Memory', self.memory)
        print('Memory length', len(self.memory))
        print('Max id', self.max_id)
        print('Min id', self.min_id)
        print('Without id', len([model for model in self.data if 'id' not in model]))
        print('Qty', len(self.data))

    def normalize(self):
        if self.min_id is None:
            raise ValueError('Models have no ids')

        mapping = []

        if self.min_id == 0:
            for model in self.data['conditions']:
                old_id = model['id']
                if model['name'] in self.memory:
                    new_id = self.memory[model['name']]
                    model['id'] = self.memory[model['name']]
                    mapping.append((old_id, new_id))
                else:
                    new_id = model['id'] + 1
                    model['id'] = new_id
                    mapping.append((old_id, new_id))

            mapping = dict(mapping)

            for model in self.data['sources']:
                if 'conditions' in model['contents']:
                    if isinstance(model['contents']['conditions'], dict):
                        keys = list(model['contents']['conditions'].keys())
                        values = list(model['contents']['conditions'].values())
                        for i in range(len(keys)):
                            keys[i] = str(mapping[int(keys[i])])
                        model['contents']['conditions'] = OrderedDict(zip(keys, values))

                    elif isinstance(model['contents']['conditions'], list):
                        for fk in model['contents']['conditions']:
                            fk['condition_id'] = mapping[fk['condition_id']]
                    else:
                        raise ValueError('DATA ERROR!!')

            for model in self.data['pilots']:
                if 'conditions' in model:
                    if all([isinstance(c, dict) for c in model['conditions']]):
                        for fk in model['conditions']:
                            fk['condition_id'] = mapping[fk['condition_id']]


class AddShipsIds(AddModelIds):
    source_key = 'ships'
    memory_url = 'https://raw.githubusercontent.com/lvisintini/xwing-data/master/data/ships.js'


if __name__ == '__main__':
    print('AddShipsIds')
    AddShipsIds()

    print('ConditionsOneBasedIds')
    ConditionsOneBasedIds()
