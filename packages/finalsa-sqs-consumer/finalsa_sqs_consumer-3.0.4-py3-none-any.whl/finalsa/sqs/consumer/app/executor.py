from typing import List, Callable, Dict
from finalsa.common.models import Meta


class Executor():

    def __init__(self, __interceptors__: List[Callable]):
        self.__interceptors__ = __interceptors__

    async def call(self, message: Dict, meta: Meta):
        if len(self.__interceptors__) == 0:
            return
        await self.call_interceptor(self.__interceptors__.pop(0), message, meta)

    async def call_interceptor(self, interceptor: Callable, message: Dict, meta: Meta):
        def caller():
            async def next_fn(message, meta):
                await self.call(message, meta)
            return next_fn
        await interceptor(message, meta, caller())
