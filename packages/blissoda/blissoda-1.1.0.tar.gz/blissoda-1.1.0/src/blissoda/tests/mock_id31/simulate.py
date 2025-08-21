import numpy

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from . import setup_globals
from . import mock_id31
from ...id31.optimize_exposure import optimize_exposure


def simulate(
    fmin: float = 1e4,
    fmax: float = 1e6,
    default_att_position: int = 2,
    desired_counts: float = 1e5,
    energy: float = 70,
    noise: bool = False,
    reduce_desired_deviation: bool = True,
    expose_with_integral_frames: bool = False,
    max_expo_time: float = 4,
    nframes_default: int = 3,
):
    setup_globals.sample.oyield = 1
    setup_globals.p3.noise = noise
    setup_globals.energy.position = energy

    lst = list()
    flux = numpy.linspace(fmin, fmax, 500)
    for fl in flux:
        setup_globals.source.rate = fl
        setup_globals.att(0)
        assert setup_globals.p3.rate == fl
        expo_time = optimize_exposure(
            setup_globals.p3,
            nframes_default=nframes_default,
            default_att_position=default_att_position,
            desired_counts=desired_counts,
            reduce_desired_deviation=reduce_desired_deviation,
            expose_with_integral_frames=expose_with_integral_frames,
        )
        if max_expo_time:
            expo_time = min(expo_time, max_expo_time)
        setup_globals.ct(expo_time, setup_globals.p3)
        lst.append(
            (setup_globals.p3.last_image.max(), expo_time, setup_globals.atten.bits)
        )
    max_intensity, expo_time, attenuator = zip(*lst)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))

    ax1.plot(flux, max_intensity)
    # ax1.set_xlabel("Pixel Value (Hz)")
    ax1.set_ylabel("Pixel value (counts)")

    xmin = flux[0]
    xmax = flux[0] + 0.85 * (flux[-1] - flux[0])
    ax1.hlines(desired_counts, xmin, xmax, linestyles="dotted")
    ax1.text(xmax, desired_counts, "target value", ha="left", va="center")

    ax2.plot(flux, expo_time)
    # ax2.set_xlabel("Pixel Value (Hz)")
    ax2.set_ylabel("Exposure time (s)")

    xmin = flux[0]
    xmax = flux[0] + 0.85 * (flux[-1] - flux[0])
    expo_default = nframes_default * 0.2
    ax2.hlines(expo_default, xmin, xmax, linestyles="dotted")
    ax2.text(xmax, expo_default, "default time", ha="left", va="center")

    ax3.plot(flux, attenuator)
    ax3.set_xlabel("Pixel Value (Hz)")
    ax3.set_ylabel("Attenuator position")

    xmin = flux[0]
    xmax = flux[0] + 0.85 * (flux[-1] - flux[0])
    ax3.hlines(default_att_position, xmin, xmax, linestyles="dotted")
    ax3.text(xmax, default_att_position, "start position", ha="left", va="center")

    fig.suptitle(
        f"{flux[0]:.0e} Hz - {flux[-1]:.0e} Hz, {setup_globals.energy.position} keV"
    )


if __name__ == "__main__":
    with mock_id31():
        simulate()
        plt.show()
