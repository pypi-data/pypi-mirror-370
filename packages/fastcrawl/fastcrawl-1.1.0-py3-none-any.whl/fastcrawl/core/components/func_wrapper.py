from typing import Any, AsyncIterator, Callable, Dict

import typeguard

from fastcrawl.core.components import validation


class FuncWrapper:
    """Wrapper for function execution.

    Args:
        func (Callable): The function to wrap.
        spec (validation.FuncSpec): The function specification.

    """

    _func: Callable
    _spec: validation.FuncSpec

    def __init__(self, func: Callable, spec: validation.FuncSpec) -> None:
        self._func = typeguard.typechecked(func)
        self._spec = spec

    async def execute(self, kwargs: Dict[str, Any]) -> AsyncIterator[Any]:
        """Executes the wrapped function.

        Args:
            kwargs (Dict[str, Any]): The keyword arguments to pass to the wrapped function.

        Yields:
            Any: The result of the wrapped function execution.

        """
        result = self._func(**kwargs)
        if self._spec.is_async and self._spec.is_iter:
            async for value in result:
                yield value
        elif self._spec.is_async:
            yield await result
        elif self._spec.is_iter:
            for value in result:
                yield value
        else:
            yield result
