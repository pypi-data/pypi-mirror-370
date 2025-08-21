from typing import Callable, List, Optional

import pydantic

from fastcrawl.core.components import dependencies, func_wrapper, validation


class Pipeline:
    """Pipeline component for processing items.

    Args:
        func (Callable): The function to wrap.

    """

    _func_wrapper: func_wrapper.FuncWrapper
    _item_param: validation.FuncParam
    _dependencies: List[dependencies.Dependency]

    def __init__(self, func: Callable) -> None:
        validator = validation.FuncValidator(func)
        spec = validator.validate_spec(
            return_types=(pydantic.BaseModel, type(None)),
            can_be_iter=False,
        )
        self._func_wrapper = func_wrapper.FuncWrapper(func, spec)
        self._item_param = validator.validate_param(param_type=pydantic.BaseModel)
        self._dependencies = dependencies.DependencyResolver(validator).resolve()

    def is_compatible_item(self, item: pydantic.BaseModel) -> bool:
        """Returns True if the item is compatible with the pipeline, False otherwise.

        Args:
            item (pydantic.BaseModel): The item to check.

        """
        return isinstance(item, self._item_param.type_)

    async def execute(self, item: pydantic.BaseModel) -> Optional[pydantic.BaseModel]:
        """Executes the pipeline with the given item.

        Args:
            item (pydantic.BaseModel): The item to process.

        Returns:
            Optional[pydantic.BaseModel]: The result of the pipeline execution.

        """
        async with dependencies.DependencyProvider(self._dependencies) as kwargs:
            kwargs[self._item_param.name] = item
            async for value in self._func_wrapper.execute(kwargs):
                return value
        return None
