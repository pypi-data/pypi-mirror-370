# Copyright 2024 Helmut Grohne <helmut@subdivi.de>
# SPDX-License-Identifier: LGPL-2.0-or-later

"""asyncio varlink client protocol implementation"""

import asyncio
import collections
import contextlib
import typing

from .conversion import FileDescriptorVarlinkType
from .error import GenericVarlinkErrorReply
from .interface import VarlinkInterface, varlinksignature
from .message import VarlinkMethodCall, VarlinkMethodReply
from .protocol import VarlinkProtocol
from .types import FileDescriptorArray, JSONObject
from .util import completing_future


class VarlinkClientProtocol(VarlinkProtocol):
    """Protocol class for a varlink client. Calls can be issued using the call
    and call_more methods. Associated replies are returned or generated from
    these methods asynchronously. There usually is no need to further derive
    this class.
    """

    _CallResult: typing.TypeAlias = tuple[
        VarlinkMethodReply, FileDescriptorArray | None
    ]

    class _PendingReply:
        def __init__(
            self,
            want_fds: bool,
            consumer_fut: asyncio.Future[None] | None = None,
        ):
            loop = asyncio.get_running_loop()
            self.future: asyncio.Future[
                "VarlinkClientProtocol._CallResult"
            ] = loop.create_future()
            self.want_fds = want_fds
            self.consumer_fut = consumer_fut or loop.create_future()

        def request_received(
            self, obj: JSONObject, fds: FileDescriptorArray | None
        ) -> None:
            if self.future.done():
                # Multiple replies not permitted.
                return
            try:
                reply = VarlinkMethodReply.fromjson(obj)
            except (TypeError, ValueError) as err:
                self.future.set_exception(err)
                return
            if not self.want_fds:
                fds = None
            elif fds:
                fds.reference_until_done(self.consumer_fut)
            self.future.set_result((reply, fds))

        def connection_lost(self, exc: Exception) -> None:
            if self.future.done():
                return
            self.future.set_exception(exc)

        def consumer_done(self) -> None:
            self.consumer_fut.set_result(None)

    class _PendingReplies:
        def __init__(self) -> None:
            self.replies = collections.deque(
                [VarlinkClientProtocol._PendingReply(True)]
            )

        def request_received(
            self, obj: JSONObject, fds: FileDescriptorArray | None
        ) -> None:
            lastreply = self.replies[-1]
            if lastreply.future.done():
                # This call does not handle any more continuations.
                return
            if obj.get("continues", False):
                self.replies.append(VarlinkClientProtocol._PendingReply(True))
            lastreply.request_received(obj, fds)

        def connection_lost(self, exc: Exception) -> None:
            lastreply = self.replies[-1]
            lastreply.connection_lost(exc)

        def consumer_done(self) -> None:
            if self.replies:
                while len(self.replies) > 1:
                    preply = self.replies.popleft()
                    assert preply.future.done()
                    preply.consumer_done()
                self.replies[0].consumer_done()

    def __init__(self) -> None:
        super().__init__()
        self._pending: collections.deque[
            VarlinkClientProtocol._PendingReply
            | VarlinkClientProtocol._PendingReplies
        ] = collections.deque()

    async def call(
        self,
        call: VarlinkMethodCall,
        fds: list[int] | None = None,
        replyfdsdone: asyncio.Future[None] | None = None,
    ) -> _CallResult | None:
        """Issue a varlink call. If the call has the more attribute set, the
        call_more method must be used instead. The given fds (if any) must
        remain available until the call method returns and the responsibility
        for closing them remains with the caller. If the caller expects file
        descriptors to be returned, it must pass a replyfdsdone future. The
        returned FileDescriptorArray (if any) will be valid until the
        replyfdsdone future is done.
        """
        assert not call.more
        if call.oneway:
            await self.send_message(call.tojson(), fds, autoclose=False)
            return None
        pending = VarlinkClientProtocol._PendingReply(
            replyfdsdone is not None, replyfdsdone
        )
        try:
            self._pending.append(pending)
            # We may pipeline calls here.
            await self.send_message(call.tojson(), fds, autoclose=False)
            return await pending.future
        finally:
            if replyfdsdone is None:
                pending.consumer_done()

    async def call_more(
        self, call: VarlinkMethodCall, fds: list[int] | None = None
    ) -> typing.AsyncGenerator[_CallResult, None]:
        """Issue a varlink call expecting multiple replies. If the call does
        not set the more attribute, the call method must be used instead. The
        given fds (if any) must remain available until the method returns and
        the responsibility for closing them remains with the caller. Replies
        generally include returned a FileDescriptorArray if file descriptors
        were received. Such an array remains valid from one iteration to the
        next. Its lifetime can be extended using its reference_until_done
        method.
        """
        assert call.more
        pending = VarlinkClientProtocol._PendingReplies()
        self._pending.append(pending)
        # We may pipeline calls here.
        sendfut = self.send_message(call.tojson(), fds, autoclose=False)
        try:
            while pending.replies:
                preply = pending.replies[0]
                result = await preply.future
                pending.replies.popleft()
                try:
                    yield result
                finally:
                    preply.consumer_done()
        finally:
            pending.consumer_done()
            await sendfut

    def request_received(
        self, obj: JSONObject, fds: FileDescriptorArray | None
    ) -> None:
        if obj.get("continues", False):
            pending = self._pending[0]
        else:
            pending = self._pending.popleft()
        pending.request_received(obj, fds)

    def connection_lost(self, exc: Exception | None) -> None:
        super().connection_lost(exc)
        if exc is None:
            exc = ConnectionResetError("Connection lost")
        while self._pending:
            pending = self._pending.popleft()
            pending.connection_lost(exc)
        self.close()

    def eof_received(self) -> None:
        super().eof_received()
        self.connection_lost(ConnectionResetError("remote closed connection"))

    def make_proxy(
        self, interface: type[VarlinkInterface]
    ) -> "VarlinkInterfaceProxy":
        """Convenience function that constructs an interface proxy object for
        the combination of protocol instance and interface class at hand.
        """
        return VarlinkInterfaceProxy(self, interface)


