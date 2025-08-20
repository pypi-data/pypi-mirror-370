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
Time Line Scrubbing Module.

Instantiate a TimeScrubber widget which broadcasts a time scrubbing event.
Show Global data as a time line graph and present media buttons.
"""

import ttkbootstrap as tb
import tkinter as tk
from tkinter import Canvas
import numpy as np
from typing import Any

from .cmn_metrics import CMNMetrics
from .config import Events


class TimeScrubber(tb.Frame):
    """Status bar widget with media playback controls and custom render area."""

    def __init__(self, master: tb.Window, style: tb.Style, cmn_metrics: CMNMetrics, **kwargs: Any) -> None:
        """
        Initialize the status bar.
        Args:
            master: Parent widget
            style: ttkbootstrap style palette to be used
            cmn_metrics: Metrics data source
            **kwargs: Additional frame configuration options
        """
        super().__init__(master, **kwargs)
        self.style: Any = style  # type hint bypass
        self.cmn_metrics: CMNMetrics = cmn_metrics
        self.configure(relief="sunken", borderwidth=1)

        self.desired_height: int = kwargs.get('height', 100)
        self.is_playing: bool = False
        self.playback_speed: float = 1.0

        # Scrubbing handle state
        self.current_time_index: int = 0  # Current position in time_stamps array
        self.handle_x: float = 0  # Current x position of handle
        self.is_dragging: bool = False
        self.drag_start_x: int = 0

        self._setup_layout()
        self._create_media_controls()
        self._create_custom_area()

    def _setup_layout(self) -> None:
        """Configure the grid layout for the frame."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1, minsize=self.desired_height)
        self.grid_propagate(False)

    def _create_media_controls(self) -> None:
        """Create playback control buttons."""
        self.media_frame: tb.Frame = tb.Frame(self)
        self.media_frame.grid(row=0, column=0, sticky="w", padx=(5, 10), pady=2)

        self.play_button: tb.Button = tb.Button(self.media_frame, text="▶", width=3, command=self._on_play_pause)
        self.play_button.pack(side="left", padx=(0, 2))

        self.stop_button: tb.Button = tb.Button(self.media_frame, text="⏹", width=3, command=self._on_stop)
        self.stop_button.pack(side="left", padx=2)

        self.prev_button: tb.Button = tb.Button(self.media_frame, text="⏮", width=3, command=self._on_previous)
        self.prev_button.pack(side="left", padx=2)

        self.next_button: tb.Button = tb.Button(self.media_frame, text="⏭", width=3, command=self._on_next)
        self.next_button.pack(side="left", padx=2)

        self.speed_values = ["0.25x", "0.5x", "1x", "1.5x", "2x", "4x"]
        self.speed_combobox: tb.Combobox = tb.Combobox(
            self.media_frame,
            values=self.speed_values,
            width=5,
            state="readonly",
        )
        self.speed_combobox.set(self.speed_values[2])  # default to 1x
        self.speed_combobox.pack(side="left", padx=(10, 0))
        self.speed_combobox.bind("<<ComboboxSelected>>", self._on_speed_change)

    def _create_custom_area(self) -> None:
        """Create custom canvas area for graph and scrubbing handle."""
        self.custom_frame: tb.Frame = tb.Frame(self, relief="ridge", borderwidth=1)
        self.custom_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)

        self.custom_frame.grid_columnconfigure(0, weight=1)
        self.custom_frame.grid_rowconfigure(0, weight=1)

        self.custom_canvas: Canvas = Canvas(
            self.custom_frame,
            bg=self.style.colors.bg,
            highlightthickness=0
        )
        self.custom_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.custom_canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse events for scrubbing
        self.custom_canvas.bind("<Button-1>", self._on_mouse_press)
        self.custom_canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.custom_canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.custom_canvas.bind("<Motion>", self._on_mouse_motion)
        self.custom_canvas.bind("<Leave>", self._on_mouse_leave)

        self.after_idle(self._draw_custom_content)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Redraw custom content when canvas size changes."""
        self.custom_canvas.delete("all")
        self._draw_custom_content()

    def _draw_custom_content(self) -> None:
        """Draw the graph line and scrubbing handle."""
        width = self.custom_canvas.winfo_width()
        height = self.custom_canvas.winfo_height()
        if width > 1 and height > 1:
            self._draw_graph_line(width, height)
            self._draw_scrubbing_handle(width, height)

    def _draw_graph_line(self, width: int, height: int) -> None:
        """
        Draw the metric graph line normalised to canvas size.
        Args:
            width: Canvas width.
            height: Canvas height.
        """
        values = self.cmn_metrics.global_data[:, 0, 0]  # Assuming metric_idx=0, mesh=0
        if len(values) == 0:
            return

        max_val = np.max(values)
        if max_val == 0:
            return

        normalised_y = values / max_val
        y_coords = (1.0 - normalised_y) * (height - 5)

        max_time = np.max(self.cmn_metrics.time_stamps) if len(self.cmn_metrics.time_stamps) > 0 else 1
        normalised_x = self.cmn_metrics.time_stamps / max_time
        x_coords = normalised_x * (width - 5)

        coords = list(zip(x_coords, y_coords))
        self.custom_canvas.create_line(*coords, width=2, fill=self.style.colors.secondary, tags="graph")

    def _draw_scrubbing_handle(self, width: int, height: int, thick: bool = False) -> None:
        """
        Draw the scrubbing handle at the current time index.
        Args:
            width: Canvas width.
            height: Canvas height.
            thick: If True, draw thicker and semi-transparent handle.
        """
        if len(self.cmn_metrics.time_stamps) == 0:
            return

        max_time = np.max(self.cmn_metrics.time_stamps)
        current_time = self.cmn_metrics.time_stamps[self.current_time_index]
        self.handle_x = (current_time / max_time) * (width - 5)

        self.custom_canvas.delete("handle")
        self.custom_canvas.create_line(
            self.handle_x, 0,
            self.handle_x, height,
            width=8 if thick else 4,
            fill=self.style.colors.primary,
            stipple="gray50" if thick else "",
            tags="handle"
        )

    def _get_nearest_time_index(self, x: float, width: int) -> int:
        """
        Find the nearest time index for a given x coordinate.
        Args:
            x: X coordinate on the canvas.
            width: Canvas width.
        Returns:
            Closest index in time_stamps.
        """
        if len(self.cmn_metrics.time_stamps) == 0:
            return 0

        max_time = np.max(self.cmn_metrics.time_stamps)
        normalized_time = x / (width - 5)
        target_time = normalized_time * max_time

        distances = np.abs(self.cmn_metrics.time_stamps - target_time)
        return int(np.argmin(distances))

    def _is_near_handle(self, x: float, y: float, tolerance: int = 10) -> bool:
        """
        Check if mouse is near the scrubbing handle.
        Args:
            x: Mouse x coordinate.
            y: Mouse y coordinate.
            tolerance: Pixel tolerance for proximity.
        Returns:
            True if mouse is near the handle, else False.
        """
        return abs(x - self.handle_x) <= tolerance

    def _on_mouse_press(self, event: tk.Event) -> None:
        """Start dragging if mouse press near the handle."""
        if self._is_near_handle(event.x, event.y):
            self.is_dragging = True

    def _on_mouse_drag(self, event: tk.Event) -> None:
        """Update scrubbing position during dragging."""
        if not self.is_dragging:
            return

        width = self.custom_canvas.winfo_width()
        x = max(0, min(event.x, width - 5))

        new_index = self._get_nearest_time_index(x, width)
        if new_index != self.current_time_index:
            self.current_time_index = new_index

            self._draw_scrubbing_handle(width, self.custom_canvas.winfo_height(), thick=True)
            self.broadcast_scrub_event()

    def _on_mouse_release(self, event: tk.Event) -> None:
        """Stop dragging and restore handle appearance."""
        if self.is_dragging:
            self.is_dragging = False

    def _on_mouse_motion(self, event: tk.Event) -> None:
        """Change cursor to indicate draggable handle."""
        if self.is_dragging:
            return

        if self._is_near_handle(event.x, event.y):
            self.custom_canvas.configure(cursor="sb_h_double_arrow")
            self._draw_scrubbing_handle(
                self.custom_canvas.winfo_width(),
                self.custom_canvas.winfo_height(),
                thick=True
            )
        else:
            self._draw_scrubbing_handle(
                self.custom_canvas.winfo_width(),
                self.custom_canvas.winfo_height(),
                thick=False
            )
            self.custom_canvas.configure(cursor="")

    def _on_mouse_leave(self, event: tk.Event) -> None:
        """Reset cursor and handle appearance when mouse leaves canvas."""
        if self.is_dragging:
            return

        self._draw_scrubbing_handle(
            self.custom_canvas.winfo_width(),
            self.custom_canvas.winfo_height(),
            thick=False
        )
        self.custom_canvas.configure(cursor="")

    def _on_play_pause(self) -> None:
        """Toggle playback state and update button."""
        self.is_playing = not self.is_playing
        self.play_button.configure(text="⏸" if self.is_playing else "▶")

        if self.is_playing:
            self._play_next_frame()

    def _play_next_frame(self) -> None:
        """Advance playback by one frame and schedule next frame by time delta."""
        if not self.is_playing:
            return

        if self.current_time_index < self.cmn_metrics.num_time_stamps - 1:
            self.current_time_index += 1
            self.refresh_custom_area()
            self.broadcast_scrub_event()

            t_current = self.cmn_metrics.time_stamps[self.current_time_index]
            t_next = self.cmn_metrics.time_stamps[self.current_time_index + 1] if self.current_time_index + 1 < self.cmn_metrics.num_time_stamps else t_current
            delay = max(1, int(((t_next - t_current) * 1000) / self.playback_speed))  # Convert to milliseconds
            self.after(delay, self._play_next_frame)
        else:
            self.is_playing = False
            self.play_button.configure(text="▶")

    def _on_stop(self) -> None:
        """Stop playback, reset time index and update UI."""
        self.is_playing = False
        self.play_button.configure(text="▶")
        self.current_time_index = 0
        self.refresh_custom_area()
        self.broadcast_scrub_event()

    def _on_previous(self) -> None:
        """Go to previous time index if possible."""
        if self.current_time_index > 0:
            self.current_time_index -= 1
            self.refresh_custom_area()
            self.broadcast_scrub_event()

    def _on_next(self) -> None:
        """Go to next time index if possible."""
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self.current_time_index += 1
            self.refresh_custom_area()
            self.broadcast_scrub_event()

    def _on_speed_change(self, event: tk.Event) -> None:
        """Update playback speed based on combobox selection."""
        speed_text = self.speed_combobox.get().replace("x", "")
        try:
            self.playback_speed = float(speed_text)
        except ValueError:
            self.playback_speed = 1.0  # fallback

    def refresh_custom_area(self) -> None:
        """Redraw the custom canvas contents."""
        self.custom_canvas.delete("all")
        self._draw_custom_content()

    def broadcast_scrub_event(self) -> None:
        """Broadcast time scrub event"""
        Events.Data = self.current_time_index
        self.master.event_generate(Events.TIMESCRUB_EVT, when="tail")
