import re
from pathlib import Path

from redragon_monitor import __version__

ROOT = Path(__file__).resolve().parent.parent


def test_get_sh_installs_current_version():
    m = re.search(r'^STABLE_REF="([^"]+)"', (ROOT / "get.sh").read_text(), re.M)
    assert m and m.group(1) == f"v{__version__}"


def test_readme_badges_show_current_version():
    portuguese = (ROOT / "README.md").read_text()
    english = (ROOT / "README.en.md").read_text()
    assert f"vers%C3%A3o-{__version__}-" in portuguese
    assert f"version-{__version__}-" in english
    assert f"/tree/v{__version__})" in portuguese and f"/tree/v{__version__})" in english


def test_readmes_link_to_each_other_and_screenshots_exist():
    portuguese = (ROOT / "README.md").read_text()
    english = (ROOT / "README.en.md").read_text()
    assert "(README.en.md)" in portuguese and "(README.md)" in english
    assert (ROOT / ".github/assets/screenshot-pt.png").is_file()
    assert (ROOT / ".github/assets/screenshot-en.png").is_file()


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
