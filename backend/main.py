from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="UAReady Email & Domain Validator",
    description=(
        "Validates internationalised email addresses and domain names conforming to "
        "SMTPUTF8 (RFC 6531), EAI (RFC 6532), and IDNA2008 standards. "
        "Built for UA Adaptation Hackathon Nepal 2026."
    ),
    version="1.0.0",
    contact={"name": "UA Hackathon Nepal 2026", "url": "https://icann.org/ua"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["Validation"])

# Serve the browser demo at /  — must come last so API routes take priority
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
