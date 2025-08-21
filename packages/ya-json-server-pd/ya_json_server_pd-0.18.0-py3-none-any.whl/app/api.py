import uvicorn
from fastapi import FastAPI

from app.handlers.exceptions import APIException, api_exception_handler
from app.views.graphql_routes import graphql_router
from app.views.routes import router

description = """A REST API for JSON content with zero coding.

Technologies::
* Python 3.13
* FastAPI 0.116
"""
app = FastAPI(
    title="Yet Another JSON Server",
    description=description,
    version="2.0.0",
    openapi_tags=[{"name": "REST API"}],
)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(FileNotFoundError, api_exception_handler)
app.add_exception_handler(Exception, api_exception_handler)

app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL"])
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", reload=True)  # pragma: no cover
