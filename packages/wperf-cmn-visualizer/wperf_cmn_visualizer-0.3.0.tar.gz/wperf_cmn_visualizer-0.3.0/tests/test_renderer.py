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

import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPalette
from wperf_cmn_visualizer.renderer import CMNRenderer

from wperf_cmn_visualizer.config import Config
from wperf_cmn_visualizer.cmn import mesh_dtype, xp_dtype, CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics
from wperf_cmn_visualizer.telemetry_loader import TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME


class TestCMNRenderer:
    """Comprehensive tests for CMNRenderer class"""

    @pytest.fixture
    def mock_cmn(self):
        """Create a mock CMN object for testing."""
        mock_cmn = MagicMock()
        mock_cmn.num_meshes = 1

        # Create a simple 2x2 mesh for testing
        mock_meshes = np.zeros(1, dtype=mesh_dtype)
        mock_mesh = mock_meshes[0]
        mock_mesh["x_dim"] = 2
        mock_mesh["y_dim"] = 2

        # Create XP nodes array
        xps = np.zeros((CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH), dtype=xp_dtype)

        # Fill in test data
        for y in range(2):
            for x in range(2):
                xp = xps[y, x]
                xp["dtc_domain"] = (x + y) % len(CMNRenderer.dtc_color_map)
                xp["node_info"]["coord"]["x"] = x
                xp["node_info"]["coord"]["y"] = y
                xp["node_info"]["nodeid"] = 1000 + y * 2 + x
                xp["node_info"]["type"] = 1
                xp["node_info"]["type_str"] = "XP"

                # Set up ports
                for p in range(4):
                    port = xp["ports"][p]
                    if p == 0:  # First port has devices
                        port["type"] = 1
                        port["type_str"] = "device_port"
                        port["cal"] = False
                        port["num_devices"] = 2
                        # Add devices
                        for d in range(2):
                            device = port["devices"][d]
                            device["nodeid"] = 100 + d
                            device["type"] = 1
                            device["type_str"] = "HN-F"
                    else:  # Other ports are empty
                        port["type"] = 0
                        port["num_devices"] = 0

        mock_mesh["xps"] = xps
        mock_cmn.meshes = mock_meshes

        # Mock get_view method
        def mock_get_view(mesh_idx, min_row, max_row, min_col, max_col):
            return xps[min_row:max_row + 1, min_col:max_col + 1]
        mock_cmn.get_view = mock_get_view

        return mock_cmn

    @pytest.fixture
    def sample_metrics_data(self):
        """Create sample metrics DataFrame for testing."""
        return pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric2", "metric1", "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0",
                "XP at X=1 Y=0",
                "HN-F (100) at X=0 Y=0 Port=0",
                "XP at X=0 Y=1",
                "HN-F (101) at X=1 Y=0 Port=0",
                "Global"
            ],
            VALUE_COLUMN_NAME: [10.5, 20.3, 30.7, 15.2, 25.8, 40.1]
        })

    @pytest.fixture
    def renderer(self, mock_cmn, sample_metrics_data):
        _ = QApplication.instance() or QApplication([])  # shared application instance
        root = QWidget()
        root.resize(400, 400)
        palette = QPalette()

        renderer = CMNRenderer(root, palette, mock_cmn, CMNMetrics(mock_cmn, sample_metrics_data, palette))
        yield renderer

        # Cleanup
        renderer.canvas.setParent(None)
        root.deleteLater()

    def test_initial_state(self, renderer):
        """Test renderer initialization"""
        assert renderer.cmn_idx == 0
        assert renderer.canvas is not None

    def test_current_mesh_property(self, renderer):
        """Test current_mesh property returns correct mesh"""
        mesh = renderer.current_mesh
        assert mesh["x_dim"] == 2
        assert mesh["y_dim"] == 2

    def test_grid_to_world_conversion(self, renderer):
        """Test grid to world coordinate conversion"""
        # Test corner
        world_x, world_y = renderer.grid_to_world(0, 0)
        expected_x = 0 * Config.GRID_CELL_SIZE
        expected_y = (2 - 0) * Config.GRID_CELL_SIZE  # y_dim - row
        assert world_x == expected_x
        assert world_y == expected_y

        # Test another position
        world_x, world_y = renderer.grid_to_world(1, 1)
        expected_x = 1 * Config.GRID_CELL_SIZE
        expected_y = (2 - 1) * Config.GRID_CELL_SIZE
        assert world_x == expected_x
        assert world_y == expected_y

    def test_world_to_grid_conversion(self, renderer):
        """Test world to grid coordinate conversion"""
        grid_row, grid_col = renderer.world_to_grid(0, 2 * Config.GRID_CELL_SIZE)
        assert grid_row == 0
        assert grid_col == 0

        grid_row, grid_col = renderer.world_to_grid(
            Config.GRID_CELL_SIZE,
            Config.GRID_CELL_SIZE
        )
        assert grid_row == 1
        assert grid_col == 1

    def test_grid_world_conversion_roundtrip(self, renderer):
        """Test that grid->world->grid conversion is consistent"""
        original_row, original_col = 1, 1
        world_x, world_y = renderer.grid_to_world(original_row, original_col)
        converted_row, converted_col = renderer.world_to_grid(world_x, world_y)

        assert converted_row == original_row
        assert converted_col == original_col

    def test_find_node_at_world_pos_within_tolerance(self, renderer):
        """Test finding node within tolerance"""
        world_x, world_y = renderer.grid_to_world(0, 0)
        tolerance = Config.XP_NODE_SQUARE_SIZE

        found = renderer.find_node_at_world_pos(world_x, world_y, tolerance)
        assert found == (0, 0)

    def test_find_node_at_world_pos_outside_tolerance(self, renderer):
        """Test not finding node outside tolerance"""
        world_x, world_y = renderer.grid_to_world(0, 0)
        # Move far enough away to be outside tolerance
        world_x += Config.XP_NODE_SQUARE_SIZE * 5
        tolerance = Config.XP_NODE_SQUARE_SIZE

        found = renderer.find_node_at_world_pos(world_x, world_y, tolerance)
        assert found is None

    def test_find_node_at_world_pos_out_of_bounds(self, renderer):
        """Test finding node outside mesh bounds"""
        # Test position outside mesh
        world_x = -100
        world_y = -100
        tolerance = Config.XP_NODE_SQUARE_SIZE

        found = renderer.find_node_at_world_pos(world_x, world_y, tolerance)
        assert found is None

    def test_render_grid_lines(self, renderer):
        """Test grid line rendering"""
        with patch.object(renderer.canvas, 'draw_line') as mock_draw_line:
            renderer._render_grid_lines()
            # Should draw lines for 2x2 grid (2 vertical + 2 horizontal = 4 lines)
            assert mock_draw_line.call_count == 4

    @pytest.mark.parametrize("zoom_level,expected_detail", [
        (1.0, "basic"),
        (3.0, "small"),
        (6.0, "medium"),
        (9.0, "full")
    ])
    def test_level_of_detail_by_zoom(self, renderer, zoom_level, expected_detail):
        """Test level of detail changes based on zoom level"""
        with patch.object(renderer, 'get_visible_bounds', return_value=(0, 1, 0, 1)), \
             patch.object(renderer.canvas, 'draw_rectangle') as mock_draw_rect, \
             patch.object(renderer.canvas, 'draw_text') as mock_draw_text, \
             patch.object(renderer.canvas, 'get_text_width', return_value=50), \
             patch.object(renderer.canvas, 'get_text_height', return_value=10), \
             patch.object(renderer.canvas, 'draw_line') as mock_draw_line:

            renderer.canvas.zoom_scale = zoom_level
            renderer._render_nodes()

            if expected_detail == "basic":
                # only render XP boxes
                mock_draw_rect.assert_called()
                assert mock_draw_rect.call_count == 4

            elif expected_detail == "small":
                mock_draw_rect.assert_called()
                assert mock_draw_rect.call_count == 12
                # Should have coordinate labels and nodeid labels, rendered with 2 instances per XP
                mock_draw_text.assert_called()
                assert mock_draw_text.call_count == 8

            elif expected_detail == "medium":
                # Should have XP labels and port lines
                mock_draw_rect.assert_called()
                assert mock_draw_rect.call_count >= 12
                mock_draw_text.assert_called()
                assert mock_draw_text.call_count >= 12
                mock_draw_line.assert_called()

            elif expected_detail == "full":
                # full detail
                mock_draw_rect.assert_called()
                assert mock_draw_rect.call_count >= 12
                mock_draw_text.assert_called()
                assert mock_draw_text.call_count >= 12
                mock_draw_line.assert_called()

    def test_on_time_changed_triggers_render(self, renderer):
        with patch.object(renderer, "_render_all") as mock_render:
            renderer._on_time_changed(1)
            assert renderer.cmn_metrics_time_idx == 1
            mock_render.assert_called_once()
