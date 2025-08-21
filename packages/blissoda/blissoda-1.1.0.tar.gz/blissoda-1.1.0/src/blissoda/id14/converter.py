"""User API for HDF5 conversion on the Bliss repl"""

import os
from typing import List, Any, Dict, Optional

from ewoksjob.client import submit

try:
    from bliss import current_session
except ImportError:
    current_session = None

from ..processor import Scan
from ..utils import directories
from ..processor import BaseProcessor
from ..persistent.parameters import ParameterInfo


class Id14Hdf5ToSpecConverter(
    BaseProcessor,
    parameters=[
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("retry_timeout", category="data access"),
        ParameterInfo("queue", category="workflows", deprecated_names=["worker"]),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("queue", "celery")
        defaults.setdefault(
            "workflow", "/data/id14/inhouse/ewoks/resources/workflows/convert.json"
        )

        super().__init__(config=config, defaults=defaults)

    def on_new_scan_metadata(self, scan: Scan) -> None:
        if not self.scan_requires_processing(scan):
            return
        kwargs = self.get_submit_arguments(scan)
        _ = submit(args=(self.workflow,), kwargs=kwargs, queue=self.queue)

    def _trigger_workflow_on_new_scan(self, scan: Scan) -> None:
        self.on_new_scan_metadata(scan)

    def scan_requires_processing(self, scan: Scan) -> bool:
        # TODO: select scan that needs processing
        return True

    def get_submit_arguments(self, scan: Scan) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_inputs(self, scan: Scan) -> List[dict]:
        task_identifier = "Hdf5ToSpec"

        filename = self.get_filename(scan)
        output_filename = self.workflow_destination(scan)
        scan_nb = scan.scan_info.get("scan_nb")

        inputs = [
            {
                "task_identifier": task_identifier,
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "output_filename",
                "value": output_filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "scan_numbers",
                "value": [scan_nb],
            },
        ]

        # Scan metadata published in id14.McaAcq.McaAcq.save
        calibration = scan.scan_info.get("instrument", dict()).get("calibration")
        if calibration:
            mca_calibration = calibration["a"], calibration["b"], 0
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "mca_calibration",
                    "value": mca_calibration,
                }
            )

        return inputs

    def get_filename(self, scan: Scan) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def workflow_destination(self, scan: Scan) -> str:
        filename = self.get_filename(scan)
        root = directories.get_processed_dir(filename)
        stem = os.path.splitext(os.path.basename(filename))[0]
        basename = f"{stem}.mca"
        return os.path.join(root, basename)

    def enable_slurm(self):
        self.queue = "slurm"

    def disable_slurm(self):
        self.queue = "celery"
