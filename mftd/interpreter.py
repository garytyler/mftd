from typing import List, Dict

from mftd import (
    DeviceConfig,
    SysexBool,
    SideSwitchAction,
    EncoderMovementType,
    MidiChannel,
    Color,
    EncoderConfig,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    EncoderIndicatorDisplayType,
    EncoderAnimation,
    EncoderIndicatorBrightness,
)


class MessageInterpreter:
    digits = "0123456789"
    MidiRoleToFunc = {
        "ld": "source",
        "lu": "scrub",
        "ru": "speed",
        "rd": "aux",
    }
    MidiFuncToRole = {v: k for k, v in MidiRoleToFunc.items()}

    def __init__(self):
        self.Device = DeviceConfig(
            system_midi_channel=MidiChannel.SYSTEM,
            bank_side_buttons=SysexBool.FALSE,
            left_button_1_function=SideSwitchAction.CC_HOLD,
            left_button_2_function=SideSwitchAction.CC_HOLD,
            left_button_3_function=SideSwitchAction.CC_HOLD,
            right_button_1_function=SideSwitchAction.CC_HOLD,
            right_button_2_function=SideSwitchAction.CC_HOLD,
            right_button_3_function=SideSwitchAction.CC_HOLD,
            super_knob_start=63,
            super_knob_end=127,
            rgb_led_brightness=100,
            indicator_global_brightness=115,
        )
        self.Encoders = [
            EncoderConfig(
                detent=SysexBool.FALSE,
                movement_type=EncoderMovementType.DIRECT_HIGH_RESOLUTION,
                switch_action_type=EncoderSwitchActionType.SHIFT_HOLD,
                switch_midi_channel=MidiChannel.SWITCH_AND_COLOR,
                switch_midi_number=n,
                switch_midi_type=EncoderMidiMessageType.SEND_CC,
                encoder_midi_channel=MidiChannel.ROTARY_ENCODER,
                encoder_midi_number=n,
                encoder_midi_type=EncoderMidiMessageType.SEND_CC,
                active_color=Color.WHITE,
                inactive_color=Color.BLACK,
                detent_color=10,
                indicator_display_type=EncoderIndicatorDisplayType.BLENDED_DOT,
                is_super_knob=SysexBool.FALSE,
                encoder_shift_midi_channel=MidiChannel.SHIFT,
            )
            for n in range(0, 16)
        ]
        self.leftEncoders = [self.Encoders[i] for i in range(0, len(self.Encoders), 2)]
        self.rightEncoders = [self.Encoders[i] for i in range(1, len(self.Encoders), 2)]

        # Target 3
        self.Encoders[0].detent = SysexBool.TRUE
        self.Encoders[0].inactive_color = Color.WHITE
        self.Encoders[1].inactive_color = Color.WHITE

        self.setupEncoderConfigs()

        self.EncoderRenames = self.getEncoderChannelRenameMaps()
        self.SideButtonRenames = self.getSideButtonChannelRenameMaps()
        self.Renames = self.EncoderRenames + self.SideButtonRenames
        self.RenamesByCc = {i["cc"]: i for i in self.Renames}
        self.RenamesByLoc = {i["loc"]: i for i in self.Renames}
        self.RenamesByRole = {i["role"]: i for i in self.Renames}

        self.EncoderRoles = set(i["role"] for i in self.EncoderRenames)
        self.SideButtonRoles = set(i["role"] for i in self.SideButtonRenames)

        self.DisabledEncoderRoles = set()
        self.DisabledEncoderIndexes = set()

        self.EnabledEncoderRoles = (
            self.EncoderRoles | self.SideButtonRoles
        ) - self.DisabledEncoderRoles

        self.MidiMetaDataByIndexMode = {}
        self.MidiMetaDataByIndexChannel = {}
        for rename in self.EncoderRenames:
            data = rename
            config = self.Encoders[rename["index"]]
            data["config"] = config
            data["side"] = "l" if not (int(config.encoder_midi_number) % 2) else "r"
            byIndexMode = self.MidiMetaDataByIndexMode.setdefault(rename["index"], {})
            mode = data["role"][::-1]
            byIndexMode[mode] = data
            byIndexChannel = self.MidiMetaDataByIndexChannel.setdefault(
                rename["index"], {}
            )
            channel = (
                int(
                    MidiChannel.ROTARY_ENCODER
                    if data["role"].endswith("u")
                    else (
                        MidiChannel.SHIFT
                        if data["role"].endswith("d")
                        else MidiChannel.SWITCH_AND_COLOR
                    )
                )
                + 1
            )
            byIndexChannel[channel] = data

    def setupEncoderConfigs(self):
        def _setupEncoderConfig(index: int, relative: bool, inactive_color: Color):
            self.Encoders[index].detent = (
                SysexBool.TRUE if relative else SysexBool.FALSE
            )
            self.Encoders[index].encoder_midi_type = (
                EncoderMidiMessageType.SEND_RELATIVE
                if relative
                else EncoderMidiMessageType.SEND_CC
            )
            self.Encoders[index].inactive_color = inactive_color

        # Target 1
        # Red
        _setupEncoderConfig(0, True, Color.RED)
        _setupEncoderConfig(4, False, Color.RED)
        # Blue
        _setupEncoderConfig(8, True, Color.BLUE)
        _setupEncoderConfig(12, False, Color.BLUE)

        # Target 2
        # Red
        _setupEncoderConfig(1, True, Color.RED)
        _setupEncoderConfig(5, False, Color.RED)
        # Blue
        _setupEncoderConfig(9, True, Color.BLUE)
        _setupEncoderConfig(13, False, Color.BLUE)

        # Target 3
        _setupEncoderConfig(2, True, Color.WHITE)
        _setupEncoderConfig(6, False, Color.WHITE)

        # Target 4
        _setupEncoderConfig(3, True, Color.WHITE)
        _setupEncoderConfig(7, False, Color.WHITE)

        # Scene
        _setupEncoderConfig(10, False, Color.BLACK)
        _setupEncoderConfig(14, False, Color.BLACK)
        _setupEncoderConfig(11, False, Color.BLACK)
        _setupEncoderConfig(15, False, Color.BLACK)

    def initEncoderAnimationAndBrightness(self):
        for encoder in self.Encoders:
            self.Mft.set_encoder_rgb_brightness(
                encoder.encoder_midi_number, EncoderAnimation.NONE
            )
            self.Mft.set_encoder_indicator_brightness(
                encoder.encoder_midi_number, EncoderIndicatorBrightness.OFF
            )
            self.Mft.set_encoder_animation(
                encoder.encoder_midi_number, EncoderAnimation.NONE
            )

    @classmethod
    def getEncoderChannelRenameMaps(cls):
        print("*********************************")
        # Handle Encoders:
        target_role_nums = [
            ["1r1", "2r1", "3rgb1", "4rgb1"],
            ["1r2", "2r2", "3rgb2", "4rgb2"],
            ["1b1", "2b1", "", ""],
            ["1b2", "2b2", "", ""],
        ]

        result = []
        for chan, mode in [
            (1, "u"),
            (2, "b"),
            (5, "d"),
        ]:
            for colIndex in range(4):
                for rowIndex in range(4):
                    ctrlIndexBaseZero = (rowIndex * 4) + colIndex
                    ctrlIndexBaseOne = ctrlIndexBaseZero + 1
                    targetRoleNum = target_role_nums[rowIndex][colIndex]
                    roleNum = targetRoleNum[len(targetRoleNum.rstrip(cls.digits)) :]
                    target = targetRoleNum[: len(targetRoleNum.rstrip(cls.digits))]
                    col = colIndex + 1
                    row = rowIndex + 1
                    side = "l" if roleNum == "1" else "r"

                    if not target:
                        continue
                    renameMap = {
                        "index": ctrlIndexBaseOne,
                        "target": target,
                        "cc": f"ch{chan}ctrl{ctrlIndexBaseOne}",
                        "loc": f"row{row}col{col}{mode}",
                        "role": f"{target}_{side}{mode}",
                    }
                    result.append(renameMap)

        return result

    @classmethod
    def getSideButtonChannelRenameMaps(cls) -> List[Dict[str, str]]:
        result = []
        # Handle side buttons
        for cc, loc, role in [
            ("ch4ctrl9", "side1", "slt"),
            ("ch4ctrl10", "side2", "slm"),
            ("ch4ctrl11", "side3", "slb"),
            ("ch4ctrl12", "side4", "srt"),
            ("ch4ctrl13", "side5", "srm"),
            ("ch4ctrl14", "side6", "srb"),
        ]:
            result.append({"cc": cc, "loc": loc, "role": role})
        return result
