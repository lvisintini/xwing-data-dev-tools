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
        'image_file_path': {
            'description': 'A file path for an image in this package.',
            'type': 'string',
            'pattern': '^(?:conditions|pilots|factions|sources|upgrades)'
                       '(?:\/[a-zA-Z\(\)\.0-9_-](?:[a-zA-Z\(\)\.0-9\ _-]*[a-zA-Z\(\)\.0-9\ _-])?)*'
                       '\.(?:png|jpg)$'
            # https://regex101.com/r/0Tt5mC/7 for tests
            # ^[a-zA-Z\(\)\.0-9_-](?:[a-zA-Z\(\)\.0-9\ _-]*[a-zA-Z\(\)\.0-9\ _-])?(?:\/[a-zA-Z\(\)\.0-9_-](?:[a-zA-Z\(\)\.0-9\ _-]*[a-zA-Z\(\)\.0-9\ _-])?)*\.[a-z0-9]{3}$
            # https://regex101.com/delete/FId7doiOjHil897MHkZ1012h to delete

            #https://regex101.com/r/rPE6YH/2 for tests
            # ^(?:conditions|pilots|factions|sources|upgrades)(?:\/[a-zA-Z\(\)\.0-9_-](?:[a-zA-Z\(\)\.0-9\ _-]*[a-zA-Z\(\)\.0-9\ _-])?)*\.(?:png|jpg)$
            #https://regex101.com/delete/VrG2IHZZKpuY4T9e7uyUiw26

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
            'image_file_path',
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
        },
    }


class PilotsBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('pilots',)
    target_key = 'pilots'
    title = 'Schema for pilots data file'

    fields = {
        'id': {
            'description': 'The pilot\'s unique id number. It\'s not used in the game but it\'s '
                           'used to link this pilot to other data in this dataset.',
            'minimum': 0,
        },
        'skill': {
            'description': 'The pilot\'s skill.',
            'anyOf': [
                {
                    'description': 'Pilot skill.',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 9,
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
                },
                "agility": {
                    'description': 'The ship\'s agility value.',
                    "minimum": 0,
                },
                "hull": {
                    'description': 'The ship\'s hull value.',
                    "minimum": 0,
                },
                "shields": {
                    'description': 'The ship\'s shields value.',
                    "minimum": 0,
                },
            },
            'additionalProperties': False,
        },
        'image': {
            'description': 'The file path for this pilot card\'s image.',
            '$ref': 'definitions.json#/definitions/image_file_path',
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
                'description': 'A condition name.',
                'type': 'string',
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
    title = 'Schema for ships data file'
    preferred_order_tail = ['common', 'huge', 'non_huge']

    common = {
        'name': {
            'type': 'string',
            'description': 'The ship\'s name as written on the card itself.',
            'minLength': 1,
        },
        'faction': {
            'type': 'array',
            'description': 'A list of factions this ship belongs to.',
            'minItems': 1,
            'items': {
                'description': 'A faction this ship belongs to.',
                '$ref': 'definitions.json#/definitions/faction'
            },
            'uniqueItems': True,
        },
        'actions': {
            'type': 'array',
            'description': 'A list of all the actions the ship is capable of.',
            'minItems': 0,
            'items': {
                'description': 'A list of all the actions the ship is capable of.',
                '$ref': 'definitions.json#/definitions/action'
            },
            'uniqueItems': True,
        },
        'attack': {
            'type': 'integer',
            'description': 'The ship\'s attack value.',
            'minimum': 0,
        },
        "agility": {
            'type': 'integer',
            'description': 'The ship\'s agility value.',
            "minimum": 0,
        },
        "hull": {
            'type': 'integer',
            'description': 'The ship\'s hull value.',
            "minimum": 0,
        },
        "shields": {
            'type': 'integer',
            'description': 'The ship\'s shields value.',
            "minimum": 0,
        },
        'xws': {
            'type': 'string',
            'description': 'The ship\'s unique XWS id as described in the XWS format.',
            'minLength': 1,
        },
    }

    small_large = {
        'maneuvers': {
            'type': 'array',
            'description': 'The huge ship\s maneuvers.',
            'maxItems': 6,
            'minItems': 0,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuvers available to the ship at a particular speed, determined '
                               'by its position in the array. ei. ship.maneuvers[1] will provide '
                               'all maneuvers available to said ship at speed 1.\n'
                               'This array may be as short as required to provide accurate data, '
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
                                   'This array may be as short as required to provide accurate '
                                   'data, meaning that a missing value for a particular maneuver '
                                   'type indicates that said maneuver is not available to that '
                                   'particular ship at that particular speed.\n.',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 3,
                },
            },
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

    huge = {
        'energy': {
            "type": "integer",
            'description': 'The ship\'s energy value.',
            'minimum': 1,
        },
        'epic_points': {
            'description': 'The ship\'s epic points value, as described in the X-Wing Epic Play '
                           'Tournament Rules.',
            'type': 'number',
            'minimum': 0,
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
            'type': 'array',
            'description': 'The ship\s maneuvers energy costs.',
            'maxItems': 6,
            'minItems': 0,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuver costs for the maneuvers available to the huge ship at a '
                               'particular speed, determined by its position in the array. ei. '
                               '``ship.maneuvers_energy[1]`` will provide all '
                               'maneuver cost for the maneuvers available to the huge ship at '
                               'speed 1.\n'
                               'This array\'s length should match the array\'s length of the '
                               'array in the maneuvers property.\n'
                               'In other words ``ship.maneuvers.length`` should equal to '
                               '``ship.maneuvers_energy.length``.',
                'type': 'array',
                'maxItems': 6,
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
                                   '\t5 = Koiogran Turn\n'
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
                },
            },
        },
        'maneuvers': {
            'type': 'array',
            'description': 'The huge ship\s maneuvers.',
            'maxItems': 6,
            'minItems': 0,
            'uniqueItems': False,
            'items': {
                'uniqueItems': False,
                'description': 'Each element in this array contains a representation of the '
                               'maneuvers available to the ship at a particular speed, determined '
                               'by its position in the array. ei. ship.maneuvers[1] will provide '
                               'all maneuvers available to said ship at speed 1.\n'
                               'This array may be as short as required to provide accurate data, '
                               'meaning that a missing speed \'index\' indicates that the ship is '
                               'is not capable of such speed.',
                'type': 'array',
                'maxItems': 6,
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
                                   '\t5 = Koiogran Turn\n'
                                   '\n'
                                   'Possible values in this array range from 0 to 1 and mean the '
                                   'following:\n'
                                   '\t0 = Maneuver unavailable\n'
                                   '\t1 = Maneuver available\n'
                                   '\n'
                                   'This array may be as short as required to provide accurate '
                                   'data, meaning that a missing value for a particular maneuver '
                                   'type indicates that said maneuver is not available to that '
                                   'particular huge ship at that particular speed.\n',
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 1,
                },
            },
        },
    }

    def build_schema(self):
        self.schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": self.title,
            "id": "{}{}#".format(self.host, self.target_filename),
            "definitions": {
                'common': {
                    'description': 'Fields used by all ships, regardless of size.',
                    'type': 'object',
                    'properties': self.common,
                    'additionalProperties': False,
                },
                'huge': {
                    'description': 'Fields used by ships huge ships only.',
                    'type': 'object',
                    'properties': self.huge,
                    'required': [
                        "name",
                        "faction",
                        "agility",
                        "hull",
                        "shields",
                        "actions",
                        "xws",
                        'maneuvers',
                        'maneuvers_energy',
                        'size'
                    ]
                },
                'non_huge': {
                    'description': 'Fields used by small and large ships only.',
                    'type': 'object',
                    'properties': self.small_large,
                    'required': [
                        "name",
                        "faction",
                        "agility",
                        "attack",
                        "hull",
                        "shields",
                        "actions",
                        "xws",
                        'maneuvers',
                        'size'
                    ]
                }
            },
            'type': 'object',
            'oneOf': [
                {
                    "$merge": {
                        "source": {
                            'description': 'Schema for common ship fields.',
                            '$ref': '#/definitions/common',
                        },
                        "with":  {
                            'description': 'Schema for huge ships.',
                            '$ref': '#/definitions/huge'
                        }
                    }
                },
                {
                    "$merge": {
                        "source": {
                            'description': 'Schema for common ship fields.',
                            '$ref': '#/definitions/common',
                        },
                        "with":                          {
                            'description': 'Schema for small and large ships.',
                            '$ref': '#/definitions/non_huge'
                        }
                    }
                },
            ],
        }

    def __init__(self, shared_definitions):
        self.build_schema()
        self.properties_order = []
        self.data = []
        self.load_data()
        self.shared_definitions = shared_definitions
        self.gather_definitions()
        self.gather_properties_order()
        self.save_schema()


