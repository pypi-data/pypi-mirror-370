from pydantic_ai.providers.google_gla import GoogleGLAProvider


class CustomGeminiGLA(GoogleGLAProvider):
    def __init__(self, api_key: str, base_url: str, *args, **kwargs) -> None:
        self._x_base_url = base_url
        super().__init__(api_key, *args, **kwargs)

    @property
    def base_url(self) -> str:
        return self._x_base_url
