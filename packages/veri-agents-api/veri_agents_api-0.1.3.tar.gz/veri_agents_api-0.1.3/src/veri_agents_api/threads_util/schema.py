from datetime import datetime

from pydantic import BaseModel, Field

class ThreadInfo(BaseModel):
    """Information about a single thread."""

    thread_id: str
    # workflow_id: str
    # name: str
    # user: str
    # metadata: dict = Field(default={})
    # creation: datetime = Field(default_factory=datetime.now)
