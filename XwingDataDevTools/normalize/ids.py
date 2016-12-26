from XwingDataDevTools.normalize.base import (
    SingleDataAnalyticalNormalizer, MultipleDataNormalizer
)


class AddModelIds(SingleDataAnalyticalNormalizer):
    """Adds 1-based ids to models if missing"""

    def __init__(self):
        self.max_id = None
        self.min_id = None
        super().__init__()

    def analise(self):
        ids = [model['id'] for model in self.data if 'id' in model]
        self.max_id = max(*ids) if len(ids) else None
        self.min_id = min(*ids) if len(ids) else None
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
                model['id'] = auto_increment_value
                auto_increment_value += 1


class RefreshIdsUsingNames(MultipleDataNormalizer):
    source_keys = ['pilots', 'ships', 'sources', 'conditions', 'upgrades']

    @staticmethod
    def analise():
        print('Nothing to print')

    def normalize(self):
        # FIXME: Get all models by name and pop them out, assume FIFO
        for model in self.data['pilots']:
            fk_model = next((m for m in self.data['ships'] if m['name'] == model['ship']['name']))
            model['ship']['ship_id'] = fk_model['id']

            if 'conditions' in model:
                for fk in model['conditions']:
                    fk_model = next((m for m in self.data['conditions'] if m['name'] == fk['name']))
                    fk['condition_id'] = fk_model['id']

        for model in self.data['sources']:
            if 'conditions' in model['contents']:
                for fk in model['contents']['conditions']:
                    fk_model = next((m for m in self.data['conditions'] if m['name'] == fk['name']))
                    fk['condition_id'] = fk_model['id']

            for fk in model['contents']['ships']:
                fk_model = next((m for m in self.data['ships'] if m['name'] == fk['name']))
                fk['ship_id'] = fk_model['id']

            for fk in model['contents']['pilots']:
                fk_model = next((m for m in self.data['pilots'] if m['name'] == fk['name']))
                fk['pilot_id'] = fk_model['id']

            for fk in model['contents']['upgrades']:
                fk_model = next((m for m in self.data['upgrades'] if m['name'] == fk['name']))
                fk['upgrade_id'] = fk_model['id']


class AddShipsIds(AddModelIds):
    source_key = 'ships'


if __name__ == '__main__':
    AddShipsIds()
    #RefreshIdsUsingNames()
