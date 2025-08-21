from typing import TYPE_CHECKING, Sequence

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from rtcvis.plf import PLF


def plot_plfs(plfs: Sequence["PLF"]):
    if plt is None:
        raise ImportError(
            "Plotting requires matplotlib. Install with `pip install rtcvis[plot]`."
        )
    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="box")

    for idx, plf in enumerate(plfs):
        ax.plot(plf.x, plf.y, label=idx)

    ax.legend(loc="upper left")

    plt.show()
