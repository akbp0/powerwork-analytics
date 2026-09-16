from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class PeriodFilter(BaseModel):
    period: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")


class WorkOrderDetailFilter(BaseModel):
    city: str | None = None
    period: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    category: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class CityRankingFilter(BaseModel):
    period: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    limit: int = Field(default=20, ge=1, le=200)


def parse_or_400(model: type[BaseModel], args: dict):
    """Returns (parsed_model, None) or (None, error_dict) for the route to
    turn into a 400 response without duplicating try/except everywhere."""
    try:
        return model(**args), None
    except ValidationError as exc:
        return None, {"error": "invalid_request", "details": exc.errors()}
