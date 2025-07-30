from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

# General Constants
DEVICE_NAME: str = "Midi Fighter Twister"  # The name of the MIDI device
PART_SIZE_BYTES: int = 24  # Maximum size of a single SysEx message part (in bytes)

# DJTT MIDI Constants
MIDI_MFR_ID_0: int = 0x00
MIDI_MFR_ID_1: int = 0x01
MIDI_MFR_ID_2: int = 0x79


class MidiChannel(IntEnum):
    """
    MIDI channels used for different message types.
    Refer to the "Encoder Settings" section in the PDF.
    """

    ROTARY_ENCODER = 0  # For rotary encoder messages (knob twists)
    SWITCH_AND_COLOR = 1  # For encoder switch and color messages
    ANIMATIONS_AND_BRIGHTNESS = 2  # For encoder animations and brightness messages
    SYSTEM = 3  # For system messages (bank changes, side button actions)
    SHIFT = 4  # For shift encoder messages
    SWITCH_ANIMATION = 5  # For switch animation messages
    SEQUENCER = 7  # For sequencer messages


class EncoderControl(IntEnum):
    """
    Control Change (CC) values used for specific encoder actions.
    Refer to the "Encoder Settings" section in the PDF.
    """

    KNOB_DECREMENT_VERY_FAST = 61  # For very fast counter-clockwise knob rotation
    KNOB_DECREMENT_FAST = 62  # For fast counter-clockwise knob rotation
    KNOB_DECREMENT = 63  # For counter-clockwise knob rotation
    KNOB_INCREMENT = 65  # For clockwise knob rotation
    KNOB_INCREMENT_FAST = 66  # For fast clockwise knob rotation
    KNOB_INCREMENT_VERY_FAST = 67  # For very fast clockwise knob rotation


class SystemMessages(IntEnum):
    """
    Control Change (CC) values used for system messages.
    Refer to the "Virtual Bank Operation" section in the PDF.
    """

    BANK_OFF = 0  # Value sent to turn off a bank
    BANK_ON = 127  # Value sent to turn on a bank

    BANK1 = 0  # CC value for Bank 1
    BANK2 = 1  # CC value for Bank 2
    BANK3 = 2  # CC value for Bank 3
    BANK4 = 3  # CC value for Bank 4

    # CC values for side buttons in each bank
    BANK1_LEFT1 = 8
    BANK1_LEFT2 = 9
    BANK1_LEFT3 = 10
    BANK1_RIGHT1 = 11
    BANK1_RIGHT2 = 12
    BANK1_RIGHT3 = 13

    BANK2_LEFT1 = 14
    BANK2_LEFT2 = 15
    BANK2_LEFT3 = 16
    BANK2_RIGHT1 = 17
    BANK2_RIGHT2 = 18
    BANK2_RIGHT3 = 19

    BANK3_LEFT1 = 20
    BANK3_LEFT2 = 21
    BANK3_LEFT3 = 22
    BANK3_RIGHT1 = 23
    BANK3_RIGHT2 = 24
    BANK3_RIGHT3 = 25

    BANK4_LEFT1 = 26
    BANK4_LEFT2 = 27
    BANK4_LEFT3 = 28
    BANK4_RIGHT1 = 29
    BANK4_RIGHT2 = 30
    BANK4_RIGHT3 = 31


class ColorValue(IntEnum):
    """
    MIDI values for setting RGB colors on the encoders.
    Refer to the "Encoders Push Switches" section in the PDF.
    """

    DEFAULT_ACTIVE = 25  # Typically red
    DEFAULT_INACTIVE = 113  # Typically blue
    DEFAULT_DETENT = 63  # Default detent color, typically pink

    BLACK = 0
    BLUE = 1
    LIGHT_BLUE = 19
    LIGHT_GREEN = 40
    GREEN = 50
    YELLOW = 64
    RED = 85
    LIGHT_RED = 88
    WHITE = 127

    PRIMARY = BLUE  # Default color for primary channel
    AUX = RED  # Default color for aux channel
    USER = GREEN  # Default color for user-defined color


