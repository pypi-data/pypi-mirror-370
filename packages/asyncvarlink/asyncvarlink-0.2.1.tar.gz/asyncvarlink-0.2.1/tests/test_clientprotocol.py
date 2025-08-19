# Copyright 2024 Helmut Grohne <helmut@subdivi.de>
# SPDX-License-Identifier: LGPL-2.0-or-later

import asyncio
import os
import socket
import typing
import unittest

from asyncvarlink import (
    ConversionError,
    FileDescriptor,
    VarlinkClientProtocol,
    VarlinkErrorReply,
    VarlinkInterface,
    VarlinkTransport,
    varlinkmethod,
)


class DemoInterface(VarlinkInterface, name="com.example.demo"):
    @varlinkmethod(return_parameter="result")
    def Method(self, argument: str) -> str: ...

    @varlinkmethod(return_parameter="result")
    def MoreMethod(self) -> typing.Iterator[str]: ...

    @varlinkmethod(return_parameter="fd")
    def CreateFd(self) -> FileDescriptor: ...


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.loop = asyncio.get_running_loop()
        self.sock1, self.sock2 = socket.socketpair(
            type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        self.proto = VarlinkClientProtocol()
        self.transport = VarlinkTransport(
            self.loop, self.sock2, self.sock2, self.proto
        )
        self.proxy = self.proto.make_proxy(DemoInterface)

    async def asyncTearDown(self) -> None:
        self.transport.close()
        await asyncio.sleep(0)
        self.assertLess(self.sock2.fileno(), 0)
        self.sock1.close()
        await super().asyncTearDown()

    async def expect_data(self, expected: bytes) -> None:
        data = await self.loop.sock_recv(self.sock1, len(expected) + 1)
        self.assertEqual(data, expected)

    def _send_data(
        self, fut: asyncio.Future, data: bytes, fds: list[int] | None = None
    ) -> None:
        if fds is None:
            fds = []
        try:
            sent = socket.send_fds(self.sock1, [data], fds)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            if sent >= len(data):
                self.loop.remove_writer(self.sock1)
                fut.set_result(None)
            else:
                self.loop.add_writer(self.sock1, self._send_data, fut, data)

    def send_data(
        self, data: bytes, fds: list[int] | None = None
    ) -> asyncio.Future[None]:
        fut = self.loop.create_future()
        self.loop.add_writer(self.sock1, self._send_data, fut, data, fds)
        return fut

    async def test_simple(self) -> None:
        fut = asyncio.ensure_future(self.proxy.Method(argument="spam"))
        await self.expect_data(
            b'{"method":"com.example.demo.Method","parameters":{"argument":"spam"}}\0'
        )
        self.assertFalse(fut.done())
        await self.send_data(b'{"parameters":{"result":"egg"}}\0')
        self.assertEqual(await fut, {"result": "egg"})

    async def test_more(self) -> None:
        gen = self.proxy.MoreMethod()
        fut = asyncio.ensure_future(anext(gen))
        await self.expect_data(
            b'{"method":"com.example.demo.MoreMethod","more":true}\0'
        )
        self.assertFalse(fut.done())
        await self.send_data(
            b'{"continues":true,"parameters":{"result":"spam"}}\0'
        )
        self.assertEqual(await fut, {"result": "spam"})
        fut = asyncio.ensure_future(anext(gen))
        await asyncio.sleep(0)
        self.assertFalse(fut.done())
        await self.send_data(b'{"parameters":{"result":"egg"}}\0')
        self.assertEqual(await fut, {"result": "egg"})
        with self.assertRaises(StopAsyncIteration):
            await anext(gen)

    async def test_invalid_argument(self) -> None:
        fut = asyncio.ensure_future(self.proxy.Method(invalid_argument=True))
        await asyncio.sleep(0)
        self.assertTrue(fut.done())
        self.assertRaises(ConversionError, fut.result)

    async def test_permission_denied(self) -> None:
        fut = asyncio.ensure_future(self.proxy.Method(argument="spam"))
        await self.expect_data(
            b'{"method":"com.example.demo.Method","parameters":{"argument":"spam"}}\0'
        )
        self.assertFalse(fut.done())
        await self.send_data(
            b'{"error":"org.varlink.service.PermissionDenied"}\0'
        )
        try:
            result = await fut
        except VarlinkErrorReply as err:
            self.assertEqual(err.name, "org.varlink.service.PermissionDenied")
        else:
            self.fail(
                f"expected a VarlinkErrorReply exception, got {result!r}"
            )

    async def test_broken_pipe_send(self) -> None:
        self.sock1.close()
        fut = asyncio.ensure_future(self.proxy.Method(argument="spam"))
        with self.assertRaises(BrokenPipeError):
            await fut
        self.assertLess(self.sock2.fileno(), 0)

    async def test_broken_pipe_receive(self) -> None:
        fut = asyncio.ensure_future(self.proxy.Method(argument="spam"))
        await self.expect_data(
            b'{"method":"com.example.demo.Method","parameters":{"argument":"spam"}}\0'
        )
        self.assertFalse(fut.done())
        self.sock1.close()
        with self.assertRaises(ConnectionResetError):
            await fut
        self.assertLess(self.sock2.fileno(), 0)

    async def test_return_fd(self) -> None:
        fut = asyncio.ensure_future(self.proxy.CreateFd())
        await self.expect_data(b'{"method":"com.example.demo.CreateFd"}\0')
        self.assertFalse(fut.done())
        rend, wend = os.pipe()
        self.addCleanup(os.close, rend)
        read_fut = self.loop.create_future()

        def _pipe_readable() -> None:
            self.loop.remove_reader(rend)
            try:
                data = os.read(rend, 7)
            except Exception as exc:
                read_fut.set_exception(exc)
            else:
                read_fut.set_result(data)

        self.loop.add_reader(rend, _pipe_readable)
        await self.send_data(b'{"parameters":{"fd":0}}\0', [wend])
        with await fut as ret:
            wfd = ret["fd"].take()
        self.addCleanup(os.close, wfd)
        os.close(wend)  # Defer closure for assertNotEqual
        self.assertNotEqual(wfd, wend)
        self.assertFalse(read_fut.done())
        os.write(wfd, b"needle")
        self.assertEqual(await read_fut, b"needle")


class ClientPipeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.loop = asyncio.get_running_loop()
        self.pipers, self.pipewc = os.pipe()
        self.piperc, self.pipews = os.pipe()
        os.set_blocking(self.pipers, False)
        os.set_blocking(self.pipews, False)
        self.proto = VarlinkClientProtocol()
        self.transport = VarlinkTransport(
            self.loop, self.piperc, self.pipewc, self.proto
        )
        self.proxy = self.proto.make_proxy(DemoInterface)

    async def expect_data(self, expected: bytes) -> None:
        fut = self.loop.create_future()
        self.loop.add_reader(self.pipers, fut.set_result, None)
        await fut
        self.loop.remove_reader(self.pipers)
        data = os.read(self.pipers, len(expected) + 1)
        self.assertEqual(data, expected)

    async def test_broken_pipe_send(self) -> None:
        os.close(self.pipers)
        fut = asyncio.ensure_future(self.proxy.Method(argument="spam"))
        with self.assertRaises(BrokenPipeError):
            await fut
        with self.assertRaisesRegex(OSError, "Bad file descriptor"):
            os.close(self.pipewc)

    async def test_broken_pipe_receive(self) -> None:
        fut = asyncio.ensure_future(self.proxy.Method(argument="spam"))
        await self.expect_data(
            b'{"method":"com.example.demo.Method","parameters":{"argument":"spam"}}\0'
        )
        self.assertFalse(fut.done())
        os.close(self.pipews)
        with self.assertRaises(ConnectionResetError):
            await fut
        with self.assertRaisesRegex(OSError, "Bad file descriptor"):
            os.close(self.pipewc)
