from __future__ import annotations

from typing import Any, Dict, Optional

from ewoksjob.client import submit
from ewoksutils.task_utils import task_inputs

from blissoda.persistent.parameters import ParameterInfo
from blissoda.utils.directories import (
    get_dataset_processed_dir,
    get_filename,
    workflow_destination,
)

from ..processor import BaseProcessor, Scan
from .cdi_plotter import CdiPlotter
from .cdi_uploader import CdiUploader


class CdiProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("counter", category="workflows"),
        ParameterInfo("upload_figures_to_logbook", category="ICAT"),
        ParameterInfo("retry_timeout", category="data access"),
        ParameterInfo("retry_period", category="data access"),
    ],
):

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        # https://gitlab.esrf.fr/bliss/blissoda/-/merge_requests/329#note_441492
        defaults = self._merge_defaults(deprecated_defaults, defaults)
        defaults.setdefault("counter", "mpx1x4_roi1")
        defaults.setdefault("upload_figures_to_logbook", False)
        defaults.setdefault("retry_timeout", 60)
        defaults.setdefault("retry_period", 1)
        super().__init__(config=config, defaults=defaults)
        # Needed for scan sequence
        self._set_parameter("trigger_at", "END")
        self._plotter = CdiPlotter(max_plots=10)
        self._uploader = CdiUploader()

    def _trigger_workflow_on_new_scan(self, scan: Scan) -> Optional[dict]:
        if not scan.scan_info.get("run_ewoks"):
            return
        workflow = {
            "graph": {"id": "cdi_plot"},
            "nodes": [
                {
                    "id": "cdi_plot_task",
                    "task_type": "class",
                    "task_identifier": "ewoksid01.tasks.cdi_plot.CdiPlot",
                }
            ],
        }

        future = submit(
            args=(workflow,),
            kwargs={
                "inputs": self._get_inputs(scan),
                "convert_destination": workflow_destination(scan),
            },
            queue="online",
        )

        self._plotter.handle_workflow_result(
            future,
            self._get_parameter("retry_timeout"),
            self._get_parameter("retry_period"),
        )

        if self._get_parameter("upload_figures_to_logbook"):
            self._uploader.upload_workflow_result(
                future,
                self._get_parameter("retry_timeout"),
                self._get_parameter("retry_period"),
            )

    def _get_inputs(self, sequence: Scan) -> list[dict[str, Any]]:

        scan_filename = get_filename(sequence)
        return task_inputs(
            inputs={
                "filename": scan_filename,
                "scan_nos": [scan.scan_info.get("scan_nb") for scan in sequence.scans],
                "axis_name": sequence.scan_info["axis_name"],
                "rc_axis_name": sequence.scan_info["rc_axis_name"],
                "counter": self._get_parameter("counter"),
                "output_folder": get_dataset_processed_dir(scan_filename),
                "retry_timeout": self._get_parameter("retry_timeout"),
                "retry_period": self._get_parameter("retry_period"),
            }
        )
