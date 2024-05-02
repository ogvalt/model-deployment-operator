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
    
    