import json
from collections import OrderedDict

from XwingDataDevTools.normalize.base import SingleDataAnalyticalNormalizer


class ForeignKeyNormalization(SingleDataAnalyticalNormalizer):
    fk_source_key = None
    fk_field_path = None
    pk_name = None

    def __init__(self):
        self.fk_data = []
        with open('{}/{}.js'.format(self.root, self.fk_source_key), 'r') as file_object:
            self.fk_data.extend(json.load(file_object, object_pairs_hook=OrderedDict))
        super().__init__()

    def analise(self):
        print('Models in fk data', len(self.fk_data))
        print('Max id in fk data', max([fkd.get('id', 0) for fkd in self.fk_data]))
        print('Models with no id in fk data', [
            fkd['name'] for fkd in self.fk_data if 'id' not in fkd
        ])

    def get_fk_field(self, model):
        fk = model
        for path in self.fk_field_path:
            fk = fk.get(path)
            if fk is None:
                break
        return fk

    def set_fk_field(self, model, new_fk):
        fk = model
        for path in self.fk_field_path[:-1]:
            fk = fk[path]
        fk[self.fk_field_path[-1]] = new_fk

    def is_fk_normalized(self, fk, current_model):
        raise NotImplementedError

    def get_fk_model(self, fk, current_model):
        raise NotImplementedError

    def construct_new_fk(self, fk, current_model):
        raise NotImplementedError


class SimpleForeignKeyNormalization(ForeignKeyNormalization):
    def get_fk_model(self, fk, current_model):
        if isinstance(fk, dict) and self.pk_name in fk:
            model = next(
                (fk_model for fk_model in self.fk_data if fk_model['id'] == fk[self.pk_name])
            )
        elif isinstance(fk, str) or isinstance(fk, bytes):
            model = next((fk_model for fk_model in self.fk_data if fk_model['name'] == fk))
        else:
            raise ValueError('fk {!r} is not recognized please, check!!'.format(fk))

        if model is None:
            raise ValueError('Model for fk {!r} not found'.format(fk))

        return model

    def is_fk_normalized(self, fk, current_model):
        return isinstance(fk, dict) and self.pk_name in fk and 'name' in fk

    def construct_new_fk(self, fk, current_model):
        if self.is_fk_normalized(fk, current_model):
            return fk

        fk_model = self.get_fk_model(fk, current_model)

        return OrderedDict([(self.pk_name, fk_model['id']), ('name', fk_model['name'])])


class PilotConditionsForeignKeyNormalization(SimpleForeignKeyNormalization):
    source_key = 'pilots'
    fk_source_key = 'conditions'
    fk_field_path = ['conditions', ]
    pk_name = 'condition_id'

    def normalize(self):
        for model in self.data:
            current_fk = self.get_fk_field(model)
            if current_fk is None:
                continue

            new_fk = []
            for fk in current_fk:
                new_fk.append(self.construct_new_fk(fk, model))

            self.set_fk_field(model, new_fk)


class PilotShipForeignKeyNormalization(SimpleForeignKeyNormalization):
    source_key = 'pilots'
    fk_source_key = 'ships'
    fk_field_path = ['ship', ]
    pk_name = 'ship_id'

    def normalize(self):
        for model in self.data:
            current_fk = self.get_fk_field(model)
            if current_fk is None:
                continue

            self.set_fk_field(model, self.construct_new_fk(current_fk, model))


