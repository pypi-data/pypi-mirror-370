import logging
import gevent.lock
from functools import wraps
from typing import Type, Callable


try:
    from bliss.common.plot import get_flint
except ImportError:
    get_flint = None

try:  # bliss < 2.2
    from bliss.flint.client.proxy import FlintClient
    from bliss.flint.client.plots import BasePlot
except ImportError:
    try:
        from flint.client.proxy import FlintClient
        from flint.client.plots import BasePlot
    except ImportError:
        FlintClient = None
        BasePlot = object


logger = logging.getLogger(__name__)


class WithFlintAccess:
    def __init__(self) -> None:
        self._client = None
        self._clientlock = gevent.lock.RLock()
        self._plots = dict()

    def _get_plot(self, plot_id: str, plot_cls: Type[BasePlot]) -> BasePlot:
        """Launches Flint and creates the plot when either is missing"""
        plot = self._plots.get(plot_id)
        if plot is None:
            plot = self._flint_client.get_plot(plot_cls, unique_name=plot_id)
            self._plots["plot_id"] = plot
        return plot

    @property
    def _flint_client(self) -> FlintClient:
        """Launches Flint when missing"""
        with self._clientlock:
            try:
                if self._client.is_available():
                    return self._client
            except (FileNotFoundError, AttributeError):
                pass
            self._client = get_flint()
            self._plots = dict()
            return self._client


def capture_errors(method) -> Callable:
    @wraps(method)
    def wrapper(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as e:
            msg = f"Flint plot error: {e}"
            logger.error(msg, exc_info=True)

    return wrapper
