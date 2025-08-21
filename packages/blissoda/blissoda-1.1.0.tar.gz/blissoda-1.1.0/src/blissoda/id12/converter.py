"""User API for HDF5 conversion on the Bliss repl"""

import os
import re
from typing import List, Optional, Dict, Any

from ewoksjob.client import submit

try:
    from bliss import current_session
except ImportError:
    current_session = None

from ..processor import Scan
from ..processor import BaseProcessor
from ..resources import resource_filename
from ..persistent.parameters import ParameterInfo


class Id12Hdf5ToAsciiConverter(
    BaseProcessor,
    parameters=[
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("external_proposal_outdir", category="parameters"),
        ParameterInfo("inhouse_proposal_outdir", category="parameters"),
        ParameterInfo("counters", category="parameters"),
        ParameterInfo("test_proposal_outdir", category="parameters"),
        ParameterInfo("retry_timeout", category="data access"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("trigger_at", "END")
        root_dir = "/data/id12/inhouse"
        defaults.setdefault(
            "external_proposal_outdir", os.path.join(root_dir, "EXTERNAL")
        )
        defaults.setdefault(
            "inhouse_proposal_outdir", os.path.join(root_dir, "INHOUSE2")
        )
        defaults.setdefault("counters", "all")
        defaults.setdefault("test_proposal_outdir", os.path.join(root_dir, "NOBACKUP"))
        defaults.setdefault("workflow", resource_filename("id12", "convert.json"))

        super().__init__(config=config, defaults=defaults)

    def on_new_scan_metadata(self, scan: Scan) -> None:
        if not self.scan_requires_processing(scan):
            return
        kwargs = self.get_submit_arguments(scan)
        _ = submit(args=(self.workflow,), kwargs=kwargs)

    def _trigger_workflow_on_new_scan(self, scan: Scan) -> None:
        self.on_new_scan_metadata(scan)

    def scan_requires_processing(self, scan: Scan) -> bool:
        return scan.scan_info["filename"] and scan.scan_info["save"]

    def get_submit_arguments(self, scan: Scan) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_inputs(self, scan: Scan) -> List[dict]:
        task_identifier = "Hdf5ToAscii"

        filename = scan.scan_info["filename"]
        output_dir = self.output_dir(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        has_subscan = len(scan.acq_chain.tree.children("root")) == 2

        return [
            {
                "task_identifier": task_identifier,
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "output_dir",
                "value": output_dir,
            },
            {
                "task_identifier": task_identifier,
                "name": "scan_numbers",
                "value": [scan_nb],
            },
            {
                "task_identifier": task_identifier,
                "name": "counters",
                "value": self.counters or "all",
            },
            {
                "task_identifier": task_identifier,
                "name": "has_subscan",
                "value": has_subscan,
            },
        ]

    def output_dir(self, scan: Scan) -> str:
        proposal = current_session.scan_saving.proposal.name

        # Proposal directory is upper case and "-" between letters and digits
        matches = re.findall(r"[A-Za-z]+|\d+", proposal.upper())
        proposal_dir = "-".join(matches)

        # Handle special cases
        proposal_dir = proposal_dir.replace("IH", "IH-")
        proposal_dir = re.sub(r"ID-(\d{2})(.+)", r"ID\1-\2", proposal_dir)

        # Select directory for the ASCII files
        if current_session.scan_saving.proposal_type == "inhouse":
            dirname = self.inhouse_proposal_outdir
        elif current_session.scan_saving.proposal_type == "tmp":
            dirname = self.test_proposal_outdir
        elif proposal_dir.startswith("IH") or proposal_dir.startswith("BLC"):
            dirname = self.inhouse_proposal_outdir
        else:
            dirname = self.external_proposal_outdir

        filename = scan.scan_info["filename"]
        collection_dataset = os.path.splitext(os.path.basename(filename))[0]
        return os.path.join(dirname, proposal_dir, collection_dataset)
