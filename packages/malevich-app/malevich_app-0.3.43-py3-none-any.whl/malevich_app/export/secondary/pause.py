import asyncio
from typing import Optional, Generic, Dict, Type, TypeVar
from pydantic import BaseModel
import malevich_app.export.secondary.const as C

T = TypeVar('T', bound=BaseModel)


class PauseModel(Generic[T]):
    def __init__(self, pauses: Dict[str, asyncio.Future], model: Optional[Type[T]] = None):
        self.__pauses = pauses
        self.__model: Optional[Type[T]] = model

    async def __call__(self, id: str = C.DEFAULT_CONTINUE_ID) -> T:
        fut = asyncio.Future()
        assert id not in self.__pauses, f"already set pause by id={id}"
        self.__pauses[id] = fut
        data = await fut

        if self.__model is not None and issubclass(self.__model, BaseModel):
            return self.__model.model_validate_json(data)
        return data


class Pause:
    def __init__(self, pauses: Dict[str, asyncio.Future]):
        self.__pauses = pauses

    def __getitem__(self, model: Type[T]) -> PauseModel[T]:
        return PauseModel(self.__pauses, model)

    async def __call__(self, id: str = C.DEFAULT_CONTINUE_ID) -> T:
        return await PauseModel(self.__pauses).__call__(id)
