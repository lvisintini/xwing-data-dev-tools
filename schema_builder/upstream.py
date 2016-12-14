import json
import copy
from collections import OrderedDict
from base import XWingSchemaBuilder, SchemaBuilder


class SharedDefinitionsBuilder(SchemaBuilder):
    target_key = 'definitions'

    definition_mapping = {
        'faction': 'faction',
        'factions': 'faction',
        'action': 'action',
        'actions': 'action',
        'slot': 'slot',
        'slots': 'slot',
        'size': 'size',
    }

    definition_fields = {
        'faction': {
            'description': 'A faction in the game.',
            'type': 'string',
            'enum': [],
        },
        'action': {
            'description': 'A action type in the game.',
            'type': 'string',
            'enum': [],
        },
        'slot': {
            'description': 'A slot type in the game.',
            'type': 'string',
            'enum': [],
        },
        'size': {
            'description': 'A ship size in the game.',
            'type': 'string',
            'enum': [],
        }
    }

    def __init__(self):
        super().__init__()
        self.properties_order = [
            'faction',
            'size',
            'slot',
            'action',
        ]
        self.build_schema()

    def apply_preferred_attr_order(self, d, order=None):
        is_schema = all([
            'definitions' in d
        ])

        for attr in d:
            if d[attr].__class__ == dict:
                if is_schema and attr == 'definitions':
                    d[attr] = self.apply_preferred_attr_order(d[attr], self.properties_order)
                else:
                    d[attr] = self.apply_preferred_attr_order(d[attr])
            if d[attr].__class__ == list:
                if all([x.__class__ == dict for x in d[attr]]):
                    d[attr] = [self.apply_preferred_attr_order(x) for x in d[attr]]
                else:
                    if attr != 'required' and is_schema:
                        d[attr].sort()
        d = OrderedDict(
            sorted(
                d.items(),
                key=lambda x: order.index(x[0]) if order else self.preferred_order.index(x[0])
            )
        )
        return d

    def add_definition_data(self, attr, enum):
        if attr in self.definition_mapping:
            definition_enum = self.definitions[self.definition_mapping[attr]]['enum']
            if enum.__class__ == list:
                definition_enum.extend(enum)
            else:
                definition_enum.append(enum)
            self.definitions[self.definition_mapping[attr]]['enum'] = list(set(definition_enum))
            self.definitions[self.definition_mapping[attr]]['enum'].sort()

    @property
    def definitions(self):
        return self.schema['definitions']

    def build_schema(self):
        super().build_schema()
        self.schema.update({
            'definitions': copy.deepcopy(self.definition_fields)
        })


