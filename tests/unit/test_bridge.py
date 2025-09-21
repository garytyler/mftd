from mftd.bridge import MidiOscBridge


def test_bridge_allows_custom_ports_and_fanout():
    bridge = MidiOscBridge(
        osc_target_port=1234,
        osc_listen_port=5678,
        encoder_fanout={7: [("192.0.2.1", 9999)]},
    )

    assert bridge.osc_target_port == 1234
    assert bridge.osc_listen_port == 5678
    assert bridge.encoder_fanout == {7: [("192.0.2.1", 9999)]}

    # Ensure the underlying forwarders see the custom ports.
    assert bridge.midi_to_osc._osc_port == 1234  # type: ignore[attr-defined]
    assert bridge.osc_to_midi._listen_port == 5678  # type: ignore[attr-defined]
    assert bridge.midi_to_osc._fanout_config == {  # type: ignore[attr-defined]
        7: [("192.0.2.1", 9999)]
    }
