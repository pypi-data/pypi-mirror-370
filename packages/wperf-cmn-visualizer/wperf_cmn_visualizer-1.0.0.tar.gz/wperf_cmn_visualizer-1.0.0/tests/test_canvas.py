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
from PySide6.QtCore import Qt, QPointF, QPoint, QEvent
from PySide6.QtGui import QWheelEvent, QMouseEvent, QColor
from wperf_cmn_visualizer.canvas import Canvas, ZoomPanCanvas

from wperf_cmn_visualizer.config import Config


class TestCanvas:
    """Tests for base Canvas class (no interaction)"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        """Create widget for each test"""
        self.parent = QWidget()
        self.canvas = Canvas(self.parent)
        self.parent.show()

    def teardown_method(self):
        """Clean up widget"""
        self.canvas.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Ensure proper initial values and objects for Canvas."""
        assert self.canvas.scene is not None
        assert self.canvas.view is not None
        assert self.canvas._brush is not None
        assert self.canvas._pen is not None

    def test_draw_text_scene_coordinates(self):
        """Test drawing text in scene coordinates."""
        self.canvas.scene.clear()
        self.canvas.draw_text(100, 50, "Test Text", QColor("white"), 12)

        items = self.canvas.scene.items()
        assert len(items) == 1

        # Position should be close to target
        text_item = items[0]
        pos = text_item.pos()
        assert abs(pos.x() + text_item.boundingRect().width() / 2 - 100) < 1
        assert abs(pos.y() + text_item.boundingRect().height() / 2 - 50) < 1

    def test_draw_rectangle_scene_coordinates(self):
        """Test drawing rectangle in scene coordinates."""
        self.canvas.scene.clear()
        self.canvas.draw_rectangle(100, 50, 40, 30, QColor("blue"), QColor("red"), 2.0)

        items = self.canvas.scene.items()
        assert len(items) == 1

    def test_text_measurement(self):
        """Test text measurement methods."""
        text = "Sample Text"
        font_size = 12

        width = self.canvas.get_text_width(text, font_size)
        height = self.canvas.get_text_height(font_size)

        assert width > 0
        assert height > 0
        assert isinstance(width, float)
        assert isinstance(height, float)


class TestZoomPanCanvas:
    """Tests for ZoomPanCanvas (interactive)"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        """Create widget and mocks for each test"""
        self.parent = QWidget()
        self.redraw_mock = Mock()
        self.hover_mock = Mock()
        self.canvas = ZoomPanCanvas(
            self.parent,
            redraw_callback=self.redraw_mock,
            hover_callback=self.hover_mock
        )
        self.parent.show()

    def teardown_method(self):
        self.canvas.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Ensure proper initial values for ZoomPanCanvas."""
        assert hasattr(self.canvas, 'zoom_scale')
        assert hasattr(self.canvas, 'offset_x')
        assert hasattr(self.canvas, 'offset_y')
        assert self.canvas.offset_x == 0.0
        assert self.canvas.offset_y == 0.0
        assert self.canvas.scene is not None
        assert self.canvas.view is not None

    def test_world_to_screen_conversion(self):
        """Check world_to_screen coordinate conversion respects zoom and offset."""
        self.canvas.zoom_scale = 2.0
        self.canvas.offset_x = 5.0
        self.canvas.offset_y = 10.0
        x_screen, y_screen = self.canvas.world_to_screen(3.0, 4.0)
        assert x_screen == 3.0 * 2.0 + 5.0  # 11.0
        assert y_screen == 4.0 * 2.0 + 10.0  # 18.0

    def test_screen_to_world_conversion(self):
        """Check screen_to_world coordinate conversion."""
        self.canvas.zoom_scale = 2.0
        self.canvas.offset_x = 5.0
        self.canvas.offset_y = 10.0
        x_world, y_world = self.canvas.screen_to_world(11.0, 18.0)
        assert abs(x_world - 3.0) < 0.001
        assert abs(y_world - 4.0) < 0.001

    def test_pan_updates_offsets(self):
        """
        Test to ensure panning works.
        Ensure redraw is called.
        """
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress, QPointF(10, 10), QPointF(10, 10),
            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), press_event)
        assert self.canvas._pan_start == QPointF(10, 10)

        move_event = QMouseEvent(
            QEvent.Type.MouseMove, QPointF(20, 30), QPointF(20, 30),
            Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), move_event)

        assert self.canvas.offset_x == 10  # 20 - 10
        assert self.canvas.offset_y == 20  # 30 - 10
        self.redraw_mock.assert_called()

    def test_pan_stops_on_mouse_release(self):
        """
        Panning stops when left mouse button released
        """
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress, QPointF(10, 10), QPointF(10, 10),
            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), press_event)

        release_event = QMouseEvent(
            QEvent.Type.MouseButtonRelease, QPointF(20, 30), QPointF(20, 30),
            Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), release_event)
        assert self.canvas._pan_start is None

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

    def test_hover_callback_called_with_world_coords(self):
        """Hovering without panning should call hover callback with world coords."""
        move_event = QMouseEvent(
            QEvent.Type.MouseMove, QPointF(30, 40), QPointF(30, 40),
            Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier
        )
        self.canvas.eventFilter(self.canvas.view.viewport(), move_event)
        self.hover_mock.assert_called_once()
        wx, wy = self.hover_mock.call_args[0]
        assert isinstance(wx, float) and isinstance(wy, float)

    def test_draw_text_world_coordinates(self):
        """Test that ZoomPanCanvas draws text with world coordinate transformations."""
        self.canvas.scene.clear()
        self.canvas.zoom_scale = 2.0
        self.canvas.offset_x = 10.0
        self.canvas.offset_y = 20.0

        # Draw text at world coordinates (50, 25)
        self.canvas.draw_text(50, 25, "World Text", QColor("white"), 12)

        items = self.canvas.scene.items()
        assert len(items) == 1

        # Expected screen position: (50*2 + 10, 25*2 + 20) = (110, 70)
        text_item = items[0]
        pos = text_item.pos()
        expected_screen_x = 50 * 2.0 + 10.0  # 110
        expected_screen_y = 25 * 2.0 + 20.0  # 70

        assert abs(pos.x() + text_item.boundingRect().width() / 2 - expected_screen_x) < 5
        assert abs(pos.y() + text_item.boundingRect().height() / 2 - expected_screen_y) < 5

    def test_text_measurement_with_scaling(self):
        """Test that text measurement accounts for zoom scaling."""
        self.canvas.zoom_scale = 2.0
        text = "Sample Text"
        font_size = 12

        width = self.canvas.get_text_width(text, font_size)
        height = self.canvas.get_text_height(font_size)

        assert width > 0
        assert height > 0
        assert isinstance(width, float)
        assert isinstance(height, float)

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
        self.canvas.zoom_scale = 0.01
        event = self._create_wheel_event(angle_delta=-120)
        self.canvas.eventFilter(self.canvas.view.viewport(), event)
        assert self.canvas.zoom_scale >= Config.MIN_ZOOM

    def test_zoom_scale_clamped_at_max(self):
        """Ensure zoom scale doesn't exceed maximum limit."""
        self.canvas.zoom_scale = 50.0
        event = self._create_wheel_event(angle_delta=120)
        self.canvas.eventFilter(self.canvas.view.viewport(), event)
        assert self.canvas.zoom_scale <= Config.MAX_ZOOM
