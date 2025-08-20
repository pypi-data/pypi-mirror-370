from dataclasses import dataclass

from ._common import GPT_4_1_NANO, PRODUCTION_MODE, AIModel, EnvironmentMode


@dataclass
class AIEndpointConfig:
    """Configuration for AI endpoint communication."""

    project_name: str
    bearer_token: str
    prompt: str
    testing_url: str
    production_url: str
    connection_timeout: int = 20
    append_json_suffix: bool = True
    json_suffix: str = " \nEnsure to output your response as json as specified in the prompt"
    chat_model: AIModel | str = GPT_4_1_NANO
    environment: EnvironmentMode = PRODUCTION_MODE

    @property
    def url(self) -> str:
        """Get the appropriate URL based on environment."""
        return self.testing_url if self.environment == EnvironmentMode.TESTING else self.production_url
