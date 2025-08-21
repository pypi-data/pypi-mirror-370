"""This module provides ..."""

import collections.abc
import typing

import pydantic

# import sthali_auth
import sthali_crud

from .config import Config

__all__ = [
    "AppSpecification",
    "Config",
    "SthaliBackend",
    "default_lifespan",
]


default_lifespan = sthali_crud.default_lifespan


@pydantic.dataclasses.dataclass
class AppSpecification(sthali_crud.AppSpecification):
    """Represents the specification of a SthaliBackend application."""

    # auth: typing.Annotated[
    #     sthali_auth.AuthSpecification,
    #     pydantic.Field(default=None, description="The dependencies for the application"),
    # ]

    def __post_init__(self):
        self.title = "SthaliBackend"
        self.description = "A FastAPI package for implement services."


class SthaliBackend(sthali_crud.SthaliCRUD):
    """A class to initialize and configure a FastAPI application with {...}.

    Args:
        app_spec (AppSpecification): The specification of the application, including title, description, summary,
            version, dependencies, and resources.
        lifespan (collections.abc.Callable[..., typing.Any]): The lifespan of the application.
            Defaults to default_lifespan.
    """

    def __init__(
        self, app_spec: AppSpecification, lifespan: collections.abc.Callable[..., typing.Any] = default_lifespan
    ) -> None:
        """Initializes the SthaliBackend instance.

        Args:
            app_spec (AppSpecification): The specification of the application, including title, description, summary,
                version, dependencies, and resources.
            lifespan (collections.abc.Callable[..., typing.Any]): The lifespan of the application.
                Defaults to default_lifespan.
        """
        # if app_spec.auth:
        #     auth = sthali_auth.Auth(app_spec.auth)
        #     breakpoint()
        #     # auth_dependency = auth.dependency
        #     # app_spec.add_dependency(auth_dependency)

        super().__init__(app_spec, lifespan)
