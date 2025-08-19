from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import IntEnum
from typing import ClassVar, Self

from .exceptions import DecodeError

_PACKET_REGISTRY: dict[int, list[type[PacketNotify]]] = {}
_LOGGER = logging.getLogger(__name__)


def from_scaled_nullable(data: bytes, scale: float, null: int) -> float | None:
    if (value := from_nullable(data, null)) is None:
        return None
    return value / scale


def to_scaled_nullable(data: float | None, length: int, scale: float, null: int) -> bytes:
    if data is None:
        return null.to_bytes(length, "big")
    return round(data * scale).to_bytes(length, "big")


def from_nullable(data: bytes, null: int) -> int | None:
    value = int.from_bytes(data, "big")
    if value == null:
        return None
    return value


def from_nullable_enum(data: bytes, enum: type[IntEnum], null: int) -> int | None:
    if (value := from_nullable(data, null)) is None:
        return None
    try:
        return enum(value)
    except ValueError:
        return value


def to_nullable(data: int | None, length: int, null: int) -> bytes:
    if data is None:
        return null.to_bytes(length, "big")
    return data.to_bytes(length, "big")


class GrillType(IntEnum):
    BEEF = 1
    VEAL = 2
    LAMB = 3
    PORK = 4
    TURKEY = 5
    CHICKEN = 6
    SAUSAGE = 7
    FISH = 8
    HAMBURGER = 9
    BBQ_SMOKE = 10
    HOT_SMOKE = 11
    COLD_SMOKE = 12
    MARK_A = 13
    MARK_B = 14
    MARK_C = 15


class Taste(IntEnum):
    RARE = 1
    MEDIUM_RARE = 2
    MEDIUM = 3
    MEDIUM_WELL = 4
    WELL_DONE = 5


class AlarmType(IntEnum):
    TEMPERATURE_RANGE = 0
    TEMPERATURE_TARGET = 1


@dataclass
class Packet:
    type: ClassVar[int]

    @classmethod
    def decode(cls, data: bytes) -> Self:
        raise NotImplementedError()

    def encode(self) -> bytes:
        raise NotImplementedError()


@dataclass
class PacketNotify(Packet):
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        if packet_type := getattr(cls, "type", None):
            _PACKET_REGISTRY.setdefault(packet_type, []).append(cls)

    @classmethod
    def decode(cls, data: bytes) -> PacketNotify:
        if len(data) < 1:
            raise DecodeError("Failed to parse packet")
        exceptions = []
        for registered_cls in _PACKET_REGISTRY.get(data[0], []):
            try:
                return registered_cls.decode(data)
            except DecodeError as exc:
                exceptions.append(exc)
        if exceptions:
            raise ExceptionGroup(f"Fail to decode {data}", exceptions)
        return PacketUnknown(data[0], data[1:])

    @classmethod
    def request(cls) -> bytes:
        raise NotImplementedError


@dataclass
class PacketNotifyAck(PacketNotify):
    """Set timer."""

    type: ClassVar[int]
    data: int

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 2:
            raise DecodeError("Packet too short")
        return cls(data=data[1])


@dataclass
class PacketWrite(Packet):
    """Base class fro packet writes."""


@dataclass
class PacketA0Notify(PacketNotify):
    """Device status"""

    type: ClassVar[int] = 0xA0
    battery: int
    version_major: int
    version_minor: int
    function_type: int
    probe_count: int
    ambient: bool
    alarm_interval: int
    alarm_sound: bool

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 6:
            raise DecodeError("Packet too short")
        if data[0] != cls.type:
            raise DecodeError("Failed to parse packet")

        battery = data[1]
        version_major = data[2]
        version_minor = data[3]
        _unknown = data[4]
        bitfield = data[5]
        function_type = bitfield & 0xF
        probe_count = (bitfield >> 4) & 0x7
        ambient = bool(bitfield >> 7)

        alarm_interval = 5
        alarm_sound = True
        if len(data) > 6:
            alarm_interval = data[6]
            alarm_sound = data[7] == 1

        return cls(
            battery=battery,
            version_major=version_major,
            version_minor=version_minor,
            function_type=function_type,
            probe_count=probe_count,
            ambient=ambient,
            alarm_interval=alarm_interval,
            alarm_sound=alarm_sound,
        )

    @classmethod
    def request(cls) -> bytes:
        return bytes(
            [
                cls.type,
                0x00,
                0x00,
            ]
        )


