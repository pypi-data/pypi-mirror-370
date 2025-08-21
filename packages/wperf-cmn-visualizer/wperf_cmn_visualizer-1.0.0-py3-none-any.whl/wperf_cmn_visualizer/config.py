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
Central Location for configuration constants, magic numbers etc.
"""

from dataclasses import dataclass


@dataclass
class Config:
    DEFAULT_TOPOLOGY_FILE: str = "topology.json"

    MAIN_WINDOW_TITLE: str = "WindowsPerf CMN Visualizer"
    MAIN_WINDOW_INIT_SIZE_RATIO: float = 0.75
    MAIN_WINDOW_MIN_SIZE: tuple[int, int] = (400, 300)

    ZOOM_FACTOR: float = 1.1
    MIN_ZOOM: float = 0.1
    MAX_ZOOM: float = 10.0
    DEFAULT_ZOOM: float = 1.0
    CANVAS_PADDING: int = 0
    GRID_CELL_SIZE: int = 30
    GRID_LINE_WIDTH: float = 1.0
    XP_NODE_SQUARE_SIZE: int = 10
    XP_PORT_LINE_LEN: int = 5
    XP_OUTLINE_WIDTH = 1.0
    XP_LABEL_FONT_SIZE: int = 7
    XP_DETAILS_FONT_SIZE: int = 2
    XP_UI_PADDING: float = 2

    TOOLTIP_FONT_SIZE: int = 12
    TOOLTIP_PADDING: float = 4.0
