import pytest
import io
from pipe_agent.app import PipeAgentApp

@pytest.fixture
def mock_app_config(tmp_path, monkeypatch, mock_server):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    monkeypatch.setenv("PIPE_AGENT_CONFIG_PATH", str(config_dir))

    # Create models.yaml pointing to the mock server
    models_yaml = config_dir / "models.yaml"
    models_yaml.write_text(f"""
models:
    - 
        id: 1
        openai_api_key: "test_key"
        api_base_url: "{mock_server}/v1/chat/completions"
        model_tag: "test-model"
        model_name: "test"
""")
    return config_dir

def test_app_e2e_basic_query(mock_app_config, monkeypatch, capsys):
    # Simulate command line arguments
    monkeypatch.setattr("sys.argv", ["pipe-agent", "Hello?"])
    
    PipeAgentApp().run()
    
    captured = capsys.readouterr()
    # The mock server repeats the question.
    # The app adds a newline at the end.
    assert captured.out == "Hello?\n"
    assert "Enter prompt" not in captured.err # Should not show interactive prompt

def test_app_e2e_stdin_query(mock_app_config, monkeypatch, capsys):
    # Prepare the content that will be piped to stdin
    input_content = "This is a test from stdin."
    
    # Simulate piped stdin using io.StringIO
    monkeypatch.setattr("sys.stdin", io.StringIO(input_content))
    monkeypatch.setattr("sys.argv", ["pipe-agent"])
    
    PipeAgentApp().run()

    captured = capsys.readouterr()
    print(f"Captured Error: {captured.err}")
    # Mock server will repeat the content of stdin
    assert captured.out == input_content + "\n"
    assert "Enter prompt" not in captured.err

def test_app_e2e_stream_query(mock_app_config, monkeypatch, capsys):
    # Simulate command line arguments
    monkeypatch.setattr("sys.argv", ["pipe-agent", "-sse", "true", "Hello world. This is a test.中文测试。日本語テスト。"])
    
    PipeAgentApp().run()
    
    captured = capsys.readouterr()
    # The mock server repeats the question, and app adds a newline.
    assert captured.out == "Hello world. This is a test.中文测试。日本語テスト。\n" 