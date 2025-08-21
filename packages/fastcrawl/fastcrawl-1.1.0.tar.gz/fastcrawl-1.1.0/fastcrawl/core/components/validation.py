import dataclasses
import inspect
import sys
import types
from typing import (
    Annotated,
    Any,
    AsyncIterable,
    Callable,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)


@dataclasses.dataclass(frozen=True)
class FuncSpec:
    """Function specification.

    Attributes:
        is_async (bool): Whether the function is asynchronous.
        is_iter (bool): Whether the function returns an iterable.

    """

    is_async: bool
    is_iter: bool


@dataclasses.dataclass(frozen=True)
class FuncParam:
    """Function parameter.

    Attributes:
        name (str): The name of the parameter.
        type_ (Type): The type of the parameter.

    """

    name: str
    type_: Type


@dataclasses.dataclass(frozen=True)
class FuncAnnotatedParam:
    """Function annotated parameter.

    Attributes:
        name (str): The name of the parameter.
        base_types (Tuple[Type, ...]): The base types of the parameter.
        annotations (List[Any]): The annotations of the parameter.
        raw (Any): Raw annotation of the parameter.

    """

    name: str
    base_types: Tuple[Type, ...]
    annotations: List[Any]
    raw: Any


class FuncValidator:
    """Function validator.

    Args:
        func (Callable): The function to validate.

    """

    _func: Callable
    _signature: inspect.Signature

    def __init__(self, func: Callable) -> None:
        self._func = func
        self._signature = inspect.signature(func)

    @property
    def func_name(self) -> str:
        """Name of the function."""
        return self._func.__name__

    def validate_param(self, param_type: Type) -> FuncParam:
        """Validates the function parameters.

        Args:
            param_type (Type): The expected type of the parameter.

        Raises:
            TypeError: If the function has no parameters matching the expected type.
            TypeError: If the function has multiple parameters matching the expected type.

        Returns:
            FuncParam: The validated function parameter.

        """
        params = [
            FuncParam(name=param.name, type_=param.annotation)
            for param in self._signature.parameters.values()
            if self._is_valid_type(param.annotation, param_type)
        ]
        if not params:
            raise TypeError(f"Function `{self.func_name}` has no parameters matching the expected type {param_type}.")
        if len(params) > 1:
            raise TypeError(
                f"Function `{self.func_name}` has multiple parameters matching the expected type {param_type}. "
                f"Expected only one parameter of this type."
            )
        return params[0]

    def validate_spec(self, return_types: Tuple[Type, ...], can_be_iter: bool) -> FuncSpec:
        """Validates the function return type and specification.

        Args:
            return_types (Tuple[Type, ...]): The expected return types.
            can_be_iter (bool): Whether the return type can be an iterable.

        Raises:
            TypeError: If the function return type does not match the expected types.

        Returns:
            FuncSpec: The validated function specification.

        """
        actual_type = self._signature.return_annotation
        if actual_type is inspect.Signature.empty or actual_type is None:
            actual_type = type(None)

        is_iter = self._validate_return_type(actual_type, return_types, can_be_iter)
        if is_iter is None:
            raise TypeError(
                f"Function `{self.func_name}` has an invalid return type. "
                f"Expected one of {return_types}, or union of them{' or iterable of them' if can_be_iter else ''}."
            )
        is_async = inspect.iscoroutinefunction(self._func) or inspect.isasyncgenfunction(self._func)
        return FuncSpec(is_async=is_async, is_iter=is_iter)

    def validate_annotated_params(self) -> List[FuncAnnotatedParam]:
        """Validates the function annotated parameters.

        Raises:
            TypeError: If the function has an invalid annotation for any parameter.

        Returns:
            List[FuncAnnotatedParam]: The validated function annotated parameters.

        """
        annotated_params = []
        for param in self._signature.parameters.values():
            origin = get_origin(param.annotation)
            if origin is Annotated:
                base_annotation, *annotations = get_args(param.annotation)
                base_types = self._get_types_from_annotation(base_annotation, param.name)
                if base_types is None:
                    raise TypeError(
                        f"Function `{self.func_name}` has an invalid annotation for parameter `{param.name}`. "
                        f"Expected base types to be a class or a union of classes."
                    )
                annotated_param = FuncAnnotatedParam(
                    name=param.name,
                    base_types=base_types,
                    annotations=annotations,
                    raw=param.annotation,
                )
                annotated_params.append(annotated_param)
        return annotated_params

    def _validate_return_type(
        self, actual_type: Any, expected_types: Tuple[Type, ...], can_be_iter: bool
    ) -> Optional[bool]:
        if self._is_valid_type(actual_type, expected_types):
            return False

        origin = get_origin(actual_type)
        args = get_args(actual_type)

        if self._is_union_type(origin):
            for arg in args:
                if not self._is_valid_type(arg, expected_types):
                    return None
            return False

        if (
            can_be_iter
            and origin is not None
            and (issubclass(origin, Iterable) or issubclass(origin, AsyncIterable))
            and len(args) == 1
        ):
            validated_arg_type = self._validate_return_type(args[0], expected_types, can_be_iter=False)
            if validated_arg_type is not None:
                return True

        return None

    def _is_valid_type(self, actual: Any, expected: Union[Type, Tuple[Type, ...]]) -> bool:
        return inspect.isclass(actual) and issubclass(actual, expected)

    def _is_union_type(self, type_: Any) -> bool:
        if type_ is Union:
            return True
        if sys.version_info >= (3, 10):
            return isinstance(type_, types.UnionType)
        return False

    def _get_types_from_annotation(self, annotation: Any, param_name: str) -> Optional[Tuple[Type, ...]]:
        if inspect.isclass(annotation):
            return (annotation,)
        if self._is_union_type(annotation):
            args = get_args(annotation)
            if all(inspect.isclass(arg) for arg in args):
                return tuple(args)
        return None
