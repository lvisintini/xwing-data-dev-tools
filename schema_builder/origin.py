import json
import copy
from collections import OrderedDict
from base import XWingSchemaBuilder, SchemaBuilder


class OverrideMixin:
    pass


class SharedDefinitionsBuilder(OverrideMixin, SchemaBuilder):
    target_key = 'definitions'
    title = 'Schema for common fields in data files'

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
        },
        'file_path': {
            'description': 'A file path',
            'type': 'string',
            'pattern': '^[a-zA-Z\(\)\.0-9_-]([a-zA-Z\(\)\.0-9\ _-]*[a-zA-Z\(\)\.0-9\ _-])?'
                       '(\/[a-zA-Z\(\)\.0-9_-]([a-zA-Z\(\)\.0-9\ _-]*[a-zA-Z\(\)\.0-9\ _-])?)*'
                       '.[a-z0-9]{3}$'
            # https://regex101.com/r/0Tt5mC/3 for tests
            # https://regex101.com/delete/FId7doiOjHil897MHkZ1012h to delete
        },
        'range': {
            'description': 'A range in expressed in range format',
            'type': 'string',
            'pattern': '^[1-5](-[1-5])?$',
            # https://regex101.com/r/Go1Poa/1
            # https://regex101.com/delete/xePtVgt5BGrmmSQFyzLwJraE
        }
    }

    def __init__(self):
        super().__init__()
        self.properties_order = [
            'faction',
            'size',
            'slot',
            'action',
            'file_path',
            'range',
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
            if 'enum' in self.definitions[self.definition_mapping[attr]]:
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


class DamageDeckBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('damage-deck-core-tfa', 'damage-deck-core',)
    target_key = 'damage-deck'
    title = 'Schema for damage deck data files (original and tfa)'

    fields = {
        'name': {
            'description': 'The card\'s name as written on the card itself.',
            'minLength': 1,
        },
        'text': {
            'description': 'The card\'s text describing its effect.',
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


class HugeShipsBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('ships', )
    target_key = 'huge-ships'
    title = 'Schema for huge ships in ships data file'

    fields = {
        'id': {
            'description': 'The ship\'s unique id number. It\'s not used in the game but it\'s '
                           'used to link this ship to other data in this dataset.',
            'type': 'integer',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'name': {
            'description': 'The ship\'s name, as written on the card itself.',
            'minLength': 1,
        },
        'factions': {
            'minItems': 1,
            'description': 'A list of factions this ship belongs to.',
            'uniqueItems': True,
            'items': {
                'description': 'A faction this ship belongs to.',
                '$ref': 'definitions.json#/definitions/faction'
            }
        },
        'actions': {
            'minItems': 0,
            'description': 'A list of all the actions the ship is capable of.',
            'items': {
                'description': 'An action this ship is capable of.',
                '$ref': 'definitions.json#/definitions/action'
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
            'allOf': [
                {
                    'description': 'Ship size must be a valid size in size in the game.',
                    '$ref': 'definitions.json#/definitions/size'
                },
                {
                    'description': 'This schema only applies to huge ships.\n'
                                   'Therefore, ship size is restricted to huge.',
                    'type': 'string',
                    'enum': ['huge', ]
                },
            ]
        },
        'maneuvers_energy': {
            'description': 'The ship\s maneuvers energy costs.',
            'maxItems': 6,
            'minItems': 6,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuver costs for the maneuvers available to the huge ship at a '
                               'particular speed, determined its position in the array. ei. '
                               '``ship.maneuvers_energy[1]`` will provide all '
                               'maneuver cost for the maneuvers available to the huge ship at '
                               'speed 1.',
                'type': 'array',
                'maxItems': 5,
                'minItems': 5,
                'items': [
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s maneuver energy cost for a Left Turn maneuver',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s maneuver energy cost for a Left Bank maneuver',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s maneuver energy cost for a Straight maneuver',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s maneuver energy cost for a Right Bank maneuver',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s maneuver energy cost for a Right Turn maneuver',
                    }
                ],
                'additionalItems': False,
            },
        },
        'maneuvers': {
            'description': 'The huge ship\s maneuvers.',
            'maxItems': 6,
            'minItems': 6,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuvers available to the ship at a particular speed, determined '
                               'its position in the array. ei. ship.maneuvers[1] will provide all '
                               'maneuvers available to said ship at speed 1.',
                'type': 'array',
                'maxItems': 5,
                'minItems': 5,
                'items': [
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 1,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Left Turn maneuver.\n'
                                       '1 means the ship is capable while 0 means it is not.',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 1,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Left Bank maneuver.\n'
                                       '1 means the ship is capable while 0 means it is not.',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 1,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Straight maneuver.\n'
                                       '1 means the ship is capable while 0 means it is not.',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 1,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Right Bank maneuver.\n'
                                       '1 means the ship is capable while 0 means it is not.',
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 1,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Right Turn maneuver.\n'
                                       '1 means the ship is capable while 0 means it is not.',
                    }
                ],
                'additionalItems': False,
            },
        },
        'xws': {
            'description': 'The ship\'s unique XWS id as described in the XWS format.',
            'minLength': 1,
        },
    }

    def load_data(self):
        for key in self.source_keys:
            with open('{}data/{}.js'.format(self.data_files_root, key), 'r') as file_object:
                unfiltered_data = json.load(file_object, object_pairs_hook=OrderedDict)
                self.data.extend([hs for hs in unfiltered_data if hs['size'] == 'huge'])


class PilotsBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('pilots',)
    target_key = 'pilots'
    title = 'Schema for pilots data file'

    fields = {
        'id': {
            'description': 'The pilot\'s unique id number. It\'s not used in the game but it\'s '
                           'used to link this pilot to other data in this dataset.',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'skill': {
            'description': 'The pilot\'s skill.',
            'anyOf': [
                {
                    'description': 'Pilot skill.',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 9,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
                {
                    'description': 'Having \'?\' as a pilot\'s skill means that there is a '
                                   'special ruling for it and it\'s variable.',
                    'pattern': '^\?$',
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 1,
                }
            ]
        },
        'ship_override': {
            'description': 'Most times, ships attributes remain the same for all its pilot '
                           'cards.\n'
                           'When they don\'t, this attribute is used to reflect those changes.\n'
                           'The values here supersede the ones provided by pilot\'s ship values. ',
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
            'additionalProperties': False,
        },
        'image': {
            'description': 'The file path for this pilot card\'s image.',
            '$ref': 'definitions.json#/definitions/file_path',
        },
        'xws': {
            'description': 'The pilot\'s unique XWS id as described in the XWS format.',
            'minLength': 1,
        },
        'text': {
            'description': 'The pilot card\'s text describing its effect.',
            'minLength': 1,
        },
        'faction': {
            'description': 'The pilot\'s faction.',
            '$ref': 'definitions.json#/definitions/faction'
        },
        'conditions': {
            'description': 'The pilot\'s related conditions.',
            'items': {
                'type': 'object',
		'properties': {
		    'condition_id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type':'string'
                    },
		},
		'required': ['name', 'condition_id'],
            	'additionalProperties': False,
            },
            'uniqueItems': True,
        },
        'slots': {
            'description': 'A list of the slots available to this pilot.',
            'items': {
                'description': 'A slot available to this ship.',
                '$ref': 'definitions.json#/definitions/slot'
            },
            'uniqueItems': False,
        },
        'ship': {
            'description': 'The pilot\'s ship name.',
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
                                   'there is a special ruling for it and it\'s variable.',
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
            'description': 'Indicates whether this pilot has a unique name or not.\n'
                           'Some pilot cards have unique names, which are '
                           'identified by the bullet to the left of the name.\n'
                           'A player cannot field two or more cards that share the same unique '
                           'name, even if those cards are of different types.'
        },
        'range': {
            'description': 'The ship\'s range. This property is for huge ships only.',
            '$ref': 'definitions.json#/definitions/range',
        }
    }


class ShipsBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('ships',)
    target_key = 'ships'
    title = 'Schema for small and large ships in ships data file'

    fields = {
        'name': {
            'description': 'The ship\'s name as written on the card itself.',
            'minLength': 1,
        },
        'factions': {
            'description': 'A list of factions this ship belongs to.',
            'minItems': 1,
            'items': {
                'description': 'A faction this ship belongs to.',
                '$ref': 'definitions.json#/definitions/faction'
            },
            'uniqueItems': True,
        },
        'actions': {
            'description': 'A list of all the actions the ship is capable of.',
            'minItems': 0,
            'items': {
                'description': 'A list of all the actions the ship is capable of.',
                '$ref': 'definitions.json#/definitions/action'
            },
            'uniqueItems': True,
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
        'maneuvers': {
            'description': 'The huge ship\s maneuvers.',
            'maxItems': 6,
            'minItems': 6,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuvers available to the ship at a particular speed, determined '
                               'its position in the array. ei. ship.maneuvers[1] will provide all '
                               'maneuvers available to said ship at speed 1.\n',
                'type': 'array',
                'maxItems': 13,
                'minItems': 0,
                'items': [
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Left Turn maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Left Bank maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Straight maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Right Bank maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Right Turn maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Koiogran Turn maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Segnor\'s Loop Left '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Segnor\'s Loop Right '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Tallon Roll Left '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Tallon Roll Right '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Backwards Left Bank '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Backwards Straight '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    },
                    {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 3,
                        "exclusiveMaximum": False,
                        "exclusiveMinimum": False,
                        'description': 'The ship\'s capability of doing a Backwards Right Bank '
                                       'maneuver.\n'
                                       'This value ranges from 0 to 3 and mean the following:\n'
                                       '\t0 = Maneuver unavailable\n'
                                       '\t1 = White maneuver\n'
                                       '\t2 = Green maneuver\n'
                                       '\t3 = Red maneuver\n'
                    }
                ],
                'additionalItems': False,
            },
        },
        'xws': {
            'description': 'The ship\'s unique XWS id as described in the XWS format.',
            'minLength': 1,
        },
        'size': {
            'description': 'The ship\'s size.',
            'allOf': [
                {
                    'description': 'Ship size must be a valid size in size in the game.',
                    '$ref': 'definitions.json#/definitions/size'
                },
                {
                    'description': 'This schema only applies to small or large ships.\n'
                                   'Therefore, ship size is restricted to small or large.',
                    'type': 'string',
                    'enum': ['small', 'large']
                },
            ],
        }
    }

    def load_data(self):
        for key in self.source_keys:
            with open('{}data/{}.js'.format(self.data_files_root, key), 'r') as file_object:
                unfiltered_data = json.load(file_object, object_pairs_hook=OrderedDict)
                self.data.extend([hs for hs in unfiltered_data if hs['size'] != 'huge'])


class SourcesBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('sources', )
    target_key = 'sources'
    title = 'Schema for sources data file'

    fields = {
        'id': {
            'description': 'The source\'s unique id number. It\'s not used in the game but it\'s '
                           'used to link this source to other data in this dataset.',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'sku': {
            'description': 'Fantasy Flight Games unique product key for this particular source.',
            'pattern': '^SWX[0-9]+$',
            'minLength': 1,
        },
        'wave': {
        },
        'name': {
            'description': 'The source\'s name as written on the package.',
            'minLength': 1,
        },
        'image': {
            'description': 'The file path for this source\'s image.',
            '$ref': 'definitions.json#/definitions/file_path',
        },
        'thumb': {
            'description': 'The file path for this source\'s thumbnail.',
            '$ref': 'definitions.json#/definitions/file_path',
        },
        'contents': {
        },
        'released': {
            'description': 'This value indicates whether this sources has been released or not',
        }
    }


class UpgradesBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('upgrades',)
    target_key = 'upgrades'
    title = 'Schema for upgrades data file'
    properties_order_tail = ['type', ]

    fields = {
        'id': {
            'description': 'The upgrade\'s unique id number. It\'s not used in the game but it\'s '
                           'used to link this upgrade to other data in this dataset.',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'unique': {
            'description': 'Some upgrade cards have unique names, which are '
                           'identified by the bullet to the left of the name.\n '
                           'A player cannot field two or more cards that share the same unique '
                           'name, even if those cards are of different types.'
        },
        'size': {
            'description': 'This ship sizes this upgrade is restricted to.',
            'uniqueItems': True,
            'items': {
                'description': 'A ship size the upgrade is restricted to.',
                '$ref': 'definitions.json#/definitions/size',
            },
        },
        'name': {
            'description': 'The upgrade\'s name as written on the card.',
            'minLength': 1,
        },
        'points': {
            'description': 'Squad points cost for this upgrade.',
        },
        'limited': {
            'description': 'Indicates if this upgrade has the Limited trait.\n'
                           'A ship cannot equip more than one copy of the same card with the '
                           'Limited trait.'
        },
        'effect': {
            'description': 'Some upgrades have effects, like bomb tokens.\n'
                           'The text for such effects go here.',
            'minLength': 1,
        },
        'ship': {
        },
        'grants': {
        },
        'energy': {
            'description': 'The upgrade\'s energy cost',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'range': {
            'description': 'The upgrade\'s range. Usually attach related.',
            '$ref': 'definitions.json#/definitions/range',
        },
        'slot': {
            'description': 'The slot used by this upgrade.',
            '$ref': 'definitions.json#/definitions/slot'
        },
        'image': {
            'description': 'The file path for this upgrade\'s image.',
            '$ref': 'definitions.json#/definitions/file_path',
        },
        'attack': {
            'description': 'The upgrade\'s attack value.',
            'minimum': 1,
            "exclusiveMinimum": False,
        },
        'text': {
            'description': 'The upgrade\'s text as written on the card.',
            'minLength': 1,
        },
        'faction': {
            'description': 'The faction this upgrade is restricted to.',
            '$ref': 'definitions.json#/definitions/faction',
        },
        'xws': {
            'description': 'The upgrade\'s unique XWS id as described in the XWS format.',
            'minLength': 1,
        },
        'conditions': {
        },
    }


class ConditionsBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('conditions',)
    target_key = 'conditions'
    title = 'Schema for conditions data file'

    fields = {
        'id': {
            'description': 'The condition\'s unique id number. It\'s not used in the game but '
                           'it\'s used to link this condition to other data in this dataset.',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'image': {
            'description': 'The file path for this condition card\'s image.',
            '$ref': 'definitions.json#/definitions/file_path',
        },
        'name': {
            'description': 'The conditions\'s name as written on the package.',
            'minLength': 1,
        },
        'text': {
            'description': 'The condition card\'s text describing its effect.',
            'minLength': 1,
        },
        'unique': {
            'description': 'Some condition cards have unique names, which are '
                           'identified by the bullet to the left of the name.\n '
                           'A player cannot field two or more cards that share the same unique '
                           'name, even if those cards are of different types.'
        },
        'xws': {
            'description': 'The conditions\'s unique XWS id as described in the XWS format.',
            'minLength': 1,
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