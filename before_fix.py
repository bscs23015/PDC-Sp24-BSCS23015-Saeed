from fastapi import FastAPI
import time
import os

app = FastAPI()

STUDENT_ID = os.getenv("STUDENT_ID", "YOUR-STUDENT-ID")


@app.middleware("http")
async def student_id_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Student-ID"] = "bscs23015"
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/generate")
async def generate(prompt: str = "Explain recursion"):
    # Simulates the naive synchronous LLM dependency.
    # While this call is sleeping, the worker is blocked and other requests wait.
    time.sleep(10)
    return {"prompt": prompt, "summary": f"Naive LLM response for: {prompt}"}
