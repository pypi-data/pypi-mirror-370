import sys
from typing import Optional, Dict, Any

from ..tests import mock_id31

# This must be done early:
# Patch modules to allow from id31 import attenuator
sys.modules["id31"] = mock_id31


from ._id31_utils import ensure_difflab6_id31_flats  # noqa: E402
from ._streamline_utils import DemoStreamlineScannerMixIn  # noqa: E402
from ..id31.streamline_scanner import Id31StreamlineScanner  # noqa: E402
from ..tests.mock_id31.setup_globals import atten, ehss  # noqa: E402

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


class DemoStreamlineScanner(DemoStreamlineScannerMixIn, Id31StreamlineScanner):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ):
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("optimize_exposure_per", "sample")
        defaults.setdefault("default_attenuator", 4)
        defaults.setdefault("energy_name", "energy")

        super().__init__(config=config, defaults=defaults)

        self.newflat, self.oldflat = ensure_difflab6_id31_flats()


def mock_shopen(**kwargs):
    arguments = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    print(f"shopen({arguments})")


def att(value):
    setup_globals.atten.bits = value


if setup_globals is None:
    streamline_scanner = None
else:
    streamline_scanner = DemoStreamlineScanner()
    setup_globals.shopen = mock_shopen
    setup_globals.energy.position = 75
    setup_globals.atten = atten
    setup_globals.att = att
    setup_globals.ehss = ehss
