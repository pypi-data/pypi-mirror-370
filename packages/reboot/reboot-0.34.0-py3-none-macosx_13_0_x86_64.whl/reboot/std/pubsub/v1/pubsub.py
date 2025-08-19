from rbt.std.collections.queue.v1.queue_rbt import Item, Queue
from rbt.std.pubsub.v1.pubsub_rbt import (
    BrokerRequest,
    BrokerResponse,
    PublishRequest,
    PublishResponse,
    PubSub,
    SubscribeRequest,
    SubscribeResponse,
    Topic,
)
from rebootdev.aio.auth.authorizers import allow
from rebootdev.aio.contexts import WorkflowContext, WriterContext
from rebootdev.aio.workflows import until


class PubSubServicer(PubSub.Servicer):

    def authorizer(self):
        return allow()

    async def Publish(
        self,
        context: WriterContext,
        request: PublishRequest,
    ) -> PublishResponse:
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
                any=request.any if request.HasField("any") else None
            )
        ]

        # Add item(s) to topic.
        #
        # If this is a new topic, we'll need to add it and schedule a
        # broker.
        new_topic = True
        for topic in self.state.topics:
            if topic.name == request.topic:
                topic.items.extend(items)
                new_topic = False
                break

        if new_topic:
            self.state.topics.append(Topic(name=request.topic, items=items))
            await self.ref().schedule().Broker(context, topic=request.topic)

        return PublishResponse()

    async def Subscribe(
        self,
        context: WriterContext,
        request: SubscribeRequest,
    ) -> SubscribeResponse:
        # Add subscriber to topic.
        #
        # If this is a new topic, we'll need to add it and schedule a
        # broker.
        new_topic = True
        for topic in self.state.topics:
            if topic.name == request.topic:
                topic.queue_ids.append(request.queue_id)
                new_topic = False
                break

        if new_topic:
            self.state.topics.append(
                Topic(name=request.topic, queue_ids=[request.queue_id]),
            )
            await self.ref().schedule().Broker(context, topic=request.topic)

        return SubscribeResponse()

    async def Broker(
        self,
        context: WorkflowContext,
        request: BrokerRequest,
    ) -> BrokerResponse:

        async for iteration in context.loop("Broker"):

            async def have_items():

                async def slice_items(state):
                    for topic in state.topics:
                        if topic.name == request.topic:
                            if len(topic.items) > 0:
                                items = topic.items[:]
                                del topic.items[:]
                                return list(topic.queue_ids), items
                            break
                    return False

                return await self.ref().Write(context, slice_items, type=tuple)

            queue_ids, items = await until(
                "Have items",
                context,
                have_items,
                type=tuple,
            )

            await Queue.forall(queue_ids).Enqueue(context, items=items)

        return BrokerResponse()
