from typing import Any

from pydantic import BaseModel


class ActionContext(BaseModel):
    obj: Any
