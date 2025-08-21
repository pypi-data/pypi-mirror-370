from gevent import monkey

monkey.patch_all()

import logging  # noqa E402
from typing import Iterator, Tuple, Dict  # noqa E402

from blissdata.data.node import get_session_node  # noqa E402

logger = logging.getLogger(__name__)


def scan_iterator(session_name) -> Iterator[Tuple[str, int, Dict]]:
    session = get_session_node(session_name)
    logger.info(f"Started listening to Bliss session '{session_name}'")
    exclude_scan_types = ("scan", "scan_group")

    for ev in session.walk_on_new_events(
        exclude_children=exclude_scan_types, wait=True
    ):
        if ev.type == ev.type.NEW_NODE and ev.node.type == "scan":
            info = ev.node.info
            workflows = info.get("workflows")
            if not workflows:
                continue
            filename = info.get("filename")
            scan_nb = info.get("scan_nb")
            yield filename, scan_nb, workflows
