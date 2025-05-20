import re

from pydantic import BaseModel


class ChatModelCostPer1MToken(BaseModel):
    input: float
    cached: float | None = None
    output: float


class ChatModelCostTable(BaseModel):
    costs: dict[str, ChatModelCostPer1MToken] = {
        "gpt-4o-mini": ChatModelCostPer1MToken(input=0.15, cached=0.075, output=0.6),
        "gpt-4o": ChatModelCostPer1MToken(input=2.5, cached=1.25, output=10.0),
        "gpt-4.5-preview": ChatModelCostPer1MToken(input=75.0, cached=37.5, output=150.0),
        "gpt-4.1-nano": ChatModelCostPer1MToken(input=0.1, cached=0.025, output=0.4),
        "gpt-4.1-mini": ChatModelCostPer1MToken(input=0.4, cached=0.1, output=1.6),
        "gpt-4.1": ChatModelCostPer1MToken(input=2.0, cached=0.5, output=8.0),
        "o1-mini": ChatModelCostPer1MToken(input=3.0, cached=0.55, output=12.0),
        "o1-preview": ChatModelCostPer1MToken(input=15.0, output=60.0),
        "o1": ChatModelCostPer1MToken(input=15.0, cached=7.5, output=60.0),
        "o1-pro": ChatModelCostPer1MToken(input=150.0, output=600.0),
        "o3-mini": ChatModelCostPer1MToken(input=1.1, cached=0.55, output=4.4),
        "o3": ChatModelCostPer1MToken(input=10.0, cached=2.5, output=40.0),
        "o4-mini": ChatModelCostPer1MToken(input=1.1, cached=0.275, output=4.4),
    }

    def get_cost(self, model_name: str) -> ChatModelCostPer1MToken | None:
        return self.costs.get(model_name, None)

    def list_models(self) -> list[str]:
        return list(self.costs.keys())


def get_openai_model_name_from_version(model_version: str) -> str:
    return re.sub(r"-\d{4}-\d{2}-\d{2}$", "", model_version)


def calculate_cost(input_tokens: int, cached_tokens: int, output_tokens: int, model_version: str) -> float:
    model_name = get_openai_model_name_from_version(model_version)
    cost_per_1m_tokens = ChatModelCostTable().get_cost(model_name)
    if cost_per_1m_tokens is None:
        print(f'Model name "{model_name}" is not found in the cost table.')
        return 0.0

    input_cost_per_1m_tokens = cost_per_1m_tokens.input / 10**6
    cached_cost_per_1m_tokens = cost_per_1m_tokens.cached / 10**6 if cost_per_1m_tokens.cached is not None else 0.0
    output_cost_per_1m_tokens = cost_per_1m_tokens.output / 10**6

    non_cached_input_tokens = input_tokens - cached_tokens
    cost = (
        non_cached_input_tokens * input_cost_per_1m_tokens
        + cached_tokens * cached_cost_per_1m_tokens
        + output_tokens * output_cost_per_1m_tokens
    )

    return cost
