from pprint import pprint

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None

from ..id14.converter import Id14Hdf5ToSpecConverter


class DemoId14Hdf5ToSpecConverter(Id14Hdf5ToSpecConverter):
    def on_new_scan_metadata(self, scan) -> None:
        kwargs = self.get_submit_arguments(scan)
        print("Workflow", self.workflow)
        print(" -> arguments")
        pprint(kwargs)


if setup_globals is None:
    id14_converter = None
else:
    id14_converter = DemoId14Hdf5ToSpecConverter()
