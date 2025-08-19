class PipeAgentError(Exception):
    """Base exception class for pipe-agent."""
    pass

class ConfigError(PipeAgentError):
    """Raised for configuration-related errors."""
    pass

class ModelError(PipeAgentError):
    """Raised for model selection errors."""
    pass

class APIError(PipeAgentError):
    """Raised for API call errors."""
    pass
