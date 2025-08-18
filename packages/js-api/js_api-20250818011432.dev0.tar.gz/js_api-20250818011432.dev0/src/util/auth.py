import os
from typing import Annotated

from fastapi import Header, HTTPException


async def get_token_header(x_api_key: Annotated[str, Header()]):
    api_key = os.environ["API_KEY"]
    if api_key is None or api_key.strip() == "":
        raise HTTPException(status_code=500, detail="API Key not set")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