class DamageDeckBuilder(XWingSchemaBuilder):
    source_keys = ('damage-deck-core-tfa', 'damage-deck-core',)
    target_key = 'damage-deck'

    fields = {
        'name': {
            'description': 'The card\'s name as written on the card itself.',
            'minLength': 1,
        },
        'text': {
            'description': 'The card\'s text describing it\'s effect.',
            'minLength': 1,
        },
        'type': {
            'description': 'Defines the type/scope of the damage this card does when dealt faceup.',
            'enum': []
        },
        'amount': {
            'description': 'Indicates how many cards of this type are included in it\'s source.',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
    }


class HugeShipsBuilder(XWingSchemaBuilder):
    source_keys = ('ships', )
    target_key = 'huge-ships'

    fields = {
        'name': {
            'description': 'The ship\'s name, as written on the card itself.',
            'minLength': 1,
        },
        'faction': {
            'minItems': 1,
            'description': 'A list of factions this ship belongs to.',
            'uniqueItems': True,
            'items': {
                'description': 'A faction this ship belongs to.',
                '$ref': 'definitions.json#/faction'
            }
        },
        'actions': {
            'minItems': 0,
            'description': 'A list of all the actions the ship is capable.',
            'items': {
                'description': 'An action this ship is capable of.',
                '$ref': 'definitions.json#/action'
            },
            'uniqueItems': True,
        },
        'energy': {
            'description': 'The ship\'s energy value.',
            'minimum': 1,
            "exclusiveMinimum": False,
        },
        'attack': {
            'description': 'The ship\'s attack value.',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        "agility": {
            'description': 'The ship\'s agility value.',
            "minimum": 0,
            "exclusiveMinimum": False,
        },
        "hull": {
            'description': 'The ship\'s hull value.',
            "minimum": 0,
            "exclusiveMinimum": False,
        },
        "shields": {
            'description': 'The ship\'s shields value.',
            "minimum": 0,
            "exclusiveMinimum": False,
        },
        'epic_points': {
            'description': 'The ship\'s epic points value, as described in the X-Wing Epic Play '
                           'Tournament Rules.',
            'type': 'number',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'size': {
            'description': 'The ship\'s size.',
            '$ref': 'definitions.json#/size',
            'pattern': '^huge$',
        },
        'maneuvers_energy': {
            'description': 'The ship\s maneuvers energy costs.',
            'maxItems': 6,
            'minItems': 0,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuver costs for the maneuvers available to the huge ship at a '
                               'particular speed, determined its position in the array. ei. '
                               '``ship.maneuvers_energy[1]`` will provide all '
                               'maneuver cost for the maneuvers available to the huge ship at '
                               'speed 1.\n'
                               'This array\'s length should match the array\'s length of the '
                               'array in the maneuvers property.\n'
                               'In other words ``ship.maneuvers.length`` should equal to '
                               '``ship.maneuvers_energy.length``.',
                'type': 'array',
                'maxItems': 5,
                'minItems': 0,
                'items': {
                    'description': 'This array is a representation of a huge ship\' maneuvers '
                                   'energy cost at a particular speed.\n'
                                   '\n'
                                   'Each value on this array references a different maneuver '
                                   'depending on its index, which maps according to the following '
                                   'list:\n'
                                   '\t0 = Left Turn\n'
                                   '\t1 = Left Bank\n'
                                   '\t2 = Straight\n'
                                   '\t3 = Right Bank\n'
                                   '\t4 = Right Turn\n'
                                   '\n'
                                   'Possible values in this array range from 0 to 3 and indicate '
                                   'the referenced maneuver\'s energy cost.\n'
                                   '\n'
                                   'This array\'s length should match the array\'s length of the '
                                   'array in the maneuvers property at the same speed.\n'
                                   'In other words ``ship.maneuvers[2].length`` should equal to '
                                   '``ship.maneuvers_energy[2].length``.',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 3,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
            },
        },
        'maneuvers': {
            'description': 'The huge ship\s maneuvers.',
            'maxItems': 6,
            'minItems': 0,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuvers available to the ship at a particular speed, determined '
                               'its position in the array. ei. ship.maneuvers[1] will provide all '
                               'maneuvers available to said ship at speed 1.\n'
                               'This array may be a short as required to provide accurate data, '
                               'meaning that a missing speed \'index\' indicates that the ship is '
                               'is not capable of such speed.',
                'type': 'array',
                'maxItems': 5,
                'minItems': 0,
                'items': {
                    'description': 'This array is a representation of a huge ship\' maneuvers at a '
                                   'particular speed.\n'
                                   '\n'
                                   'Each value on this array references a different maneuver '
                                   'depending on its index, which maps according to the following '
                                   'list:\n'
                                   '\t0 = Left Turn\n'
                                   '\t1 = Left Bank\n'
                                   '\t2 = Straight\n'
                                   '\t3 = Right Bank\n'
                                   '\t4 = Right Turn\n'
                                   '\n'
                                   'Possible values in this array range from 0 to 1 and mean the '
                                   'following:\n'
                                   '\t0 = Maneuver unavailable\n'
                                   '\t1 = Maneuver available\n'
                                   '\n'
                                   'This array may be a short as required to provide accurate '
                                   'data, meaning that a missing value for a particular maneuver '
                                   'type indicates that said maneuver is not available to that '
                                   'particular huge ship at that particular speed.\n',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 1,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
            },
        },
        'xws': {
            'description': 'The ships unique XWS as described in the XWS format.',
            'minLength': 1,
        },
    }

    def load_data(self):
        for key in self.source_keys:
            with open('{}data/{}.js'.format(self.data_files_root, key), 'r') as file_object:
                unfiltered_data = json.load(file_object, object_pairs_hook=OrderedDict)
                self.data.extend([hs for hs in unfiltered_data if hs['size'] == 'huge'])


class PilotsBuilder(XWingSchemaBuilder):
    source_keys = ('pilots',)
    target_key = 'pilots'
    fields = {
        'id': {
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'skill': {
            'anyOf': [
                {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 9,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
                {
                    'pattern': '^\?$',
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1,
                }
            ]
        },
        'ship_override': {
            'properties': {
                'attack': {
                    'description': 'The ship\'s attack value.',
                    'minimum': 0,
                    "exclusiveMinimum": False,
                },
                "agility": {
                    'description': 'The ship\'s agility value.',
                    "minimum": 0,
                    "exclusiveMinimum": False,
                },
                "hull": {
                    'description': 'The ship\'s hull value.',
                    "minimum": 0,
                    "exclusiveMinimum": False,
                },
                "shields": {
                    'description': 'The ship\'s shields value.',
                    "minimum": 0,
                    "exclusiveMinimum": False,
                },
            },
            'required': [],
            'additionalProperties': False,
        },
        'image': {
            'minLength': 1,
            'pattern': '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(/[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
        },
        'xws': {
            'description': 'The pilots unique XWS as described in the XWS format.',
            'minLength': 1,
        },
        'text': {
            'description': 'The card\'s text describing it\'s effect.',
            'minLength': 1,
        },
        'faction': {
            'description': 'The pilot\'s faction.',
            '$ref': 'definitions.json#/faction'
        },
        'conditions': {
            'description': 'The pilot\'s related conditions.',
            'items': {
                'type': 'string',
            },
            'uniqueItems': True,
        },
        'slots': {
            'description': 'A list of the slots available to this pilot.',
            'items': {
                'description': 'A slot available to this ship.',
                '$ref': 'definitions.json#/slots'
            },
            'uniqueItems': False,
        },
        'ship': {
            'description': 'The pilot\'s ship name.',
            'type': 'string',
            'minLength': 1,
        },
        'points': {
            'description': 'This pilot\'s squad points cost.',
            'anyOf': [
                {
                    'description': 'Squad points cost.',
                    'type': 'integer',
                    'minimum': 1,
                    "exclusiveMinimum": False,
                },
                {
                    'description': 'Having \'?\' as a pilot\'s squad points cost means that '
                                   'there is a special ruling for them an they are variable.',
                    'pattern': '^\?$',
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1,
                }
            ]
        },
        'name': {
            'description': 'The pilot\'s name, as written on the card itself.',
            'minLength': 1,
        },
        'unique': {
            'type': "boolean",
            'description': 'This value indicates whether this pilot is unique or not, as '
                           'indicated by a black dot next to pilot\'s name in the card (if '
                           'unique).',
        },
        'range': {
            'type': 'string',
            'description': 'The ship\s range. This property is for huge ships only.',
            'pattern': '^[0-9]-[0-9]$',
        }
    }


class ShipsBuilder(XWingSchemaBuilder):
    source_keys = ('ships',)
    target_key = 'ships'

    fields = {
        'name': {
            'description': 'The ship\'s name as written on the card itself.',
            'minLength': 1,
        },
        'faction': {
            'minItems': 1,
            'items': {
                '$ref': 'definitions.json#/faction'
            },
            'uniqueItems': True,
        },
        'actions': {
            'minItems': 0,
            'items': {
                '$ref': 'definitions.json#/action'
            },
            'uniqueItems': False,
        },
        'attack': {
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        "agility": {
            "minimum": 0,
            "exclusiveMinimum": False,
        },
        "hull": {
            "minimum": 0,
            "exclusiveMinimum": False,
        },
        "shields": {
            "minimum": 0,
            "exclusiveMinimum": False,
        },
        'maneuvers': {
            'description': 'The huge ship\s maneuvers.',
            'maxItems': 6,
            'minItems': 0,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuvers available to the ship at a particular speed, determined '
                               'its position in the array. ei. ship.maneuvers[1] will provide all '
                               'maneuvers available to said ship at speed 1.\n'
                               'This array may be a short as required to provide accurate data, '
                               'meaning that a missing speed \'index\' indicates that the ship is '
                               'is not capable of such speed.',
                'type': 'array',
                'maxItems': 13,
                'minItems': 0,
                'items': {
                    'description': 'This array is a representation of a ship\' maneuvers at a '
                                   'particular speed.\n'
                                   '\n'
                                   'Each value on this array references a different maneuver '
                                   'depending on its index, which maps according to the following '
                                   'list:\n'
                                   '\t00 = Left Turn\n'
                                   '\t01 = Left Bank\n'
                                   '\t02 = Straight\n'
                                   '\t03 = Right Bank\n'
                                   '\t04 = Right Turn\n'
                                   '\t05 = Koiogran Turn\n'
                                   '\t06 = Segnor\'s Loop Left\n'
                                   '\t07 = Segnor\'s Loop Right\n'
                                   '\t08 = Tallon Roll Left\n'
                                   '\t09 = Tallon Roll Right\n'
                                   '\t10 = Backwards Left Bank\n'
                                   '\t11 = Backwards Straight\n'
                                   '\t12 = Backwards Right Bank\n'
                                   '\n'
                                   'Possible values in this array range from 0 to 3 and mean the '
                                   'following:\n'
                                   '\t0 = Maneuver unavailable\n'
                                   '\t1 = White maneuver\n'
                                   '\t2 = Green maneuver\n'
                                   '\t3 = Red maneuver\n'
                                   '\n'
                                   'This array may be a short as required to provide accurate '
                                   'data, meaning that a missing value for a particular maneuver '
                                   'type indicates that said maneuver is not available to that '
                                   'particular ship at that particular speed.\n.',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 3,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
            },
        },
        'xws': {
            'minLength': 1,
        },
        'size': {
            'description': 'The ship\'s size.',
            '$ref': 'definitions.json#/size',
            'pattern': '^(large|small)$'
        }
    }

    def load_data(self):
        for key in self.source_keys:
            with open('{}data/{}.js'.format(self.data_files_root, key), 'r') as file_object:
                unfiltered_data = json.load(file_object, object_pairs_hook=OrderedDict)
                self.data.extend([hs for hs in unfiltered_data if hs['size'] != 'huge'])


class SourcesBuilder(XWingSchemaBuilder):
    source_keys = ('sources',)
    target_key = 'sources'

    fields = {
        'id': {
            'type': 'integer',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
    }


class UpgradesBuilder(XWingSchemaBuilder):
    source_keys = ('upgrades',)
    target_key = 'upgrades'

    fields = {
        'id': {
            'type': 'integer',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
    }


class ConditionsBuilder(XWingSchemaBuilder):
    source_keys = ('conditions',)
    target_key = 'conditions'

    fields = {
        'id': {
            'type': 'integer',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'image': {
            'minLength': 1,
            'pattern': '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(/[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
        }
    }


if __name__ == '__main__':
    sd = SharedDefinitionsBuilder()

    builders = [
        HugeShipsBuilder,
        ShipsBuilder,
        PilotsBuilder,
        UpgradesBuilder,
        SourcesBuilder,
        DamageDeckBuilder,
        ConditionsBuilder,
    ]

    for builder in builders:
        builder(sd)

    sd.save_schema()
    #sd.print_schema()