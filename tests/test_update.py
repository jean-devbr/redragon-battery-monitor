import pytest

from redragon_monitor.update.application.check_for_update import CheckForUpdateUseCase
from redragon_monitor.update.domain.update_status import UpdateStatus
from redragon_monitor.update.domain.version import Version
from redragon_monitor.update.infrastructure.github_stable_ref_source import GitHubStableRefSource
from redragon_monitor.update.infrastructure.terminal_update_launcher import TerminalUpdateLauncher

URL = "https://example.invalid/get.sh"


class StaticSource:
    def __init__(self, result):
        self._result = result

    def latest_version(self):
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def test_version_parse_and_compare():
    assert Version.parse("v0.4.0") == Version(0, 4, 0)
    assert Version.parse("0.10.0") > Version.parse("0.9.9")
    assert str(Version(1, 2, 3)) == "1.2.3"


@pytest.mark.parametrize("text", ["", "1.2", "v1.2.x", "latest"])
def test_version_rejects_invalid(text):
    with pytest.raises(ValueError):
        Version.parse(text)


@pytest.mark.parametrize(
    "latest, expected",
    [(Version(0, 5, 0), UpdateStatus.AVAILABLE), (Version(0, 4, 0), UpdateStatus.UP_TO_DATE), (Version(0, 3, 0), UpdateStatus.UP_TO_DATE)],
)
def test_check_for_update_compares_versions(latest, expected):
    check = CheckForUpdateUseCase(StaticSource(latest), Version(0, 4, 0)).execute()
    assert check.status is expected and check.latest == latest


@pytest.mark.parametrize("error", [OSError("sem rede"), ValueError("formato")])
def test_check_for_update_failure_is_reported(error):
    check = CheckForUpdateUseCase(StaticSource(error), Version(0, 4, 0)).execute()
    assert check.status is UpdateStatus.FAILED and check.latest is None and not check.available


def test_source_reads_stable_ref_from_installer():
    script = '#!/usr/bin/env bash\nset -euo pipefail\n\nSTABLE_REF="v0.5.1"\n'
    source = GitHubStableRefSource(URL, fetch=lambda url, timeout: script)
    assert source.latest_version() == Version(0, 5, 1)


def test_source_without_stable_ref_fails():
    source = GitHubStableRefSource(URL, fetch=lambda url, timeout: "echo nada")
    with pytest.raises(ValueError):
        source.latest_version()


def test_launcher_opens_first_available_terminal():
    spawned = []
    launcher = TerminalUpdateLauncher(
        URL, which=lambda name: f"/usr/bin/{name}" if name == "gnome-terminal" else None, spawn=spawned.append
    )
    assert launcher.launch("pt")
    command = spawned[0]
    assert command[:4] == ["/usr/bin/gnome-terminal", "--", "bash", "-c"]
    assert f"curl -fsSL {URL} | REDRAGON_LANG=pt bash;" in command[4]
    assert "setsid -f" in command[4] and "Pressione Enter" in command[4]


def test_launcher_without_terminal_returns_false():
    launcher = TerminalUpdateLauncher(URL, which=lambda name: None, spawn=lambda cmd: None)
    assert not launcher.launch("en")
    assert launcher.manual_command() == f"curl -fsSL {URL} | bash"
