# PDC-Sp24-BSCS23015-Saeed
Esha Saeed - bscs23015

# Final PDC Project

This project contains a FastAPI application with two versions of the same service:
- `before_fix.py` shows the blocking, synchronous implementation.
- `after_fix.py` shows the improved version with a circuit breaker and non-blocking execution.

## Requirements

- Ubuntu
- Python 3.10 or newer
- `pip`

## Create A Virtual Environment

```bash
cd ~/Desktop/final_pdc
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install --upgrade pip
pip install fastapi uvicorn pytest
```

## Run The Code

To run the improved version:

```bash
uvicorn after_fix:app --reload
```

To run the original version:

```bash
uvicorn before_fix:app --reload
```

The API will be available at:

```bash
http://127.0.0.1:8000
```

## Test The Application

If you add or already have automated tests, run them with:

```bash
pytest
```

Since this workspace does not currently include test files, you can still do a quick manual smoke test in Ubuntu using `curl`:

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/generate?prompt=Explain%20recursion"
```

## Notes

- `after_fix.py` includes a `/health` endpoint and a `/generate` endpoint.
- The improved version is designed to avoid blocking the server when the simulated LLM call is slow.
- The `X-Student-ID` response header is set in both files.
