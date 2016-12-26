from pprint import pprint
from collections import OrderedDict

from XwingDataDevTools.normalize.base import SingleDataAnalyticalNormalizer


class OrderNormalizer(SingleDataAnalyticalNormalizer):
    def analise(self):
        fields = set()
        for model in self.data:
            fields.update(model.keys())
        pprint(list(fields))

    def normalize(self):
        for i in range(len(self.data)):
            model = self.data[i]
            self.data[i] = OrderedDict(
                sorted(
                    model.items(),
                    key=lambda pair: self.preferred_order.index(pair[0])
                )
            )


class ShipsOrderNormalizer(OrderNormalizer):
    source_key = 'ships'
    preferred_order = [
        'id',
        'xws',
        'name',
        'size',
        'energy',
        'attack',
        'agility',
        'hull',
        'shields',
        'epic_points',
        'faction',
        'factions',
        'actions',
        'maneuvers',
        'maneuvers_energy',
    ]


class ConditionsOrderNormalizer(OrderNormalizer):
    source_key = 'conditions'
    preferred_order = [
        'id',
        'xws',
        'name',
        'unique',
        'image',
        'text',
    ]


class DamageDeckOrderNormalizer(OrderNormalizer):
    preferred_order = [
        'name',
        'type',
        'amount',
        'text',
    ]


class DamageDeckCoreOrderNormalizer(DamageDeckOrderNormalizer):
    source_key = 'damage-deck-core'


class DamageDeckCoreTfaOrderNormalizer(DamageDeckOrderNormalizer):
    source_key = 'damage-deck-core-tfa'


class PilotsOrderNormalizer(OrderNormalizer):
    source_key = 'pilots'
    preferred_order = [
        'id',
        'xws',
        'name',
        'unique',
        'faction',
        'ship',
        'skill',
        'points',
        'slots',
        'text',
        'image',
        'range',
        'conditions',
        'ship_override',
    ]

    ship_override_order = [
        'attack',
        'agility',
        'hull',
        'shields',
    ]

    conditions_order = [
        'condition_id',
        'name',
    ]

    ship_order = [
        'ship_id',
        'name',
    ]

    def normalize(self):
        super().normalize()

        for model in self.data:
            if isinstance(model['ship'], dict):
                model['ship'] = OrderedDict(
                    sorted(
                        model['ship'].items(),
                        key=lambda pair: self.ship_order.index(pair[0])
                    )
                )

            if 'ship_override' in model:
                model['ship_override'] = OrderedDict(
                    sorted(
                        model['ship_override'].items(),
                        key=lambda pair: self.ship_override_order.index(pair[0])
                    )
                )

            if 'conditions' in model:
                if all([isinstance(fk, dict) for fk in model['conditions']]):
                    for i in range(len(model['conditions'])):
                        model['conditions'][i] = OrderedDict(
                            sorted(
                                model['conditions'][i].items(),
                                key=lambda pair: self.conditions_order.index(pair[0])
                            )
                        )
                    model['conditions'] = sorted(
                        model['conditions'],
                        key=lambda fk: fk['condition_id']
                    )
                else:
                    model['conditions'].sort()


class SourcesOrderNormalizer(OrderNormalizer):
    source_key = 'sources'
    preferred_order = [
        'id',
        'sku',
        'name',
        'wave',
        'image',
        'thumb',
        'contents',
        'released',
        'release_date',
        'announcement_date',
    ]

    contents_order = [
        'ships',
        'pilots',
        'upgrades',
        'conditions',
    ]

    conditions_order = [
        'condition_id',
        'amount',
        'name',
    ]

    pilots_order = [
        'pilot_id',
        'amount',
        'name',
    ]

    ships_order = [
        'ship_id',
        'amount',
        'name',
    ]

    upgrades_order = [
        'upgrade_id',
        'amount',
        'name',
    ]

    def normalize(self):
        super().normalize()

        for model in self.data:
            for i in range(len(model['contents'])):
                model['contents'] = OrderedDict(
                    sorted(
                        model['contents'].items(),
                        key=lambda pair: self.contents_order.index(pair[0])
                    )
                )

            if 'conditions' in model['contents']:
                if isinstance(model['contents']['conditions'], list):
                    for i in range(len(model['contents']['conditions'])):
                        model['contents']['conditions'][i] = OrderedDict(
                            sorted(
                                model['contents']['conditions'][i].items(),
                                key=lambda pair: self.conditions_order.index(pair[0])
                            )
                        )
                    model['contents']['conditions'] = sorted(
                        model['contents']['conditions'],
                        key=lambda fk: fk['condition_id']
                    )
                else:
                    alt_conditions_order = sorted(model['contents']['conditions'].keys())
                    model['contents']['conditions'] = OrderedDict(
                        sorted(
                            model['contents']['conditions'].items(),
                            key=lambda pair: alt_conditions_order.index(pair[0])
                        )
                    )

            if 'ships' in model['contents']:
                if all([isinstance(fk, dict) for fk in model['contents']['ships']]):
                    for i in range(len(model['contents']['ships'])):
                        model['contents']['ships'][i] = OrderedDict(
                            sorted(
                                model['contents']['ships'][i].items(),
                                key=lambda pair: self.ships_order.index(pair[0])
                            )
                        )
                    model['contents']['ships'] = sorted(
                        model['contents']['ships'],
                        key=lambda fk: fk['ship_id']
                    )
                else:
                    model['contents']['ships'].sort()

            if 'upgrades' in model['contents']:
                if isinstance(model['contents']['upgrades'], list):
                    for i in range(len(model['contents']['upgrades'])):
                        model['contents']['upgrades'][i] = OrderedDict(
                            sorted(
                                model['contents']['upgrades'][i].items(),
                                key=lambda pair: self.upgrades_order.index(pair[0])
                            )
                        )
                    model['contents']['upgrades'] = sorted(
                        model['contents']['upgrades'],
                        key=lambda fk: fk['upgrade_id']
                    )
                else:
                    alt_upgrades_order = sorted(model['contents']['upgrades'].keys())
                    model['contents']['upgrades'] = OrderedDict(
                        sorted(
                            model['contents']['upgrades'].items(),
                            key=lambda pair: alt_upgrades_order.index(pair[0])
                        )
                    )

            if 'pilots' in model['contents']:
                if isinstance(model['contents']['pilots'], list):
                    for i in range(len(model['contents']['pilots'])):
                        model['contents']['pilots'][i] = OrderedDict(
                            sorted(
                                model['contents']['pilots'][i].items(),
                                key=lambda pair: self.pilots_order.index(pair[0])
                            )
                        )
                    model['contents']['pilots'] = sorted(
                        model['contents']['pilots'],
                        key=lambda fk: fk['pilot_id']
                    )
                else:
                    alt_pilots_order = sorted(model['contents']['pilots'].keys())
                    model['contents']['pilots'] = OrderedDict(
                        sorted(
                            model['contents']['pilots'].items(),
                            key=lambda pair: alt_pilots_order.index(pair[0])
                        )
                    )


