"""Main init file for FastAPI project interoperability"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from converters.api.router import api_router, error_router


def get_application() -> FastAPI:
    """Create app."""
    _app = FastAPI(
        title="envidat-converters",
        license_info={
            "name": "MIT",
            "url": "https://gitlabext.wsl.ch/EnviDat/envidat-converters/-/raw/main/LICENSE",
        },
    )
    return _app


# Create app instance
app = get_application()

# Add routers
app.include_router(api_router)
app.include_router(error_router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
