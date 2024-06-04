from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


def customizer(schema):
    properties = schema['properties']

    for key, value in properties.items():
        schema_type = None
        if 'anyOf' in properties[key]:
            for item in properties[key]['anyOf']:
                if '$ref' in item:
                    schema_type = item
                    break
                if 'enum' in item:
                    item.update({'type': 'string'})
                    schema_type = item
                    break
                if item['type'] != 'null':
                    schema_type = item
                    break

        if schema_type is None:
            continue

        properties[key].update(schema_type)
        del properties[key]['anyOf']

    schema['properties'] = properties

    if "x-kubernetes-preserve-unknown-fields" in schema:
        del schema["x-kubernetes-preserve-unknown-fields"]

    return schema


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(json_schema_extra=customizer)
