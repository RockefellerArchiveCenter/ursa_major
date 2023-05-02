import json
from os.path import join

import rac_schema_validator


def validate_bag_data(bag_data, schema_name):
    """Validates bag data against RAC schemas."""
    base_file = open(join('rac_schemas', 'schemas', 'base.json'), 'r')
    base_schema = json.load(base_file)
    base_file.close()
    with open(join('rac_schemas', 'schemas', schema_name), 'r') as object_file:
        object_schema = json.load(object_file)
        return rac_schema_validator.is_valid(bag_data, object_schema, base_schema)
