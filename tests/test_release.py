import re
from pathlib import Path

from redragon_monitor import __version__

ROOT = Path(__file__).resolve().parent.parent


def test_get_sh_installs_current_version():
    m = re.search(r'^STABLE_REF="([^"]+)"', (ROOT / "get.sh").read_text(), re.M)
    assert m and m.group(1) == f"v{__version__}"


def test_readme_badge_shows_current_version():
    readme = (ROOT / "README.md").read_text()
    assert f"vers%C3%A3o-{__version__}-" in readme
    assert f"/tree/v{__version__})" in readme


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
