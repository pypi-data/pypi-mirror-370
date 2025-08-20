from pydantic import BaseModel


class Distribution(BaseModel):
    type: str
    parameters: dict[str, float]


class ParameterDistribution(BaseModel):
    name: str
    distribution: Distribution
