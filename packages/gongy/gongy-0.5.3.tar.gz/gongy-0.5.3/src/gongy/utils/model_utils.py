# ruff: noqa: ANN401
"""Model utils."""

from __future__ import annotations

__all__: tuple[str, ...] = ("AllTrueModel",)

from types import UnionType
from typing import Any, Self, Union, cast, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined


def _is_optional(tp: Any) -> bool:
    origin = get_origin(tp)
    return origin in (UnionType, Union)


def _unwrap_optional(tp: Any) -> Any:
    if not _is_optional(tp):
        return tp
    args = get_args(tp)
    return next((a for a in args if a is not type(None)), None)


def _is_bool_or_optional_bool(tp: Any) -> bool:
    if tp is bool:
        return True
    return _unwrap_optional(tp) is bool if _is_optional(tp) else False


def _is_subclass_of_all_true_model(tp: Any) -> bool:
    try:
        return isinstance(tp, type) and issubclass(tp, AllTrueModel)
    except TypeError:
        return False


def _list_inner_all_true_model(tp: Any) -> Any:
    if get_origin(tp) is list:
        (inner,) = get_args(tp)
        inner = _unwrap_optional(inner) if _is_optional(inner) else inner
        if _is_subclass_of_all_true_model(inner):
            return inner
    return None


def _dict_val_inner_all_true_model(tp: Any) -> Any:
    if get_origin(tp) is dict:
        key_type, val_type = get_args(tp)
        if key_type is not str:
            return None
        val_type = _unwrap_optional(val_type) if _is_optional(val_type) else val_type
        if _is_subclass_of_all_true_model(val_type):
            return val_type
    return None


class AllTrueModel(BaseModel):
    """Base model that defaults all boolean fields to True."""

    @classmethod
    def all(cls: type[Self]) -> Self:
        """Create an instance of the model with all boolean fields set to True."""
        kwargs: dict[str, Any] = {}

        for name, field in cls.model_fields.items():
            ann = field.annotation
            inner_ann = _unwrap_optional(ann) if _is_optional(ann) else ann

            # 1) bool or Optional[bool]
            if _is_bool_or_optional_bool(ann):
                kwargs[name] = True
                continue

            # 2) Nested AllTrueModel (including Optional[Nested])
            if _is_subclass_of_all_true_model(inner_ann):
                inner_ann = cast("type[AllTrueModel]", inner_ann)
                kwargs[name] = inner_ann.all()
                continue

            # 3) list[...] of AllTrueModel (including Optional[list[...] ])
            if list_inner := _list_inner_all_true_model(inner_ann):
                kwargs[name] = [list_inner.all()]
                continue

            # 4) dict[str, ...] of AllTrueModel (including Optional[dict[...] ])
            if dict_val_inner := _dict_val_inner_all_true_model(inner_ann):
                kwargs[name] = {"example": dict_val_inner.all()}
                continue

            # 5) Fallback: default / factory / None if optional
            if field.default is not PydanticUndefined:
                kwargs[name] = field.default
            elif field.default_factory is not None:
                kwargs[name] = field.default_factory()  # type: ignore[call-arg]
            elif _is_optional(ann):
                kwargs[name] = None

        try:
            return cls(**kwargs)  # type: ignore[call-arg]
        except Exception:  # noqa: BLE001
            # If required non-bool/non-nested fields exist without defaults, fall back.
            return cls.model_construct(**kwargs)  # type: ignore[call-arg]
