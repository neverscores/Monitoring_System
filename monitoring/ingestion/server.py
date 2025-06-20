from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from collections import deque
import socket
import logging
import time
from monitoring.influx_client import write_metrics
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import request_validation_exception_handler


app = FastAPI()

# Store up to 1000 recent metrics in memory
metrics_history = deque(maxlen=1000)

class CPU(BaseModel):
    per_core: List[float]
    average: float

class Memory(BaseModel):
    total: int
    used: int
    free: int
    percent: float

class Disk(BaseModel):
    total: int
    used: int
    free: int
    percent: float

class MetricsPayload(BaseModel):
    timestamp: int
    hostname: str
    cpu: CPU
    memory: Memory
    disk: Disk
# Simple in-memory store of received metrics
received_metrics = []

# auth token
AUTH_TOKEN = "dummy_token"

@app.post("/ingest")
async def ingest_metrics(payload: MetricsPayload, authorization: Optional[str] = Header(None)):
    if authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    received_metrics.append(payload.dict())
    print("Calling write_metrics with:", payload.dict())
    metrics_history.append(payload.dict()) 
    write_metrics(payload.dict()) 
    return {"message": "Metrics received"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Metrics API!"}

    
@app.get("/history")
def get_history():
    return list(metrics_history)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"Validation error: {exc.errors()}")
    return await request_validation_exception_handler(request, exc)
