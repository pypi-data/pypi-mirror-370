from blissoda.demo.id22 import stscan_processor
from blissoda.demo.id22 import id22_xrpd_processor

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


def id22_stscan_demo(expo=0.2, npoints=10):
    stscan_processor.submit_workflows()


def id22_xrpd_demo(expo=0.2, npoints=10):
    id22_xrpd_processor.enable(setup_globals.difflab6)
    try:
        setup_globals.loopscan(
            npoints,
            expo,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
    finally:
        id22_xrpd_processor.disable()
