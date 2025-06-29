import time
from typing import Optional

from mftd import constants
from mftd.midi import create_midi_input, create_midi_output
from mftd.sysex.device import DeviceConfigOut, DeviceConfig, DeviceConfigIn
from mftd.sysex.encoder import EncoderConfig


class MidiFighterTwister:
    def __init__(self):
        self.midi_in = create_midi_input()
        self.midi_out = create_midi_output()

    def set_device_config(self, config: DeviceConfig):
        out_config = DeviceConfigOut.from_config(config)
        if self.midi_out:
            for sysex_msg in out_config.to_sysex():
                self.midi_out.send_message(sysex_msg)

    def get_device_config(self) -> Optional[DeviceConfig]:
        """
        Retrieves the device configuration from the Midi Fighter Twister.

        This method sends a SysEx request to the device and waits for a response.
        It will return a DeviceConfig object on success, or None if a timeout occurs.
        """
        if not self.midi_out or not self.midi_in:
            return None

        # Drain any unexpected messages from the input buffer.
        while self.midi_in.get_message():
            pass

        request_message = (
            0xF0,
            constants.MIDI_MFR_ID_0,
            constants.MIDI_MFR_ID_1,
            constants.MIDI_MFR_ID_2,
            constants.SysexCommands.PULL_CONF,
            0x00,
            0xF7,
        )
        self.midi_out.send_message(request_message)

        print("Sent config request. Waiting for response...")
        start_time = time.time()
        timeout_seconds = 2.0
        while time.time() - start_time < timeout_seconds:
            message_tuple = self.midi_in.get_message()
            if message_tuple and message_tuple[0]:
                message = message_tuple[0]
                # Print the received message for debugging purposes
                print(f"Received MIDI message: {[hex(b) for b in message]}")
                try:
                    config_in = DeviceConfigIn.from_sysex(message)
                    if config_in:
                        print("Successfully parsed config.")
                        return config_in.to_config()
                except ValueError as e:
                    # Print the exact error to see why parsing fails
                    print(f"Could not parse message: {e}")
                    # Continue to the next message
                    pass
            time.sleep(0.01)

        print("Timeout reached. No valid config received.")
        return None

    def set_encoder_config(self, index, config: EncoderConfig):
        pass
