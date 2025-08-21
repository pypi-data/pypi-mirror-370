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

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QToolButton, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QPointF, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QPaintEvent, QMouseEvent, QIcon, QPolygonF
import numpy as np
from typing import Any

from .cmn_metrics import CMNMetrics


class TimelineCanvas(QWidget):
    """Widget for drawing the timeline graph and handling scrubbing."""

    scrub_changed = Signal(int)
    """Signal for Scrubbing. Emitted when time stamp index is changed"""

    def __init__(self, master: QWidget, cmn_metrics: CMNMetrics, **kwargs):
        """
        Initialize the status bar.
        Args:
            master: Parent widget
            cmn_metrics: Metrics data source
            **kwargs: Additional widget configuration options
        """
        super().__init__(master, **kwargs)
        self.cmn_metrics = cmn_metrics
        self.current_time_index = 0
        self.handle_x = 0.0
        self.is_dragging = False
        self.is_hovering = False
        self._skip_line_redraw = False

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the graph line and scrubbing handle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        height = self.height()
        if width > 1 and height > 1:
            if not self._skip_line_redraw:
                self._draw_graph_line(painter, width, height)
            self._draw_scrubbing_handle(painter, width, height)

    def _draw_graph_line(self, painter: QPainter, width: int, height: int) -> None:
        """
        Draw the metric graph line normalised to canvas size.
        Args:
            width: Canvas width.
            height: Canvas height.
        """
        if self.cmn_metrics.global_data.size == 0:
            return

        values = self.cmn_metrics.global_data[:, 0, 0]  # Assuming metric_idx=0, mesh=0
        if len(values) == 0:
            return

        max_val = np.max(values)
        if max_val == 0:
            return

        normalized_y = values / max_val
        y_coords = (1.0 - normalized_y) * (height - 5)

        max_time = np.max(self.cmn_metrics.time_stamps) if len(self.cmn_metrics.time_stamps) > 0 else 1
        normalized_x = self.cmn_metrics.time_stamps / max_time
        x_coords = normalized_x * (width - 5)

        pen = QPen(QColor(70, 130, 180), 2)
        painter.setPen(pen)
        polygon = QPolygonF([QPointF(x, y) for x, y in zip(x_coords, y_coords)])
        painter.setPen(QPen(QColor(70, 130, 180), 2))
        painter.drawPolyline(polygon)

    def _draw_scrubbing_handle(self, painter: QPainter, width: int, height: int) -> None:
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

        if self.is_dragging or self.is_hovering:
            colour = QColor(220, 20, 60, 100)
            pen = QPen(colour, 8)
        else:
            colour = QColor(220, 20, 60)
            pen = QPen(colour, 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(int(self.handle_x), 0 + 5, int(self.handle_x), height - 5)

    def _get_nearest_time_index(self, x: float) -> int:
        """
        Find the nearest time index for a given x coordinate.
        Args:
            x: X coordinate on the canvas.
        Returns:
            Closest index in time_stamps.
        """
        if len(self.cmn_metrics.time_stamps) == 0:
            return 0

        width = self.width()
        max_time = np.max(self.cmn_metrics.time_stamps)
        normalized_time = x / (width - 5)
        target_time = normalized_time * max_time

        distances = np.abs(self.cmn_metrics.time_stamps - target_time)
        return int(np.argmin(distances))

    def _is_near_handle(self, x: float, tolerance: int = 10) -> bool:
        """
        Check if mouse is near the scrubbing handle.
        Args:
            x: Mouse x coordinate.
            tolerance: Pixel tolerance for proximity.
        Returns:
            True if mouse is near the handle, else False.
        """
        return abs(x - self.handle_x) <= tolerance

    def _update_tooltip(self) -> None:
        """Update tooltip with current timestamp value."""
        if 0 <= self.current_time_index < len(self.cmn_metrics.time_stamps) and self.is_hovering:
            time_value = self.cmn_metrics.time_stamps[self.current_time_index]
            self.setToolTip(f"Time: {time_value:.3f}(s)")
        else:
            self.setToolTip("")

    def _update_handle_only(self):
        """Update only the handle region to avoid redrawing the expensive line."""
        update_region_width = 20
        old_handle_x = self.handle_x

        if len(self.cmn_metrics.time_stamps) > 0:
            max_time = np.max(self.cmn_metrics.time_stamps)
            current_time = self.cmn_metrics.time_stamps[self.current_time_index]
            self.handle_x = (current_time / max_time) * (self.width() - 5)

        old_rect = QRect(
            int(old_handle_x - update_region_width), 0,
            int(2 * update_region_width), self.height()
        )
        new_rect = QRect(
            int(self.handle_x - update_region_width), 0,
            int(2 * update_region_width), self.height()
        )

        self._skip_line_redraw = True
        self.update(old_rect)
        self.update(new_rect)
        self._skip_line_redraw = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Start dragging if mouse press near the handle."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_near_handle(event.position().x()):
            self.is_dragging = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update scrubbing position during dragging or handle hover effects."""
        x = event.position().x()
        if self.is_dragging:
            x = max(5, min(x, self.width() - 5))
            new_index = self._get_nearest_time_index(x)
            if new_index != self.current_time_index:
                self.current_time_index = new_index
                self._update_tooltip()
                self._update_handle_only()
                QTimer.singleShot(0, lambda: self.scrub_changed.emit(self.current_time_index))
        else:
            was_hovering = self.is_hovering
            self.is_hovering = self._is_near_handle(x)
            if self.is_hovering != was_hovering:
                self.setCursor(Qt.CursorShape.SizeHorCursor if self.is_hovering else Qt.CursorShape.ArrowCursor)
                if self.is_hovering:
                    self._update_tooltip()
                self._update_handle_only()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Stop dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.update()

    def leaveEvent(self, event) -> None:
        """Reset hover state when mouse leaves widget."""
        if not self.is_dragging:
            self.is_hovering = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setToolTip("")
            self._update_handle_only()

    def set_time_index(self, index: int) -> None:
        """Set the current time index and update display."""
        if 0 <= index < len(self.cmn_metrics.time_stamps):
            self.current_time_index = index
            self._update_tooltip()
            self.update()


class TimeScrubber(QWidget):
    """Status bar widget with media playback controls and custom render area."""

    # Signal emitted when time position changes
    time_changed = Signal(int)

    def __init__(self, master: QWidget, cmn_metrics: CMNMetrics, height: int, **kwargs: Any) -> None:
        """
        Initialize the time scrubber.
        Args:
            master: Parent widget
            cmn_metrics: Metrics data source
            **kwargs: Additional configuration options
        """
        super().__init__(master)
        self.master = master
        self.cmn_metrics = cmn_metrics
        self.desired_height = height

        # Playback state
        self.is_playing = False
        self.playback_speed = 1.0
        self.current_time_index = 0

        # Timer for playback
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._play_next_frame)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setFixedHeight(self.desired_height)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 2, 5, 2)
        self._create_media_controls(main_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setLineWidth(1)
        main_layout.addWidget(separator)

        self.timeline_canvas = TimelineCanvas(self.master, self.cmn_metrics)
        self.timeline_canvas.scrub_changed.connect(self._on_scrub_changed)
        main_layout.addWidget(self.timeline_canvas, 1)

    def _create_media_controls(self, parent_layout: QHBoxLayout) -> None:
        """Create playback control buttons."""

        def create_button(icon_name: str, tooltip: str, callback):
            btn = QToolButton()
            btn.setIcon(QIcon.fromTheme(icon_name))
            btn.setToolTip(tooltip)
            btn.setAutoRaise(True)
            btn.setFixedSize(30, 30)
            btn.clicked.connect(callback)
            parent_layout.addWidget(btn)
            return btn

        self.play_button = create_button("media-playback-start", "Play/Pause", self._on_play_pause)
        self.stop_button = create_button("media-playback-stop", "Stop", self._on_stop)
        self.prev_button = create_button("media-skip-backward", "Previous", self._on_previous)
        self.next_button = create_button("media-skip-forward", "Next", self._on_next)

        # Speed combobox remains unchanged
        self.speed_combobox = QComboBox()
        self.speed_values = ["0.25x", "0.5x", "1x", "1.5x", "2x", "4x"]
        self.speed_combobox.addItems(self.speed_values)
        self.speed_combobox.setCurrentText("1x")
        self.speed_combobox.setFixedHeight(30)
        self.speed_combobox.currentTextChanged.connect(self._on_speed_change)
        parent_layout.addWidget(self.speed_combobox)

    def _on_play_pause(self) -> None:
        """Toggle playback state and update play button icon."""
        self.is_playing = not self.is_playing
        icon_name = "media-playback-pause" if self.is_playing else "media-playback-start"
        self.play_button.setIcon(QIcon.fromTheme(icon_name))
        if self.is_playing:
            self._start_playback()
        else:
            self.playback_timer.stop()

    def _start_playback(self) -> None:
        """Start playback from current position."""
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self._schedule_next_frame()
        else:
            self.is_playing = False
            self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))

    def _schedule_next_frame(self) -> None:
        """Schedule the next frame based on time delta."""
        if not self.is_playing or self.current_time_index >= len(self.cmn_metrics.time_stamps) - 1:
            return
        t_current = self.cmn_metrics.time_stamps[self.current_time_index]
        t_next = self.cmn_metrics.time_stamps[self.current_time_index + 1]
        delay = max(1, int(((t_next - t_current) * 1000) / self.playback_speed))
        self.playback_timer.start(delay)

    def _play_next_frame(self) -> None:
        """Advance playback by one frame."""
        self.playback_timer.stop()
        if not self.is_playing:
            return
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self.current_time_index += 1
            self.timeline_canvas.set_time_index(self.current_time_index)
            self._broadcast_scrub_event()
            self._schedule_next_frame()
        else:
            self.is_playing = False
            self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))

    def _on_stop(self) -> None:
        """Stop playback, reset time index and update UI."""
        self.is_playing = False
        self.playback_timer.stop()
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.current_time_index = 0
        self.timeline_canvas.set_time_index(self.current_time_index)
        self._broadcast_scrub_event()

    def _on_previous(self) -> None:
        """Go to previous time index if possible."""
        if self.current_time_index > 0:
            self.current_time_index -= 1
            self.timeline_canvas.set_time_index(self.current_time_index)
            self._broadcast_scrub_event()

    def _on_next(self) -> None:
        """Go to next time index if possible."""
        if self.current_time_index < len(self.cmn_metrics.time_stamps) - 1:
            self.current_time_index += 1
            self.timeline_canvas.set_time_index(self.current_time_index)
            self._broadcast_scrub_event()

    def _on_speed_change(self, speed_text: str) -> None:
        """Update playback speed based on combobox selection."""
        try:
            speed = float(speed_text.replace("x", ""))
            # catch case with NaN. In python NaN != NaN
            if speed != speed or speed <= 0:
                raise ValueError("Invalid speed")
            self.playback_speed = speed
        except ValueError:
            self.playback_speed = 1.0  # fallback

    def _on_scrub_changed(self, time_index: int) -> None:
        """Handle scrubbing from the timeline canvas."""
        self.current_time_index = time_index
        self._broadcast_scrub_event()

    def _broadcast_scrub_event(self) -> None:
        """Broadcast time scrub event."""
        self.time_changed.emit(self.current_time_index)
