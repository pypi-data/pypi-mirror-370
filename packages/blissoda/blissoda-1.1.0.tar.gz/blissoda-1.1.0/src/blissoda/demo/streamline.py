import os

from ._streamline_utils import DemoStreamlineScannerMixIn
from ..streamline.scanner import StreamlineScanner

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


class DemoStreamlineScanner(DemoStreamlineScannerMixIn, StreamlineScanner):
    def run(self, *args, **kwargs):
        if not os.path.exists(self.workflow):
            raise RuntimeError(
                "the workflow file no longer exists, execute 'init_workflow' again"
            )
        super().run(*args, **kwargs)


if setup_globals is None:
    streamline_scanner = None
else:
    streamline_scanner = DemoStreamlineScanner()
