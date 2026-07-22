from pydantic import BaseModel


class ReviewResponse(BaseModel):
    review: str