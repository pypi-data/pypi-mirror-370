from types import SimpleNamespace
from pipe_agent.processing import PromptBuilder

def test_prompt_builder_basic():
    # Mock args and config
    args = SimpleNamespace(prompt_before=None, prompt_after=None)
    config = SimpleNamespace(
        prompt_before=None, 
        prompt_after=None, 
        prompt_concat_nl=True
    )
    
    builder = PromptBuilder(config, args)
    result = builder.build("main prompt")
    assert result == "main prompt"

def test_prompt_builder_with_cli_args():
    args = SimpleNamespace(
        prompt_before=["cli before"], 
        prompt_after=["cli after"]
    )
    config = SimpleNamespace(
        prompt_before=None, 
        prompt_after=None, 
        prompt_concat_nl=True
    )
    
    builder = PromptBuilder(config, args)
    result = builder.build("main")
    assert result == "cli before\nmain\ncli after"

def test_prompt_builder_with_config_vars():
    args = SimpleNamespace(prompt_before=None, prompt_after=None)
    config = SimpleNamespace(
        prompt_before="config before", 
        prompt_after="config after", 
        prompt_concat_nl=True
    )
    
    builder = PromptBuilder(config, args)
    result = builder.build("main")
    assert result == "config before\nmain\nconfig after"

def test_prompt_builder_full_concatenation():
    args = SimpleNamespace(
        prompt_before=["cli before 1", "cli before 2"], 
        prompt_after=["cli after 1"]
    )
    config = SimpleNamespace(
        prompt_before="config before", 
        prompt_after="config after", 
        prompt_concat_nl=True
    )
    
    builder = PromptBuilder(config, args)
    result = builder.build("main")
    expected = "config before\ncli before 1\ncli before 2\nmain\ncli after 1\nconfig after"
    assert result == expected

def test_prompt_builder_no_newline_concatenation():
    args = SimpleNamespace(prompt_before=["before"], prompt_after=["after"])
    config = SimpleNamespace(
        prompt_before=None, 
        prompt_after=None, 
        prompt_concat_nl=False
    )
    
    builder = PromptBuilder(config, args)
    result = builder.build("main")
    assert result == "beforemainafter" 