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

import tkinter as tk
import ttkbootstrap as tb
from unittest.mock import Mock
from wperf_cmn_visualizer.canvas import ZoomPanCanvas
from wperf_cmn_visualizer.config import Config


class TestZoomPanCanvas:
    """Tests for ZoomPanCanvas to ensure basic callbacks work"""
    def setup_method(self):
        """
        Constructor Hook to set up tests. Pytest Provided
        """
        self.root = tb.Window()
        self.root.withdraw()
        self.root.update()
        # mock redraw function and mouse hover callback function
        self.redraw_mock = Mock()
        self.mock_hover = Mock()
        self.canvas = ZoomPanCanvas(self.root, redraw_callback=self.redraw_mock, width=100, height=100)
        self.canvas.hover_callback = self.mock_hover

    def teardown_method(self):
        """
        Destructor Hook to clean up. Pytest provided
        """
        self.canvas.destroy()
        self.root.destroy()

    def test_initial_state(self):
        """
        Test to ensure proper initialisation
        """
        assert self.canvas.offset_x == 0.0
        assert self.canvas.offset_y == 0.0
        assert self.canvas.zoom_scale == Config.DEFAULT_ZOOM

    def test_pan_updates_offsets(self):
        """
        Test to ensure panning works.
        Ensure redraw is called.
        """
        event_press = Mock(x=10, y=10)
        self.canvas._start_pan(event_press)
        assert self.canvas._pan_start_x == 10
        assert self.canvas._pan_start_y == 10

        event_drag = Mock(x=20, y=30)
        self.canvas._do_pan(event_drag)
        # Offsets should be updated by dx=10, dy=20
        assert self.canvas.offset_x == 10
        assert self.canvas.offset_y == 20
        self.redraw_mock.assert_called()

    def test_hover_callback_invoked(self):
        """
        Ensure house hover callback is called.
        """
        event_move = Mock(x=50, y=60)
        self.canvas._on_mouse_move(event_move)

        expected_x = (50 - self.canvas.offset_x) / self.canvas.zoom_scale
        expected_y = (60 - self.canvas.offset_y) / self.canvas.zoom_scale
        # redraw is not called. hover call back is responsible for this
        self.mock_hover.assert_called_with(expected_x, expected_y)

    def test_zoom_in_updates_scale(self):
        """
        Simulate scrolling with Mouse Wheel.
        Check if canvas zoom scale is changed.
        Ensure redraw is called.
        """
        event_zoom_in = Mock()
        event_zoom_in.type = tk.EventType.MouseWheel
        event_zoom_in.delta = 120
        event_zoom_in.x = 50
        event_zoom_in.y = 50

        old_scale = self.canvas.zoom_scale

        self.canvas._do_zoom(event_zoom_in)
        assert self.canvas.zoom_scale > old_scale
        self.redraw_mock.assert_called()

    def test_zoom_out_updates_scale(self):
        """
        Simulate scrolling with Mouse Wheel.
        Check if canvas zoom scale is changed.
        Ensure redraw is called.
        """
        event_zoom_in = Mock()
        event_zoom_in.type = tk.EventType.MouseWheel
        event_zoom_in.delta = -120
        event_zoom_in.x = 50
        event_zoom_in.y = 50

        old_scale = self.canvas.zoom_scale

        self.canvas._do_zoom(event_zoom_in)
        assert self.canvas.zoom_scale < old_scale
        self.redraw_mock.assert_called()

    def test_dynamic_grid_cell_size_scales_with_zoom(self):
        """
        Test that grid cell size increases with zoom scale.
        """
        base_size = Config.GRID_CELL_SIZE
        self.canvas.zoom_scale = 1.0
        size_at_1x = self.canvas.get_dynamic_grid_cell_size()

        self.canvas.zoom_scale = 2.0
        size_at_2x = self.canvas.get_dynamic_grid_cell_size()

        assert size_at_1x == base_size
        assert size_at_2x > size_at_1x
