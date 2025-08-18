"""Root router to import all other routers."""

from typing import Callable

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.routing import APIRoute

from converters.api import envidat_converter_api


class RouteErrorHandler(APIRoute):
    """Custom APIRoute that handles application errors and exceptions."""

    def get_route_handler(self) -> Callable:
        """Original route handler for extension."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Route handler with improved logging."""
            try:
                return await original_route_handler(request)
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise Exception from e
                raise HTTPException(status_code=500, detail="Internal server error")

        return custom_route_handler


# Create APIRouter() instance
api_router = APIRouter()

# Add routers to api_router
api_router.include_router(envidat_converter_api.router)

# Setup error router
error_router = APIRouter(route_class=RouteErrorHandler)
