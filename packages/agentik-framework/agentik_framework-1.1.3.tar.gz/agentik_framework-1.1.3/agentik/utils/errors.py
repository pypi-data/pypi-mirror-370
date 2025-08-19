class AgentikError(Exception):
    """Base Agentik error."""


class AuthError(AgentikError):
    """Authentication / permission error (e.g., invalid API key)."""


class RateLimitError(AgentikError):
    """API rate limited (429)."""


class NetworkError(AgentikError):
    """Network or timeout error."""


class ToolError(AgentikError):
    """A tool raised an error."""


class ConfigError(AgentikError):
    """Invalid configuration."""
