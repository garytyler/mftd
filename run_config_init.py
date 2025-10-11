from mftd import (
    EncoderConfig,
    SideSwitchAction,
    MidiChannel,
    DeviceConfig,
    SysexBool,
    EncoderMovementType,
    EncoderSwitchActionType,
    EncoderMidiMessageType,
    Color,
    EncoderIndicatorDisplayType,
    MidiFighterTwister,
    EncoderAnimation,
    EncoderIndicatorBrightness,
    EncoderRgbBrightness,
)


class MftConfigInitializer:
    def __init__(self, mft: MidiFighterTwister = None):
        self._mft = mft
        self._device = self.getDeviceConfig()
        self._encoders = self.getEncoderConfigs()

    def configureDevice(self):
        self._setDeviceAndEncoderConfigs(self._device, self._encoders)
        self._setEncoderAnimationAndBrightnessConfigs()
        self._mft.set_encoder_rgb_brightness(14, EncoderRgbBrightness.LOW)
        self._mft.set_encoder_rgb_brightness(15, EncoderRgbBrightness.LOW)

    def _setDeviceAndEncoderConfigs(self, device, encoders):
        for config in self._encoders:
            self._mft.set_encoder_config(config.encoder_midi_number, config)
        self._mft.set_device_config(self._device)

    def _setEncoderAnimationAndBrightnessConfigs(self):
        for encoder in self._encoders:
            self._mft.set_encoder_rgb_brightness(
                encoder.encoder_midi_number, EncoderRgbBrightness.MID
            )
            self._mft.set_encoder_indicator_brightness(
                encoder.encoder_midi_number, EncoderIndicatorBrightness.OFF
            )
            self._mft.set_encoder_animation(
                encoder.encoder_midi_number, EncoderAnimation.NONE
            )

    @staticmethod
    def getDeviceConfig():
        return DeviceConfig(
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

    def getEncoderConfigs(self):
        encoders = []

        def _setupEncoderConfig(
            index: int,
            relative: bool,
            inactive_color: Color,
        ):
            encoders[index].detent = SysexBool.TRUE if relative else SysexBool.FALSE
            encoders[index].encoder_midi_type = (
                EncoderMidiMessageType.SEND_RELATIVE
                if relative
                else EncoderMidiMessageType.SEND_CC
            )
            encoders[index].inactive_color = inactive_color

        for n in range(16):
            encoders.append(
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
            )

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
        _setupEncoderConfig(10, True, Color.BLACK)
        _setupEncoderConfig(11, True, Color.BLACK)
        _setupEncoderConfig(14, True, Color.WHITE)
        _setupEncoderConfig(15, True, Color.WHITE)

        return encoders
