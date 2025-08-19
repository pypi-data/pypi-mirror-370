from __future__ import annotations

import logging
from asyncio import Future
from collections.abc import Callable
from typing import TypeVar

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .const import MainService
from .exceptions import DecodeError, WriteFailed
from .packets import Packet, PacketNotify, PacketNotifyAck, PacketWrite
from .services import NotifyCharacteristic, WriteCharacteristic

_LOGGER = logging.getLogger(__name__)

_PacketNotifyType = TypeVar("_PacketNotifyType", bound=PacketNotify)


class Client:
    def __init__(
        self, client: BleakClient, notify_callback: Callable[[Packet], None] | None
    ) -> None:
        self.bleak_client = client
        self._notify_callbacks = []
        if notify_callback:
            self._notify_callbacks.append(notify_callback)

    @property
    def is_connected(self) -> bool:
        return self.bleak_client.is_connected

    def notify_callbacks(self, packet: Packet):
        for callback in self._notify_callbacks:
            callback(packet)

    async def _start_notify(self):
        def notify_data(char_specifier: BleakGATTCharacteristic, data: bytearray):
            try:
                packet_data = NotifyCharacteristic.decode(data)
                packet = PacketNotify.decode(packet_data)
                _LOGGER.debug("Notify: %s", packet)
            except DecodeError as exc:
                _LOGGER.error("Failed to decode: %s with error %s", data, exc)
            self.notify_callbacks(packet)

        await self.bleak_client.start_notify(MainService.notify.uuid, notify_data)

    @staticmethod
    async def connect(
        device: BLEDevice,
        notify_callback: Callable[[Packet], None] | None = None,
        disconnected_callback: Callable[[], None] | None = None,
    ) -> Client:
        def _disconnected_callback(client: BleakClient):
            _LOGGER.info("Device disconnected %s", client.address)
            if disconnected_callback:
                disconnected_callback()

        bleak_client = await establish_connection(
            BleakClient,
            device=device,
            name="ToGrill Connection",
            disconnected_callback=_disconnected_callback,
        )
        try:
            client = Client(bleak_client, notify_callback)
            await client._start_notify()
        except Exception:
            await bleak_client.disconnect()
            pass
        return client

    async def disconnect(self) -> None:
        await self.bleak_client.disconnect()

    async def request(self, packet: type[PacketNotify]) -> None:
        await self.bleak_client.write_gatt_char(
            MainService.write.uuid, WriteCharacteristic.encode(packet.request()), False
        )

    async def write(self, packet: PacketWrite) -> PacketNotify:
        result_future = Future[PacketNotify]()

        def _callback(packet_notify: Packet):
            if not isinstance(packet_notify, PacketNotify):
                return

            if packet.type != packet.type:
                return

            if result_future.cancelled() or result_future.done():
                return

            if isinstance(packet_notify, PacketNotifyAck):
                if packet_notify.data == 0:
                    result_future.set_exception(WriteFailed("Failed to write data"))
                    return

            result_future.set_result(packet_notify)

        self._notify_callbacks.append(_callback)
        try:
            await self.bleak_client.write_gatt_char(
                MainService.write.uuid, WriteCharacteristic.encode(packet.encode()), False
            )
            return await result_future
        finally:
            self._notify_callbacks.remove(_callback)

    async def read(self, packet_type: type[_PacketNotifyType]) -> _PacketNotifyType:
        result = Future[packet_type]()

        def _callback(packet: Packet):
            if isinstance(packet, packet_type):
                if not result.cancelled() and not result.done():
                    result.set_result(packet)

        self._notify_callbacks.append(_callback)
        try:
            await self.request(packet_type)
            return await result
        finally:
            self._notify_callbacks.remove(_callback)
