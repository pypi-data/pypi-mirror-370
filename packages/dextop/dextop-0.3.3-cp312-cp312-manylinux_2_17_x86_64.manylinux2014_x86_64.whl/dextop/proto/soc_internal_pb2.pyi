from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoardType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BROADCAST: _ClassVar[BoardType]
    SOC: _ClassVar[BoardType]
    ARM: _ClassVar[BoardType]
    TORSO: _ClassVar[BoardType]
    CHASSIS: _ClassVar[BoardType]

BROADCAST: BoardType
SOC: BoardType
ARM: BoardType
TORSO: BoardType
CHASSIS: BoardType

class FirmwareVersion(_message.Message):
    __slots__ = (
        "hardware_version",
        "software_version",
        "compile_time",
        "main_hash",
        "sub_hash",
    )
    HARDWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMPILE_TIME_FIELD_NUMBER: _ClassVar[int]
    MAIN_HASH_FIELD_NUMBER: _ClassVar[int]
    SUB_HASH_FIELD_NUMBER: _ClassVar[int]
    hardware_version: int
    software_version: int
    compile_time: int
    main_hash: str
    sub_hash: str
    def __init__(
        self,
        hardware_version: _Optional[int] = ...,
        software_version: _Optional[int] = ...,
        compile_time: _Optional[int] = ...,
        main_hash: _Optional[str] = ...,
        sub_hash: _Optional[str] = ...,
    ) -> None: ...

class UpdateQuery(_message.Message):
    __slots__ = ("board", "packet_bytes")
    BOARD_FIELD_NUMBER: _ClassVar[int]
    PACKET_BYTES_FIELD_NUMBER: _ClassVar[int]
    board: BoardType
    packet_bytes: bytes
    def __init__(
        self,
        board: _Optional[_Union[BoardType, str]] = ...,
        packet_bytes: _Optional[bytes] = ...,
    ) -> None: ...

class UpdateReply(_message.Message):
    __slots__ = ("board", "success", "old_version", "new_version")
    BOARD_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    OLD_VERSION_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSION_FIELD_NUMBER: _ClassVar[int]
    board: BoardType
    success: bool
    old_version: FirmwareVersion
    new_version: FirmwareVersion
    def __init__(
        self,
        board: _Optional[_Union[BoardType, str]] = ...,
        success: bool = ...,
        old_version: _Optional[_Union[FirmwareVersion, _Mapping]] = ...,
        new_version: _Optional[_Union[FirmwareVersion, _Mapping]] = ...,
    ) -> None: ...
