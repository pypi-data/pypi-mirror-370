import datetime

import matplotlib.pyplot as plt
import numpy as np

from .widget_base import WidgetMPL


class ClockWidget(WidgetMPL):
    def __init__(
        self,
        lv,
        text_colour="white",
        background="black",
        show_seconds=False,
        show_minutes=True,
        show_hours=True,
        **kwargs
    ):
        """
        Create a clock face to indicate the time of day.

        Parameters
        ----------
        lv: lavavu.Viewer
            The viewer object to plot with.
        text_colour:
            Matplotlib compatable colour.
        background:
            Matplotlib compatable colour.
        show_hours: bool
            Whether or not to show the hour hand.
        show_minutes: bool
            Whether or not to show the minute hand.
        show_seconds: bool
            Whether or not to show the second hand.
        scale: float
            The size of the widget, where 1.0 means it will take up the entire height of the final image.
        offset: tuple[float, float]
            The position of the widget, with (0,0) placing it in the top left, and (1,1) the bottom right.
        """

        super().__init__(lv=lv, **kwargs)
        self.text_colour = text_colour
        self.background = background
        self.show_hours = show_hours
        self.show_minutes = show_minutes
        self.show_seconds = show_seconds
        self.lines = []

    def _make_mpl(self):
        """
        Creates a blank clock face.
        Based on https://inprogrammer.com/analog-clock-python/
        """
        fig = plt.figure(figsize=(2.5, 2.5), dpi=100)
        fig.patch.set_facecolor((0, 0, 0, 0))  # make background transparent
        ax = fig.add_subplot(111, polar=True)
        plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False))
        ax.set_xticklabels(range(1, 13))
        ax.tick_params(axis="x", which="major", labelcolor=self.text_colour)
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.pi / 3.0)
        ax.grid(False)
        plt.ylim(0, 1)

        ax.set_facecolor(self.background)
        ax.spines["polar"].set_color(self.text_colour)

        return fig, ax

    def _update_mpl(self, fig, ax, time: datetime.time = None, **kwargs):
        """
        Adds clock hands.

        Parameters
        ----------
        time: datetime.time
        """

        if time is None:
            return

        hour = time.hour
        minute = time.minute
        second = time.second
        angles_h = (
            2 * np.pi * hour / 12
            + 2 * np.pi * minute / (12 * 60)
            + 2 * second / (12 * 60 * 60)
            - np.pi / 6.0
        )
        angles_m = (
            2 * np.pi * minute / 60 + 2 * np.pi * second / (60 * 60) - np.pi / 6.0
        )
        angles_s = 2 * np.pi * second / 60 - np.pi / 6.0

        if self.show_seconds:
            lines = ax.plot(
                [angles_s, angles_s], [0, 0.9], color=self.text_colour, linewidth=1
            )
            self.lines.extend(lines)
        if self.show_minutes:
            lines = ax.plot(
                [angles_m, angles_m], [0, 0.7], color=self.text_colour, linewidth=2
            )
            self.lines.extend(lines)
        if self.show_hours:
            lines = ax.plot(
                [angles_h, angles_h], [0, 0.3], color=self.text_colour, linewidth=4
            )
            self.lines.extend(lines)

    def _reset_mpl(self, fig, ax, **kwargs):
        """
        Removes the clock hands.
        """
        for i in self.lines:
            i.remove()
        self.lines.clear()
