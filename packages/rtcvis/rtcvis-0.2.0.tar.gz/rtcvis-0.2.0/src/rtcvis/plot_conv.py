import ast
import functools

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure
from matplotlib.widgets import Button, CheckButtons, Slider, TextBox, Widget

from rtcvis.conv import DELTA, LAMBDA, ConvType, conv, conv_at_x
from rtcvis.plf import PLF


class ConvProperties:
    def __init__(self, a: PLF, b: PLF, conv_type: ConvType):
        """Computes several properties needed for plotting convolutions.

        Computes the min and max values for the slider, x axis and y axis as well as
        the result of the convolution.

        Args:
            a (PLF): PLF a.
            b (PLF): PLF b.
            conv_type (ConvType): The type of convolution.
        """
        # allow computing the convolution for all x where a and b overlap
        PADDING = 0.5
        is_deconv = conv_type in (ConvType.MAX_PLUS_DECONV, ConvType.MIN_PLUS_DECONV)
        if is_deconv:
            min_deconv_result = conv(a=a, b=b, conv_type=ConvType.MIN_PLUS_DECONV)
            max_deconv_result = conv(a=a, b=b, conv_type=ConvType.MAX_PLUS_DECONV)
            conv_min_y = max_deconv_result.min.y
            conv_max_y = min_deconv_result.max.y
            self.slider_min = a.x_start - b.x_end
            self.slider_max = a.x_end - b.x_start
            self.result = (
                min_deconv_result
                if conv_type == ConvType.MIN_PLUS_DECONV
                else max_deconv_result
            )
        else:
            min_conv_result = conv(a=a, b=b, conv_type=ConvType.MIN_PLUS_CONV)
            max_conv_result = conv(a=a, b=b, conv_type=ConvType.MAX_PLUS_CONV)
            conv_min_y = min_conv_result.min.y
            conv_max_y = max_conv_result.max.y
            self.slider_min = a.x_start + b.x_start
            self.slider_max = b.x_end + a.x_end
            self.result = (
                min_conv_result
                if conv_type == ConvType.MIN_PLUS_CONV
                else max_conv_result
            )
        self.min_x = (
            min(a.x_start, b.x_start - (a.x_end - a.x_start), self.slider_min) - PADDING
        )
        self.max_x = (
            max(a.x_end, b.x_end + (a.x_end - a.x_start), self.slider_max) + PADDING
        )
        self.min_y = min(a.min.y, b.min.y, conv_min_y) - PADDING
        self.max_y = max(a.max.y, b.max.y, conv_max_y) + PADDING


def plot_conv() -> None:
    """Opens an interactive plot for convolutions.

    The plot is very interactive:

    The functions to be used can be entered using textboxes.

    The delta for which the convolution should be computed can be specified using a
    slider.

    The type of convolution can also be selected using buttons.

    The plot can show the original PLF a, the transformed PLF a, PLF b, the
    sum/difference of those two and the full result of the convolution. All functions
    can individually be toggled in the legend.
    """
    if plt is None:
        raise ImportError(
            "Plotting requires matplotlib. Install with `pip install rtcvis[plot]`."
        )

    # create a figure with all required axes
    fig, axs = plt.subplot_mosaic(
        "aaaa;bbbb;0123;pppp;ssss",
        height_ratios=[0.04, 0.04, 0.05, 1, 0.03],
        layout="constrained",
    )
    ax_textbox_a = axs["a"]
    ax_textbox_b = axs["b"]
    ax_slider = axs["s"]
    ax_plot = axs["p"]

    # references to all widgets of draw_conv to prevent garbage collection
    conv_widgets: tuple[Widget, ...] = ()

    # "global state" variables that will be shared across multiple calls of draw_conv
    conv_type = ConvType.MAX_PLUS_CONV
    a, b = PLF([]), PLF([])
    visibilities = [False, True, True, True, True]
    x = [0.0]

    def update_plf(text: str, selector: str, textbox: TextBox):
        nonlocal a, b
        try:
            points, x_end = ast.literal_eval(text)
            if not (
                isinstance(points, list)
                and all(
                    isinstance(a, tuple)
                    and len(a) == 3
                    and all(isinstance(b, (int, float)) for b in a)
                    for a in points
                )
                and isinstance(x_end, (int, float))
            ):
                raise Exception()
            new_plf = PLF.from_rtctoolbox(points, x_end)
            if selector == "a":
                a = new_plf
            elif selector == "b":
                b = new_plf
            textbox.text_disp.set_color("black")
        except Exception:
            textbox.text_disp.set_color("red")

    def textbox_callback(text: str, selector: str, textbox: TextBox):
        update_plf(text, selector, textbox)
        draw_conv_plot()

    # create the textboxes
    textbox_a = TextBox(
        ax_textbox_a,
        "a:",
        initial="[(0, 0, 0), (1, 1, 0), (2, 2, 0), (3, 3, 0)], 5",
        textalignment="left",
    )
    textbox_b = TextBox(
        ax_textbox_b, "b:", initial="[(0, 0, 0), (1, 0, 1)], 5", textalignment="left"
    )
    textbox_a.on_submit(lambda text: textbox_callback(text, "a", textbox_a))
    textbox_b.on_submit(lambda text: textbox_callback(text, "b", textbox_b))

    def draw_conv_plot():
        nonlocal conv_widgets
        # add the actual convolution plot
        ax_plot.clear()
        ax_slider.clear()
        # keep references so they're not garbage collected
        conv_widgets = draw_conv(
            a=a,
            b=b,
            conv_type=conv_type,
            fig=fig,
            ax_plot=ax_plot,
            ax_slider=ax_slider,
            visibilities=visibilities,
            x=x,
        )

    def update_conv_type(ctype: ConvType, event: MouseEvent):
        nonlocal conv_type
        conv_type = ctype
        draw_conv_plot()

    # create buttons for selecting the ConvolutionType
    buttons = []
    for i, ctype in enumerate(ConvType):
        ax_button = axs[str(i)]
        button = Button(ax_button, ctype.operator_desc)
        button.on_clicked(functools.partial(update_conv_type, ctype))
        buttons.append(button)  # keep reference to prevent garbage collection
        ax_button.texts[-1].set_fontsize("large")

    update_plf(textbox_a.text, "a", textbox_a)
    update_plf(textbox_b.text, "b", textbox_b)
    draw_conv_plot()

    plt.show()


