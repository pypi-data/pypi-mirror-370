from novacordpy import NovaClient

def test_client_run():
    client = NovaClient("FAKE_TOKEN")
    assert isinstance(client, NovaClient)
