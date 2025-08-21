from typing import AsyncIterator, Callable, List, Optional, Union

import pydantic

from fastcrawl import models
from fastcrawl.core.components import dependencies, func_wrapper, validation

HandlerReturnType = AsyncIterator[Optional[Union[models.Request, pydantic.BaseModel]]]


class Handler:
    """Handler component for processing responses.

    Args:
        func (Callable): The function to wrap.

    """

    _func_wrapper: func_wrapper.FuncWrapper
    _response_param: validation.FuncParam
    _dependencies: List[dependencies.Dependency]

    def __init__(self, func: Callable) -> None:
        validator = validation.FuncValidator(func)
        spec = validator.validate_spec(
            return_types=(models.Request, pydantic.BaseModel, type(None)),
            can_be_iter=True,
        )
        self._func_wrapper = func_wrapper.FuncWrapper(func, spec)
        self._response_param = validator.validate_param(param_type=models.Response)
        self._dependencies = dependencies.DependencyResolver(validator).resolve()

    async def execute(self, response: models.Response) -> HandlerReturnType:
        """Executes the handler with the given response.

        Args:
            response (models.Response): The response to process.

        Yields:
            Optional[Union[models.Request, pydantic.BaseModel]]: The result of the handler execution.

        """
        async with dependencies.DependencyProvider(self._dependencies) as kwargs:
            kwargs[self._response_param.name] = response
            async for value in self._func_wrapper.execute(kwargs):
                yield value