class SourcesBuilder(OverrideMixin, XWingSchemaBuilder):
    source_keys = ('sources', )
    target_key = 'sources'
    title = 'Schema for sources data file'

    fields = {
        'id': {
            'description': 'The source\'s unique id number. It\'s not used in the game but it\'s '
                           'used to link this source to other data in this dataset.',
            'minimum': 0,
        },
        'sku': {
            'description': 'Fantasy Flight Games unique product key for this particular source.',
            'pattern': '^SWX[0-9]+$',
            'minLength': 1,
        },
        'wave': {
            'description': 'The sources wave (or product line).',
            'anyOf': [
                {
                    'description': 'Wave number. This value is usually presented in roman numerals '
                                   'but here is presented in arabic numerals.',
                    'type': 'integer',
                    'minimum': 0,
                },
                {
                    'description': 'Some sources are not grouped under particular wave, but under '
                                   'a particular product line.\n'
                                   'When that\s the case, use text fot that type.',
                    'type': 'string',
                    'minLength': 1,
                }
            ]
        },
        'name': {
            'description': 'The source\'s name as written on the package.',
            'minLength': 1,
        },
        'image': {
            'description': 'The file path for this source\'s image.',
            '$ref': 'definitions.json#/definitions/image_file_path',
        },
        'thumb': {
            'description': 'The file path for this source\'s thumbnail.',
            '$ref': 'definitions.json#/definitions/image_file_path',
        },
        'contents': {
            'description': 'The sources contents',
            'properties': {
                'ships': {
                    'description': 'The ships included in this source.',
                    "type": "array",
                    'uniqueItems': True,
                    "items": {
                        'type': 'string',
                        'description': 'A ship\'s name.'
                    }
                },
                "pilots": {
                    "type": "object",
                    'description': 'The pilots included in this source.\n'
                                   'The object property names (casted as integers) are the ids '
                                   'of the upgrades included.\n'
                                   'Their corresponding integer values indicate how many of those '
                                   'pilots are included in the source.',
                    'additionalProperties': True,
                },
                "upgrades": {
                    "type": "object",
                    'description': 'The upgrades included in this source.\n'
                                   'The object property names (casted as integers) are the ids '
                                   'of the upgrades included.\n'
                                   'Their corresponding integer values indicate how many of those '
                                   'upgrades are included in the source.',
                    'additionalProperties': True,
                },
                "conditions": {
                    "type": "object",
                    'description': 'The conditions included in this source.\n'
                                   'The object property names (casted as integers) are the ids '
                                   'of the conditions included.\n'
                                   'Their corresponding integer values indicate how many of those '
                                   'conditions are included in the source.',
                    'additionalProperties': True,
                },
            },
            'required': ['ships', 'pilots', 'upgrades'],
            'additionalProperties': False,
        },
        'released': {
            'description': 'This value indicates whether this sources has been released or not',
        },
        'release_date': {
            'description': 'Indicates the date on which the source was released.',
            'format': 'date'
        },
        'announcement_date': {
            'description': 'Indicates the date on which the source was announced.',
            'format': 'date'
        },
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
            'description': 'The ships this upgrade is restricted to.',
            'uniqueItems': True,
            "items": {
                'type': 'string',
                'description': 'A ship\'s name.'
            }
        },
        'grants': {
            'description': 'A list of improvements the upgrade grants to the ship it\'s '
                           'attached to.',
            'uniqueItems': False,
            "items": {
                'type': 'object',
                'description': 'An improvement granted by the upgrade',
                'anyOf': [
                    {
                        'description': 'The improved granted by this upgrade (action).',
                        'type': 'object',
                        'properties': {
                            'type': {
                                'description': 'This upgrade grants an action.',
                                'type': 'string',
                                'enum': ['action', ],
                            },
                            'name': {
                                'description': 'The action granted by this upgrade',
                                '$ref': 'definitions.json#/definitions/action',
                            }
                        },
                        'required': ['name', 'type'],
                        'additionalProperties': False,
                    },
                    {
                        'description': 'The improved granted by this upgrade (slot).',
                        'type': 'object',
                        'properties': {
                            'type': {
                                'description': 'This upgrade grants a slot.',
                                'type': 'string',
                                'enum': ['slot', ],
                            },
                            'name': {
                                'description': 'The slot granted by this upgrade',
                                '$ref': 'definitions.json#/definitions/slot',
                            }
                        },
                        'required': ['name', 'type'],
                        'additionalProperties': False,
                    }

                ],
            }
        },
        'energy': {
            'description': 'The upgrade\'s energy cost',
            'minimum': 0,
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
            '$ref': 'definitions.json#/definitions/image_file_path',
        },
        'attack': {
            'description': 'The upgrade\'s attack value.',
            'minimum': 1,
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
            'description': 'The upgrades\'s related conditions.',
            'items': {
                'description': 'A condition name.',
                'type': 'string',
            },
            'uniqueItems': True,
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
        },
        'image': {
            'description': 'The file path for this condition card\'s image.',
            '$ref': 'definitions.json#/definitions/image_file_path',
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