class _KwOnlyFunction(typing.Protocol):
    def __call__(self, **kwargs: typing.Any) -> typing.Any: ...


class _ResourceManager:
    """A context manager that yields a given result on entry and calls a given
    cleanup function on exit.
    """

    def __init__(self, result: typing.Any, close: typing.Callable[[], None]):
        self._result = result
        self._close = close

    def __enter__(self) -> typing.Any:
        return self._result

    def __exit__(self, *exc: typing.Any) -> None:
        self._close()


class VarlinkInterfaceProxy:
    """Interface proxy class for a varlink client. Its only purpose is to
    provide a suitable __getattr__ method such that methods declared on a
    VarlinkInterface subclass can be invoked on the proxy object and result in
    calls on a protocol instance.
    """

    def __init__(
        self,
        protocol: VarlinkClientProtocol,
        interface: type[VarlinkInterface],
    ):
        """The given protocol instance is used to actually perform calls. A
        protocol instance can be used with multiple proxy objects concurrently.
        The interface subclass (not instance) is used to generate conversions
        for proxy methods. Its methods can be stubbed as they are never called
        from a proxy. What matters is the types of its methods as they are used
        for converting between Python and JSON objects.
        """
        self._protocol = protocol
        self._interface = interface

    def __getattr__(self, attr: str) -> _KwOnlyFunction:
        """Look up a method on the VarlinkInterface subclass and return a proxy
        method if available. Raises AttributeError if no suitable method could
        be found. The type of the proxy method is dynamic. It is generally
        asynchronous and must be called within an asyncio event loop. It may or
        may not return a generator. All arguments must be keyword arguments.
        If the return type contains file descriptors, the result is
        additionally wrapped in a synchronous context manager.
        """
        try:
            fqmethod = f"{self._interface.name}.{attr}"
        except ValueError as err:
            raise AttributeError(f"invalid method name {attr}") from err
        # Intentionally propagate AttributeError
        method = getattr(self._interface, attr)
        if (signature := varlinksignature(method)) is None:
            raise AttributeError(f"no {attr} varlink method found")
        if signature.more:

            async def proxy_call_more(
                **kwargs: typing.Any,
            ) -> typing.AsyncGenerator[typing.Any, None]:
                with FileDescriptorArray.new_managed() as pfds:
                    # This may raise a ConversionError.
                    parameters = signature.parameter_type.tojson(
                        kwargs, {FileDescriptorVarlinkType: pfds}
                    )
                    async for reply, rfds in self._protocol.call_more(
                        VarlinkMethodCall(fqmethod, parameters, more=True),
                        [fd.fileno() for fd in pfds],
                    ):
                        if reply.error is None:
                            # This may raise a ConversionError.
                            ret = signature.return_type.fromjson(
                                reply.parameters,
                                {FileDescriptorVarlinkType: rfds},
                            )
                            if signature.return_type.contains_fds:
                                if rfds is None:
                                    yield contextlib.nullcontext(ret)
                                else:
                                    sentinel = object()
                                    rfds.reference(sentinel)
                                    yield _ResourceManager(
                                        ret, lambda: rfds.release(sentinel)
                                    )
                            else:
                                yield ret
                        else:
                            raise GenericVarlinkErrorReply(
                                reply.error, reply.parameters
                            )

            return proxy_call_more

        async def proxy_call(**kwargs: typing.Any) -> typing.Any:
            with FileDescriptorArray.new_managed() as pfds:
                # This may raise a ConversionError
                parameters = signature.parameter_type.tojson(
                    kwargs, {FileDescriptorVarlinkType: pfds}
                )
                with completing_future() as donefut:
                    result = await self._protocol.call(
                        VarlinkMethodCall(fqmethod, parameters),
                        [fd.fileno() for fd in pfds],
                        donefut,
                    )
                    assert result is not None
                    reply, fda = result
                    if reply.error is None:
                        # This may raise a ConversionError.
                        ret = signature.return_type.fromjson(
                            reply.parameters, {FileDescriptorVarlinkType: fda}
                        )
                        if not signature.return_type.contains_fds:
                            return ret
                        if fda is None:
                            return contextlib.nullcontext(ret)
                        sentinel = object()
                        fda.reference(sentinel)
                        return _ResourceManager(
                            ret, lambda: fda.release(sentinel)
                        )
                    raise GenericVarlinkErrorReply(
                        reply.error, reply.parameters
                    )

        return proxy_call
