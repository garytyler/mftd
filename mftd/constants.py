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
    # The two LED groups share one animation/brightness value space and are
    # told apart by channel alone.  Verified against 2026 firmware: a ring
    # brightness value sent on channel 2 is silently ignored, while the same
    # value on channel 5 takes effect.  Both member names predate that check
    # and describe the wrong group; renaming them is a separate task.
    ANIMATIONS_AND_BRIGHTNESS = 2  # RGB (button) LED animations and brightness
    SYSTEM = 3  # For system messages (bank changes, side button actions)
    SHIFT = 4  # For shift encoder messages
    SWITCH_ANIMATION = 5  # LED ring (indicator) animations and brightness
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


class SystemMessage(IntEnum):
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
    # Banks 5-8 exist only on the 8-bank firmware image.  Their bank-change
    # CCs are documented; their side-button CCs are not — Appendix 1 of the
    # 2026 guide still covers banks 1-4 only, so they are deliberately absent.
    BANK5 = 4  # CC value for Bank 5
    BANK6 = 5  # CC value for Bank 6
    BANK7 = 6  # CC value for Bank 7
    BANK8 = 7  # CC value for Bank 8

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


class Color(IntEnum):
    """Colour bytes for the 2026 Expanded map.

    Only meaningful while the device is on ``ColorMap.EXPANDED``; under
    ``ColorMap.CLASSIC`` the same bytes select unrelated colours, which is why
    ``DeviceConfig.color_map`` defaults to ``EXPANDED``.

    Names follow one pattern, ``{BASE}_{LIGHT|FULL|DARK|DARKEST}``:

    * 14 hue families, every one carrying all four shades.
    * ``GREY_*``, which adds ``LIGHTEST`` -- the only place that fifth word
      appears -- plus ``BLACK`` and ``WHITE`` as endpoints.  Every ``GREY_``
      name has a ``GRAY_`` alias for the same byte.
    * ``S_*``, promoted from the palette's unstructured upper half.  **An
      ``S_`` name has only the shades listed here, never a guaranteed four**,
      and its suffix means position in that colour's own ramp rather than an
      absolute brightness.  Family ``_DARK`` peaks at channel 82-127, while
      ``S_OLIVE_DARK`` sits below that range at 63 and ``S_PERIWINKLE_DARK``
      above it at 233, near a family ``_FULL``.

    Removed in 0.4.0, all of which existed in 0.3.0 with Classic values and
    now raise ``AttributeError``:

    * Bare hues ``RED``, ``GREEN`` and ``BLUE``.  Deliberately not reused:
      the same name against the Expanded map returns a different colour, and
      a rename is louder than a silent change of meaning.
    * ``PRIMARY``, ``AUX`` and ``USER``, which were aliases of those hues.
    * ``DEFAULT_DETENT`` (byte 63), which is not a named member of this map.

    ``WHITE`` is the one name kept across the change, and its byte moved from
    127 to 3.  Code that stored the old byte reads back as a plain ``int``,
    since 127 is no longer a member.
    """

    # --- Neutrals -------------------------------------------------------
    BLACK = 0  # #000000
    GREY_DARKEST = 1  # #1E1E1E
    GREY_DARK = 71  # #202020
    GREY_FULL = 117  # #404040
    GREY_LIGHT = 118  # #757575
    GREY_LIGHTEST = 2  # #7F7F7F
    WHITE = 3  # #FFFFFF

    # US spellings, aliases of the members above rather than new colours.
    GRAY_DARKEST = GREY_DARKEST
    GRAY_DARK = GREY_DARK
    GRAY_FULL = GREY_FULL
    GRAY_LIGHT = GREY_LIGHT
    GRAY_LIGHTEST = GREY_LIGHTEST

    # --- Hue families: all four shades, always ---------------------------
    # red, hue 0 deg
    RED_LIGHT = 4  # #FF4C4C
    RED_FULL = 5  # #FF0000
    RED_DARK = 6  # #7F0000
    RED_DARKEST = 7  # #1E0000
    # orange, hue 20 deg
    ORANGE_LIGHT = 8  # #FFBD6C
    ORANGE_FULL = 9  # #FF5400
    ORANGE_DARK = 10  # #591D00
    ORANGE_DARKEST = 11  # #271B00
    # yellow, hue 60 deg
    YELLOW_LIGHT = 12  # #FFFF4C
    YELLOW_FULL = 13  # #FFFF00
    YELLOW_DARK = 14  # #595900
    YELLOW_DARKEST = 15  # #191900
    # lime, hue 100 deg
    LIME_LIGHT = 16  # #88FF4C
    LIME_FULL = 17  # #54FF00
    LIME_DARK = 18  # #1D5900
    LIME_DARKEST = 19  # #142B00
    # green, hue 120 deg
    GREEN_LIGHT = 20  # #4CFF4C
    GREEN_FULL = 21  # #00FF00
    GREEN_DARK = 22  # #007F00
    GREEN_DARKEST = 23  # #001E00
    # emerald, hue 126 deg
    EMERALD_LIGHT = 24  # #4CFF5E
    EMERALD_FULL = 25  # #00FF19
    EMERALD_DARK = 26  # #00590D
    EMERALD_DARKEST = 27  # #001902
    # jade, hue 133 deg
    JADE_LIGHT = 28  # #4CFF88
    JADE_FULL = 29  # #28F656
    JADE_DARK = 30  # #0B681F
    JADE_DARKEST = 31  # #002413
    # mint, hue 156 deg
    MINT_LIGHT = 32  # #4CFFB7
    MINT_FULL = 33  # #00FF99
    MINT_DARK = 34  # #005935
    MINT_DARKEST = 35  # #001912
    # azure, hue 200 deg
    AZURE_LIGHT = 36  # #4CC3FF
    AZURE_FULL = 37  # #00A9FF
    AZURE_DARK = 38  # #004152
    AZURE_DARKEST = 39  # #001019
    # cobalt, hue 220 deg
    COBALT_LIGHT = 40  # #4C88FF
    COBALT_FULL = 41  # #0055FF
    COBALT_DARK = 42  # #001D59
    COBALT_DARKEST = 43  # #000819
    # blue, hue 240 deg
    BLUE_LIGHT = 44  # #4C4CFF
    BLUE_FULL = 45  # #0000FF
    BLUE_DARK = 46  # #00007F
    BLUE_DARKEST = 47  # #00001E
    # violet, hue 260 deg
    VIOLET_LIGHT = 48  # #874CFF
    VIOLET_FULL = 49  # #5400FF
    VIOLET_DARK = 50  # #190064
    VIOLET_DARKEST = 51  # #0F0030
    # magenta, hue 300 deg
    MAGENTA_LIGHT = 52  # #FF4CFF
    MAGENTA_FULL = 53  # #FF00FF
    MAGENTA_DARK = 54  # #590059
    MAGENTA_DARKEST = 55  # #190019
    # rose, hue 340 deg
    ROSE_LIGHT = 56  # #FF4C87
    ROSE_FULL = 57  # #FF0054
    ROSE_DARK = 58  # #59001D
    ROSE_DARKEST = 59  # #220013

    # --- Selected from the palette's unstructured range ------------------
    # Partial ramps: an S_ name has only the shades listed here.
    S_TRUE_ORANGE = 96  # #FF7F00
    S_BROWN = 126  # #B35F00
    S_BROWN_DARK = 105  # #693C1C
    S_BROWN_DARKEST = 83  # #402100
    S_RUST = 61  # #993500
    S_GOLD = 109  # #FFE126
    S_GOLD_DARK = 97  # #B9B000
    S_CHARTREUSE = 74  # #AFED06
    S_CHARTREUSE_DARK = 111  # #67B50F
    S_OLIVE = 62  # #795100
    S_OLIVE_DARK = 125  # #3F3100
    S_MIDNIGHT_BLUE = 112  # #1E1E30
    S_PALE_CYAN = 119  # #E0FFFF
    S_PERIWINKLE = 115  # #9A99FF
    S_PERIWINKLE_DARK = 93  # #877FE9
    S_PURPLE = 94  # #D31DFF
    S_MAGENTA_ROSE = 82  # #B21A7D

    # --- Firmware factory bytes ------------------------------------------
    # What a factory device reports, kept so EncoderConfig's defaults still
    # describe one.  These are byte values, not colour choices.
    DEFAULT_ACTIVE = BLUE_FULL
    DEFAULT_INACTIVE = RED_FULL


