from blissoda.demo.id12 import id12_converter

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


def id12_demo(expo=0.2, npoints=10):
    id12_converter.enable()
    try:
        setup_globals.loopscan(
            npoints,
            expo,
            setup_globals.diode1,
            setup_globals.diode2,
            setup_globals.mca1,
        )
    finally:
        id12_converter.disable()
