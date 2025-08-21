import logging
import types
from typing import Annotated, Any, AsyncIterator, Callable, Dict, List, Optional, Type

from fastcrawl.core.components import func_wrapper, validation


class Depends:
    """Represents a dependency on a callable.

    Args:
        func (Callable): The callable that this dependency represents.

    """

    func: Callable

    def __init__(self, func: Callable) -> None:
        if not callable(func):
            raise TypeError(f"Expected callable, got {type(func).__name__}")
        self.func = func


class Dependency:
    """Dependency component that encapsulates a callable and its dependencies.

    Args:
        name (str): The name of the dependency.
        func (Callable): The callable that this dependency encapsulates.
        spec (validation.FuncSpec): The function specification.
        dependencies (Optional[List["Dependency"]]): The list of dependencies for this dependency.
        kwargs (Optional[Dict[str, Any]]): Additional keyword arguments for the dependency.

    """

    name: str

    _func_wrapper: func_wrapper.FuncWrapper
    _dependencies: List["Dependency"]
    _kwargs: Dict[str, Any]

    def __init__(
        self,
        name: str,
        func: Callable,
        spec: validation.FuncSpec,
        dependencies: Optional[List["Dependency"]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self._func_wrapper = func_wrapper.FuncWrapper(func, spec)
        self._dependencies = dependencies or []
        self._kwargs = kwargs or {}

    async def execute(self) -> AsyncIterator[Any]:
        """Executes the dependency.

        Yields:
            Any: The result of the dependency execution.

        """
        async with DependencyProvider(self._dependencies) as kwargs:
            kwargs.update(self._kwargs)
            return self._func_wrapper.execute(kwargs)


class DependencyProvider:
    """Provider for dependency execution.

    Args:
        dependencies (List[Dependency]): The list of dependencies to execute.

    """

    _dependencies: List[Dependency]
    _iterators: List[AsyncIterator[Any]]

    def __init__(self, dependencies: List[Dependency]) -> None:
        self._dependencies = dependencies
        self._iterators = []

    async def __aenter__(self) -> Dict[str, Any]:
        """Enters the dependency provider context.

        Returns:
            Dict[str, Any]: Executed dependencies values.

        """
        result = {}
        for dependency in self._dependencies:
            iterator = await dependency.execute()
            async for value in iterator:
                result[dependency.name] = value
                break
            self._iterators.append(iterator)
        return result

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> None:
        """Exits the dependency provider context and cleans up iterators."""
        for iterator in self._iterators:
            async for _ in iterator:
                pass


class DependencyResolver:
    """Resolver for dependencies.

    Args:
        parent_func_validator (validation.FuncValidator): Validator of the function for which
            dependencies need to be resolved.

    """

    _parent_func_validator: validation.FuncValidator

    def __init__(self, parent_func_validator: validation.FuncValidator) -> None:
        self._parent_func_validator = parent_func_validator

    def resolve(self) -> List[Dependency]:
        """Returns resolved dependencies."""
        return self._resolve(self._parent_func_validator)

    def _resolve(self, parent_func_validator: validation.FuncValidator) -> List[Dependency]:
        dependencies = []

        for param in parent_func_validator.validate_annotated_params():
            for annotation in param.annotations:
                if not isinstance(annotation, Depends):
                    continue
                dependency = self._resolve_builtin_dependency(param, annotation, parent_func_validator.func_name)
                if not dependency:
                    validator = validation.FuncValidator(annotation.func)
                    spec = validator.validate_spec(param.base_types, can_be_iter=True)
                    dependency = Dependency(
                        name=param.name,
                        func=annotation.func,
                        spec=spec,
                        dependencies=self._resolve(validator),
                    )
                dependencies.append(dependency)

        return dependencies

    def _resolve_builtin_dependency(
        self,
        param: validation.FuncAnnotatedParam,
        dep: Depends,
        parent_func_name: str,
    ) -> Optional[Dependency]:
        if param.raw is LoggerDependency:
            return Dependency(
                name=param.name,
                func=dep.func,
                spec=validation.FuncSpec(is_async=False, is_iter=False),
                kwargs={"name": parent_func_name},
            )
        return None


LoggerDependency = Annotated[logging.Logger, Depends(logging.getLogger)]
