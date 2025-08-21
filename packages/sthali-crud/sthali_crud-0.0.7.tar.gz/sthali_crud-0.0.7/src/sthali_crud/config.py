"""{...}."""

import json
import pathlib
import typing

import sthali_db
import yaml


class Types:
    any = typing.Any
    none = None
    bool = bool
    true = True
    false = False
    str = str
    int = int
    float = float
    list = list
    dict = dict


class ConfigException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Config:
    """{...}.

    Atributes:
        types (Types): The types attribute.
        spec_file_path(pathlib.Path): The spec file path.
    """

    types = sthali_db.Types()

    def __init__(self, spec_file_path: str) -> None:
        self.spec_file_path = pathlib.Path(spec_file_path)

    def _get_type(self, name: str) -> typing.Any:
        """Get the type based on the given type string.

        Args:
            name (str): The type string.

        Returns:
            typing.Any: The corresponding type.

        Raises:
            ConfigException: If the type string is invalid.
        """
        name = name.strip().lower()
        try:
            return self.types.get(name)
        except AttributeError as exception:
            raise ConfigException("Invalid type") from exception

    @property
    def app_specification_file_content(self) -> dict[str, typing.Any]:
        match self.spec_file_path.suffix:
            case ".json":
                fn = json.load
            case ".yaml" | ".yml":
                fn = yaml.safe_load
            case _:
                raise ConfigException("Invalid file extension")

        with self.spec_file_path.open() as spec_file:
            return fn(spec_file)

    @property
    def app_specification(self) -> dict[str, typing.Any]:
        _app_specification = self.app_specification_file_content
        for resource in _app_specification["resources"]:
            for field in resource["fields"]:
                if isinstance(field["type"], str):
                    field["type"] = self._get_type(field["type"])
                elif isinstance(field["type"], list):
                    types_list = tuple(self._get_type(t) for t in field["type"])
                    field["type"] = typing.Union[types_list]
                else:
                    raise ConfigException("Invalid field type")
                if "has_default" in field:
                    field["has_default"] = self._get_type(field["has_default"])
        return _app_specification
