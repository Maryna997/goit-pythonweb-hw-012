import aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from api import contacts, auth, users

app = FastAPI()


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)


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


app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)
