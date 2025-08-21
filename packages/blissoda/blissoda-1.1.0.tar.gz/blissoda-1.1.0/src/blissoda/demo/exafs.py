from typing import Dict, Any, Optional

try:
    from bliss import setup_globals
    from bliss.physics import units
except ImportError:
    units = None
    setup_globals = None

from ..exafs.processor import ExafsProcessor
from ..resources import resource_filename


class DemoExafsProcessor(ExafsProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("workflow", resource_filename("exafs", "exafs.ows"))
        defaults.setdefault("_scan_type", "any")
        counters = defaults.setdefault("_counters", dict())
        energy_unit = setup_globals.energy.unit or "eV"
        counters.setdefault(
            "any",
            {
                "mu_name": "mu",
                "energy_name": "energy",
                "energy_unit": energy_unit,
            },
        )

        super().__init__(config=config, defaults=defaults)

    def _scan_type_from_scan(self, scan) -> Optional[str]:
        return "any"

    def _multi_xas_scan(self, scan) -> bool:
        return False

    def _multi_xas_subscan_size(self, scan) -> int:
        return 0

    def run(self, expo=0.003):
        e0 = 8800  # eV
        e1 = 9600  # eV
        step_size = 0.5  # eV
        intervals = int((e1 - e0) / step_size) - 1

        from_unit = "eV"
        to_unit = self.counters["energy_unit"]

        if units:
            e0 = (e0 * units.ur(from_unit)).to(to_unit).magnitude
            e1 = (e1 * units.ur(from_unit)).to(to_unit).magnitude
        else:
            assert (
                from_unit == to_unit
            ), f"counters energy unit is '{to_unit}' instead of 'eV'"

        scan = setup_globals.ascan(
            setup_globals.energy, e0, e1, intervals, expo, setup_globals.mu, run=False
        )
        super().run(scan)


if setup_globals is None:
    exafs_processor = None
else:
    exafs_processor = DemoExafsProcessor()
    exafs_processor.refresh_period = 0.5
