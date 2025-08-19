from rbt.std.index.v1.index_rbt import (
    Entry,
    Index,
    IndexCreateRequest,
    IndexCreateResponse,
    IndexInsertRequest,
    IndexInsertResponse,
    IndexRangeRequest,
    IndexRangeResponse,
    IndexRemoveRequest,
    IndexRemoveResponse,
    IndexReverseRangeRequest,
    IndexReverseRangeResponse,
    IndexSearchRequest,
    IndexSearchResponse,
    IndexStringifyRequest,
    IndexStringifyResponse,
    InvalidRangeError,
    Node,
    NodeCreateRequest,
    NodeCreateResponse,
    NodeEntry,
    NodeInsertRequest,
    NodeInsertResponse,
    NodeRangeRequest,
    NodeRangeResponse,
    NodeRemoveRequest,
    NodeRemoveResponse,
    NodeReverseRangeRequest,
    NodeReverseRangeResponse,
    NodeSearchRequest,
    NodeSearchResponse,
    NodeStringifyRequest,
    NodeStringifyResponse,
    Value,
)
from rbt.v1alpha1.errors_pb2 import InvalidArgument
from rebootdev.aio.auth.authorizers import allow_if, is_app_internal
from rebootdev.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)


class NodeServicer(Node.singleton.Servicer):

    def authorizer(self):
        return allow_if(all=[is_app_internal])

    async def Create(
        self,
        context: WriterContext,
        state: Node.State,
        request: NodeCreateRequest,
    ) -> NodeCreateResponse:
        state.order = request.order
        state.is_leaf = request.is_leaf
        state.keys.extend(request.keys)
        state.children_ids.extend(request.children_ids)
        state.values.extend(request.values)
        state.next_id = request.next_id
        state.prev_id = request.prev_id
        return NodeCreateResponse()

    async def Search(
        self,
        context: ReaderContext,
        state: Node.State,
        request: NodeSearchRequest,
    ) -> NodeSearchResponse:
        found = False
        value = None
        if state.is_leaf:
            for i, k in enumerate(state.keys):
                if request.key == k:
                    found = True
                    value = state.values[i]
                    break
        else:
            child, _ = self._find_child(state, key=request.key)
            response = await child.Search(context, key=request.key)
            found = response.found
            value = response.value
        return NodeSearchResponse(found=found, value=value)

    async def Insert(
        self,
        context: TransactionContext,
        state: Node.State,
        request: NodeInsertRequest,
    ) -> NodeInsertResponse:
        if state.is_leaf:
            inserted = False
            for i, k in enumerate(state.keys):
                if request.key == k:
                    state.values[i] = request.value
                elif request.key < k:
                    state.keys.insert(i, request.key)
                    state.values.insert(i, request.value)
                else:
                    continue
                inserted = True
                break
            if not inserted:
                state.keys.append(request.key)
                state.values.append(request.value)

            if len(state.keys) < state.order:
                return NodeInsertResponse(split=False)
        else:
            child, index = self._find_child(state, key=request.key)
            response = await child.Insert(
                context,
                key=request.key,
                value=request.value,
            )

            if not response.split:
                return NodeInsertResponse(split=False)

            # Child split, we possibly need to split too.
            promoted_key = response.promoted_key
            new_child_id = response.new_child_id

            state.keys.insert(index, promoted_key)
            state.children_ids.insert(index + 1, new_child_id)

            if len(state.keys) < state.order:
                return NodeInsertResponse(split=False)

        # Split.
        mid = state.order // 2

        new_child, _ = await Node.Create(
            context,
            order=state.order,
            is_leaf=state.is_leaf,
            keys=state.keys[mid:] if state.is_leaf else state.keys[mid + 1:],
            children_ids=[] if state.is_leaf else state.children_ids[mid + 1:],
            values=state.values[mid:] if state.is_leaf else [],
            next_id=state.next_id,
            prev_id=context.state_id if state.is_leaf else "",
        )
        new_child_id = new_child.state_id
        promoted_key = state.keys[mid]
        state.keys[:] = state.keys[:mid]
        state.children_ids[:] = (
            [] if state.is_leaf else state.children_ids[:mid + 1]
        )
        state.values[:] = state.values[:mid] if state.is_leaf else []
        state.next_id = new_child_id if state.is_leaf else ""

        return NodeInsertResponse(
            split=True,
            promoted_key=promoted_key,
            new_child_id=new_child_id,
        )

    async def Remove(
        self,
        context: TransactionContext,
        state: Node.State,
        request: NodeRemoveRequest,
    ) -> NodeRemoveResponse:
        if state.is_leaf:
            for i, k in enumerate(state.keys):
                if request.key == k:
                    state.keys.pop(i)
                    state.values.pop(i)
                    return NodeRemoveResponse()
        else:
            child, _ = self._find_child(state, key=request.key)
            await child.Remove(context, key=request.key)
        return NodeRemoveResponse()

    async def Range(
        self,
        context: ReaderContext,
        state: Node.State,
        request: NodeRangeRequest,
    ) -> NodeRangeResponse:
        if request.limit == 0:
            raise Node.RangeAborted(
                InvalidRangeError(
                    message="Range requires a non-zero `limit` value."
                )
            )

        entries: list[NodeEntry] = []

        if state.is_leaf:
            start_index = 0
            if request.start_key:
                for i, k in enumerate(state.keys):
                    if request.start_key <= k:
                        start_index = i
                        break

            remaining = request.limit
            for i in range(
                start_index, min(len(state.keys), start_index + remaining)
            ):
                entries.append(
                    NodeEntry(key=state.keys[i], value=state.values[i])
                )
                remaining -= 1

            if remaining > 0 and state.next_id:
                next_node = Node.ref(state.next_id)
                response = await next_node.Range(
                    context,
                    start_key=request.start_key,
                    limit=remaining,
                )
                entries.extend(response.entries)
        else:
            if not request.start_key:
                # If no start key is provided, we start from the first
                # child.
                child = Node.ref(state.children_ids[0])
            else:
                child, _ = self._find_child(state, key=request.start_key)
            return await child.Range(
                context,
                start_key=request.start_key,
                limit=request.limit,
            )
        return NodeRangeResponse(entries=entries)

    async def ReverseRange(
        self,
        context: ReaderContext,
        state: Node.State,
        request: NodeReverseRangeRequest,
    ) -> NodeReverseRangeResponse:
        if request.limit == 0:
            raise Node.ReverseRangeAborted(
                InvalidRangeError(
                    message="Reverse range requires a non-zero `limit` value."
                )
            )

        entries: list[NodeEntry] = []

        if state.is_leaf:
            start_index = len(state.keys) - 1
            if request.start_key:
                for i in range(len(state.keys) - 1, -1, -1):
                    k = state.keys[i]
                    if request.start_key >= k:
                        start_index = i
                        break

            remaining = request.limit
            for i in range(start_index, max(-1, start_index - remaining), -1):
                entries.append(
                    NodeEntry(key=state.keys[i], value=state.values[i])
                )
                remaining -= 1

            if remaining > 0 and state.prev_id:
                prev_node = Node.ref(state.prev_id)
                response = await prev_node.ReverseRange(
                    context,
                    start_key=request.start_key,
                    limit=remaining,
                )
                entries.extend(response.entries)
        else:
            if not request.start_key:
                # If no start key is provided, we start from the last
                # child.
                child = Node.ref(state.children_ids[-1])
            else:
                child, _ = self._find_child(state, key=request.start_key)
            return await child.ReverseRange(
                context,
                start_key=request.start_key,
                limit=request.limit,
            )
        return NodeReverseRangeResponse(entries=entries)

    def _find_child(
        self,
        state,
        *,
        key: int,
    ) -> tuple[Node.WeakReference, int]:
        assert not state.is_leaf
        for i, k in enumerate(state.keys):
            if key < k:
                return Node.ref(state.children_ids[i]), i
        return Node.ref(state.children_ids[len(state.keys)]), len(state.keys)

    async def Stringify(
        self,
        context: ReaderContext,
        state: Node.State,
        request: NodeStringifyRequest,
    ) -> NodeStringifyResponse:
        if state.is_leaf:
            value = "  " * request.level + f"Leaf: {state.keys}\n"
        else:
            value = "  " * request.level + f"Inner: {state.keys}\n"
            for child_id in state.children_ids:
                child = Node.ref(child_id)
                response = await child.Stringify(
                    context,
                    level=request.level + 1,
                )
                value += response.value
        return NodeStringifyResponse(value=value)


