class ConfigError(Exception):
    """Erro base de configuração."""

class ConfigFileNotFound(ConfigError):
    pass

class ConfigParseError(ConfigError):
    pass

class ConfigValidationError(ConfigError):
    pass