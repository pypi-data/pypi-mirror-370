from typing import Callable, Optional
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute

def override_route(
    app: FastAPI,
    *,
    name: str,
    new_endpoint: Callable,
):
    """
    Replace the handler of a route with a new one, preserving all other route settings.
    """
    found: Optional[APIRoute] = None
    for r in app.routes:
        if isinstance(r, APIRoute) and r.name == name:
            found = r
            break
    if not found:
        raise LookupError(f"Method {name} not found")

    app.routes.remove(found)

    app.add_api_route(
        found.path,
        new_endpoint,
        methods=list(found.methods),
        response_model=found.response_model,
        status_code=found.status_code,
        tags=found.tags,
        summary=found.summary,
        description=found.description,
        response_description=found.response_description,
        responses=found.responses,
        deprecated=found.deprecated,
        name=found.name,
        include_in_schema=found.include_in_schema,
        response_model_exclude_unset=found.response_model_exclude_unset,
        response_model_exclude_defaults=found.response_model_exclude_defaults,
        response_model_exclude_none=found.response_model_exclude_none,
        openapi_extra=found.openapi_extra,
    )