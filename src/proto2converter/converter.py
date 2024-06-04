import argparse
import pathlib

import yaml

import google.protobuf.message
import google.protobuf.text_format
import google.protobuf.json_format
import tritonclient.grpc as tritongrpcclient


def model_config_pb2_to_json(filepath: pathlib.Path) -> str:
    """
    Converts a ModelConfig protobuf to a JSON string.
    """
    with open(filepath, "r") as f:
        json_obj = google.protobuf.json_format.MessageToJson(
            google.protobuf.text_format.Parse(
                f.read(),
                tritongrpcclient.model_config_pb2.ModelConfig()
            ),
            preserving_proto_field_name=True
        )
    return json_obj


def model_config_pb2_from_yaml(filepath: pathlib.Path) -> str:
    """
    Converts a ModelConfig protobuf to a YAML string.
    """
    json_str = model_config_pb2_to_json(filepath)

    return yaml.dump(
        yaml.load(json_str, Loader=yaml.FullLoader), Dumper=yaml.Dumper, sort_keys=False,
    )


converters = {
    "json": model_config_pb2_to_json,
    "yaml": model_config_pb2_from_yaml
}


def main():
    parser = argparse.ArgumentParser(description="Convert a ModelConfig protobuf to a JSON or YAML string.")
    parser.add_argument("filepath", type=pathlib.Path, help="Path to the ModelConfig protobuf file.")
    parser.add_argument("format", choices=converters.keys(), help="Output format.")
    args = parser.parse_args()

    print(converters[args.format](args.filepath))


if __name__ == "__main__":
    sys.exit(main())
