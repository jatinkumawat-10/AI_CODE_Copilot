from pydantic import BaseModel


class ApprovalStatusUpdate(BaseModel):
    status: str  # one of: approved | rejected | applied
