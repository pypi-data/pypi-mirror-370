from typing import Optional, Dict, Any

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None

from ..id32.processor import Id32SpecGenProcessor


class DemoId32Processor(Id32SpecGenProcessor):
    QUEUE = None

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        super().__init__(detectors=("difflab6",), config=config, defaults=defaults)


if setup_globals is None:
    id32_processor = None
else:
    id32_processor = DemoId32Processor()
