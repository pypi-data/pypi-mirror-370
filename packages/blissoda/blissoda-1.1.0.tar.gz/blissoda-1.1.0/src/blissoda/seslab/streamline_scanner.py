from typing import Any, Dict, Optional

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None

from streamline_changer.sample_changer import SampleChanger
from ..streamline.scanner import StreamlineScanner


class StreamlineSesScanner(StreamlineScanner):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ):
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("sample_changer_name", "streamline_sc")

        super().__init__(config=config, defaults=defaults)

    def measure_sample(self, *args, has_qrcode: bool = True, **kwargs):
        return None

    def _get_calibration(self):
        return {"non_empty": None}

    def _newsample(self, sample_name: str):
        print("NEW SAMPLE:", sample_name)


if setup_globals is None:
    streamline_sc = None
    streamline_scanner = None
else:
    try:
        streamline_sc = SampleChanger(
            setup_globals.streamline_translation, setup_globals.streamline_wago
        )
    except AttributeError:
        streamline_sc = None
    streamline_scanner = StreamlineSesScanner()
