import yaml
import pydantic
import jsonref


class KubeResourceBase:
    """KubeResourceBase is base class that provides methods to converts dataclass
    into Kubernetes CR. It provides ability to create a Kubernetes CRD from the
    class and supports deserialization of the object JSON from K8s into Python
    objects with support for Metadata.
    """

    @classmethod
    def apischema(cls):
        """Get serialized openapi 3.0 schema for the cls.

        The output is a dict with (possibly nested) key-value pairs based on
        the schema of the class. This is used to generate the CRD schema down
        the line which rely on (a subset?) of OpenAPIV3 schema for the
        definition of a Kubernetes Custom Resource.
        """
        if not hasattr(cls, "spec"):
            raise KeyError("spec field is missing")

        spec: pydantic.BaseModel = cls.spec

        spec_json_schema = spec.model_json_schema()
        spec_jsonref_schema = jsonref.replace_refs(spec_json_schema, proxies=False)
        del spec_jsonref_schema["$defs"]

        return spec_jsonref_schema

    @classmethod
    def additional_printer_columns(cls):
        if not hasattr(cls, "additionalPrinterColumns"):
            return []

        return cls.additionalPrinterColumns

    @classmethod
    def apischema_json(cls):
        """JSON Serialized OpenAPIV3 schema for the cls."""
        return jsonref.dumps(cls.apischema())

    @classmethod
    def apischema_yaml(cls):
        """YAML Serialized OpenAPIV3 schema for the cls."""
        yaml_schema = yaml.load(cls.apischema_json(), Loader=yaml.Loader)
        return yaml.dump(yaml_schema, Dumper=yaml.Dumper)

    @classmethod
    def singular(cls):
        """Return the 'singular' name of the CRD.

        This is currently just the lower case name of the Python class.
        """
        return cls.__name__.lower()

    @classmethod
    def plural(cls):
        """Plural name of the CRD.

        This defaults ot just the lower case name of the Python class with an
        additional 's' in the end of the name. This might not be correct for
        all CRs though.

        TODO: Make singular and plural a configurable parameter using dunder
        attributes on cls like ``__group__`` and ``__version__``.
        """
        return f'{cls.singular()}s'

    @classmethod
    def shortNames(cls):
        """
        List of short names of the CRD

        Attributes __short_names__
        """

        if not hasattr(cls, "__short_names__"):
            return []

        return [name.lower() for name in cls.__short_names__]

    @classmethod
    def crd_schema_dict(cls):
        """Return cls serialized as a Kubernetes CRD schema dict.

        This returns a dict representation of the Kubernetes CRD Object of cls.
        """
        crd = {
            'apiVersion': 'apiextensions.k8s.io/v1',
            'kind': 'CustomResourceDefinition',
            'metadata': {
                'name': f'{cls.plural()}.{cls.__group__}',
            },
            'spec': {
                'group': cls.__group__,
                'scope': 'Namespaced',
                'names': {
                    'singular': cls.singular(),
                    'plural': cls.plural(),
                    'kind': cls.__name__,
                },
                'versions': [
                    {
                        'name': cls.__version__,
                        # This API is served by default, currently there is no
                        # support for multiple versions.
                        'served': True,
                        'storage': True,
                        'schema': {
                            'openAPIV3Schema': {
                                'type': 'object',
                                'properties': {
                                    'spec': cls.apischema(),
                                },
                            }
                        },
                    }
                ],
            },
        }

        short_names = cls.shortNames()

        if short_names:
            crd["spec"]["names"]["shortNames"] = short_names

        additionalPrinterColumns = cls.additional_printer_columns()

        if additionalPrinterColumns:
            crd["spec"]["versions"][0]["additionalPrinterColumns"] = additionalPrinterColumns

        return crd

    @classmethod
    def crd_schema(cls):
        """Serialized YAML representation of Kubernetes CRD definition for cls.

        This serializes the dict representation from
        :py:method:`crd_schema_dict` to YAML.
        """
        return yaml.dump(
            yaml.load(
                jsonref.dumps(cls.crd_schema_dict()), Loader=yaml.Loader
            ),
            Dumper=yaml.Dumper,
        )
    
    @classmethod
    def json_schema(cls):
        """Serialized JSON representation of Kubernetes CRD definition for cls.

        This serializes the dict representation from
        :py:method:`crd_schema_dict` to JSON.
        """
        return jsonref.dumps(cls.crd_schema_dict())
