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

from unittest.mock import Mock
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPointF, QPoint, QEvent, QSize
from PySide6.QtGui import QWheelEvent, QMouseEvent
from wperf_cmn_visualizer.canvas import ZoomPanCanvas


class TestZoomPanCanvas:
    """Tests for ZoomPanCanvas PySide6 version"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        """Create widget and mocks for each test"""
        self.parent = QWidget()
        self.redraw_mock = Mock()
        self.canvas = ZoomPanCanvas(self.parent, redraw_callback=self.redraw_mock)
        self.parent.show()

    def teardown_method(self):
        """Clean up widget"""
        self.canvas.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Ensure proper initial values and objects"""
        assert self.canvas.zoom_scale == 1.0
        assert self.canvas.offset_x == 0.0
        assert self.canvas.offset_y == 0.0
        assert self.canvas.scene is not None
        assert self.canvas.view is not None

    def test_pan_updates_offsets(self):
        """
        Test to ensure panning works.
        Ensure redraw is called.
        """
        press_event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(10, 10), QPointF(10, 10), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        self.canvas.eventFilter(self.canvas.view.viewport(), press_event)
        assert self.canvas._pan_start == QPointF(10, 10)

        move_event = QMouseEvent(QEvent.Type.MouseMove, QPointF(20, 30), QPointF(20, 30), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        self.canvas.eventFilter(self.canvas.view.viewport(), move_event)

        assert self.canvas.offset_x == 10  # 20 - 10
        assert self.canvas.offset_y == 20  # 30 - 10
        self.redraw_mock.assert_called()

    def test_pan_stops_on_mouse_release(self):
        """
        Panning stops when left mouse button released
        """
        press_event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(10, 10), QPointF(10, 10), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        self.canvas.eventFilter(self.canvas.view.viewport(), press_event)
        release_event = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(20, 30), QPointF(20, 30), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        self.canvas.eventFilter(self.canvas.view.viewport(), release_event)
        assert self.canvas._pan_start is None

    def test_world_to_screen_conversion(self):
        """
        Check world_to_screen coordinate conversion respects zoom and offset
        """
        self.canvas.zoom_scale = 2.0
        self.canvas.offset_x = 5.0
        self.canvas.offset_y = 10.0
        x_screen, y_screen = self.canvas.world_to_screen(3.0, 4.0)
        assert x_screen == 3.0 * 2.0 + 5.0
        assert y_screen == 4.0 * 2.0 + 10.0

    def test_zoom_in_updates_scale(self):
        """
        Simulate scrolling with Mouse Wheel.
        Check if canvas zoom scale is changed.
        Ensure redraw is called.
        """
        old_scale = self.canvas.zoom_scale
        pos = QPointF(50, 50)
        wheel_event = QWheelEvent(
            pos, pos, QPoint(0, 0), QPoint(0, 120),
            Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollUpdate, False
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), wheel_event)
        assert self.canvas.zoom_scale > old_scale
        self.redraw_mock.assert_called()

    def test_zoom_out_updates_scale(self):
        """
        Simulate scrolling with Mouse Wheel.
        Check if canvas zoom scale is changed.
        Ensure redraw is called.
        """
        self.canvas.zoom_scale = 2.0
        old_scale = self.canvas.zoom_scale
        pos = QPointF(50, 50)
        wheel_event = QWheelEvent(
            pos, pos, QPoint(0, 0), QPoint(0, -120),
            Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollUpdate, False
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), wheel_event)
        assert self.canvas.zoom_scale < old_scale
        self.redraw_mock.assert_called()

    def _create_wheel_event(self, angle_delta=120, pos=QPointF(50, 50)):
        return QWheelEvent(
            pos,
            pos,
            QPoint(0, 0),
            QPoint(0, angle_delta),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollUpdate,
            False
        )

    def test_zoom_scale_clamped_at_min(self):
        """Ensure zoom scale doesn't go below minimum limit."""
        self.canvas.zoom_scale = 0.1
        event = self._create_wheel_event(angle_delta=-120)
        self.canvas.wheelEvent(event)
        assert self.canvas.zoom_scale >= 0.1

    def test_zoom_scale_clamped_at_max(self):
        """Ensure zoom scale doesn't exceed maximum limit."""
        self.canvas.zoom_scale = 10.0
        event = self._create_wheel_event(angle_delta=120)
        self.canvas.wheelEvent(event)
        assert self.canvas.zoom_scale <= 10.0
