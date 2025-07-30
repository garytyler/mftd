# Thin stateless API for interacting with the Midi Fighter Twister via SysEx
# and basic MIDI commands.
from __future__ import annotations

import time
from dataclasses import fields
from typing import Iterable, Optional, List, Dict

from . import constants
from .device import DeviceConfig
from .protocol import MidiOutput, MidiInput


class MftSysexApi:
    """Stateless helper for sending and receiving SysEx messages."""

    @staticmethod
    def set_device_config(
        midi_out: MidiOutput,
        data: Dict[int, int],
    ) -> None:

        def _int(value: int) -> int:
            if hasattr(value, "value"):
                return int(value.value)
            return int(value)

        pairs: list[int] = []

        for addr, val in data.items():
            if val is not None:
                pairs.extend([addr, _int(val)])

        header = [
            0xF0,
            constants.MIDI_MFR_ID_0,
            constants.MIDI_MFR_ID_1,
            constants.MIDI_MFR_ID_2,
            constants.SysexCommands.PUSH_CONF,
        ]
        payload = header.copy()
        for i in range(0, len(pairs), 2):
            if len(payload) - len(header) + 2 > constants.PART_SIZE_BYTES:
                payload.append(0xF7)
                MftSysexApi._send_sysex(midi_out, payload)
                payload = header.copy()
            payload.extend(pairs[i : i + 2])

        if len(payload) > len(header):
            payload.append(0xF7)
            MftSysexApi._send_sysex(midi_out, payload)

    @staticmethod
    def set_encoder_config(
        midi_out: MidiOutput,
        encoder_index: int,
        data: Dict[int, int],
    ) -> None:

        sysex_tag = encoder_index + 1

        params: List[int] = []
        for address, value in data.items():
            if value is None:
                continue
            elif hasattr(value, "value"):
                int_value = value.value
            else:
                int_value = int(value)
            params.extend([address, int_value])
        if not params:
            return

        if params:
            bytes_remaining = len(params)
            total_parts = (
                bytes_remaining + constants.PART_SIZE_BYTES - 1
            ) // constants.PART_SIZE_BYTES
            for part in range(1, total_parts + 1):
                size = (
                    bytes_remaining
                    if bytes_remaining <= constants.PART_SIZE_BYTES
                    else constants.PART_SIZE_BYTES
                )
                bytes_remaining -= constants.PART_SIZE_BYTES

                payload = (
                    [0xF0]
                    + [
                        constants.MIDI_MFR_ID_0,
                        constants.MIDI_MFR_ID_1,
                        constants.MIDI_MFR_ID_2,
                    ]
                    + [
                        constants.SysexCommands.BULK_XFER,
                        0x00,
                        sysex_tag,
                        part,
                        total_parts,
                        size,
                    ]
                    + params[:size]
                    + [0xF7]
                )
                params = params[size:]

                MftSysexApi._send_sysex(midi_out, payload)

    @staticmethod
    def get_device_config(
        midi_out: MidiOutput,
        midi_in: MidiInput,
        timeout: float = 1.0,
    ) -> Dict[int, int] | None:
        request = [
            0xF0,
            constants.MIDI_MFR_ID_0,
            constants.MIDI_MFR_ID_1,
            constants.MIDI_MFR_ID_2,
            constants.SysexCommands.PULL_CONF,
            0x00,
            0xF7,
        ]
        MftSysexApi._send_sysex(midi_out, request)

        config_values = {}
        end = time.time() + timeout

        # Loop to receive sysex messages until timeout
        while time.time() < end:
            remaining_time = end - time.time()
            if remaining_time <= 0:
                break

            response = MftSysexApi._receive_sysex(
                midi_in, constants.SysexCommands.PULL_CONF, remaining_time
            )

            if response:
                # The payload is a sequence of address-value pairs
                for i in range(6, len(response) - 1, 2):
                    addr = response[i]
                    val = response[i + 1]
                    config_values[addr] = val

        if not config_values:
            raise RuntimeError("Failed to receive device configuration")

        # Build address-to-name map from dataclass metadata
        addr_to_name = {
            f.metadata["addr"]: f.name
            for f in fields(DeviceConfig)
            if "addr" in f.metadata
        }

        # Verify that all configuration values have been received
        if len(config_values) < len(addr_to_name):
            unseen_addrs = set(addr_to_name) - set(config_values.keys())
            unseen_names = [addr_to_name[addr] for addr in unseen_addrs]
            raise RuntimeError(f"Missing config values: {unseen_names}")

        return config_values

    @staticmethod
    def get_encoder_config(
        midi_out: MidiOutput,
        midi_in: MidiInput,
        encoder_index: int,
        timeout: float = 1.0,
    ) -> Dict[int, int]:
        sysex_tag = encoder_index + 1
        request = [
            0xF0,
            constants.MIDI_MFR_ID_0,
            constants.MIDI_MFR_ID_1,
            constants.MIDI_MFR_ID_2,
            constants.SysexCommands.BULK_XFER,
            0x01,
            sysex_tag,
            0xF7,
        ]
        MftSysexApi._send_sysex(midi_out, request)
        responses: dict[int, int] = {}
        while True:
            data = MftSysexApi._receive_sysex(
                midi_in, constants.SysexCommands.BULK_XFER, timeout
            )
            if not data:
                break
            if data[6] != sysex_tag:
                continue
            part = data[7]
            total = data[8]
            size = data[9]
            for i in range(0, size - 1, 2):
                addr = data[10 + i]
                val = data[11 + i]
                responses[addr] = val
            if part == total:
                break
        if not responses:
            raise RuntimeError(
                f"Failed to receive encoder config for encoder {encoder_index}"
            )

        return responses

    @staticmethod
    def set_encoder_value(
        midi_out: MidiOutput,
        encoder_index: int,
        value: int,
        channel: int = constants.MidiChannel.ROTARY_ENCODER,
    ) -> None:

        if not 0 <= channel <= 15:
            raise ValueError("channel must be in range 0-15")

        if not 0 <= encoder_index < constants.Encoders.DEVICE_KNOB_MAX:
            raise ValueError("encoder_index must be in range 0-63")

        if not 0 <= value <= 127:
            raise ValueError("value must be in range 0-127")

        status = 0xB0 | (channel & 0x0F)
        message = [status, encoder_index, value]
        MftSysexApi._send_midi(midi_out, message)

    @staticmethod
    def set_encoder_animation_and_brightness(
        midi_out: MidiOutput,
        encoder_index: int,
        value: int,
        channel: int = constants.MidiChannel.ANIMATIONS_AND_BRIGHTNESS,
    ) -> None:
        status = 0xB0 | (channel & 0x0F)
        message = [status, encoder_index, value]
        MftSysexApi._send_midi(midi_out, message)

    @staticmethod
    def get_encoder_value(
        midi_out: MidiOutput,
        midi_in: MidiInput,
        encoder_index: int,
        channel: int = constants.MidiChannel.ROTARY_ENCODER,
        timeout: float = 1.0,
    ) -> Optional[int]:
        if not 0 <= channel <= 15:
            raise ValueError("channel must be in range 0-15")

        if not 0 <= encoder_index < constants.Encoders.DEVICE_KNOB_MAX:
            raise ValueError("encoder_index must be in range 0-63")

        MftSysexApi.set_encoder_value(
            midi_out, encoder_index, constants.MidiChannel.ROTARY_ENCODER
        )
        return MftSysexApi._receive_cc(midi_in, channel, encoder_index, timeout)

    # Private helper functions -------------------------------------------------
    @staticmethod
    def _send_sysex(midi_out: MidiOutput, data: Iterable[int]) -> None:
        try:
            int_data = []
            for item in data:
                if hasattr(item, "value"):
                    int_data.append(item.value)
                else:
                    int_data.append(int(item))
            midi_out.send_message(int_data)
        except Exception as exc:
            print(f"Error sending SysEx message: {exc}")

    @staticmethod
    def _send_midi(midi_out: MidiOutput, message: Iterable[int]) -> None:
        try:
            midi_out.send_message(list(message))
        except Exception as exc:
            print(f"Error sending MIDI message: {exc}")

    @staticmethod
    def _receive_sysex(
        midi_in: MidiInput,
        command: int,
        timeout: float,
    ) -> Optional[list[int]]:
        end = time.time() + timeout
        while time.time() < end:
            msg = midi_in.get_message()
            if msg:
                data = msg[0]
                if (
                    len(data) > 5
                    and data[0] == 0xF0
                    and data[1] == constants.MIDI_MFR_ID_0
                    and data[2] == constants.MIDI_MFR_ID_1
                    and data[3] == constants.MIDI_MFR_ID_2
                    and data[4] == command
                ):
                    return list(data)
            time.sleep(0.01)
        return None

    @staticmethod
    def _receive_cc(
        midi_in: MidiInput,
        channel: int,
        cc: int,
        timeout: float,
    ) -> Optional[int]:
        end = time.time() + timeout
        status = 0xB0 + channel
        while time.time() < end:
            msg = midi_in.get_message()
            if msg:
                data = msg[0]
                if (
                    len(data) == 3
                    and (data[0] & 0xF) == channel
                    and data[0] == status
                    and data[1] == cc
                ):
                    return data[2]
            time.sleep(0.01)
        return None
