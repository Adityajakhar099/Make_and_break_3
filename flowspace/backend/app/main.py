from .api import app  # re-use the FastAPI app defined in api.py

# If run directly with `python -m app.main` uvicorn won't auto-run,
# use `uvicorn app.main:app --reload --port 8000`
