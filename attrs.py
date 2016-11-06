import json
import copy
from collections import OrderedDict
from pprint import pprint

# FIXME
# definitsion = Slots
# definition = factions
# shipoverride = ship definition
# xws definition = redo all names -> maybe
# actions definitions
#

# FIXME
# Ships.faction for ships.factions
# normalize all manouver arrays
# normalize size attr
# separate huge from small and large

# FIXME
# Asteroids

# FIXME
# New project ultimate Game references merging LearToPlay, game reference and FAQ with errata

# FIXME
# Mark cards with errata.
# Card Clarifications


class SchemaBuilder:
    host = 'https://github.com/lvisintini/xwing-data/schema/'
    target_key = ''

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
        'enum',
        'minLength',
        'maxLength',
        'pattern',
        'minimum',
        'maximum',
        'exclusiveMinimum',
        'exclusiveMaximum',
        'maxItems',
        'minItems',
        'items',
    ]

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
            with open('./data/{}.js'.format(key), 'r') as file_object:
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
            if isinstance(self.properties[attr]['type'], list):
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
            'type': 'string',
            'enum': [],
        },
        'action': {
            'type': 'string',
            'enum': [],
        },
        'slot': {
            'type': 'string',
            'enum': [],
        },
        'size': {
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
            'description': 'The ship\'s name as written on the card itself.',
            'minLength': 1,
        },
        'factions': {
            'minItems': 1,
        },
        'actions': {
          'minItems': 0,
        },
        'energy': {
            'minimum': 1,
            "exclusiveMinimum": False,
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
        'epic_points': {
            'type': 'number',
            'minimum': 0,
            "exclusiveMinimum": False,
        },
        'size': {
            '$ref': 'definitions.json#/size',
            'pattern': '^huge$',
        },
        'maneuvers_energy': {
            'maxItems': 6,
            'minItems': 6,
            'items': {
                'type': 'array',
                'maxItems': 5,
                'minItems': 5,
                'items': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 3,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
            },
        },
        'maneuvers': {
            'maxItems': 6,
            'minItems': 6,
            'items': {
                'type': 'array',
                'maxItems': 5,
                'minItems': 5,
                'items': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 1,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
            },
        },
        'xws': {
            '$ref': 'definitions.json#/xws'
        },
    }

    def load_data(self):
        for key in self.source_keys:
            with open('./data/{}.js'.format(key), 'r') as file_object:
                unfiltered_data = json.load(file_object, object_pairs_hook=OrderedDict)
                self.data.extend([hs for hs in unfiltered_data if hs['size'] == 'huge'])


class PilotsBuilder(XWingSchemaBuilder):
    source_keys = ('pilots',)
    target_key = 'pilots'

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


class ShipsBuilder(XWingSchemaBuilder):
    source_keys = ('ships',)
    target_key = 'ships'

    fields = {
        'name': {
            'description': 'The ship\'s name as written on the card itself.',
            'minLength': 1,
        },
        'factions': {
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
            'maxItems': 6,
            'minItems': 6,
            'items': {
                'type': 'array',
                'maxItems': 10,
                'minItems': 10,
                'items': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 3,
                    "exclusiveMaximum": False,
                    "exclusiveMinimum": False,
                },
            },
        },
        'xws': {
            '$ref': 'definitions.json#/xws'
        },
        'size': {
            '$ref': 'definitions.json#/size'
        }
    }

    def load_data(self):
        for key in self.source_keys:
            with open('./data/{}.js'.format(key), 'r') as file_object:
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


if __name__ == '__main__':
    sd = SharedDefinitionsBuilder()

    builders = [
        HugeShipsBuilder,
        ShipsBuilder,
        PilotsBuilder,
        UpgradesBuilder,
        SourcesBuilder,
        DamageDeckBuilder,
    ]

    for builder in builders:
        builder(sd)

    sd.save_schema()
    #sd.print_schema()


'''
    def explore_models(self):
        for model_name, model_data in self.models.items():
            properties = self.schemas[model_name]['properties']
            required = set(list(model_data[0].keys()))
            for model in model_data:
                required.intersection_update(model.keys())
            self.schemas[model_name]['required'] = list(required)
            self.schemas[model_name]['required'].sort()


            for model_obj in model_data:
                for attr, value in model_obj.items():
                    required.add(attr)

                    if attr in self.DEFINITIONS['Main']:
                        self.actions.extend(value)
                    if attr == 'action':
                        self.actions.append(value)

                    if attr == 'slots':
                        slots.extend(value)
                    if attr == 'slot':
                        slots.append(value)

                    if attr == 'factions':
                        factions.extend(value)
                    if attr == 'faction':
                        factions.append(value)


        slots = list(set(slots))
        slots.sort()

        factions = list(set(factions))
        factions.sort()

        actions = list(set(actions))
        actions.sort()

        self.schemas['Upgrades']['properties']['slot']['enum'] = slots
        self.schemas['Pilots']['properties']['slots']['items'] = OrderedDict()
        self.schemas['Pilots']['properties']['slots']['items']['type'] = 'string'
        self.schemas['Pilots']['properties']['slots']['items']['enum'] = slots

        self.schemas['Pilots']['properties']['faction']['enum'] = factions
        self.schemas['Ships']['properties']['factions']['items'] = OrderedDict()
        self.schemas['Ships']['properties']['factions']['items']['type'] = 'string'
        self.schemas['Ships']['properties']['factions']['items']['enum'] = factions

        self.schemas['Ships']['properties']['actions']['items'] = OrderedDict()
        self.schemas['Ships']['properties']['actions']['items']['type'] = 'string'
        self.schemas['Ships']['properties']['actions']['items']['enum'] = actions
'''