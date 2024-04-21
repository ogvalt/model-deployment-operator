import pathlib

import google.protobuf.message
import google.protobuf.text_format
import google.protobuf.json_format
import tritonclient.grpc as tritongrpcclient

def pbtxt_to_json(filepath: pathlib.Path) -> str:
    with open(filepath, "r") as f:
        json_obj = google.protobuf.json_format.MessageToJson(
            google.protobuf.text_format.Parse(
                f.read(), 
                tritongrpcclient.model_config_pb2.ModelConfig()
            )
        )
    return json_obj
