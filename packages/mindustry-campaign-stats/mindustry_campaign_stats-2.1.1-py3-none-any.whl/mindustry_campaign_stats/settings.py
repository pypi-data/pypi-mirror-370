from typing import BinaryIO, Union, Dict
from mutf8 import decode_modified_utf8
from enum import IntEnum
import ubjson
import struct


class SettingType(IntEnum):
    Boolean = 0
    Int = 1
    Long = 2
    Float = 3
    String = 4
    Binary = 5


class SettingsReader:
    fp: BinaryIO

    def __init__(self, fp: BinaryIO):
        self.fp = fp

    def read_mutf8(self) -> str:
        return decode_modified_utf8(
            self.read_bytes(
                self.read_uint16()
            )
        )

    def read_boolean(self) -> bool:
        return self.unpack('?')

    def read_float(self) -> float:
        return self.unpack('f', 4)

    def read_int8(self) -> int:
        return self.unpack('b')

    def read_uint16(self) -> int:
        return self.unpack('H', 2)

    def read_int32(self) -> int:
        return self.unpack('i', 4)

    def read_int64(self) -> int:
        return self.unpack('q', 8)

    def read_bytes(self, size: int) -> bytes:
        return self.fp.read(size)

    def unpack(self, fmt: str, size: int = 1) -> Union[bool, float, int, bytes]:
        ret = struct.unpack(
            f'>{fmt}',
            self.read_bytes(size)
        )

        return ret[0] if len(ret) == 1 else ret


def load(fp: BinaryIO) -> Dict[str, Union[bool, float, int, bytes, str]]:
    settings = {}
    reader = SettingsReader(fp)

    fields_count = reader.read_int32()

    if fields_count <= 0:
        raise ValueError('Invalid settings files: fields count is lower than or equal to 0')

    for _ in range(fields_count):
        field_name = reader.read_mutf8()
        field_type_id = reader.read_int8()

        try:
            field_type = SettingType(field_type_id)
        except ValueError:
            raise ValueError(f'Unhandled field type ID "{field_type_id}" for field "{field_name}"') from None

        if field_type == SettingType.Boolean:
            settings[field_name] = reader.read_boolean()
        elif field_type == SettingType.Int:
            settings[field_name] = reader.read_int32()
        elif field_type == SettingType.Long:
            settings[field_name] = reader.read_int64()
        elif field_type == SettingType.Float:
            settings[field_name] = reader.read_float()
        elif field_type == SettingType.String:
            settings[field_name] = reader.read_mutf8()
        elif field_type == SettingType.Binary:
            settings[field_name] = reader.read_bytes(reader.read_int32())

            # If it looks like ubjson data, try to read it
            if settings[field_name].startswith((b'{', b'[')):
                try:
                    settings[field_name] = ubjson.loadb(settings[field_name])
                except:
                    pass

    if reader.read_bytes(1):
        raise ValueError('Expected EOF, but got something to read')

    return settings