class DetentColorValue(IntEnum):
    """
    MIDI values for setting the detent color on the encoders.
    """

    RED = 0
    ORANGE = 1
    LIGHT_ORANGE = 2
    PINK = 5
    PURPLE = 10
    BLUE = 127

    DEFAULT = 63


class AnimationValues(IntEnum):
    """
    MIDI values for setting different animation effects for the encoders.
    Refer to the "Setting RGB / Indicator Segment Animation State" section.
    """

    NONE = 0  # No animation

    # RGB Strobe Animations
    RGB_TOGGLE_8_BEATS = 1  # Toggle RGB color every 8 beats
    RGB_TOGGLE_4_BEATS = 2  # Toggle RGB color every 4 beats
    RGB_TOGGLE_2_BEATS = 3  # Toggle RGB color every 2 beats
    RGB_TOGGLE_1_BEAT = 4  # Toggle RGB color every beat
    RGB_TOGGLE_HALF_BEAT = 5  # Toggle RGB color every half beat
    RGB_TOGGLE_QUARTER_BEAT = 6  # Toggle RGB color every quarter beat
    RGB_TOGGLE_EIGHTH_BEAT = 7  # Toggle RGB color every eighth beat
    RGB_TOGGLE_SIXTEENTH_BEAT = 8  # Toggle RGB color every sixteenth beat

    # RGB Pulse Animations
    RGB_PULSE_8_BEATS = 10  # Pulse RGB color every 8 beats
    RGB_PULSE_4_BEATS = 11  # Pulse RGB color every 4 beats
    RGB_PULSE_2_BEATS = 12  # Pulse RGB color every 2 beats
    RGB_PULSE_1_BEAT = 13  # Pulse RGB color every beat
    RGB_PULSE_HALF_BEAT = 14  # Pulse RGB color every half beat
    RGB_PULSE_QUARTER_BEAT = 15  # Pulse RGB color every quarter beat
    RGB_PULSE_EIGHTH_BEAT = 16  # Pulse RGB color every eighth beat

    # RGB Brightness Values
    RGB_BRIGHTNESS_OFF = 17  # Turn off RGB brightness
    RGB_BRIGHTNESS_MID = 32  # Set RGB brightness to mid level
    RGB_BRIGHTNESS_MAX = 47  # Set RGB brightness to maximum level

    # Indicator Strobe Animations
    INDICATOR_TOGGLE_8_BEATS = 49  # Toggle indicator LED every 8 beats
    INDICATOR_TOGGLE_4_BEATS = 50  # Toggle indicator LED every 4 beats
    INDICATOR_TOGGLE_2_BEATS = 51  # Toggle indicator LED every 2 beats
    INDICATOR_TOGGLE_1_BEAT = 52  # Toggle indicator LED every beat
    INDICATOR_TOGGLE_HALF_BEAT = 53  # Toggle indicator LED every half beat
    INDICATOR_TOGGLE_QUARTER_BEAT = 54  # Toggle indicator LED every quarter beat
    INDICATOR_TOGGLE_EIGHTH_BEAT = 55  # Toggle indicator LED every eighth beat
    INDICATOR_TOGGLE_SIXTEENTH_BEAT = 56  # Toggle indicator LED every sixteenth beat

    # Indicator Pulse Animations
    INDICATOR_PULSE_8_BEATS = 57  # Pulse indicator LED every 8 beats
    INDICATOR_PULSE_4_BEATS = 58  # Pulse indicator LED every 4 beats
    INDICATOR_PULSE_2_BEATS = 59  # Pulse indicator LED every 2 beats
    INDICATOR_PULSE_1_BEAT = 60  # Pulse indicator LED every beat
    INDICATOR_PULSE_HALF_BEAT = 61  # Pulse indicator LED every half beat
    INDICATOR_PULSE_QUARTER_BEAT = 62  # Pulse indicator LED every quarter beat
    INDICATOR_PULSE_EIGHTH_BEAT = 63  # Pulse indicator LED every eighth beat
    INDICATOR_PULSE_SIXTEENTH_BEAT = 64  # Pulse indicator LED every sixteenth beat

    # Indicator Brightness Values
    INDICATOR_BRIGHTNESS_OFF = 65  # Turn off indicator brightness
    INDICATOR_BRIGHTNESS_25 = 72  # Set indicator brightness to 25%
    INDICATOR_BRIGHTNESS_MID = 80  # Set indicator brightness to mid level
    INDICATOR_BRIGHTNESS_MAX = 95  # Set indicator brightness to maximum level

    # Rainbow Cycle Animation
    RAINBOW_CYCLE = 127  # Set RGB segment to a rainbow cycle animation