def draw_conv(
    a: PLF,
    b: PLF,
    conv_type: ConvType,
    fig: Figure,
    ax_plot: Axes,
    ax_slider: Axes,
    visibilities: list[bool],
    x: list[float],
) -> tuple[Widget, ...]:
    """Draws a convolution of the given type into existing axes.

    Args:
        a (PLF): PLF a.
        b (PLF): PLF b.
        conv_type (ConvType): The type of convolution.
        fig (Figure): The figure object.
        ax_plot (Axes): The axes into which the plot should be drawn. Has to be cleared
            before calling this function.
        ax_slider (Axes): The axes into which the slider should be drawn. Also has to
            be cleared before.
        visibilities (list[bool]): List of flags that toggle whether each displayed
            function should be visible by default.
        x (list[float]): List with 1 entry that represents the current x value. This
            entry will be changed when the slider is used.

    Returns:
        tuple[Widget, ...]: References to the widgets created by this function. Store
            them in a local variable so they're not garbage collected!
    """
    conv_properties = ConvProperties(a=a, b=b, conv_type=conv_type)

    color_a = mcolors.TABLEAU_COLORS["tab:cyan"]
    color_trans_a = mcolors.TABLEAU_COLORS["tab:olive"]
    color_b = mcolors.TABLEAU_COLORS["tab:orange"]
    color_sum = mcolors.TABLEAU_COLORS["tab:purple"]
    color_result = mcolors.TABLEAU_COLORS["tab:gray"]
    colors = (color_a, color_trans_a, color_b, color_sum, color_result)

    ax_plot.set_aspect("equal", adjustable="box")

    # compute initial convolution result
    initial_x = min(conv_properties.slider_max, max(conv_properties.slider_min, x[0]))
    conv_result = conv_at_x(a, b, initial_x, conv_type)

    # Create bottom slider
    deltax_slider = Slider(
        ax=ax_slider,
        label=f"${DELTA}$",
        valmin=conv_properties.slider_min,
        valmax=conv_properties.slider_max,
        valinit=initial_x,
        valfmt="%.2f",
    )

    # plot a (but hide it by default)
    (graph_a,) = ax_plot.plot(a.x, a.y, label=conv_type.a_desc, color=color_a)
    graph_a.set_visible(visibilities[0])

    # plot transformed a
    (graph_trans_a,) = ax_plot.plot(
        conv_result.transformed_a.x,
        conv_result.transformed_a.y,
        label=conv_type.a_trans_desc,
        color=color_trans_a,
    )
    graph_trans_a.set_visible(visibilities[1])

    # plot b
    (graph_b,) = ax_plot.plot(b.x, b.y, label=conv_type.b_desc, color=color_b)
    graph_b.set_visible(visibilities[2])

    # plot convolution sum
    (graph_sum,) = ax_plot.plot(
        conv_result.sum.x,
        conv_result.sum.y,
        label=conv_type.sum_desc,
        color=color_sum,
    )
    graph_sum.set_visible(visibilities[3])

    # add marker for conv result
    (graph_sum_marker,) = ax_plot.plot(
        [conv_result.result.x],
        [conv_result.result.y],
        marker=".",
        color=color_sum,
    )
    graph_sum_marker.set_visible(visibilities[3])

    # plot full result of convolution
    conv_plf = conv_properties.result
    (graph_result,) = ax_plot.plot(
        conv_plf.x,
        conv_plf.y,
        label=conv_type.operator_desc,
        color=color_result,
    )
    graph_result.set_visible(visibilities[4])
    # add marker for where we're currently at
    (graph_result_marker,) = ax_plot.plot(
        [initial_x],
        [conv_plf(initial_x)],
        marker=".",
        color=color_result,
    )
    graph_result_marker.set_visible(visibilities[4])

    # Slider update function
    def slider_callback(val):
        # update x
        x[0] = val

        # Recompute convolution
        conv_result = conv_at_x(a, b, val, conv_type)

        # Update transformed a
        graph_trans_a.set_xdata(conv_result.transformed_a.x)
        graph_trans_a.set_ydata(
            conv_result.transformed_a.y
        )  # y doesn't really change but hey

        # Update sum PLF
        graph_sum.set_xdata(conv_result.sum.x)
        graph_sum.set_ydata(conv_result.sum.y)

        # Update sum marker
        graph_sum_marker.set_xdata([conv_result.result.x])
        graph_sum_marker.set_ydata([conv_result.result.y])

        # update result marker
        graph_result_marker.set_xdata([val])
        graph_result_marker.set_ydata([conv_plf(val)])

        fig.canvas.draw_idle()

    # register the slider
    deltax_slider.on_changed(slider_callback)

    # create legend with check buttons for toggling the visibility
    rax = ax_plot.inset_axes((0.0, 0.0, 0.12, 0.2))
    check = CheckButtons(
        ax=rax,
        labels=[
            conv_type.a_desc,
            conv_type.a_trans_desc,
            conv_type.b_desc,
            conv_type.sum_desc,
            conv_type.operator_desc,
        ],
        actives=[
            graph_a.get_visible(),
            graph_trans_a.get_visible(),
            graph_b.get_visible(),
            graph_sum.get_visible(),
            graph_result.get_visible(),
        ],
        label_props={"color": colors},
        frame_props={"edgecolor": colors},
        check_props={"facecolor": colors},
    )

    # make the background semi-transparent
    rax.patch.set_alpha(0.7)

    # make the font a bit larger
    for text in check.labels:
        text.set_fontsize("large")

    # checkbox update function
    def check_callback(label: str | None):
        if label == conv_type.a_desc:
            visibilities[0] = not visibilities[0]
            graph_a.set_visible(not graph_a.get_visible())
        elif label == conv_type.a_trans_desc:
            visibilities[1] = not visibilities[1]
            graph_trans_a.set_visible(not graph_trans_a.get_visible())
        elif label == conv_type.b_desc:
            visibilities[2] = not visibilities[2]
            graph_b.set_visible(not graph_b.get_visible())
        elif label == conv_type.sum_desc:
            visibilities[3] = not visibilities[3]
            graph_sum_marker.set_visible(not graph_sum.get_visible())
            graph_sum.set_visible(not graph_sum.get_visible())
        elif label == conv_type.operator_desc:
            visibilities[4] = not visibilities[4]
            graph_result_marker.set_visible(not graph_result.get_visible())
            graph_result.set_visible(not graph_result.get_visible())
        fig.canvas.draw_idle()

    # register the checkboxes
    check.on_clicked(check_callback)

    # set limits, title and xlabel
    ax_plot.set_xlim(conv_properties.min_x, conv_properties.max_x)
    ax_plot.set_ylim(conv_properties.min_y, conv_properties.max_y)
    ax_plot.set_title(
        f"{conv_type}: ${conv_type.operator_desc[1:-1]} = {conv_type.full_desc[1:-1]}$"
    )
    ax_plot.set_xlabel(f"${LAMBDA}$")
    ax_plot.grid(color="0.9")

    return (deltax_slider, check)
