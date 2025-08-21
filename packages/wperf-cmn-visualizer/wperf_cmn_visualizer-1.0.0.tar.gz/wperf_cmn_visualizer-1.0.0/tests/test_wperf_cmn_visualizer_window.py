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

import argparse
from unittest.mock import Mock, patch
from PySide6.QtCore import QSize, QRect
from wperf_cmn_visualizer.wperf_cmn_visualizer import wperfCmnVisualizer

from wperf_cmn_visualizer.config import Config


class TestWindowSetup:

    @patch('wperf_cmn_visualizer.wperf_cmn_visualizer.QGuiApplication.primaryScreen')
    def test_setup_window_with_zero_dimensions(self, mock_primary_screen):
        """
        Ensure that if primary screen size getter does not cause window creation failure.
        Ensure that window is created with minimum size.
        """
        mock_screen = Mock()
        mock_screen.size.return_value = QSize(0, 0)
        mock_primary_screen.return_value = mock_screen
        args = argparse.Namespace(topology=None, telemetry=None)
        visualiser = wperfCmnVisualizer.__new__(wperfCmnVisualizer)
        visualiser.args = args
        visualiser.app = Mock()
        visualiser.window = Mock()

        visualiser._set_up_window()

        min_width, min_height = Config.MAIN_WINDOW_MIN_SIZE
        expected_geometry = QRect(0, 0, min_width, min_height)
        visualiser.window.setGeometry.assert_called_with(expected_geometry)
        visualiser.window.setMinimumSize.assert_called_with(min_width, min_height)

    @patch('wperf_cmn_visualizer.wperf_cmn_visualizer.QGuiApplication.primaryScreen')
    def test_setup_window_with_normal_dimensions(self, mock_primary_screen):
        """
        Ensure that with reasonable primary screen size, window creation size is
        as expected.
        """
        mock_screen = Mock()
        mock_screen.size.return_value = QSize(1920, 1080)
        mock_primary_screen.return_value = mock_screen

        visualiser = wperfCmnVisualizer.__new__(wperfCmnVisualizer)
        visualiser.args = argparse.Namespace(topology=None, telemetry=None)
        visualiser.app = Mock()
        visualiser.window = Mock()

        visualiser._set_up_window()

        expected_width = int(1920 * Config.MAIN_WINDOW_INIT_SIZE_RATIO)
        expected_height = int(1080 * Config.MAIN_WINDOW_INIT_SIZE_RATIO)
        expected_x = (1920 - expected_width) // 2
        expected_y = (1080 - expected_height) // 2
        expected_geometry = QRect(expected_x, expected_y, expected_width, expected_height)
        visualiser.window.setGeometry.assert_called_with(expected_geometry)
        visualiser.window.setMinimumSize.assert_called_with(*Config.MAIN_WINDOW_MIN_SIZE)

    @patch('wperf_cmn_visualizer.wperf_cmn_visualizer.CMNRenderer')
    @patch('wperf_cmn_visualizer.wperf_cmn_visualizer.QVBoxLayout')
    @patch('wperf_cmn_visualizer.wperf_cmn_visualizer.QWidget')
    @patch('wperf_cmn_visualizer.wperf_cmn_visualizer.TabbedInterface')
    def test_setup_widgets_without_telemetry(self, _, __, mock_vboxlayout, mock_renderer):
        """
        Ensure that when telemetry is not available, only CMNRenderer is displayed.
        No TimeScrubber is instantiated.
        """
        visualiser = wperfCmnVisualizer.__new__(wperfCmnVisualizer)
        visualiser.app = Mock()
        visualiser.window = Mock()
        visualiser.window.setCentralWidget = Mock()
        visualiser.cmn = Mock()
        visualiser.cmn.num_meshes = 1
        visualiser.cmn_metrics = None  # No telemetry

        mock_layout = Mock()
        mock_vboxlayout.return_value = mock_layout

        visualiser._setup_widgets()

        # CMNRenderer should be instantiated
        mock_renderer.assert_called_once()
        # No TimeScrubber should be created
        assert not hasattr(visualiser, 'time_scrubber')
