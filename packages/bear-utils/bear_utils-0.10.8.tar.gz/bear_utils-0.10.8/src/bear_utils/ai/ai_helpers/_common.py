from enum import Enum, StrEnum


class EnvironmentMode(Enum):
    TESTING = "testing"
    PRODUCTION = "production"


class AIModel(StrEnum):
    """Enumeration of AI models."""

    GPT_5 = "gpt-5"
    GPT_5_NANO = "gpt-5-nano"
    GPT_5_MINI = "gpt-5-mini"

    GPT_4_1 = "gpt-4.1"
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_4_1_MINI = "gpt-4.1-mini"


GPT_5 = AIModel.GPT_5
GPT_5_NANO = AIModel.GPT_5_NANO
GPT_5_MINI = AIModel.GPT_5_MINI

GPT_4_1 = AIModel.GPT_4_1
GPT_4_1_NANO = AIModel.GPT_4_1_NANO
GPT_4_1_MINI = AIModel.GPT_4_1_MINI

TESTING_MODE = EnvironmentMode.TESTING
PRODUCTION_MODE = EnvironmentMode.PRODUCTION
