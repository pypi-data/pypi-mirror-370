# BSD 3-Clause License
#
# Copyright (c) 2025, Arm Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Main application class for wperf_cmn_visualizer
"""

import argparse
import ttkbootstrap as tb
from typing import Optional

from .config import Config
from .topology_loader import cmn_topology_loader
from .telemetry_loader import cmn_telemetry_loader
from .cmn import CMN
from .cmn_metrics import CMNMetrics
from .renderer import CMNRenderer
from .time_scrubber import TimeScrubber


class wperfCmnVisualizer:
    """
    GUI application class for the Wperf CMN Visualizer.
    Handles window creation, layout, and launching the Tkinter event loop.
    """

    def __init__(self, args: argparse.Namespace):
        """
        Initialise the application with the provided topology file.
        Args:
            args (argparse.Namespace): Parsed command line arguments.
        """

        # open main window
        self.args = args
        self.window: tb.Window = tb.Window(themename="cosmo")
        self._set_up_window()

        # load topology
        self.topology = cmn_topology_loader()
        if self.args.topology is not None:
            self.topology.load_topology_from_file(self.args.topology)

        # construct CMN object
        self.cmn: CMN = CMN(self.topology.data)

        # load telemetry is available
        self.telemetry = cmn_telemetry_loader()
        if self.args.telemetry:
            self.telemetry.load_telemetry_from_file(self.args.telemetry)
            self.cmn_metrics: Optional[CMNMetrics] = CMNMetrics(self.cmn, self.telemetry.data)
            # Initialise time scrubber
            self.time_scrubber: TimeScrubber = TimeScrubber(
                self.window, self.window.style, self.cmn_metrics, height=200
            )
            self.time_scrubber.pack(side=tb.BOTTOM, fill=tb.X)
        else:
            self.cmn_metrics = None

        # construct cmn_renderer with optional metrics
        self.cmn_renderer: CMNRenderer = CMNRenderer(
            self.window, self.window.style, self.cmn, self.cmn_metrics
        )

    def _set_up_window(self) -> None:
        """
        Configure the main application window's appearance and geometry.
        """
        self.window.title(Config.MAIN_WINDOW_TITLE)

        # centre window on screen
        screen_width: int = self.window.winfo_screenwidth()
        screen_height: int = self.window.winfo_screenheight()
        width: int = int(screen_width * Config.MAIN_WINDOW_INIT_SIZE_RATIO)
        height: int = int(screen_height * Config.MAIN_WINDOW_INIT_SIZE_RATIO)
        x: int = (screen_width - width) // 2
        y: int = (screen_height - height) // 2

        min_width, min_height = Config.MAIN_WINDOW_MIN_SIZE
        if width < min_width or height < min_height:
            width = min_width
            height = min_height

        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.minsize(min_width, min_height)

    def run(self) -> int:
        """
        Start the application's main event loop.
        Returns:
            int: to be used as exit code
        """
        try:
            self.window.mainloop()
            return 0
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1