class DetentColor(IntEnum):
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


class EncoderAnimation(IntEnum):
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
    RGB_BRIGHTNESS_LOW = 24
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


class EncoderRgbBrightness(IntEnum):
    """Convenience enum for RGB LED brightness levels."""

    OFF = EncoderAnimation.RGB_BRIGHTNESS_OFF
    LOW = EncoderAnimation.RGB_BRIGHTNESS_LOW
    MID = EncoderAnimation.RGB_BRIGHTNESS_MID
    MAX = EncoderAnimation.RGB_BRIGHTNESS_MAX


class EncoderIndicatorBrightness(IntEnum):
    """Convenience enum for indicator LED brightness levels."""

    OFF = EncoderAnimation.INDICATOR_BRIGHTNESS_OFF
    QUARTER = EncoderAnimation.INDICATOR_BRIGHTNESS_25
    MID = EncoderAnimation.INDICATOR_BRIGHTNESS_MID
    MAX = EncoderAnimation.INDICATOR_BRIGHTNESS_MAX


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
    """Encoder switch actions, numbered as the 2026 firmware orders them.

    ``ENC_RESET_VALUE_MAX`` was inserted at 5, shifting every later member up
    by one — notably ``SHIFT_HOLD``, which was 6.  Pre-2026 firmware numbers
    these differently and is not supported.
    """

    CC_HOLD = 0  # Switch sends a CC message
    CC_TOGGLE = 1  # Switch toggles CC
    NOTE_HOLD = 2  # Switch sends a Note On
    NOTE_TOGGLE = 3  # Switch toggles Note On/Off
    ENC_RESET_VALUE = 4  # Resets the encoder to 0, or 63 when detent is on
    ENC_RESET_VALUE_MAX = 5  # Resets the encoder to 127, or 63 when detent is on
    ENC_FINE_ADJUST = 6  # Encoder sensitivity reduced for fine adjustment
    SHIFT_HOLD = 7  # Encoder sends a secondary value
    SHIFT_TOGGLE = 8  # Switch toggles between primary/secondary values


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
    SPREAD = 3  # Indicator displays a blended bar that starts in the middle and spreads in both directions


