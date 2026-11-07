from redragon_monitor.services import autostart


def test_enable_disable_roundtrip(tmp_path):
    cfg = str(tmp_path)
    assert not autostart.is_enabled(cfg)
    path = autostart.enable("/opt/venv/bin/python -m redragon_monitor.main --minimized", cfg)
    assert path == tmp_path / "autostart" / "redragon-battery-monitor.desktop"
    text = path.read_text()
    assert "Exec=/opt/venv/bin/python -m redragon_monitor.main --minimized" in text
    assert "Type=Application" in text
    assert autostart.is_enabled(cfg)
    autostart.disable(cfg)
    assert not autostart.is_enabled(cfg)
    autostart.disable(cfg)


def test_default_exec_uses_current_python():
    import sys

    assert autostart.default_exec().startswith(sys.executable)
    assert autostart.default_exec().endswith("-m redragon_monitor.main --minimized")
