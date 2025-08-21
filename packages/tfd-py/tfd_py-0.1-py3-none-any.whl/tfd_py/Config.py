class Config:
    _instance = None
    
    def __init__(self, api_key=None, language='en', debug=False):
        """Initialize the configuration with an API key.

        Args:
            api_key (_type_, Required): Your OpenAPI key goes here. Defaults to None.
            language (str, optional): The language for the API response, Possible options here are ko, en, de, fr, ja, zh-CN, zh-TW, it, pl, pt, ru, es. Defaults to 'en' (English).
        Raises:
            ValueError: If api_key is None, a ValueError is raised.
            RuntimeError: If Config has not been initialized, a RuntimeError is raised when trying to access the instance.
        """
        if api_key is None:
            raise ValueError("API key must be provided")
        self.api_key = api_key
        self.language = language
        self.debug = debug
        Config._instance = self
    
    @classmethod
    def get(cls):
        if cls._instance is None:
            raise RuntimeError("Config has not been initialized")
        return cls._instance