class ColorMap(IntEnum):
    """Which palette RGB colour values are interpreted against (2026, addr 33).

    ``Color``'s members are Expanded values.  Under ``CLASSIC`` the same bytes
    select unrelated colours from the pre-2026 hue sweep, so every name in
    ``Color`` describes something other than what the hardware shows -- and
    does so silently, since the byte stays valid under either map.
    """

    CLASSIC = 0  # The pre-2026 hue sweep; Color's names do not apply
    EXPANDED = 1  # Launchpad-style palette; what Color's members assume


class SleepTimer(IntEnum):
    """How long the unit idles before sleeping (2026, addr 36)."""

    OFF = 0
    MIN_1 = 1
    MIN_3 = 2
    MIN_5 = 3
    MIN_10 = 4
    MIN_20 = 5
    MIN_30 = 6
    MIN_60 = 7


class SleepAnimation(IntEnum):
    """What the LEDs do once the sleep timer elapses (2026, addr 37)."""

    TURN_OFF = 0  # All LEDs off until a control is touched
    RAINBOW_WAVE = 1  # Diagonal colour wave across the RGB LEDs


class SysexCommand(IntEnum):
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
    """Side switch actions, numbered as the 2026 firmware orders them.

    The 2026 spec inserted the two shift-page toggles at 6-7 and ``BANK_SELECT``
    at 10, and extended the direct bank jumps from four to eight.  Everything
    after ``SHIFT_PAGE2`` therefore moved: ``CYCLE_BANK`` went from 0x0C to
    0x13, and 0x0C now selects Bank 2.
    """

    CC_HOLD = 0x00  # Sends a CC message
    CC_TOGGLE = 0x01  # Toggles CC
    NOTE_HOLD = 0x02  # Sends a Note On
    NOTE_TOGGLE = 0x03  # Toggles Note On/Off
    SHIFT_PAGE1 = 0x04  # Activates a secondary 'Shift' page
    SHIFT_PAGE2 = 0x05  # Activates a secondary 'Shift' page
    SHIFT_PAGE1_TOGGLE = 0x06  # Latches the 'Shift' page instead of holding it
    SHIFT_PAGE2_TOGGLE = 0x07  # Latches the 'Shift' page instead of holding it
    NEXT_BANK = 0x08  # Increments the bank selection
    PREV_BANK = 0x09  # Decrements the bank selection
    BANK_SELECT = 0x0A  # Hold, then press an encoder to choose a bank
    BANK1 = 0x0B  # Selects Bank 1
    BANK2 = 0x0C  # Selects Bank 2
    BANK3 = 0x0D  # Selects Bank 3
    BANK4 = 0x0E  # Selects Bank 4
    BANK5 = 0x0F  # Selects Bank 5 (8-bank firmware only)
    BANK6 = 0x10  # Selects Bank 6 (8-bank firmware only)
    BANK7 = 0x11  # Selects Bank 7 (8-bank firmware only)
    BANK8 = 0x12  # Selects Bank 8 (8-bank firmware only)
    CYCLE_BANK = 0x13  # Cycles through the banks


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