class RgbBrightnessValues(IntEnum):
    """Convenience enum for RGB LED brightness levels."""

    OFF = AnimationValues.RGB_BRIGHTNESS_OFF.value
    MID = AnimationValues.RGB_BRIGHTNESS_MID.value
    MAX = AnimationValues.RGB_BRIGHTNESS_MAX.value


class IndicatorBrightnessValues(IntEnum):
    """Convenience enum for indicator LED brightness levels."""

    OFF = AnimationValues.INDICATOR_BRIGHTNESS_OFF.value
    QUARTER = AnimationValues.INDICATOR_BRIGHTNESS_25.value
    MID = AnimationValues.INDICATOR_BRIGHTNESS_MID.value
    MAX = AnimationValues.INDICATOR_BRIGHTNESS_MAX.value


class EncoderControlType(IntEnum):
    """Encoder Control Type Constants (Not currently used in the firmware - for future use)"""

    ENCODER = 0  # Encoder sends MIDI messages
    SWITCH = 1  # Switch sends MIDI messages
    SHIFT = 2  # Reserved for future functionality


class EncoderMovementType(IntEnum):
    """Encoder Movement Type Constants. Refer to the "Encoder Settings" section in the PDF."""

    DIRECT_HIGH_RESOLUTION = 0  # The highest resolution movement available
    RESPONSIVE = 1  # Responsive movement
    VELOCITY_SENSITIVE = 2  # Velocity-sensitive movement


class EncoderSwitchActionType(IntEnum):
    """Encoder Switch Action Type Constants. Refer to the "Encoder Settings" section in the PDF."""

    CC_HOLD = 0  # Switch sends a CC message
    CC_TOGGLE = 1  # Switch toggles CC
    NOTE_HOLD = 2  # Switch sends a Note On
    NOTE_TOGGLE = 3  # Switch toggles Note On/Off
    ENC_RESET_VALUE = 4  # Switch resets the encoder value
    ENC_FINE_ADJUST = 5  # Encoder sensitivity reduced for fine adjustment
    SHIFT_HOLD = 6  # Encoder sends a secondary value
    SHIFT_TOGGLE = 7  # Switch toggles between primary/secondary values


class EncoderMidiMessageType(IntEnum):
    """Encoder Midi Message Type Constants. Refer to the "Encoder Settings" section in the PDF."""

    SEND_NOTE = 0x00  # Encoder sends Note On messages
    SEND_CC = 0x01  # Encoder sends Control Change messages
    SEND_RELATIVE = 0x02  # Encoder sends relative CC messages
    SEND_NOTE_OFF = 0x03  # Encoder sends Note Off messages
    SEND_SWITCH_VEL_CONTROL = 0x03  # Not currently used
    SEND_REL_ENC_MOUSE_EMU_DRAG = 0x04  # Not currently used
    SEND_REL_ENC_MOUSE_EMU_SCROLL = 0x05  # Not currently used


class EncoderIndicatorDisplayType(IntEnum):
    """Encoder Indicator Display Type Constants. Refer to the "Encoder Settings" section in the PDF."""

    DOT = 0  # Indicator displays a single LED
    BAR = 1  # Indicator displays a bar graph
    BLENDED_BAR = 2  # Indicator displays a blended bar graph
    BLENDED_DOT = 3  # Indicator displays a blended dot


class SysexCommands(IntEnum):
    """
    SysEx commands used for configuring the MFT.
    Refer to the "Encoder Settings" section in the PDF.
    """

    PUSH_CONF = 0x01  # Command to push configuration to the MFT
    PULL_CONF = 0x02  # Command to pull configuration from the MFT
    SYSTEM = 0x03  # Command for system-related SysEx messages
    BULK_XFER = 0x04  # Command for bulk transfer of encoder settings


