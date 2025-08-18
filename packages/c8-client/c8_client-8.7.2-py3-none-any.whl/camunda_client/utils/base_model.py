from typing import Any, Literal, Callable

from pydantic import BaseModel, ConfigDict
from pydantic.main import IncEx


class JsonBaseModel(BaseModel):
    """
    Extends pydantic.BaseModel

    Is used as the base model for all JSON models to communicate with external APIs.
    Validates fields by their alias (python snake case) and their name (JSON property camel case).
    Always uses the alias to generate JSON objects and excludes 'None' values.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_alias=True,
        validate_by_name=True
    )

    def model_dump_json(
            self,
            *,
            indent: int | None = None,
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            context: Any | None = None,
            by_alias: bool | None = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal['none', 'warn', 'error'] = True,
            fallback: Callable[[Any], Any] | None = None,
            serialize_as_any: bool = False,
    ) -> str:
        return super().model_dump_json(exclude_none=True,
                                       by_alias=True,
                                       indent=indent,
                                       include=include,
                                       exclude=exclude,
                                       context=context,
                                       exclude_unset=exclude_unset,
                                       exclude_defaults=exclude_defaults,
                                       round_trip=round_trip,
                                       warnings=warnings,
                                       fallback=fallback,
                                       serialize_as_any=serialize_as_any)

    def model_dump(
            self,
            *,
            mode: Literal['json', 'python'] | str = 'python',
            include: IncEx | None = None,
            exclude: IncEx | None = None,
            context: Any | None = None,
            by_alias: bool | None = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal['none', 'warn', 'error'] = True,
            fallback: Callable[[Any], Any] | None = None,
            serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=True,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any
        )