class SourceContentsForeignKeyNormalization(ForeignKeyNormalization):

    def normalize(self):
        for model in self.data:
            current_fk = self.get_fk_field(model)
            if current_fk is None:
                continue

            if isinstance(current_fk, list):
                new_fk = []
                for fk in current_fk:
                    new_fk.append(self.construct_new_fk(fk, model))
            elif isinstance(current_fk, dict):
                new_fk = []
                for fk in current_fk.items():
                    new_fk.append(self.construct_new_fk(fk, model))
            else:
                new_fk = self.construct_new_fk(current_fk, model)

            self.set_fk_field(model, new_fk)

    def is_fk_normalized(self, fk, current_model):
        return isinstance(fk, dict) and self.pk_name in fk and 'amount' in fk and 'name' in fk

    def get_fk_model(self, fk, current_model):
        if isinstance(fk, dict) and self.pk_name in fk:
            model = next(
                (fk_model for fk_model in self.fk_data if fk_model['id'] == fk[self.pk_name])
            )
        elif isinstance(fk, tuple) and fk[0].isdigit():
            model = next(
                (fk_model for fk_model in self.fk_data if fk_model['id'] == int(fk[0]))
            )
        else:
            raise ValueError('fk {!r} is not recognized please, check!!'.format(fk))

        if model is None:
            raise ValueError('Model for fk {!r} not found'.format(fk))

        return model

    def construct_new_fk(self, fk, current_model):
        if self.is_fk_normalized(fk, current_model):
            return fk

        fk_model = self.get_fk_model(fk, current_model)

        if 'amount' in fk:
            amount = fk['amount']
        elif isinstance(fk, tuple):
            amount = fk[1]
        else:
            raise ValueError('fk {!r} missing amount!!'.format(fk))

        return OrderedDict([
            (self.pk_name, fk_model['id']),
            ('amount', amount),
            ('name', fk_model['name'])
        ])


class SourceShipsForeignKeyNormalization(SourceContentsForeignKeyNormalization):
    source_key = 'sources'
    fk_source_key = 'ships'
    fk_field_path = ['contents', 'ships']
    pk_name = 'ship_id'

    amounts = {
        0: {'TIE Fighter': 2, 'X-Wing': 1},
        1: {'X-Wing': 1},
        2: {'Y-Wing': 1},
        3: {'TIE Fighter': 1},
        4: {'TIE Advanced': 1},
        5: {'TIE Interceptor': 1},
        6: {'A-Wing': 1},
        7: {'YT-1300': 1},
        8: {'Firespray-31': 1},
        9: {'B-Wing': 1},
        10: {'HWK-290': 1},
        11: {'TIE Bomber': 1},
        12: {'Lambda-Class Shuttle': 1},
        13: {'TIE Interceptor': 2},
        14: {'Z-95 Headhunter': 1},
        15: {'TIE Defender': 1},
        16: {'E-Wing': 1},
        17: {'TIE Phantom': 1},
        18: {'A-Wing': 1, 'B-Wing': 1},
        19: {'CR90 Corvette (Aft)': 1, 'CR90 Corvette (Fore)': 1},
        20: {'GR-75 Medium Transport': 1, 'X-Wing': 1},
        21: {'YT-2400': 1},
        22: {'VT-49 Decimator': 1},
        23: {'Y-Wing': 1, 'Z-95 Headhunter': 2},
        24: {'StarViper': 1},
        25: {'M3-A Interceptor': 1},
        26: {'Aggressor': 1},
        27: {'Raider-class Corvette (Aft)': 1, 'Raider-class Corvette (Fore)': 1,
             'TIE Advanced': 1},
        28: {'YV-666': 1},
        29: {'Kihraxz Fighter': 1},
        30: {'K-Wing': 1},
        31: {'TIE Punisher': 1},
        32: {'T-70 X-Wing': 1, 'TIE/fo Fighter': 2},
        33: {'T-70 X-Wing': 1},
        34: {'TIE/fo Fighter': 1},
        35: {'JumpMaster 5000': 1},
        36: {'G-1A Starfighter': 1},
        37: {'TIE Adv. Prototype': 1},
        38: {'Attack Shuttle': 1, 'VCX-100': 1},
        39: {'Gozanti-Class Cruiser': 1, 'TIE Fighter': 2},
        40: {'TIE Bomber': 1, 'TIE Defender': 1},
        41: {'T-70 X-Wing': 1, 'YT-1300': 1},
        42: {'ARC-170': 1},
        43: {'TIE/sf Fighter': 1},
        44: {'Protectorate Starfighter': 1},
        45: {'Lancer-class Pursuit Craft': 1},
        46: {'TIE Fighter': 1},
        47: {'Upsilon-class Shuttle': 1},
        48: {'Quadjumper': 1},
        49: {'U-Wing': 1},
        50: {'TIE Striker': 1}
    }

    def get_fk_model(self, fk, model):
        if isinstance(fk, dict) and 'ship_id' in fk:
            model = next((ship for ship in self.fk_data if ship['id'] == fk['ship_id']))
        elif isinstance(fk, tuple) and fk[0].isdigit():
            model = next((ship for ship in self.fk_data if ship['id'] == int(fk[0])))
        elif isinstance(fk, str) or isinstance(fk, bytes):
            model = next((ship for ship in self.fk_data if ship['name'] == fk))
        else:
            raise ValueError('fk {!r} is not recognized please, check!!')

        if model is None:
            raise ValueError('Ship for pk {!r} not found'.format(fk))

        return model

    def construct_new_fk(self, fk, model):
        if self.is_fk_normalized(fk, model):
            return fk

        fk_model = self.get_fk_model(fk, model)

        if 'amount' in fk:
            amount = fk['amount']
        elif isinstance(fk, tuple):
            amount = fk[1]
        else:
            amount = self.amounts[model['id']][fk]

        return OrderedDict([
            (self.pk_name, fk_model['id']),
            ('amount', amount),
            ('name', fk_model['name'])
        ])


