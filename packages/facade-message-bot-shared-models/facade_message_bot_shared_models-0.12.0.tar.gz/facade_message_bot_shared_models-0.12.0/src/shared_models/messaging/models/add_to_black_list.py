from pydantic import BaseModel, Field
from typing import Annotated


class AddToBlackList(BaseModel):
    text: Annotated[str, Field(description="The text to be added to the blacklist.")]
