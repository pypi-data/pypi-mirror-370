from pydantic import BaseModel, Field
from typing import Annotated


class ErrorResponse(BaseModel):
    exception: Annotated[str, Field(description="The type of exception that occurred.")]
    detail: Annotated[
        str | None, Field(description="A human-readable message describing the error.")
    ] = None