class SourceUpgradesForeignKeyNormalization(SourceContentsForeignKeyNormalization):
    source_key = 'sources'
    fk_source_key = 'upgrades'
    fk_field_path = ['contents', 'upgrades']
    pk_name = 'upgrade_id'


class SourceConditionsForeignKeyNormalization(SourceContentsForeignKeyNormalization):
    source_key = 'sources'
    fk_source_key = 'conditions'
    fk_field_path = ['contents', 'conditions']
    pk_name = 'condition_id'


class SourcePilotsForeignKeyNormalization(SourceContentsForeignKeyNormalization):
    source_key = 'sources'
    fk_source_key = 'pilots'
    fk_field_path = ['contents', 'pilots']
    pk_name = 'pilot_id'


class UpgradeConditionsForeignKeyNormalization(SimpleForeignKeyNormalization):
    source_key = 'upgrades'
    fk_source_key = 'conditions'
    fk_field_path = ['conditions', ]
    pk_name = 'condition_id'

    def normalize(self):
        for model in self.data:
            current_fk_field = self.get_fk_field(model)
            if current_fk_field is None:
                continue

            new_fk = []
            for fk in current_fk_field:
                new_fk.append(self.construct_new_fk(fk, model))

            self.set_fk_field(model, new_fk)


class UpgradeShipForeignKeyNormalization(SimpleForeignKeyNormalization):
    source_key = 'upgrades'
    fk_source_key = 'ships'
    fk_field_path = ['ship', ]
    pk_name = 'ship_id'

    def normalize(self):
        for model in self.data:
            current_fk_field = self.get_fk_field(model)
            if current_fk_field is None:
                continue

            new_fk = []
            for fk in current_fk_field:
                new_fk.append(self.construct_new_fk(fk, model))

            self.set_fk_field(model, new_fk)


class UpgradeShipsForeignKeyNormalization(UpgradeShipForeignKeyNormalization):
    fk_field_path = ['ships', ]


if __name__ == '__main__':
    SourceShipsForeignKeyNormalization()
    SourceUpgradesForeignKeyNormalization()
    SourceConditionsForeignKeyNormalization()
    SourcePilotsForeignKeyNormalization()
    UpgradeConditionsForeignKeyNormalization()
    UpgradeShipsForeignKeyNormalization()
    PilotConditionsForeignKeyNormalization()
    PilotShipForeignKeyNormalization()
