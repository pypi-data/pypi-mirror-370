try:
    from bliss import setup_globals
except ImportError:
    setup_globals = None


def ensure_shutter_open():
    if setup_globals.ehss.state == setup_globals.ehss.state.CLOSED:
        setup_globals.shopen()
