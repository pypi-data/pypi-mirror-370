from blissoda.demo.id32 import id32_processor

try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


def id32_demo(expo=0.2, npoints=10):
    print("The workflow is expected to fail so this only tests the triggering.")
    id32_processor.enable()
    try:
        setup_globals.loopscan(npoints, expo, setup_globals.difflab6)
    finally:
        id32_processor.disable()
