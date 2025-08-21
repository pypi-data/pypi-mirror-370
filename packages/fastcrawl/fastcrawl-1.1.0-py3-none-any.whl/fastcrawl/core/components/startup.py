from typing import AsyncIterator, Callable, List, Optional

from fastcrawl import models
from fastcrawl.core.components import dependencies, func_wrapper, validation


class Startup:
    """Startup component for the crawler.

    Args:
        func (Callable): The function to wrap.

    """

    _func_wrapper: func_wrapper.FuncWrapper
    _dependencies: List[dependencies.Dependency]

    def __init__(self, func: Callable) -> None:
        validator = validation.FuncValidator(func)
        spec = validator.validate_spec(
            return_types=(models.Request, type(None)),
            can_be_iter=True,
        )
        self._func_wrapper = func_wrapper.FuncWrapper(func, spec)
        self._dependencies = dependencies.DependencyResolver(validator).resolve()

    async def execute(self) -> AsyncIterator[Optional[models.Request]]:
        """Executes the startup function."""
        async with dependencies.DependencyProvider(self._dependencies) as kwargs:
            async for value in self._func_wrapper.execute(kwargs):
                yield value