@dataclass
class PacketA1Notify(PacketNotify):
    """Temperature on probes"""

    type: ClassVar[int] = 0xA1
    temperatures: list[float | None]

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 1:
            raise DecodeError("Packet too short")
        if data[0] != cls.type:
            raise DecodeError("Failed to parse packet")

        temperatures = [
            int.from_bytes(data[index : index + 2], "big") for index in range(1, len(data), 2)
        ]

        def convert(value: int) -> float | None:
            if value == 65535:
                return None
            if value > 32768:
                return (value - 32768) / 10
            return value / 10

        temperatures = [convert(temperature) for temperature in temperatures]

        return cls(temperatures=temperatures)

    @classmethod
    def request(cls) -> bytes:
        return bytes(
            [
                cls.type,
                0x00,
            ]
        )


@dataclass
class PacketA3Notify(PacketNotifyAck):
    type: ClassVar[int] = 0xA3


@dataclass
class PacketA300Write(PacketWrite):
    """Set min max temperature."""

    type: ClassVar[int] = 0xA3
    alarm_type: ClassVar[int] = 0x00
    probe: int
    minimum: float | None
    maximum: float | None

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 7:
            raise DecodeError("Packet too short")
        if data[2] != cls.alarm_type:
            raise DecodeError("Invalid subtype")
        return cls(
            probe=data[1],
            minimum=from_scaled_nullable(data[3:5], 10.0, 0xFFFF),
            maximum=from_scaled_nullable(data[5:7], 10.0, 0xFFFF),
        )

    def encode(self) -> bytes:
        return bytes(
            [
                self.type,
                self.probe,
                self.alarm_type,
                *to_scaled_nullable(self.minimum, 2, 10.0, 0xFFFF),
                *to_scaled_nullable(self.maximum, 2, 10.0, 0xFFFF),
            ]
        )


@dataclass(kw_only=True)
class PacketA301Write(PacketWrite):
    """Set target temperature."""

    type: ClassVar[int] = 0xA3
    alarm_type: ClassVar[int] = 0x01
    probe: int
    target: float | None

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 7:
            raise DecodeError("Packet too short")
        if data[2] != cls.alarm_type:
            raise DecodeError("Invalid subtype")

        return cls(
            probe=data[1],
            target=from_scaled_nullable(data[3:5], 10.0, 0xFFFF),
        )

    def encode(self) -> bytes:
        return bytes(
            [
                self.type,
                self.probe,
                self.alarm_type,
                *to_scaled_nullable(self.target, 2, 10.0, 0xFFFF),
                0,
                0,
            ]
        )


@dataclass(kw_only=True)
class PacketA303Write(PacketWrite):
    """Set grill data."""

    type: ClassVar[int] = 0xA3
    alarm_type: ClassVar[int] = 0x03
    probe: int
    grill_type: int | None = None
    taste: int | None = None

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 7:
            raise DecodeError("Packet too short")
        if data[2] != cls.alarm_type:
            raise DecodeError("Invalid subtype")
        return cls(
            probe=data[1],
            grill_type=from_nullable_enum(data[3:5], GrillType, 0),
            taste=from_nullable_enum(data[5:7], Taste, 0),
        )

    def encode(self) -> bytes:
        return bytes(
            [
                self.type,
                self.probe,
                self.alarm_type,
                *to_nullable(self.grill_type, 2, 0),
                *to_nullable(self.taste, 2, 0),
            ]
        )


@dataclass
class PacketA5Notify(PacketNotify):
    """Status from probe"""

    type: ClassVar[int] = 0xA5
    probe: int
    message: int

    class Message(IntEnum):
        PROBE_ACKNOWLEDGE = 0
        DEVICE_LOW_POWER = 1
        DEVICE_HIGH_TEMP = 2
        PROBE_BELOW_MINIMUM = 3
        PROBE_ABOVE_MAXIMUM = 4
        PROBE_ALARM = 5
        PROBE_DISCONNECTED = 6
        IGNITION_FAILURE = 7
        AMBIENT_LOW_TEMP = 8
        AMBIENT_OVER_HEAT = 9
        AMBIENT_COOL_DOWN = 10
        PROBE_TIMER_ALARM = 12

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 3:
            raise DecodeError("Packet too short")
        if data[0] != cls.type:
            raise DecodeError("Failed to parse packet")

        try:
            message = PacketA5Notify.Message(data[2])
        except ValueError:
            message = data[2]

        return cls(probe=data[1], message=message)


