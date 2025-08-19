from pipe_agent.api import ApiClient
from pipe_agent.config import Model

def test_api_client_non_stream(mock_server):
    model = Model(
        id=1,
        openai_api_key="test_key",
        api_base_url=f"{mock_server}/v1/chat/completions",
        model_tag="test-model"
    )
    client = ApiClient(model)
    
    messages = [{"role": "user", "content": "Hello world."}]
    response_iterator = client.call(messages, use_sse=False)
    
    response = "".join(response_iterator)
    assert response == "Hello world."

def test_api_client_stream(mock_server):
    model = Model(
        id=1,
        openai_api_key="test_key",
        api_base_url=f"{mock_server}/v1/chat/completions",
        model_tag="test-model"
    )
    client = ApiClient(model)
    
    prompt = "Hello world. This is a test."
    messages = [{"role": "user", "content": prompt}]
    response_iterator = client.call(messages, use_sse=True)
    
    # The mock server splits by punctuation.
    chunks = list(response_iterator)
    assert len(chunks) == 2
    assert chunks[0] == "Hello world."
    assert chunks[1] == " This is a test." # Note the leading space kept by regex
    
    full_response = "".join(chunks)
    assert full_response == prompt 