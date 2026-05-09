from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from enum import Enum
from fastapi import FastAPI

app = FastAPI()

STUDENT_ID = os.getenv("STUDENT_ID", "YOUR-STUDENT-ID")


@app.middleware("http")
async def student_id_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Student-ID"] = "bscs23015"
    return response


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 2
    recovery_timeout: float = 5.0
    failure_count: int = 0
    state: CircuitState = CircuitState.CLOSED
    opened_at: float | None = None

    def allow_request(self) -> bool:
        if self.state != CircuitState.OPEN:
            return True
        if self.opened_at is None:
            return False
        if time.monotonic() - self.opened_at >= self.recovery_timeout:
            self.state = CircuitState.HALF_OPEN
            return True
        return False

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.monotonic()


breaker = CircuitBreaker()


def slow_llm_call(prompt: str) -> str:
    time.sleep(10)
    return f"Naive LLM response for: {prompt}"


async def safe_llm_call(prompt: str) -> str:
    if not breaker.allow_request():
        raise RuntimeError("circuit_open")

    try:
        # Move the blocking LLM call off the event loop and cap how long we wait.
        result = await asyncio.wait_for(asyncio.to_thread(slow_llm_call, prompt), timeout=2.0)
        breaker.record_success()
        return result
    except Exception:
        breaker.record_failure()
        raise


@app.get("/health")
async def health():
    return {"status": "ok", "breaker": breaker.state.value}


@app.get("/generate")
async def generate(prompt: str = "Explain recursion"):
    try:
        summary = await safe_llm_call(prompt)
        return {
            "mode": "live",
            "prompt": prompt,
            "summary": summary,
            "breaker": breaker.state.value,
        }
    except Exception:
        # Fallback keeps the API responsive when the upstream model is slow or down.
        return {
            "mode": "fallback",
            "prompt": prompt,
            "summary": f"Fallback summary for: {prompt}",
            "breaker": breaker.state.value,
        }