@dataclass
class PacketA6Write(PacketWrite):
    """Set alarm behaviour."""

    class Unit(IntEnum):
        UNIT_CELCIUS = 0
        UNIT_FARENHEIT = 1

    type: ClassVar[int] = 0xA6
    temperature_unit: int | None = None
    alarm_interval: int | None = None

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 3:
            raise DecodeError("Packet too short")
        if data[1] == 0xFF:
            temperature_unit = None
        else:
            try:
                temperature_unit = PacketA6Write.Unit(data[1])
            except ValueError:
                temperature_unit = data[2]

        if data[2] == 0xFF:
            alarm_interval = None
        else:
            alarm_interval = data[2]

        return cls(
            temperature_unit=temperature_unit,
            alarm_interval=alarm_interval,
        )

    def encode(self) -> bytes:
        if self.temperature_unit is None:
            temperature_unit_data = 0xFF
        else:
            temperature_unit_data = self.temperature_unit

        if self.alarm_interval is None:
            alarm_interval_data = 0xFF
        else:
            alarm_interval_data = self.alarm_interval

        return bytes(
            [
                self.type,
                temperature_unit_data,
                alarm_interval_data,
            ]
        )


@dataclass
class PacketA7Write(PacketWrite):
    """Set timer."""

    type: ClassVar[int] = 0xA7
    probe: int
    time: timedelta
    unknown: int = 1

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 5:
            raise DecodeError("Packet too short")
        return cls(
            time=timedelta(seconds=int.from_bytes(data[3:5], "big")), probe=data[1], unknown=data[2]
        )

    def encode(self) -> bytes:
        seconds = round(self.time.total_seconds())
        return bytes(
            [
                self.type,
                self.probe,
                self.unknown,
                *seconds.to_bytes(2, "big"),
            ]
        )


@dataclass
class PacketA7Notify(PacketNotifyAck):
    type: ClassVar[int] = 0xA7


@dataclass
class PacketA8Write(PacketWrite):
    """Set alarm behaviour."""

    type: ClassVar[int] = 0xA8
    probe: int
    unknown: int = 0

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 3:
            raise DecodeError("Packet too short")
        if data[0] != cls.type:
            raise DecodeError("Invalid type")
        return cls(probe=data[1], unknown=data[2])

    def encode(self) -> bytes:
        return bytes(
            [
                self.type,
                self.probe,
                self.unknown,
            ]
        )


@dataclass
class PacketA8Notify(PacketNotify):
    """Status from probe"""

    type: ClassVar[int] = 0xA8
    probe: int
    alarm_type: int | None
    temperature_1: float | None = None
    temperature_2: float | None = None
    grill_type: int | None = None
    taste: int | None = None
    time: timedelta = timedelta()

    AlarmType = AlarmType

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 12:
            raise DecodeError("Packet too short")
        if data[0] != cls.type:
            raise DecodeError("Failed to parse type")

        return cls(
            probe=data[1],
            alarm_type=from_nullable_enum(data[2:3], AlarmType, 0xFF),
            temperature_1=from_scaled_nullable(data[3:5], 10.0, 0xFFFF),
            temperature_2=from_scaled_nullable(data[5:7], 10.0, 0xFFFF),
            grill_type=from_nullable_enum(data[7:9], GrillType, 0x0),
            taste=from_nullable_enum(data[9:11], Taste, 0x0),
            time=timedelta(seconds=int.from_bytes(data[11:13], "big")),
        )

    def encode(self) -> bytes:
        seconds = round(self.time.total_seconds())
        return bytes(
            [
                self.type,
                self.probe,
                *to_nullable(self.alarm_type, 1, 0xFF),
                *to_scaled_nullable(self.temperature_1, 2, 10.0, 0xFFFF),
                *to_scaled_nullable(self.temperature_2, 2, 10.0, 0xFFFF),
                *to_nullable(self.grill_type, 2, 0x0),
                *to_nullable(self.taste, 2, 0x0),
                *seconds.to_bytes(2, "big"),
            ]
        )


@dataclass
class PacketUnknown(PacketNotify):
    type: int
    data: bytes

    @classmethod
    def decode(cls, data: bytes) -> Self:
        if len(data) < 1:
            raise DecodeError("Packet too short")
        return cls(data[0], data=data[1:])
