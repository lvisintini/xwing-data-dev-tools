import json
from collections import OrderedDict
from pprint import pprint

# FIXME
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
    data_files_root = '/home/lvisintini/src/xwing-data/'
    schema_files_root = '/home/lvisintini/src/xwing-data-dev-tools/schemas/'
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
        'uniqueItems',
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
        with open('{}/{}.json'.format(self.schema_files_root, self.target_key), 'w') as file_object:
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
            with open('{}data/{}.js'.format(self.data_files_root, key), 'r') as file_object:
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
