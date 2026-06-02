from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import DOMAIN, LENS, PROFILE, ROOT, SURFACE, TIMPOS, VALUE


@pytest.fixture
def paths() -> dict[str, Path]:
    return {
        "root": ROOT,
        "domain": DOMAIN,
        "surface": SURFACE,
        "lens": LENS,
        "profile": PROFILE,
        "value": VALUE,
        "timpos": TIMPOS,
    }

