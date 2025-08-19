from rbt.std.collections.queue.v1.queue_rbt import (
    DequeueRequest,
    DequeueResponse,
    EnqueueRequest,
    EnqueueResponse,
    Item,
    Queue,
)
from rebootdev.aio.auth.authorizers import allow
from rebootdev.aio.contexts import WorkflowContext, WriterContext
from rebootdev.aio.workflows import until
from typing import Optional


class QueueServicer(Queue.Servicer):

    def authorizer(self):
        return allow()

    async def Enqueue(
        self,
        context: WriterContext,
        request: EnqueueRequest,
    ) -> EnqueueResponse:
        if sum(
            [
                request.HasField("value"),
                request.HasField("bytes"),
                request.HasField("any"),
                len(request.items) > 0,
            ]
        ) != 1:
            raise TypeError(
                "Only one of `value`, `bytes`, `any`, or `items` should be set"
            )

        items = request.items if len(request.items) > 0 else [
            Item(
                value=request.value if request.HasField("value") else None,
                bytes=request.bytes if request.HasField("bytes") else None,
                any=request.any if request.HasField("any") else None,
            ),
        ]

        self.state.items.extend(items)

        return EnqueueResponse()

    async def Dequeue(
        self,
        context: WorkflowContext,
        request: DequeueRequest,
    ) -> DequeueResponse:
        bulk = request.bulk
        at_most: Optional[int] = None
        if request.bulk and request.HasField("at_most"):
            at_most = request.at_most

        async def have_items():

            async def slice_items(state):
                if len(state.items) > 0:
                    count = 1 if not bulk else (at_most or len(state.items))
                    items = state.items[:count]
                    del state.items[:count]
                    return items
                return False

            return await self.ref().Write(context, slice_items, type=list)

        items = await until("Have items", context, have_items, type=list)

        if not bulk:
            assert (len(items) == 1)
            item = items[0]
            return DequeueResponse(
                value=item.value if item.HasField("value") else None,
                bytes=item.bytes if item.HasField("bytes") else None,
                any=item.any if item.HasField("any") else None,
            )
        else:
            return DequeueResponse(items=items)
