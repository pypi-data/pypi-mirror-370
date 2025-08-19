from typing import Dict, Optional

class LunaVerseXError(Exception):
    pass

class APIError(LunaVerseXError):
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class ValidationError(LunaVerseXError):
    pass

class ConfigurationError(LunaVerseXError):
    pass

class ModelNotFoundError(ValidationError):
    pass