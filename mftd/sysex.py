# Thin stateless API for interacting with the Midi Fighter Twister via SysEx
# and basic MIDI commands.
from __future__ import annotations

import time
from typing import Iterable, Optional, List

from . import constants
from .device import DeviceConfig
from .encoder import EncoderConfig
from .protocol import MidiOutput, MidiInput


class MftSysexApi:
    """Stateless helper for sending and receiving SysEx messages."""

    @staticmethod
    def set_device_config(
        midi_out: MidiOutput,
        config: DeviceConfig,
    ) -> None:
        """Send the full :class:`DeviceConfig` to the device."""
        print("Sending device configuration to the MIDI Fighter Twister...")
        print(config)

        def _int(value: int) -> int:
            if hasattr(value, "value"):
                return int(value.value)
            return int(value)

        pairs: list[int] = []

        for addr in config.ADDRESSES_TO_NAMES:
            val = config[addr]
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
    def get_device_config(
        midi_out: MidiOutput,
        midi_in: MidiInput,
        timeout: float = 1.0,
    ) -> DeviceConfig | None:
        """Request and return the current :class:`DeviceConfig`."""
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
        response = MftSysexApi._receive_sysex(
            midi_in, constants.SysexCommands.PULL_CONF, timeout
        )
        if not response:
            raise RuntimeError("Failed to receive device configuration")
        end = time.time() + timeout
        config = DeviceConfig()
        received = set()
        unseen = set(config.keys())
        for i in range(6, len(response) - 1, 2):
            addr = response[i]
            val = response[i + 1]
            config[addr] = val
            unseen.remove(addr)
            received.add(addr)
        if unseen:
            unseen_names = [config.ADDRESSES_TO_NAMES[addr] for addr in unseen]
            raise RuntimeError(f"Missing config values: {unseen_names}")

        while time.time() < end and len(received) < len(config.keys()):
            remaining = end - time.time()
            response = MftSysexApi._receive_sysex(
                midi_in, constants.SysexCommands.PULL_CONF, remaining
            )
            if not response:
                break
            for i in range(6, len(response) - 1, 2):
                addr = response[i]
                val = response[i + 1]
                config[addr] = val
                received.add(addr)

        return config

    @staticmethod
    def set_encoder_config(
        midi_out: MidiOutput,
        encoder_index: int,
        config: EncoderConfig,
    ) -> None:
        """Send an `EncoderConfig` for a specific encoder."""

        sysex_tag = encoder_index + 1
        params: List[int] = []
        defaults = EncoderConfig()
        for name, address in config.NAMES_TO_ADDRESSES.items():
            value = config[name]
            if value is None:
                continue
            if getattr(defaults, name) == value:
                continue
            if hasattr(value, "value"):
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

        # bytes_remaining = len(params)
        # total_parts = (
        #     bytes_remaining + constants.PART_SIZE_BYTES - 1
        # ) // constants.PART_SIZE_BYTES
        # sysex_tag = encoder_index + 1
        # part = 1
        # while params:
        #     size = min(len(params), constants.PART_SIZE_BYTES)
        #     payload = (
        #         [
        #             0xF0,
        #             constants.MIDI_MFR_ID_0,
        #             constants.MIDI_MFR_ID_1,
        #             constants.MIDI_MFR_ID_2,
        #             constants.SysexCommands.BULK_XFER,
        #             0x00,
        #             sysex_tag,
        #             part,
        #             total_parts,
        #             size,
        #         ]
        #         + params[:size]
        #         + [0xF7]
        #     )
        #     params = params[size:]
        #     MftSysexApi._send_sysex(midi_out, payload)
        #     part += 1

    @staticmethod
    def get_encoder_config(
        midi_out: MidiOutput,
        midi_in: MidiInput,
        encoder_index: int,
        timeout: float = 1.0,
    ) -> EncoderConfig:
        """Request and return the :class:`EncoderConfig` for an encoder."""
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
        cfg = EncoderConfig()
        for name, address in cfg.NAMES_TO_ADDRESSES.items():
            if address in responses:
                setattr(cfg, name, responses[address])
        return cfg

    @staticmethod
    def set_encoder_value(
        midi_out: MidiOutput,
        encoder_index: int,
        value: int,
        channel: int = constants.MidiChannel.ROTARY_ENCODER,
    ) -> None:
        """Send a control change with the specified value."""
        message = [0xB0 + channel, encoder_index, value]
        MftSysexApi._send_midi(midi_out, message)

    # Backwards compatibility -------------------------------------------------
    send_encoder_value = set_encoder_value

    # Private helper functions -------------------------------------------------
    @staticmethod
    def _send_sysex(midi_out: MidiOutput, data: Iterable[int]) -> None:
        try:
            # Ensure all data is converted to integers
            int_data = []
            print("Before prepping SysEx message items:", data)
            for item in data:
                print("Processing item:", item)
                if hasattr(item, "value"):
                    print("Item has value attribute:", item)
                    # Handle enum types
                    int_data.append(item.value)

                else:
                    # Handle regular ints and booleans
                    int_data.append(int(item))
            print("Sending SysEx message:", int_data)
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
