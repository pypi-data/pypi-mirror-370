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
from wperf_cmn_visualizer.wperf_cmn_visualizer import wperfCmnVisualizer
from wperf_cmn_visualizer.config import Config


class TestWindowSetup:

    @patch('tkinter.Tk')
    def test_setup_window_with_zero_dimensions(self, mock_tk):
        mock_window = Mock()
        mock_tk.return_value = mock_window

        mock_window.winfo_screenwidth.return_value = 0
        mock_window.winfo_screenheight.return_value = 0

        visualiser = wperfCmnVisualizer.__new__(wperfCmnVisualizer)
        visualiser.args = argparse.Namespace()
        visualiser.window = mock_window

        visualiser._set_up_window()

        min_width, min_height = Config.MAIN_WINDOW_MIN_SIZE
        expected_geometry = f"{min_width}x{min_height}+0+0"
        mock_window.geometry.assert_called_with(expected_geometry)