class SysexBool(IntEnum):
    """
    Values used in SysEx messages.
    Refer to the "Encoder Settings" section in the PDF.
    """

    FALSE = 0x00  # Value for false
    TRUE = 0x01  # Value for true


class SideSwitchAction(IntEnum):
    """
    Actions for side switch buttons.
    Refer to the "Global Settings" section in the PDF.
    """

    CC_HOLD = 0x00  # Sends a CC message
    CC_TOGGLE = 0x01  # Toggles CC
    NOTE_HOLD = 0x02  # Sends a Note On
    NOTE_TOGGLE = 0x03  # Toggles Note On/Off
    SHIFT_PAGE1 = 0x04  # Activates a secondary 'Shift' page
    SHIFT_PAGE2 = 0x05  # Activates a secondary 'Shift' page
    NEXT_BANK = 0x06  # Increments the bank selection
    PREV_BANK = 0x07  # Decrements the bank selection
    BANK1 = 0x08  # Selects Bank 1
    BANK2 = 0x09  # Selects Bank 2
    BANK3 = 0x0A  # Selects Bank 3
    BANK4 = 0x0B  # Selects Bank 4
    CYCLE_BANK = 0x0C  # Cycles through the banks


@dataclass
class Encoders:
    """
    Encoder constants for the MFT device.
    Refer to the "Midi Fighter Twister Hardware" section in the PDF.
    """

    DEVICE_KNOB_PER_BANK: int = 16  # Number of encoders per bank
    DEVICE_KNOB_NUM: int = 64  # Total number of encoders
    DEVICE_KNOB_MAX: int = DEVICE_KNOB_NUM  # Maximum encoder index
    DEVICE_BANK_NUM: int = 4  # Number of banks

    @dataclass
    class Bank1:
        ENCODER_1: int = 0
        ENCODER_2: int = 1
        ENCODER_3: int = 2
        ENCODER_4: int = 3
        ENCODER_5: int = 4
        ENCODER_6: int = 5
        ENCODER_7: int = 6
        ENCODER_8: int = 7
        ENCODER_9: int = 8
        ENCODER_10: int = 9
        ENCODER_11: int = 10
        ENCODER_12: int = 11
        ENCODER_13: int = 12
        ENCODER_14: int = 13
        ENCODER_15: int = 14
        ENCODER_16: int = 15

    @dataclass
    class Bank2:
        ENCODER_1: int = 16
        ENCODER_2: int = 17
        ENCODER_3: int = 18
        ENCODER_4: int = 19
        ENCODER_5: int = 20
        ENCODER_6: int = 21
        ENCODER_7: int = 22
        ENCODER_8: int = 23
        ENCODER_9: int = 24
        ENCODER_10: int = 25
        ENCODER_11: int = 26
        ENCODER_12: int = 27
        ENCODER_13: int = 28
        ENCODER_14: int = 29
        ENCODER_15: int = 30
        ENCODER_16: int = 31

    @dataclass
    class Bank3:
        ENCODER_1: int = 32
        ENCODER_2: int = 33
        ENCODER_3: int = 34
        ENCODER_4: int = 35
        ENCODER_5: int = 36
        ENCODER_6: int = 37
        ENCODER_7: int = 38
        ENCODER_8: int = 39
        ENCODER_9: int = 40
        ENCODER_10: int = 41
        ENCODER_11: int = 42
        ENCODER_12: int = 43
        ENCODER_13: int = 44
        ENCODER_14: int = 45
        ENCODER_15: int = 46
        ENCODER_16: int = 47

    @dataclass
    class Bank4:
        ENCODER_1: int = 48
        ENCODER_2: int = 49
        ENCODER_3: int = 50
        ENCODER_4: int = 51
        ENCODER_5: int = 52
        ENCODER_6: int = 53
        ENCODER_7: int = 54
        ENCODER_8: int = 55
        ENCODER_9: int = 56
        ENCODER_10: int = 57
        ENCODER_11: int = 58
        ENCODER_12: int = 59
        ENCODER_13: int = 60
        ENCODER_14: int = 61
        ENCODER_15: int = 62
        ENCODER_16: int = 63