class IndexServicer(Index.singleton.Servicer):

    def authorizer(self):
        return allow_if(all=[is_app_internal])

    async def Create(
        self,
        context: TransactionContext,
        state: Index.State,
        request: IndexCreateRequest,
    ) -> IndexCreateResponse:
        state.order = request.order
        root, _ = await Node.Create(
            context,
            order=request.order,
            is_leaf=True,
            keys=[],
        )
        state.root_id = root.state_id
        return IndexCreateResponse()

    async def Search(
        self,
        context: ReaderContext,
        state: Index.State,
        request: IndexSearchRequest,
    ) -> IndexSearchResponse:
        root = Node.ref(state.root_id)
        response = await root.Search(context, key=request.key)
        if response.found:
            assert response.HasField("value")
            value = Value()
            value.ParseFromString(response.value)
            if value.HasField("value"):
                return IndexSearchResponse(
                    found=response.found,
                    value=value.value,
                )
            elif value.HasField("bytes"):
                return IndexSearchResponse(
                    found=response.found,
                    bytes=value.bytes,
                )
            else:
                assert value.HasField("any")
                return IndexSearchResponse(
                    found=response.found,
                    any=value.any,
                )

        return IndexSearchResponse(found=False)

    async def Insert(
        self,
        context: TransactionContext,
        state: Index.State,
        request: IndexInsertRequest,
    ) -> IndexInsertResponse:
        value = Value()
        if request.HasField("value"):
            value.value.CopyFrom(request.value)
        elif request.HasField("bytes"):
            value.bytes = request.bytes
        elif request.HasField("any"):
            value.any.CopyFrom(request.any)
        else:
            raise Index.InsertAborted(InvalidArgument())

        root = Node.ref(state.root_id)

        response = await root.Insert(
            context,
            key=request.key,
            value=value.SerializeToString(),
        )

        if response.split:
            promoted_key = response.promoted_key
            new_child_id = response.new_child_id
            new_root, _ = await Node.Create(
                context,
                order=state.order,
                is_leaf=False,
                keys=[promoted_key],
                children_ids=[root.state_id, new_child_id],
            )
            state.root_id = new_root.state_id

        return IndexInsertResponse()

    async def Remove(
        self,
        context: TransactionContext,
        state: Index.State,
        request: IndexRemoveRequest,
    ) -> IndexRemoveResponse:
        root = Node.ref(state.root_id)
        await root.Remove(context, key=request.key)
        return IndexRemoveResponse()

    async def Range(
        self,
        context: ReaderContext,
        state: Index.State,
        request: IndexRangeRequest,
    ) -> IndexRangeResponse:
        root = Node.ref(state.root_id)
        node_response = await root.Range(
            context,
            start_key=request.start_key,
            limit=request.limit,
        )

        index_entries = await self._entry_from_node_entry(
            node_response.entries
        )

        return IndexRangeResponse(entries=index_entries)

    async def ReverseRange(
        self,
        context: ReaderContext,
        state: Index.State,
        request: IndexReverseRangeRequest,
    ) -> IndexReverseRangeResponse:
        root = Node.ref(state.root_id)
        node_response = await root.ReverseRange(
            context,
            start_key=request.start_key,
            limit=request.limit,
        )

        index_entries = await self._entry_from_node_entry(
            node_response.entries
        )

        return IndexReverseRangeResponse(entries=index_entries)

    async def _entry_from_node_entry(
        self,
        node_entries: list[NodeEntry],
    ) -> list[Entry]:
        index_entries: list[Entry] = []

        for node_entry in node_entries:
            index_entry = Entry(key=node_entry.key)
            value = Value()
            value.ParseFromString(node_entry.value)
            if value.HasField("value"):
                index_entry.value.CopyFrom(value.value)
            elif value.HasField("bytes"):
                index_entry.bytes = value.bytes
            else:
                assert value.HasField("any")
                index_entry.any.CopyFrom(value.any)
            index_entries.append(index_entry)

        return index_entries

    async def Stringify(
        self,
        context: ReaderContext,
        state: Index.State,
        request: IndexStringifyRequest,
    ) -> IndexStringifyResponse:
        root = Node.ref(state.root_id)
        response = await root.Stringify(context, level=0)
        return IndexStringifyResponse(value=response.value)


def servicers():
    return [
        IndexServicer,
        NodeServicer,
    ]
