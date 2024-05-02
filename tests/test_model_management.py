import tritonclient.http as tritonhttpclient

import numpy as np

import testing.repository as repository_utils

def test_load_model_to_triton(setup_triton, models_repository):
    triton_client: tritonhttpclient.InferenceServerClient = setup_triton

    model_name = "simple"

    config_path = models_repository[model_name]["config"]
    model_path = models_repository[model_name]["model"]

    with open(model_path, "rb") as f:
        model_bytes = f.read()

    json_obj = repository_utils.pbtxt_to_json(config_path)

    triton_client.load_model(
        model_name=model_name,
        config=json_obj,
        files={
            "file:1/model.graphdef": model_bytes,
        },
    )
    
    inputs = []
    outputs = []
    inputs.append(tritonhttpclient.InferInput("INPUT0", [8, 16], "INT32"))
    inputs.append(tritonhttpclient.InferInput("INPUT1", [8, 16], "INT32"))

    # Initialize the data
    inputs[0].set_data_from_numpy(np.ones([8, 16], dtype=np.int32))
    inputs[1].set_data_from_numpy(np.zeros([8, 16], dtype=np.int32))

    outputs.append(tritonhttpclient.InferRequestedOutput("OUTPUT0"))
    outputs.append(tritonhttpclient.InferRequestedOutput("OUTPUT1"))

    results = triton_client.infer(
        model_name,
        inputs,
        model_version="1",
        outputs=outputs,
        )

    output0_data = results.as_numpy("OUTPUT0")
    output1_data = results.as_numpy("OUTPUT1")

    assert triton_client.is_model_ready(model_name, model_version="1")
    assert triton_client.get_model_repository_index()
    np.testing.assert_array_equal(output0_data, np.ones([8, 16], dtype=np.int32))
    np.testing.assert_array_equal(output1_data, np.ones([8, 16], dtype=np.int32))




    