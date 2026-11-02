"""FastAPI demo for the Tool Agent.

Run (after installing requirements):
    uvicorn app:app --reload

Try:
    POST /run
    {"task": "score lead Bright Homes Realty, Real Estate, Austin TX, hello@brighthomes.example, 512-555-0100, https://brighthomes.example"}

    GET /tools  (the tool manifest, same as tools.json)

This file is optional for the portfolio demo. The core logic lives in
agent.py and works with plain Python, no server needed.
"""

import json
import os

from agent import run_task

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    FastAPI = None
    BaseModel = object


if FastAPI is None:
    raise SystemExit("Install requirements first: pip install -r requirements.txt")

app = FastAPI(title="Tool Agent")

with open(os.path.join(os.path.dirname(__file__), "tools.json"), encoding="utf-8") as f:
    TOOLS = json.load(f)


class Task(BaseModel):
    task: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tools")
def list_tools():
    return {"tools": TOOLS}


@app.post("/run")
def run(body: Task):
    return run_task(body.task)