class UpgradesOrderNormalizer(OrderNormalizer):
    source_key = 'upgrades'

    preferred_order = [
        'id',
        'xws',
        'name',
        'unique',
        'limited',
        'slot',
        'points',
        'faction',
        'ship',
        'ships',
        'size',
        'sizes',
        'energy',
        'attack',
        'range',
        'text',
        'effect',
        'grants',
        'conditions',
        'image',
    ]

    sizes_order = [
        'small',
        'large',
        'huge',
    ]

    ships_order = [
        'ship_id',
        'name',
    ]

    conditions_order = [
        'condition_id',
        'name',
    ]

    grants_order = [
        'type',
        'name'
    ]

    def normalize(self):
        super().normalize()
        for model in self.data:
            if 'size' in model:
                model['size'] = sorted(
                    model['size'],
                    key=lambda s: self.sizes_order.index(s)
                )
            if 'sizes' in model:
                model['sizes'] = sorted(
                    model['sizes'],
                    key=lambda s: self.sizes_order.index(s)
                )

            if 'ship' in model:
                if all([isinstance(fk, dict) for fk in model['ship']]):
                    for i in range(len(model['ship'])):
                        model['ship'][i] = OrderedDict(
                            sorted(
                                model['ship'][i].items(),
                                key=lambda pair: self.ships_order.index(pair[0])
                            )
                        )
                    model['ship'] = sorted(
                        model['ship'],
                        key=lambda fk: fk['ship_id']
                    )
                else:
                    model['ship'].sort()

            if 'ships' in model:
                if all([isinstance(fk, dict) for fk in model['ships']]):
                    for i in range(len(model['ships'])):
                        model['ships'][i] = OrderedDict(
                            sorted(
                                model['ships'][i].items(),
                                key=lambda pair: self.ships_order.index(pair[0])
                            )
                        )
                    model['ships'] = sorted(
                        model['ships'],
                        key=lambda fk: fk['ship_id']
                    )
                else:
                    model['ships'].sort()

            if 'conditions' in model:
                if all([isinstance(fk, dict) for fk in model['conditions']]):
                    for i in range(len(model['conditions'])):
                        model['conditions'][i] = OrderedDict(
                            sorted(
                                model['conditions'][i].items(),
                                key=lambda pair: self.conditions_order.index(pair[0])
                            )
                        )
                    model['conditions'] = sorted(
                        model['conditions'],
                        key=lambda fk: fk['condition_id']
                    )
                else:
                    model['conditions'].sort()

            if 'grants' in model:
                for i in range(len(model['grants'])):
                    model['grants'][i] = OrderedDict(
                        sorted(
                            model['grants'][i].items(),
                            key=lambda pair: self.grants_order.index(pair[0])
                        )
                    )
                model['grants'] = sorted(
                    model['grants'],
                    key=lambda fk: fk['type']
                )


def set_preferred_order():
    ShipsOrderNormalizer()
    ConditionsOrderNormalizer()
    DamageDeckCoreOrderNormalizer()
    DamageDeckCoreTfaOrderNormalizer()
    PilotsOrderNormalizer()
    SourcesOrderNormalizer()
    UpgradesOrderNormalizer()


if __name__ == '__main__':
    set_preferred_order()
