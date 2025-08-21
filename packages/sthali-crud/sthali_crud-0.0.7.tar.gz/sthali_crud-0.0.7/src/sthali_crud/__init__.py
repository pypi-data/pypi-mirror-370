"""{...}."""

import collections.abc
import contextlib
import logging
import typing

import fastapi
import pydantic
import sthali_db

from .config import Config
from .crud import CRUD
from .router import Router

__all__ = [
    "AppSpecification",
    "Config",
    "SthaliCRUD",
    "default_lifespan",
]


@pydantic.dataclasses.dataclass
class ResourceSpecification:
    """Represents the specification of the resource.

    Attributes:
        db (sthali_db.DBSpecification): The database specification for the resource.
        name (str): The name of the resource.
        fields (list[sthali_db.FieldSpecification]): The list of field definitions for the resource.
    """

    db: typing.Annotated[
        sthali_db.DBSpecification,
        pydantic.Field(description="The database specification for the resource"),
    ]
    name: typing.Annotated[str, pydantic.Field(description="The name of the resource")]
    fields: typing.Annotated[
        list[sthali_db.FieldSpecification],
        pydantic.Field(description="The list of field definitions for the resource"),
    ]


@pydantic.dataclasses.dataclass
class AppSpecification:
    """Represents the specification of a SthaliCRUD application.

    Attributes:
        resources (List[ResourceSpecification]): The list of resource specifications.
        dependencies (list[typing.Any]): The dependencies of the application. Default is None.
        description (str): The description of the application. Default value is "A FastAPI package for CRUD
            operations".
        summary (str | None): The summary of the application. Default value is None.
        title (str): The title of the application. Default value is "SthaliCRUD".
        version (str): The version of the application. Default value is "0.1.0".
    """

    resources: typing.Annotated[
        list[ResourceSpecification],
        pydantic.Field(default=None, description="The list of resource specifications"),
    ]
    dependencies: typing.Annotated[
        list[typing.Any],
        pydantic.Field(default=None, description="The dependencies of the application"),
    ]
    description: typing.Annotated[
        str,
        pydantic.Field(
            default="A FastAPI package for CRUD operations", description="The description of the application",
        ),
    ]
    summary: typing.Annotated[str | None, pydantic.Field(default=None, description="The summary of the application")]
    title: typing.Annotated[str, pydantic.Field(default="SthaliCRUD", description="The title of the application")]
    version: typing.Annotated[str, pydantic.Field(default="0.1.0", description="The version of the application")]

    def add_dependency(self, dependency: typing.Any) -> None:
        """Adds a dependency to the application.

        Args:
            dependency (typing.Any): The dependency to add to the application.
        """
        dependencies = self.dependencies or []
        dependencies.append(dependency)
        self.dependencies = dependencies


@contextlib.asynccontextmanager
async def default_lifespan(app: fastapi.FastAPI) -> typing.AsyncGenerator[None, None]:
    """A context manager that handles the startup and shutdown of Sthali application.

    Args:
        app (fastapi.FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    logging.info("Startup", extra={"app": app.title})
    yield
    logging.info("Shutdown", extra={"app": app.title})


class SthaliCRUD:
    """A class to initialize and configure a FastAPI application with CRUD operations for specified resources.

    Attributes:
        app (fastapi.FastAPI): The FastAPI application instance.

    Args:
        app_spec (AppSpecification): The specification of the application, including title, description, summary,
            version, dependencies, and resources.
        lifespan (collections.abc.Callable[..., typing.Any]): The lifespan of the application.
            Defaults to default_lifespan.
    """

    def __init__(
        self, app_spec: AppSpecification, lifespan: collections.abc.Callable[..., typing.Any] = default_lifespan,
    ) -> None:
        """Initializes the SthaliCRUD instance.

        Args:
            app_spec (AppSpecification): The specification of the application, including title, description, summary,
                version, dependencies, and resources.
            lifespan (collections.abc.Callable[..., typing.Any]): The lifespan of the application.
                Defaults to default_lifespan.
        """
        app = fastapi.FastAPI(
            title=app_spec.title,
            description=app_spec.description,
            summary=app_spec.summary,
            version=app_spec.version,
            dependencies=app_spec.dependencies,
            lifespan=lifespan,
        )
        self.app = app

        _db: dict[str, sthali_db.DB] = {}
        for resource in app_spec.resources:
            models = sthali_db.Models(resource.name, resource.fields)
            db = sthali_db.DB(resource.db, resource.name)
            crud = CRUD(db, models)
            router = Router(crud, resource.name, models)
            self.app.include_router(router.api_router)
            _db[resource.name] = db
        self.app.extra["db"] = _db
