from datetime import datetime

from pydantic import BaseModel


class AccountSummary(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountStats(BaseModel):
    """Placeholder until game catalog / library exists."""

    orders_count: int
    message: str = "Game library coming soon."
