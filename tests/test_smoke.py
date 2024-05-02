def test_readiness(setup_triton):
    triton_client = setup_triton
    assert triton_client.is_server_ready()
