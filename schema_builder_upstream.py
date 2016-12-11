import json
import copy
from collections import OrderedDict
from pprint import pprint

# FIXME
# shipoverride = ship definition
# xws definition = redo all names -> maybe -> maybe a separate app that links the xws repo to the data repo

# FIXME
# defninitions should be local and external, somehow. can calculated on the fly if necesary
#

# FIXME
# Asteroids
# Attributes order in the data. define one.

# FIXME
# New project ultimate Game references merging LearToPlay, game reference and FAQ with errata

# FIXME
# Mark cards with errata.
# Errata up to date.
# Card Clarifications.
# release date
# Add text for nameless pilots (pilot_hability, flavour_text)

# Schema to doc


class SchemaBuilder:
    host = 'https://github.com/lvisintini/xwing-data/schema/'
    files_root = '../xwing-data/'
    target_key = ''

    local_definitions = {}

    schema = None

    preferred_order = [
        '$schema',
        'id',
        'title',
        'type',
        'default',
        'description',
        'definitions',
        'properties',
        'required',
        'additionalProperties',
        '$ref',
        'oneOf',
        'allOf',
        'anyOf',
        'not',
        'enum',
        'minLength',
        'maxLength',
        'pattern',
        'multipleOf',
        'minimum',
        'maximum',
        'exclusiveMinimum',
        'exclusiveMaximum',
        'maxItems',
        'minItems',
        'items',
    ]

    schema_combining_attrs = ['$ref', 'anyOf', 'allOf', 'not', 'oneOf']

    attribute_mapping = {
        int: 'integer',
        float: 'number',
        list: 'array',
        str: 'string',
        dict: 'object',
        OrderedDict: 'object',
        bool: 'boolean',
        None: 'null',
    }

    def __init__(self):
        self.build_schema()
        self.properties_order = []

    def js_attr(self, obj):
        return self.attribute_mapping[obj.__class__]

    def print_schema(self):
        name = ' '.join(self.target_key.split('-')).capitalize()
        print(name, '-'*(100-len(name)))
        pprint(self.schema)

    @property
    def target_filename(self):
        return "{}.json".format(self.target_key)

    def build_schema(self):
        self.schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "id": "{}{}".format(self.host, self.target_filename),
            "definitions": self.local_definitions,
        }

    def apply_preferred_attr_order(self, d, order=None):
        is_schema = all([
            d.get('type') == 'object',
            'properties' in d
        ])

        for attr in d:
            if d[attr].__class__ == dict:
                if is_schema and attr == 'properties':
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

    def save_schema(self):
        self.schema = self.apply_preferred_attr_order(self.schema)
        with open('./schemas/{}.json'.format(self.target_key), 'w') as file_object:
            json.dump(self.schema, file_object, indent=2)


class XWingSchemaBuilder(SchemaBuilder):
    source_keys = ()
    fields = {}

    def __init__(self, shared_definitions):
        super().__init__()
        self.data = []
        self.load_data()
        self.shared_definitions = shared_definitions
        self.explore_models()
        self.print_properties()
        self.save_schema()

    def build_schema(self):
        super().build_schema()
        self.schema.update({
            'type': 'object',
            'required': [],
            'additionalProperties': False,
            'properties': {},
        })

    @property
    def properties(self):
        return self.schema['properties']

    @property
    def required(self):
        return self.schema['required']

    @required.setter
    def required(self, value):
        self.schema['required'] = value

    def load_data(self):
        for key in self.source_keys:
            with open('{}data/{}.js'.format(self.files_root, key), 'r') as file_object:
                self.data.extend(json.load(file_object, object_pairs_hook=OrderedDict))

    def gather_required(self):
        required = []
        for model in self.data:
            for attr in model.keys():
                if attr not in required:
                    required.append(attr)
        self.required = required

    def print_properties(self):
        name = ' '.join(self.target_key.split('-')).capitalize()
        print(name, '-'*(100-len(name)))
        pprint(self.properties)
        print('fields not in properties', set(self.fields.keys()).difference(self.properties.keys()))
        print('properties not in fields', set(self.properties.keys()).difference(self.fields.keys()))

    def gather_definitions(self):
        for model in self.data:
            for attr, data in model.items():
                    self.shared_definitions.add_definition_data(attr, data)

    def gather_properties_order(self):
        for model in self.data:
            for attr in model.keys():
                if attr not in self.properties_order:
                    self.properties_order.append(attr)

        # Workaround for object type properties.
        for model in self.data:
            for attr in model.keys():
                if self.js_attr(model[attr]) == 'object':
                    for nested_attr in model[attr].keys():
                        if nested_attr not in self.properties_order:
                            self.properties_order.append(nested_attr)

    def explore_models(self):
        self.gather_required()
        self.gather_definitions()
        self.gather_properties_order()

        for model in self.data:
            for attr, value in model.items():

                # Load data from field definitions if this is the first time we evaluate this prop
                if attr not in self.properties:
                    self.properties[attr] = {'type': []}
                    for k, v in self.fields.get(attr, {}).items():
                        self.properties[attr][k] = v

                # Populate types
                attr_type = self.js_attr(value)
                if isinstance(self.properties[attr]['type'], list):
                    if attr_type not in self.properties[attr]['type']:
                        self.properties[attr]['type'].append(self.js_attr(value))
                        self.properties[attr]['type'].sort()

                # Handle local enums
                if 'enum' in self.properties[attr]:
                    if value.__class__ == list:
                        self.properties[attr]['enum'].extend(value)
                    else:
                        self.properties[attr]['enum'].append(value)
                    self.properties[attr]['enum'] = list(set(self.properties[attr]['enum']))
                    self.properties[attr]['enum'].sort()

        for attr in self.properties.keys():
            if set(self.properties[attr].keys()).intersection(self.schema_combining_attrs):
                self.properties[attr].pop('type')
            elif isinstance(self.properties[attr]['type'], list):
                if len(self.properties[attr]['type']) == 1:
                    self.properties[attr]['type'] = self.properties[attr]['type'][0]


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
            'description': 'A ship size in the game',
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
            'description': 'The card\'s text describing it\'s effect on the target.',
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
            'description': 'The faction (or factions) this ship belongs to.',
            'items': {
                '$ref': 'definitions.json#/faction'
            }
        },
        'actions': {
            'minItems': 0,
            'description': 'A list of all the actions the ship is capable.',
            'items': {
                '$ref': 'definitions.json#/action'
            }
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
            'items': {
                'description': 'Each element in this array contains a representation of the '
                               'maneuver costs for the maneuvers available to the huge ship at a '
                               'particular speed, determined its position in the array. ei. '
                               '``ship.maneuvers_energy[1]`` will provide all '
                               'maneuver cost for the maneuvers available to the huge ship at '
                               'speed 1.\n'
                               'This array\'s length should match the array\'s length of the '
                               'array in the maneuvers property.\n'
                               'In other words ``ship.maneuvers.length`` should equal to '
                               '``ship.maneuvers_energy.length``',
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
                                   '``ship.maneuvers_energy[2].length``',
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
            'items': {
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
                                   'particular huge ship at that particular speed.\n.',
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
            with open('{}data/{}.js'.format(self.files_root, key), 'r') as file_object:
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
            }
        },
        'actions': {
            'minItems': 0,
            'items': {
                '$ref': 'definitions.json#/action'
            }
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
            'items': {
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
            'pattern': '^(huge|small)$'
        }
    }

    def load_data(self):
        for key in self.source_keys:
            with open('{}data/{}.js'.format(self.files_root, key), 'r') as file_object:
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