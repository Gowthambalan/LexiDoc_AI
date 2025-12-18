from pydantic import BaseModel

class RecentResponseOut(BaseModel):
    username: str
    filename: str | None
    response_time: float | None
    qtokens: float | None
    atokens: float | None
    total_tokens: float | None
    cost: float | None

    class Config:
        from_attributes = True
