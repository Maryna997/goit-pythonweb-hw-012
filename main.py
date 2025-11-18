import os

import aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from api import contacts, auth, users

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

app = FastAPI()


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, please try again later"},
    )


app.mount(
    "/codedocs",
    StaticFiles(directory="docs/_build/html", html=True),
    name="codedocs"
)

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)
