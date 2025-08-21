"""{...}."""

import collections.abc
import functools
import typing

import fastapi
import fastapi.params
import pydantic

import sthali_db

from .crud import CRUD


@pydantic.dataclasses.dataclass
class RouterSpecification:
    """Represents the configuration for a router.

    Attributes:
        prefix (str): The prefix for the router.
        routes (list[Route]): The list of routes for the router.
        tags (list[str]): The tags for the router.
    """

    @pydantic.dataclasses.dataclass
    class Route:
        """Represents a route in the application.

        Attributes:
            path (str): The URL path for the route.
            endpoint (collections.abc.Callable[..., typing.Any]): The function that handles the route.
            response_model (typing.Any): The response model for the route.
            methods (list[str]): The HTTP methods supported by the route.
            status_code (int): The HTTP status code for the response. Default is 200.
            dependencies (list[type[fastapi.params.Depends]]): The dependencies for the route. Default is None.
            name (str | None): The name of the route. Default is None.
        """

        path: typing.Annotated[str, pydantic.Field(description="The URL path for the route")]
        endpoint: typing.Annotated[
            collections.abc.Callable[..., typing.Any], pydantic.Field(description="The function that handles the route")
        ]
        response_model: typing.Annotated[typing.Any, pydantic.Field(description="The response model for the route")]
        methods: typing.Annotated[
            list[typing.Literal["GET", "POST", "PUT", "PATCH", "DELETE"]],
            pydantic.Field(description="The HTTP methods supported by the route"),
        ]
        status_code: typing.Annotated[
            int, pydantic.Field(default=200, description="The HTTP status code for the response")
        ]
        dependencies: typing.Annotated[
            list[type[fastapi.params.Depends]],
            pydantic.Field(default=None, description="The dependencies for the route"),
        ]
        name: typing.Annotated[str | None, pydantic.Field(description="The name of the route")] = None

    prefix: typing.Annotated[str, pydantic.Field(description="The prefix for the router")]
    routes: typing.Annotated[list[Route], pydantic.Field(description="The list of routes for the router")]
    tags: typing.Annotated[list[str], pydantic.Field(description="The tags for the router")]


class Router:
    @staticmethod
    def _replace_type_hint(
        original_func: collections.abc.Callable[..., typing.Any], type_name: str, new_type: type
    ) -> collections.abc.Callable[..., typing.Any]:
        if original_func.__annotations__ and type_name in original_func.__annotations__:
            original_func.__annotations__[type_name] = new_type
        return original_func

    @staticmethod
    def _wrapper_endpoint(
        original_func: collections.abc.Callable[..., typing.Any],
        before_func: collections.abc.Callable[..., typing.Any] = lambda *args, **kwargs: None,
        after_func: collections.abc.Callable[..., typing.Any] = lambda *args, **kwargs: None,
    ) -> collections.abc.Callable[..., typing.Any]:
        @functools.wraps(original_func)
        async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            before_func(*args, **kwargs)
            result = await original_func(*args, **kwargs)
            after_func(*args, **kwargs)
            return result

        return wrapper  # type: ignore

    def __init__(self, crud: CRUD, resource_name: str, models: sthali_db.Models) -> None:
        self.crud = crud
        self.resource_name = resource_name
        self.models = models

    @property
    def create_endpoint(self) -> collections.abc.Callable[..., typing.Any]:
        return self._wrapper_endpoint(self._replace_type_hint(self.crud.create, "resource", self.models.create_model))

    @property
    def read_endpoint(self) -> collections.abc.Callable[..., typing.Any]:
        return self._wrapper_endpoint(self.crud.read)

    @property
    def update_endpoint(self) -> collections.abc.Callable[..., typing.Any]:
        return self._wrapper_endpoint(self._replace_type_hint(self.crud.update, "resource", self.models.update_model))

    @property
    def delete_endpoint(self) -> collections.abc.Callable[..., typing.Any]:
        return self._wrapper_endpoint(self.crud.delete)

    @property
    def read_many_endpoint(self) -> collections.abc.Callable[..., typing.Any]:
        return self._wrapper_endpoint(self.crud.read_many)

    @property
    def routes(self) -> list[RouterSpecification.Route]:
        return [
            RouterSpecification.Route(
                path="/",
                endpoint=self.create_endpoint,
                response_model=self.models.response_model,
                methods=["POST"],
                status_code=201,
            ),  # type: ignore
            RouterSpecification.Route(
                path="/{resource_id}/",
                endpoint=self.read_endpoint,
                response_model=self.models.response_model,
                methods=["GET"],
            ),  # type: ignore
            RouterSpecification.Route(
                path="/{resource_id}/",
                endpoint=self.update_endpoint,
                response_model=self.models.response_model,
                methods=["PUT"],
            ),  # type: ignore
            RouterSpecification.Route(
                path="/{resource_id}/",
                endpoint=self.update_endpoint,
                response_model=self.models.response_model,
                methods=["PATCH"],
                name="Update partial",
            ),  # type: ignore
            RouterSpecification.Route(
                path="/{resource_id}/",
                endpoint=self.delete_endpoint,
                response_model=None,
                methods=["DELETE"],
                status_code=204,
            ),  # type: ignore
            RouterSpecification.Route(
                path="/",
                endpoint=self.read_many_endpoint,
                response_model=list[self.models.response_model],
                methods=["GET"],
            ),  # type: ignore
        ]

    @property
    def api_router(self) -> fastapi.APIRouter:
        router = fastapi.APIRouter(prefix=f"/{self.resource_name}", tags=[self.resource_name])
        for route in self.routes:
            router.add_api_route(
                path=route.path,
                endpoint=route.endpoint,
                response_model=route.response_model,
                methods=route.methods,  # type: ignore
                status_code=route.status_code,
                dependencies=route.dependencies,  # type: ignore
            )
        return router
