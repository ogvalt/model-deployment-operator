import pytest
import pathlib
import triton_testcontainer as tritoncontainer


@pytest.fixture(scope="session")
def setup_triton(request):
    # start triton
    triton = tritoncontainer.TritonContainer()

    triton.start()

    def remove_triton_container():
        triton.stop()

    request.addfinalizer(remove_triton_container)

    return triton.get_client()

@pytest.fixture
def models_repository(shared_datadir) -> dict:

    models_repository_path: pathlib.Path = shared_datadir / "models_repository"

    repository_models = {
        "simple":{
            "model": models_repository_path / "simple" / "1" / "model.graphdef",
            "config": models_repository_path / "simple" / "config.pbtxt",
        }
    }

    return repository_models

    