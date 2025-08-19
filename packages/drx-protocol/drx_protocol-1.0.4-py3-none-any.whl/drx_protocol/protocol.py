"""DrX communication protocol"""

import base64
import logging
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, overload

from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.Hash import SHA1, SHA256
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.PublicKey import RSA

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT, RSA_KEY_BITS, AES_salt
from .exceptions import (
    ApiError,
    DrxError,
    InvalidParameter,
    MessageIdError,
    UnexpectedPayload,
)
from .tcp import drx_tcp

_LOGGER = logging.getLogger(__name__)


@dataclass
class drx_command:
    """Drx command dataclass."""

    cmd: str
    cmd_type: str = "?"
    value: float = 0.0
    error: bool = False
    array: bytes = b""


class drx_protocol:
    """DrX communication protocol."""

    def __init__(
        self,
        host: str,
        serial: str,
        organization: str,
        signature: str,
        port: int = DEFAULT_PORT,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._tcp = drx_tcp(host, serial, port, timeout)

        self._serial = serial
        self._organization = organization
        self._signature = signature
        self._mess_id: int = 0
        self._token: str = ""
        self._aes_key: bytes | None = None
        self._aes_iv: bytes | None = None
        self._authenticated: bool = False
        self._connecting: bool = False

    @overload
    def send_command(self, command: list[drx_command]) -> dict[str, drx_command]: ...

    @overload
    def send_command(self, command: drx_command) -> drx_command: ...

    def send_command(self, command: list[drx_command] | drx_command) -> dict[str, drx_command] | drx_command:
        """Send a list of commands to the DrX device and get the response"""
        payload_array = b""
        debug_str = f"DrX {self._serial}: Sending"

        single_cmd = False
        if isinstance(command, drx_command):
            single_cmd = True
            command = [command]

        # construct the payload array
        for cmd in command:
            payload_array += f"{cmd.cmd}{cmd.cmd_type}".encode("utf-8") + struct.pack("f", cmd.value)
            if cmd.cmd_type in [">", "<"]:
                payload_array += cmd.array

            # construct debug Sending string
            if _LOGGER.isEnabledFor(logging.DEBUG):
                if cmd.cmd_type in [">", "<"]:
                    debug_str += f" {cmd.cmd}{cmd.cmd_type} {int(cmd.value)} bytes array"
                else:
                    debug_str += f" {cmd.cmd}{cmd.cmd_type}"
                    if cmd.cmd_type == "=":
                        debug_str += f"{cmd.value}"

        _LOGGER.debug(debug_str)

        # send the message
        (command_id, payload) = self._send_AES(payload_array)

        # check the command ID of the response
        if command_id != "C":
            raise ApiError(f"DrX {self._serial}: Received command ID '{command_id}' while expecting 'C' during send commands")

        # Parse the response message
        result = self._parse_payload(payload)
        if single_cmd:
            return list(result.values())[0]
        return result

    def close(self) -> None:
        """Disconnect from the DrX device"""
        self._tcp.close()

    def _send(self, mess: bytes) -> tuple[str, bytes]:
        """Send a message to the DrX device and get back the response payload"""
        if not self._authenticated and not self._connecting:
            self._connect()

        # send the message
        self._tcp.send(mess)

        # receive the header of the response
        header = self._tcp.receive(3)
        command_id = header[0:1].decode("utf-8")
        if command_id == "E":
            raise ApiError(f"DrX {self._serial}: Received API error")
        mess_len = int.from_bytes(header[1:3], "little")

        # receive the encrypted payload now the message lenght is known
        return (command_id, self._tcp.receive(mess_len - 3))

    def _send_AES(self, payload_array: bytes, command_id: str = "C") -> tuple[str, bytes]:
        """Send a message to the DrX device using AES encryption and get back the response payload"""
        # check if authenticated
        if not self._authenticated and not self._connecting:
            self._connect()

        # construct the payload
        self._mess_id += 1
        payload_len = 3 + len(payload_array)
        payload = self._mess_id.to_bytes(1, "little") + payload_len.to_bytes(2, "little") + payload_array

        # AES enctypt the payload
        encrypted_payload = self._aes_encrypt(payload)

        # construct the message
        mess_len = 3 + len(encrypted_payload)
        message = command_id.encode("utf-8") + mess_len.to_bytes(2, "little") + encrypted_payload

        # send the message
        recv_command_id, encrypted_response = self._send(message)

        # decrypt the response using AES
        recv_payload = self._aes_decrypt(encrypted_response)

        return (recv_command_id, recv_payload)

    def _aes_encrypt(self, payload: bytes) -> bytes:
        """Encrypt a payload using AES encryption"""
        if self._aes_key is None or self._aes_iv is None:
            raise InvalidParameter(f"DrX {self._serial}: First call construct_aes_key before using AES encryption")

        # zero padding to 16 byte blocks
        pad_len = 16 - (len(payload) % 16)
        payload += bytes(pad_len)

        cipher = AES.new(key=self._aes_key, mode=AES.MODE_CBC, iv=self._aes_iv)
        return cipher.encrypt(payload)

    def _aes_decrypt(self, payload: bytes) -> bytes:
        """Decrypt a payload using AES decryption"""
        if self._aes_key is None or self._aes_iv is None:
            raise InvalidParameter(f"DrX {self._serial}: First call construct_aes_key before using AES decryption")

        cipher = AES.new(key=self._aes_key, mode=AES.MODE_CBC, iv=self._aes_iv)
        return cipher.decrypt(payload)

    def _float_len(self, data: bytes | str) -> bytes:
        """Gets the length of the data, converts it to a float and converts that to 4 bytes"""
        return struct.pack("f", len(data))

    def _parse_payload(self, payload: bytes) -> dict[str, drx_command]:
        """Parse a received payload and return a dict containing the commands with there values"""
        # check that at least the Payload header is received
        recv_payload_len = len(payload)
        if recv_payload_len < 3:
            raise UnexpectedPayload(f"DrX {self._serial}: Payload is only {recv_payload_len} long, expected at least 11 bytes")

        # Check the message ID
        if (recv_mess_id := payload[0]) != self._mess_id:
            raise MessageIdError(f"DrX {self._serial}: Received message ID {recv_mess_id} does not match send message ID {self._mess_id}")

        # Check the payload length
        payload_len = int.from_bytes(payload[1:3], "little")
        if recv_payload_len < payload_len:
            raise UnexpectedPayload(f"DrX {self._serial}: Payload is only {recv_payload_len} long, while payload header specifies {payload_len}")

        # Loop over the received commands and process them
        data = {}
        idx = 3
        while idx + 8 <= payload_len:
            cmd_str = payload[idx : idx + 4].decode("utf-8")
            idx += 4
            cmd = cmd_str[0:3]
            cmd_type = cmd_str[3]
            [value] = struct.unpack("f", payload[idx : idx + 4])
            idx += 4

            if cmd_type in ["?", "="]:
                # normal float value received
                data[cmd] = drx_command(cmd, cmd_type, value)
            elif cmd_type == "!":
                # received an error
                _LOGGER.warning(
                    "DrX %s: Received error code %s for cmd %s",
                    self._serial,
                    int(value),
                    cmd,
                )
                data[cmd] = drx_command(cmd, cmd_type, value, error=True)
            elif cmd_type in [">", "<"]:
                # received a data array
                int_value = int(value)
                array = payload[idx : idx + int_value]
                idx += int_value
                data[cmd] = drx_command(cmd, cmd_type, value, array=array)
            else:
                raise UnexpectedPayload(f"DrX {self._serial}: Received type '{cmd_type}' which is not supported")

        # print debug Receive string
        if _LOGGER.isEnabledFor(logging.DEBUG):
            debug_str = f"DrX {self._serial}: Received"
            for cmd, drx_cmd in data.items():
                if drx_cmd.error:
                    debug_str += f" {cmd}: err {int(drx_cmd.value)}"
                elif drx_cmd.array:
                    debug_str += f" {cmd}: {int(drx_cmd.value)} bytes array"
                else:
                    debug_str += f" {cmd}: {drx_cmd.value}"
            _LOGGER.debug(debug_str)

        return data

    def _handshake(self) -> None:
        """Send a handshake request to the DrX device"""

        # generate the RSA public/private key pair
        rsa_key = RSA.generate(RSA_KEY_BITS)

        # convert the rsa_key.e and rsa_key.n to base64 encoding
        exponent = base64.b64encode(rsa_key.e.to_bytes((rsa_key.e.bit_length() + 7) // 8, byteorder="big"))
        modulus = base64.b64encode(rsa_key.n.to_bytes((rsa_key.n.bit_length() + 7) // 8, byteorder="big"))

        # construct header and payload header
        payload_len = 3 + 8 + len(exponent) + 8 + len(modulus) + 8 + len(self._organization)
        mess_len = 3 + payload_len
        self._mess_id += 1
        message = b"H" + mess_len.to_bytes(2, "little") + self._mess_id.to_bytes(1, "little") + payload_len.to_bytes(2, "little")

        # Exp command
        message += b"Exp>" + self._float_len(exponent) + exponent

        # Mod command
        message += b"Mod>" + self._float_len(modulus) + modulus

        # Org command
        message += b"Org>" + self._float_len(self._organization) + bytes(self._organization, "utf-8")

        # send the message
        _LOGGER.debug(
            "DrX %s: Sending handshake with organization %s",
            self._serial,
            self._organization,
        )
        try:
            command_id, encrypted_payload = self._send(message)
        except DrxError:
            self.close()
            raise

        # check response command_id
        if command_id != "H":
            self.close()
            raise ApiError(f"DrX {self._serial}: Received command ID '{command_id}' while expecting 'H' during handshake")

        # decrypt response using RSA
        rsa = PKCS1_v1_5.new(rsa_key)
        payload = rsa.decrypt(encrypted_payload, None, 0)
        if payload is None:
            raise UnexpectedPayload(f"DrX {self._serial}: Did not receive a payload during handshake")

        # parse the decrypted response
        try:
            data = self._parse_payload(payload)
        except DrxError:
            self.close()
            raise

        # Check the token and store it
        cmd = data.get("Tok", drx_command("Tok", error=True))
        if cmd.error:
            self.close()
            raise ApiError(f"DrX {self._serial}: Received error code {int(cmd.value)} while obtaining token")

        self._token = cmd.array.decode("utf-8")

    def _construct_aes_key(self) -> None:
        """Construct the AES key and AES iv"""
        if not self._token:
            raise InvalidParameter(f"DrX {self._serial}: First call handshake before constructing AES key to obtain the token")

        # construct password
        password = f"{self._organization}{self._serial}{self._token}"

        # hash the password using SHA256
        sha_256 = SHA256.new()
        sha_256.update(password.encode("utf-8"))
        password_hash = sha_256.digest()

        # Use password-based key derivation with PBKDF2 to get the AES key and AES iv
        key = PBKDF2(password_hash, AES_salt, 48, count=1000, hmac_hash_module=SHA1)  # type: ignore
        self._aes_key = key[0:32]
        self._aes_iv = key[32:48]

    def _signature_authenicaton(self) -> None:
        """send the signature to the device for authentication"""
        if not self._aes_key:
            raise InvalidParameter(f"DrX {self._serial}: First call handshake before constructing AES key to obtain the token")

        # Sig command
        payload_array = b"Sig>" + self._float_len(self._signature) + self._signature.encode("utf-8")

        _LOGGER.debug("DrX %s: Sending signature for authentication", self._serial)
        (command_id, _) = self._send_AES(payload_array, command_id="S")

        # check the command_id
        if command_id != "A":
            raise ApiError(f"DrX {self._serial}: Received command ID '{command_id}' while expecting 'A' during authentication")

        _LOGGER.debug("DrX %s: Authenticated succesfully", self._serial)
        self._authenticated = True

    def _connect(self) -> None:
        """connect to the DrX device"""
        self._connecting = True
        try:
            self._handshake()
            self._construct_aes_key()
            self._signature_authenicaton()
        finally:
            self._connecting = False


class drx_property:
    """Base class for DrX properties"""

    def __init__(self, cmd: str):
        self.cmd = cmd


class drx_float(drx_property):
    """DrX float property class"""

    def __get__(self, instance, owner) -> float | None:
        val = instance._cache.get(self.cmd)
        if val is None or val.error:
            return None
        return val.value

    def __set__(self, instance, value: float) -> None:
        instance.send_command(drx_command(self.cmd, "=", value))


class drx_int(drx_property):
    """DrX integer property class"""

    def __get__(self, instance, owner) -> int | None:
        val = instance._cache.get(self.cmd)
        if val is None or val.error:
            return None
        return int(val.value)

    def __set__(self, instance, value: int) -> None:
        instance.send_command(drx_command(self.cmd, "=", float(value)))


class drx_bool(drx_property):
    """DrX boolean property class"""

    def __get__(self, instance, owner) -> bool | None:
        val = instance._cache.get(self.cmd)
        if val is None or val.error:
            return None
        return bool(val.value)

    def __set__(self, instance, value: bool) -> None:
        instance.send_command(drx_command(self.cmd, "=", float(value)))


T = TypeVar("T", bound=Enum)


class drx_enum(drx_property, Generic[T]):
    """DrX enum property class, the enum is supplied during init"""

    def __init__(self, cmd: str, enum: type[T], offset: int | None = None):
        drx_property.__init__(self, cmd)
        self._enum = enum
        self._offset = offset

    def __get__(self, instance, owner) -> T | None:
        val = instance._cache.get(self.cmd)
        if val is None or val.error:
            return None
        new_val = int(val.value)
        if self._offset is not None:
            new_val = new_val - self._offset
        return self._enum(new_val)

    def __set__(self, instance, value: T) -> None:
        new_val = float(value.value)
        if self._offset is not None:
            new_val = new_val + self._offset
        instance.send_command(drx_command(self.cmd, "=", new_val))
