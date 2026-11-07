import re
import urllib.request
from typing import Callable, Optional

from redragon_monitor.update.domain.version import Version

STABLE_REF = re.compile(r'^STABLE_REF="([^"]+)"', re.M)
TIMEOUT_S = 5
USER_AGENT = "redragon-battery-monitor"

Fetch = Callable[[str, float], str]


def _http_get(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


class GitHubStableRefSource:
    def __init__(self, installer_url: str, fetch: Optional[Fetch] = None, timeout: float = TIMEOUT_S):
        self._installer_url = installer_url
        self._fetch = fetch or _http_get
        self._timeout = timeout

    def latest_version(self) -> Version:
        match = STABLE_REF.search(self._fetch(self._installer_url, self._timeout))
        if match is None:
            raise ValueError("STABLE_REF não encontrado no instalador publicado")
        return Version.parse(match.group(1))
