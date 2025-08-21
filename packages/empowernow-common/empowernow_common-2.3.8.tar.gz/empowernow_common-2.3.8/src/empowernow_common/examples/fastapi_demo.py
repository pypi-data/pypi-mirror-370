"""Run `uvicorn empowernow_common.examples.fastapi_demo:app --reload` to see a
secured endpoint powered by EmpowerNow Common.
"""

from __future__ import annotations

import os
from fastapi import FastAPI, Depends, HTTPException
from empowernow_common import init
from empowernow_common.client import OAuthClient
from empowernow_common.utils.logging_config import setup_default_logging

# Configure runtime helpers -------------------------------------------------
# One-liner bootstrap
init(strict_fips=False, enable_default_logging=False)
setup_default_logging()

# OAuth client --------------------------------------------------------------
OAUTH_TOKEN_URL = os.getenv("EXAMPLE_TOKEN_URL", "https://idp.example.com/oauth/token")
OAUTH_AUTH_URL = os.getenv(
    "EXAMPLE_AUTH_URL", "https://idp.example.com/oauth/authorize"
)
CLIENT_ID = os.getenv("EXAMPLE_CLIENT_ID", "demo")
CLIENT_SECRET = os.getenv("EXAMPLE_CLIENT_SECRET", "demo-secret")

oauth_client = OAuthClient(
    token_url=OAUTH_TOKEN_URL,
    authorization_url=OAUTH_AUTH_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

# FastAPI app ---------------------------------------------------------------
app = FastAPI(title="EmpowerNow Demonstration API")


async def get_token():
    try:
        return await oauth_client.get_token()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.get("/secure")
async def secure(token=Depends(get_token)):
    return {
        "message": "You reached a protected endpoint!",
        "token_excerpt": f"{token.access_token[:8]}…",
    }
