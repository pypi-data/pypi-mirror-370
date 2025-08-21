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

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPointF, QTimer, QEvent
from PySide6.QtGui import QMouseEvent
import pytest
from unittest.mock import Mock, patch
import numpy as np
from typing import cast
from wperf_cmn_visualizer.time_scrubber import TimelineCanvas, TimeScrubber

from wperf_cmn_visualizer.cmn_metrics import CMNMetrics


def create_mock_cmn_metrics(num_timestamps=10) -> CMNMetrics:
    """Create a properly mocked CMNMetrics instance with deterministic data."""
    mock_metrics = Mock(spec=CMNMetrics)

    mock_metrics.time_stamps = np.linspace(0, 1.0, num_timestamps)
    time_normalized = np.linspace(0, 2 * np.pi, num_timestamps)
    # arbitary function: y = 10 + 10sin(2pix)
    sine_values = 10 + 10 * np.sin(time_normalized)
    mock_metrics.global_data = sine_values.reshape(num_timestamps, 1, 1)

    return cast(CMNMetrics, mock_metrics)


class TestTimelineCanvas:
    """Tests for TimelineCanvas widget."""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        self.parent = QWidget()
        self.mock_metrics = create_mock_cmn_metrics(num_timestamps=10)
        self.canvas = TimelineCanvas(self.parent, self.mock_metrics)
        self.canvas.resize(400, 100)
        self.parent.show()

    def teardown_method(self):
        self.canvas.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Test initial state of TimelineCanvas."""
        assert self.canvas.current_time_index == 0
        assert self.canvas.handle_x == 0.0
        assert not self.canvas.is_dragging
        assert not self.canvas.is_hovering
        assert not self.canvas._skip_line_redraw

    def test_get_nearest_time_index_empty(self):
        """
        Test finding nearest time index returns gracefully
        for empty timestamps array.
        """
        empty_metrics = create_mock_cmn_metrics(num_timestamps=0)
        empty_metrics.time_stamps = np.array([])
        empty_canvas = TimelineCanvas(self.parent, empty_metrics)
        assert empty_canvas._get_nearest_time_index(100) == 0

    def test_get_nearest_time_index(self):
        """
        Test finding nearest time index for given x coordinate.
        Test with known data: 10 timestamps from 0 to 1.0, so
        x=0 -> index 0, x=395 -> index 9
        """
        assert self.canvas._get_nearest_time_index(5) == 0  # Near start
        assert 4 <= self.canvas._get_nearest_time_index(200) <= 5  # Near middle
        assert self.canvas._get_nearest_time_index(395) == 9  # Near end

    def test_is_near_handle(self):
        """Test handle proximity detection."""
        self.canvas.handle_x = 100

        # Test within tolerance
        # 5 pixels away when default tolerance is 10
        assert self.canvas._is_near_handle(95)
        assert self.canvas._is_near_handle(105)
        assert self.canvas._is_near_handle(100)

        # Test outside tolerance
        assert not self.canvas._is_near_handle(85)  # 15 pixels away
        assert not self.canvas._is_near_handle(115)

        # Test custom tolerance
        assert self.canvas._is_near_handle(85, tolerance=20)

    def test_mouse_press_starts_dragging(self):
        """
        Test that mouse press near handle starts dragging.
        Set handle position and simulate mouse press near it
        """
        self.canvas.handle_x = 100.0
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(105, 50),  # Near handle
            QPointF(105, 50),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.canvas.mousePressEvent(press_event)
        assert self.canvas.is_dragging

    def test_mouse_press_doesnt_start_dragging(self):
        """
        Test that mouse press far from handle does not start dragging.
        Set handle position and simulate mouse press.
        """
        self.canvas.handle_x = 100.0
        far_press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(200, 50),  # Far from handle
            QPointF(200, 50),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.canvas.mousePressEvent(far_press_event)
        assert not self.canvas.is_dragging

    def test_mouse_move_during_dragging(self):
        """
        Test mouse movement during dragging updates time index.
        Set mouse dragging and simulate mouse move event.
        Patch singleShot and confirm scrub event emission.
        """
        self.canvas.is_dragging = True
        # Move to x=200 (~middle of canvas)
        move_event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(200, 50),
            QPointF(200, 50),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )

        with patch.object(QTimer, 'singleShot') as mock_timer:
            self.canvas.mouseMoveEvent(move_event)
            assert 4 <= self.canvas.current_time_index <= 5
            mock_timer.assert_called_once()

    def test_mouse_move_hover_effects(self):
        """
        Test hover effects when not dragging.
        Test that mouse style is changed.
        Test internal state management is correct.
        """
        self.canvas.is_dragging = False
        self.canvas.handle_x = 100.0
        # Move near handle
        hover_event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(105, 50),
            QPointF(105, 50),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.canvas.mouseMoveEvent(hover_event)
        assert self.canvas.is_hovering
        assert self.canvas.cursor().shape() == Qt.CursorShape.SizeHorCursor

        # Move away from handle reset states
        away_event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(200, 50),
            QPointF(200, 50),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.canvas.mouseMoveEvent(away_event)
        assert not self.canvas.is_hovering
        assert self.canvas.cursor().shape() == Qt.CursorShape.ArrowCursor

    def test_mouse_release_stops_dragging(self):
        """Test mouse release stops dragging."""
        self.canvas.is_dragging = True
        release_event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            QPointF(100, 50),
            QPointF(100, 50),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.canvas.mouseReleaseEvent(release_event)
        assert not self.canvas.is_dragging

    def test_leave_event_resets_hover(self):
        """Test that leaving widget resets hover state."""
        self.canvas.is_hovering = True
        self.canvas.is_dragging = False
        self.canvas.leaveEvent(None)
        assert not self.canvas.is_hovering
        assert self.canvas.cursor().shape() == Qt.CursorShape.ArrowCursor

    def test_leave_event_not_reset_hover_dragging(self):
        """Test that mouse leave does not reset hover state if dragging."""
        self.canvas.is_hovering = True
        self.canvas.is_dragging = True
        self.canvas.leaveEvent(None)
        assert self.canvas.is_hovering  # Should remain True when dragging


class TestTimeScrubber:
    """Tests for TimeScrubber widget."""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        self.parent = QWidget()
        self.mock_metrics = create_mock_cmn_metrics(num_timestamps=10)
        self.scrubber = TimeScrubber(self.parent, self.mock_metrics, height=50)
        self.parent.show()

    def teardown_method(self):
        self.scrubber.deleteLater()
        self.parent.deleteLater()

    def test_initial_state(self):
        """Test initial state of TimeScrubber."""
        assert not self.scrubber.is_playing
        assert self.scrubber.playback_speed == 1.0
        assert self.scrubber.current_time_index == 0
        assert self.scrubber.height() == 50

        # Check UI components exist
        assert hasattr(self.scrubber, 'play_button')
        assert hasattr(self.scrubber, 'stop_button')
        assert hasattr(self.scrubber, 'prev_button')
        assert hasattr(self.scrubber, 'next_button')
        assert hasattr(self.scrubber, 'speed_combobox')
        assert hasattr(self.scrubber, 'timeline_canvas')

    def test_play_pause_functionality(self):
        """Test play/pause button functionality."""

        # Test that default is not playing.
        assert not self.scrubber.is_playing
        # Test play
        self.scrubber._on_play_pause()
        assert self.scrubber.is_playing
        # Test pause
        self.scrubber._on_play_pause()
        assert not self.scrubber.is_playing

    def test_stop_functionality(self):
        """Test stop button functionality."""
        signal_mock = Mock()
        self.scrubber.time_changed.connect(signal_mock)

        # Set up playing state with slightly advanced time index
        self.scrubber.is_playing = True
        self.scrubber.current_time_index = 5
        self.scrubber._on_stop()

        # check state and callbacks
        assert not self.scrubber.is_playing
        assert self.scrubber.current_time_index == 0
        signal_mock.assert_called_with(0)

    def test_previous_next_functionality(self):
        """Test previous/next button functionality."""
        signal_mock = Mock()
        self.scrubber.time_changed.connect(signal_mock)

        # Start at index 5
        self.scrubber.current_time_index = 5

        # Test previous
        self.scrubber._on_previous()
        assert self.scrubber.current_time_index == 4
        signal_mock.assert_called_with(4)

        # Test next
        signal_mock.reset_mock()
        self.scrubber._on_next()
        assert self.scrubber.current_time_index == 5
        signal_mock.assert_called_with(5)

    def test_previous_next_functionality_boundaries(self):
        """
        Test previous/next button functionality on boundaries.
        When current time index is on a boundary, there should be no overflow/underflow.
        """
        self.scrubber.current_time_index = 0
        self.scrubber._on_previous()
        assert self.scrubber.current_time_index == 0

        self.scrubber.current_time_index = len(self.mock_metrics.time_stamps) - 1
        self.scrubber._on_next()
        assert self.scrubber.current_time_index == len(self.mock_metrics.time_stamps) - 1

    @pytest.mark.parametrize("speed_text, expected_speed", [
        ("2x", 2.0),
        ("0.5x", 0.5),
        ("0.25x", 0.25),
        ("1.5x", 1.5),
        ("4x", 4.0),
    ])
    def test_speed_change_valid(self, speed_text, expected_speed):
        """Test valid playback speed changes."""
        self.scrubber._on_speed_change(speed_text)
        assert self.scrubber.playback_speed == expected_speed

    @pytest.mark.parametrize("invalid_text", ["invalid", "not_a_number", "NaNx"])
    def test_speed_change_invalid(self, invalid_text):
        """Test that invalid speeds strings fall back to 1.0."""
        self.scrubber._on_speed_change(invalid_text)
        assert self.scrubber.playback_speed == 1.0

    def test_playback_timing(self):
        """
        Test playback timing calculations with known data and known speed.
        """
        with patch.object(self.scrubber.playback_timer, 'start') as mock_start:
            self.scrubber.is_playing = True
            self.scrubber.current_time_index = 0
            self.scrubber.playback_speed = 2.0

            self.scrubber._schedule_next_frame()

            # Calculate expected delay with known timestamps
            # time_stamps = [0.0, 0.111..., 0.222..., ...] for 10 timestamps
            time_delta = self.mock_metrics.time_stamps[1] - self.mock_metrics.time_stamps[0]
            expected_delay = max(1, int((time_delta * 1000) / 2.0))

            mock_start.assert_called_with(expected_delay)

            args = mock_start.call_args[0]
            delay_called = args[0]
            assert 50 <= delay_called <= 60  # Should be around 111ms / 2 = 55ms
