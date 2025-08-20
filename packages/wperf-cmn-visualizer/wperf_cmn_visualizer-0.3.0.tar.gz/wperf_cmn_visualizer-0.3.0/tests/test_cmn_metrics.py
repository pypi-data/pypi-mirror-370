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
import pandas as pd
import numpy as np
from unittest import mock
from unittest.mock import MagicMock, patch
from PySide6.QtGui import QPalette, QColor
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics

from wperf_cmn_visualizer.cmn import CMN, CMN_MAX_PORTS, CMN_MAX_CHILDS, CMN_XP_DEVICE_ID
from wperf_cmn_visualizer.cmn import CMN_MAX_MESH_WIDTH, CMN_MAX_MESH_HEIGHT
from wperf_cmn_visualizer.cmn import mesh_dtype
from wperf_cmn_visualizer.telemetry_loader import TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME


class TestCMNMetrics:
    """Tests for CMNMetrics data structure and operations."""

    @pytest.fixture
    def mock_cmn(self):
        """Create a mock CMN object for testing."""
        mock_cmn = MagicMock(spec=CMN)
        mock_cmn.num_meshes = 1

        mock_meshes = np.zeros(1, dtype=mesh_dtype)
        mock_mesh = mock_meshes[0]

        mock_mesh["x_dim"] = 2
        mock_mesh["y_dim"] = 2

        for y in range(2):
            for x in range(2):
                xp = mock_mesh["xps"][y, x]
                # Set up XP node info
                xp["node_info"]["coord"]["x"] = x
                xp["node_info"]["coord"]["y"] = y
                xp["node_info"]["nodeid"] = 1000 + y * 2 + x
                xp["node_info"]["type"] = CMN_XP_DEVICE_ID
                xp["node_info"]["type_str"] = "XP"

                # Set up ports
                xp["num_device_ports"] = 1

                # First port has devices
                port = xp["ports"][0]
                port["type"] = 1
                port["type_str"] = "device_port"
                port["num_devices"] = 2

                # Add devices to first port
                for d in range(2):
                    device = port["devices"][d]
                    device["coord"]["x"] = x
                    device["coord"]["y"] = y
                    device["nodeid"] = 100 + y * 2 + x + d
                    device["type"] = 1
                    device["type_str"] = "HN-F"

                # Other ports are empty
                for p in range(1, CMN_MAX_PORTS):
                    port = xp["ports"][p]
                    port["num_devices"] = 0

        mock_cmn.meshes = mock_meshes
        return mock_cmn

    @pytest.fixture
    def sample_metrics_data(self):
        """Create sample metrics DataFrame for testing."""
        return pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric2", "metric1", "metric2", "metric3"
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

    def test_metrics_initialization_basic(self, mock_cmn, sample_metrics_data):
        """Test basic CMNMetrics initialization."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        assert len(metrics.metric_names) == 3
        assert "metric1" in metrics.metric_names
        assert "metric2" in metrics.metric_names
        assert "metric3" in metrics.metric_names

        assert metrics.metric_id_map["metric1"] == 0
        assert metrics.metric_id_map["metric2"] == 1
        assert metrics.metric_id_map["metric3"] == 2

        assert len(metrics.time_stamps) == 2
        assert metrics.time_stamps[0] == 0.5
        assert metrics.time_stamps[1] == 1.0
        assert metrics.num_time_stamps == 2

        assert hasattr(metrics, 'global_data')
        assert metrics.global_data.shape == (2, 3, 1)

    def test_xp_data_loading(self, mock_cmn, sample_metrics_data):
        """Test loading XP metric data."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        # Check XP at X=0 Y=0, time=0.5, metric1
        time_idx = 0
        mesh_idx = 0
        metric_idx = 0  # metric1
        y, x = 0, 0
        assert metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x] == 10.5

        # Check XP at X=1 Y=0, time=0.5, metric2
        metric_idx = 0  # metric1
        y, x = 0, 1
        assert metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x] == 20.3

        # Check XP at X=0 Y=1, time=1.0, metric1
        time_idx = 1
        metric_idx = 0  # metric1
        y, x = 1, 0
        assert metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x] == 15.2

    def test_global_data_loading(self, mock_cmn, sample_metrics_data):
        """Test loading global metric data."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        time_idx = 1
        mesh_idx = 0
        metric_idx = 2  # metric3
        assert metrics.global_data[time_idx, metric_idx, mesh_idx] == 40.1

    def test_node_parsing_edge_cases(self, mock_cmn):
        """Test edge cases in node string parsing."""
        edge_case_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "Global",  # Global node
                "XP at X=0 Y=0",  # Valid XP
                "XP at X=999 Y=999",  # Out of bounds XP
                "HN-F (100) at X=0 Y=0 Port=0",  # Valid device
                "HN-F (999) at X=0 Y=0 Port=0"  # Device with unmatched nodeid
            ],
            VALUE_COLUMN_NAME: [1.0, 2.0, 3.0, 4.0, 5.0]
        })

        metrics = CMNMetrics(mock_cmn, edge_case_data, QPalette())

        time_idx = 0
        mesh_idx = 0

        # Check global data
        assert metrics.global_data[time_idx, :, mesh_idx] == 1.0

        # Check valid XP
        assert metrics.xp_data[time_idx, :, mesh_idx, 0, 0] == 2.0

        # Check valid device
        assert metrics.device_data[time_idx, :, mesh_idx, 0, 0, 0, 0] == 4.0

        # Check out of bounds XP is not loaded (should remain 0)
        for y in range(CMN_MAX_MESH_HEIGHT):
            for x in range(CMN_MAX_MESH_WIDTH):
                if y == 0 and x == 0:
                    continue  # Skip the valid one
                assert metrics.xp_data[time_idx, :, mesh_idx, y, x] == 0.0

    def test_invalid_port_handling(self, mock_cmn):
        """Test handling of invalid port numbers."""
        invalid_port_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "HN-F (100) at X=0 Y=0 Port=0",  # Valid port
                f"HN-F (100) at X=0 Y=0 Port={CMN_MAX_PORTS}",  # Invalid port (too high)
                "HN-F (100) at X=0 Y=0 Port=-1"  # Invalid port (negative)
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0]
        })

        metrics = CMNMetrics(mock_cmn, invalid_port_data, QPalette())

        # Only valid port should be loaded
        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0

        # Valid port should have data
        assert metrics.device_data[time_idx, :, mesh_idx, y, x, 0, 0] == 10.0

    def test_device_nodeid_matching(self, mock_cmn):
        """Test device nodeid matching in port devices."""
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]

        # Clear existing devices and add new ones
        port["num_devices"] = 3
        port["devices"][0]["nodeid"] = 100
        port["devices"][1]["nodeid"] = 200
        port["devices"][2]["nodeid"] = 300

        nodeid_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "HN-F (100) at X=0 Y=0 Port=0",  # First device
                "HN-F (200) at X=0 Y=0 Port=0",  # Second device
                "HN-F (300) at X=0 Y=0 Port=0",  # Third device
                "HN-F (999) at X=0 Y=0 Port=0"   # Non-existent device
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 40.0]
        })

        metrics = CMNMetrics(mock_cmn, nodeid_data, QPalette())

        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        port = 0

        assert metrics.device_data[time_idx, :, mesh_idx, y, x, port, 0] == 10.0
        assert metrics.device_data[time_idx, :, mesh_idx, y, x, port, 1] == 20.0
        assert metrics.device_data[time_idx, :, mesh_idx, y, x, port, 2] == 30.0

    def test_multiple_time_stamps(self, mock_cmn):
        """Test handling of multiple time stamps."""
        multi_time_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 1.0, 1.5, 0.5, 1.0, 1.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric2", "metric2", "metric2"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "XP at X=1 Y=0", "XP at X=1 Y=0", "XP at X=1 Y=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 15.0, 25.0, 35.0]
        })

        metrics = CMNMetrics(mock_cmn, multi_time_data, QPalette())

        assert len(metrics.time_stamps) == 3
        assert metrics.time_stamps[0] == 0.5
        assert metrics.time_stamps[1] == 1.0
        assert metrics.time_stamps[2] == 1.5

        # Check data at different time stamps
        mesh_idx = 0

        # XP at X=0 Y=0, metric1
        assert metrics.xp_data[0, 0, mesh_idx, 0, 0] == 10.0
        assert metrics.xp_data[1, 0, mesh_idx, 0, 0] == 20.0
        assert metrics.xp_data[2, 0, mesh_idx, 0, 0] == 30.0

        # XP at X=1 Y=0, metric2
        assert metrics.xp_data[0, 1, mesh_idx, 0, 1] == 15.0
        assert metrics.xp_data[1, 1, mesh_idx, 0, 1] == 25.0
        assert metrics.xp_data[2, 1, mesh_idx, 0, 1] == 35.0

    def test_empty_metrics_data(self, mock_cmn):
        """Test handling of empty metrics DataFrame."""
        empty_data = pd.DataFrame({
            TIME_COLUMN_NAME: pd.Series([], dtype='float64'),
            METRICS_COLUMN_NAME: pd.Categorical([]),
            NODE_COLUMN_NAME: pd.Series([], dtype='string'),
            VALUE_COLUMN_NAME: pd.Series([], dtype='float64')
        })

        metrics = CMNMetrics(mock_cmn, empty_data, QPalette())

        assert len(metrics.metric_names) == 0
        assert len(metrics.metric_id_map) == 0
        assert len(metrics.time_stamps) == 0
        assert metrics.num_time_stamps == 0

        # Data array should still be initialized but empty in time dimension
        assert metrics.xp_data.shape[0] == 0
        assert metrics.port_data.shape[0] == 0
        assert metrics.device_data.shape[0] == 0
        assert metrics.global_data.shape[0] == 0

    def test_malformed_node_strings(self, mock_cmn):
        """Test handling of malformed node strings."""
        malformed_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0",  # Valid XP string
                "XP at X=abc Y=def",  # Invalid coordinates
                "HN-F at X=0 Y=0 Port=0",  # Missing nodeid
                "Random string",  # Completely invalid
                ""  # Empty string
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 40.0, 50.0]
        })

        metrics = CMNMetrics(mock_cmn, malformed_data, QPalette())

        # Only the valid XP should be loaded
        time_idx = 0
        mesh_idx = 0
        assert metrics.xp_data[time_idx, :, mesh_idx, 0, 0] == 10.0

        # All other positions should remain at default values
        for y in range(CMN_MAX_MESH_HEIGHT):
            for x in range(CMN_MAX_MESH_WIDTH):
                if y == 0 and x == 0:  # ignore valid case
                    continue
                assert metrics.xp_data[time_idx, :, mesh_idx, y, x] == 0.0

    def test_metrics_hash_consistency(self, mock_cmn, sample_metrics_data):
        """Test that metrics hash is consistent with metrics array."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())

        for i, metric in enumerate(metrics.metric_names):
            assert metrics.metric_id_map[metric] == i

        # Test that hash lookup gives correct metric ID
        assert metrics.metric_id_map["metric1"] == 0
        assert metrics.metric_id_map["metric2"] == 1
        assert metrics.metric_id_map["metric3"] == 2

    def test_time_stamp_sorting(self, mock_cmn):
        """Test that time stamps are properly sorted."""
        unsorted_time_data = pd.DataFrame({
            TIME_COLUMN_NAME: [2.0, 0.5, 1.5, 1.0, 0.5, 2.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric1", "metric1", "metric1", "metric1", "metric1"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        })

        metrics = CMNMetrics(mock_cmn, unsorted_time_data, QPalette())

        # Check that time stamps are sorted and unique
        expected_times = [0.5, 1.0, 1.5, 2.0]
        assert len(metrics.time_stamps) == 4
        assert np.array_equal(metrics.time_stamps, expected_times)
        assert metrics.num_time_stamps == 4

    def test_device_index_bounds_checking(self, mock_cmn):
        """Test device index bounds checking with CMN_MAX_CHILDS."""
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        port["num_devices"] = CMN_MAX_CHILDS + 5

        # Add devices up to the limit
        for i in range(CMN_MAX_CHILDS + 5):
            if i < CMN_MAX_CHILDS:
                port["devices"][i]["nodeid"] = i

        # overflow child count by arbitary amount 5
        device_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * (CMN_MAX_CHILDS + 5),
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1"] * (CMN_MAX_CHILDS + 5)
            ),
            NODE_COLUMN_NAME: [
                f"HN-F ({i}) at X=0 Y=0 Port=0" for i in range(CMN_MAX_CHILDS + 5)
            ],
            VALUE_COLUMN_NAME: list(range(CMN_MAX_CHILDS + 5))
        })

        metrics = CMNMetrics(mock_cmn, device_data, QPalette())  # should not crash

        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        port_idx = 0

        for i in range(CMN_MAX_CHILDS):
            assert metrics.device_data[time_idx, :, mesh_idx, y, x, port_idx, i] == i

    def test_multi_metric_data_separation(self, mock_cmn, sample_metrics_data):
        """Test that multiple metrics are properly separated in data arrays."""
        # Extend sample data with more metrics and nodes
        extended_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: [
                "XP at X=0 Y=0", "XP at X=0 Y=0", "XP at X=0 Y=0",
                "XP at X=1 Y=0", "XP at X=1 Y=0", "XP at X=1 Y=0",
                "XP at X=0 Y=1", "XP at X=0 Y=1", "XP at X=0 Y=1"
            ],
            VALUE_COLUMN_NAME: [100, 5.2, 0.85, 150, 3.8, 0.92, 120, 4.1, 0.78]
        })

        metrics = CMNMetrics(mock_cmn, extended_data, QPalette())

        # Verify metric separation
        assert len(metrics.metric_names) == 3
        assert "metric1" in metrics.metric_names
        assert "metric2" in metrics.metric_names
        assert "metric3" in metrics.metric_names

        # Test data access for different metrics
        metric1 = metrics.metric_id_map["metric1"]
        metric2 = metrics.metric_id_map["metric2"]
        metric3 = metrics.metric_id_map["metric3"]

        # Check XP at (0,0) time=0.5
        assert metrics.xp_data[0, metric1, 0, 0, 0] == 100
        assert metrics.xp_data[0, metric2, 0, 0, 0] == 5.2
        assert metrics.xp_data[0, metric3, 0, 0, 0] == 0.85

        # Check XP at (1,0) time=1.0
        assert metrics.xp_data[1, metric1, 0, 0, 1] == 150
        assert metrics.xp_data[1, metric2, 0, 0, 1] == 3.8
        assert metrics.xp_data[1, metric3, 0, 0, 1] == 0.92

    def test_multi_metric_device_data(self, mock_cmn):
        """Test device data with multiple metrics."""
        # Set up mock CMN with devices
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        port["num_devices"] = 2
        port["devices"][0]["nodeid"] = 100
        port["devices"][1]["nodeid"] = 101

        multi_metric_device_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical([
                "xp_tx_read_metric_name", "hnf_snoop_send_metric_name", "xp_tx_read_metric_name", "hnf_snoop_send_metric_name",
                "xp_tx_read_metric_name", "hnf_snoop_send_metric_name", "xp_tx_read_metric_name", "hnf_snoop_send_metric_name"
            ]),
            NODE_COLUMN_NAME: [
                "HN-F (100) at X=0 Y=0 Port=0", "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (101) at X=0 Y=0 Port=0", "HN-F (101) at X=0 Y=0 Port=0",
                "HN-F (100) at X=0 Y=0 Port=0", "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (101) at X=0 Y=0 Port=0", "HN-F (101) at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [50.0, 25.0, 60.0, 30.0, 55.0, 28.0, 65.0, 32.0]
        })

        metrics = CMNMetrics(mock_cmn, multi_metric_device_data, QPalette())

        xp_tx_read_metric = metrics.metric_id_map["xp_tx_read_metric_name"]
        hnf_snoop_send_metric = metrics.metric_id_map["hnf_snoop_send_metric_name"]

        # Check device 0 (nodeid 100) at time=0.5
        assert metrics.device_data[0, xp_tx_read_metric, 0, 0, 0, 0, 0] == 50.0
        assert metrics.device_data[0, hnf_snoop_send_metric, 0, 0, 0, 0, 0] == 25.0

        # Check device 1 (nodeid 101) at time=1.0
        assert metrics.device_data[1, xp_tx_read_metric, 0, 0, 0, 0, 1] == 65.0
        assert metrics.device_data[1, hnf_snoop_send_metric, 0, 0, 0, 0, 1] == 32.0

    def test_multi_metric_global_data(self, mock_cmn):
        """Test global data with multiple metrics across time."""
        global_multi_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.5, 1.5, 1.5],
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3",
                "metric1", "metric2", "metric3"
            ]),
            NODE_COLUMN_NAME: ["Global"] * 9,
            VALUE_COLUMN_NAME: [450.5, 65.2, 0.82, 475.3, 67.8, 0.89, 460.1, 66.5, 0.85]
        })

        metrics = CMNMetrics(mock_cmn, global_multi_data, QPalette())

        metric1 = metrics.metric_id_map["metric1"]
        metric2 = metrics.metric_id_map["metric2"]
        metric3 = metrics.metric_id_map["metric3"]

        # Check values across different times
        assert metrics.global_data[0, metric1, 0] == 450.5
        assert metrics.global_data[0, metric2, 0] == 65.2
        assert metrics.global_data[0, metric3, 0] == 0.82

        assert metrics.global_data[1, metric1, 0] == 475.3
        assert metrics.global_data[2, metric2, 0] == 66.5

    def test_mixed_node_types_multi_metrics(self, mock_cmn):
        """Test handling of mixed node types with multiple metrics."""
        # Set up device in mock CMN
        mesh = mock_cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        port["num_devices"] = 1
        port["devices"][0]["nodeid"] = 200

        mixed_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 6 + [1.0] * 6,
            METRICS_COLUMN_NAME: pd.Categorical([
                "metric_a", "metric_a", "metric_a", "metric_b", "metric_b", "metric_b",
                "metric_a", "metric_a", "metric_a", "metric_b", "metric_b", "metric_b"
            ]),
            NODE_COLUMN_NAME: [
                "Global", "XP at X=0 Y=0", "HN-F (200) at X=0 Y=0 Port=0",
                "Global", "XP at X=0 Y=0", "HN-F (200) at X=0 Y=0 Port=0",
                "Global", "XP at X=0 Y=0", "HN-F (200) at X=0 Y=0 Port=0",
                "Global", "XP at X=0 Y=0", "HN-F (200) at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10, 20, 30, 40, 50, 60, 15, 25, 35, 45, 55, 65]
        })

        metrics = CMNMetrics(mock_cmn, mixed_data, QPalette())

        metric_a_idx = metrics.metric_id_map["metric_a"]
        metric_b_idx = metrics.metric_id_map["metric_b"]

        # Check all data types are populated correctly
        # Time 0.5
        assert metrics.global_data[0, metric_a_idx, 0] == 10
        assert metrics.global_data[0, metric_b_idx, 0] == 40
        assert metrics.xp_data[0, metric_a_idx, 0, 0, 0] == 20
        assert metrics.xp_data[0, metric_b_idx, 0, 0, 0] == 50
        assert metrics.device_data[0, metric_a_idx, 0, 0, 0, 0, 0] == 30
        assert metrics.device_data[0, metric_b_idx, 0, 0, 0, 0, 0] == 60

        # Time 1.0
        assert metrics.global_data[1, metric_a_idx, 0] == 15
        assert metrics.global_data[1, metric_b_idx, 0] == 45

    def test_value_to_colour_returns_white_on_invalid_range(self, mock_cmn, sample_metrics_data):
        """Ensure that when _value_to_colour is supplied with invalid ranges, return values is white"""
        palette = QPalette()
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm._value_to_colour(10, 20, 10) == palette.color(QPalette.ColorRole.Window).name()
        assert cm._value_to_colour(10, 10, 10) == palette.color(QPalette.ColorRole.Window).name()

    def test_value_to_colour_maps_correctly_at_bounds(self, mock_cmn, sample_metrics_data):
        """Basic tests for _value_to_colour function"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm._value_to_colour(0, 0, 100) == "#FFFFFF"
        assert cm._value_to_colour(100, 0, 100) == "#FF0000"
        assert cm._value_to_colour(50, 0, 100) == "#FF7F7F"

    def test_value_to_colour_clamps_to_range(self, mock_cmn, sample_metrics_data):
        """Ensure _value_to_colour clamps colour between white and red"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm._value_to_colour(-100, 0, 10) == "#FFFFFF"
        assert cm._value_to_colour(100, 0, 10) == "#FF0000"

    def test_get_xp_colour_returns_expected_hex(self, mock_cmn, sample_metrics_data):
        """Ensure XP colour getter reads from xp_data member and produces correct colour"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        cm.xp_data[0, 0, 0, 0, 0] = 5.0
        with mock.patch.object(cm, 'get_metric_min_max', return_value=(0.0, 10.0)):
            colour = cm.get_xp_colour(0, 0, 0, 0, 0)

        assert colour == "#FF7F7F"

    def test_get_port_colour_returns_expected_hex(self, mock_cmn, sample_metrics_data):
        """Ensure port colour getter reads from port_data member and produces correct colour"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        cm.port_data[0, 0, 0, 0, 0, 0] = 10.0
        with mock.patch.object(cm, 'get_metric_min_max', return_value=(0.0, 10.0)):
            colour = cm.get_port_colour(0, 0, 0, 0, 0, 0)

        assert colour == "#FF0000"

    def test_get_device_colour_returns_expected_hex(self, mock_cmn, sample_metrics_data):
        """Ensure device colour getter reads from device_data member and produces correct colour"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        cm.device_data[0, 0, 0, 0, 0, 0, 0] = 0.0
        with mock.patch.object(cm, 'get_metric_min_max', return_value=(0.0, 10.0)):
            colour = cm.get_device_colour(0, 0, 0, 0, 0, 0, 0)

        assert colour == "#FFFFFF"

    def test_palette_storage_and_usage(self, mock_cmn, sample_metrics_data):
        """Test that the palette is properly stored and used"""
        palette = QPalette()
        cm = CMNMetrics(mock_cmn, sample_metrics_data, palette)
        assert cm.palette is palette
        assert isinstance(cm.palette, QPalette)

    def test_custom_palette_affects_color_output(self, mock_cmn, sample_metrics_data):
        """Test that different palettes produce different base colors"""
        palette1 = QPalette()
        palette2 = QPalette()
        palette2.setColor(QPalette.ColorRole.Window, QColor(200, 200, 200))

        cm1 = CMNMetrics(mock_cmn, sample_metrics_data, palette1)
        cm2 = CMNMetrics(mock_cmn, sample_metrics_data, palette2)

        color1 = cm1._value_to_colour(0, 0, 100)
        color2 = cm2._value_to_colour(0, 0, 100)
        assert color1 != color2

    def test_dark_theme_palette(self, mock_cmn, sample_metrics_data):
        """Test color mapping with a dark theme palette"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, "#2D2D2D")

        cm = CMNMetrics(mock_cmn, sample_metrics_data, dark_palette)

        min_color = cm._value_to_colour(0, 0, 100)
        assert min_color == "#2D2D2D"
        max_color = cm._value_to_colour(100, 0, 100)
        assert max_color == "#FF0000"

    def test_light_theme_palette(self, mock_cmn, sample_metrics_data):
        """Test color mapping with a light theme palette"""
        light_palette = QPalette()
        light_palette.setColor(QPalette.ColorRole.Window, "#FFFFFF")

        cm = CMNMetrics(mock_cmn, sample_metrics_data, light_palette)

        min_color = cm._value_to_colour(0, 0, 100)
        assert min_color == "#FFFFFF"
        max_color = cm._value_to_colour(100, 0, 100)
        assert max_color == "#FF0000"
        mid_color = cm._value_to_colour(50, 0, 100)
        assert mid_color == "#FF7F7F"

    def test_get_metric_min_max_caches_correctly(self, mock_cmn, sample_metrics_data):
        """Ensure that get_metric_min_max uses cached values when it can"""
        cm = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())
        cm.xp_data[0, 0, 0, 0, 0] = 3.0
        cm.device_data[0, 0, 0, 0, 0, 0, 0] = 7.0

        original_min = min
        original_max = max

        with patch('builtins.min') as mock_min, patch('builtins.max') as mock_max:
            mock_min.side_effect = original_min
            mock_max.side_effect = original_max

            # First call would call min and max
            result1 = cm.get_metric_min_max(0, 0)
            assert mock_min.called
            assert mock_max.called

            mock_min.reset_mock()
            mock_max.reset_mock()

            # Second call should NOT call min and max (cached)
            result2 = cm.get_metric_min_max(0, 0)
            assert not mock_min.called
            assert not mock_max.called

        assert result1 == result2
        assert cm._last_min_max == result2

    def test_get_metric_min_max_caches_invalidate(self, mock_cmn, sample_metrics_data):
        """Ensure that get_metric_min_max recalculates when needed"""
        cm = CMNMetrics(mock_cmn, sample_metrics_data, QPalette())
        cm.xp_data[0, 0, 0, 0, 0] = 3.0
        cm.device_data[0, 0, 0, 0, 0, 0, 0] = 7.0

        original_min = min
        original_max = max

        with patch('builtins.min') as mock_min, patch('builtins.max') as mock_max:
            mock_min.side_effect = original_min
            mock_max.side_effect = original_max

            # First call would call min and max
            _ = cm.get_metric_min_max(0, 0)
            assert mock_min.called
            assert mock_max.called

            mock_min.reset_mock()
            mock_max.reset_mock()

            # Second call should cause recalculation
            _ = cm.get_metric_min_max(1, 0)
            assert mock_min.called
            assert mock_max.called

    def test_aggregation_basic_mean(self, mock_cmn):
        """Ensure basic device metric aggregation single port"""
        data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5] * 2,
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 2),
            NODE_COLUMN_NAME: [
                "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (101) at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0]
        })

        metrics = CMNMetrics(mock_cmn, data, QPalette())

        # check device values
        time_idx = 0
        metric_idx = 0
        mesh_idx = 0
        y, x, port = 0, 0, 0

        # Check initial device data
        device_values = metrics.device_data[time_idx, metric_idx, mesh_idx, y, x, port, :2]
        assert np.allclose(device_values, [10.0, 20.0])

        # Check port data is mean of device data: (10 + 20)/2 = 15
        port_value = metrics.port_data[time_idx, metric_idx, mesh_idx, y, x, port]
        assert np.isclose(port_value, 15.0)

        # Check XP data is mean over ports - only one port so same as port mean
        xp_value = metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x]
        assert np.isclose(xp_value, 15.0)

    def test_aggregation_with_empty_ports(self, mock_cmn):
        """Test that empty ports dont contribute data to aggregation"""
        mesh = mock_cmn.meshes[0]
        xp = mesh["xps"][0, 0]
        xp["ports"][1]["num_devices"] = 0  # simulat empty port 1

        # Prepare data for devices only on port 0
        data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5],
            METRICS_COLUMN_NAME: pd.Categorical(["metric1", "metric1"]),
            NODE_COLUMN_NAME: [
                "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (101) at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 20.0]
        })

        metrics = CMNMetrics(mock_cmn, data, QPalette())

        time_idx = 0
        metric_idx = 0
        mesh_idx = 0
        y, x = 0, 0

        port_0_val = metrics.port_data[time_idx, metric_idx, mesh_idx, y, x, 0]
        assert np.isclose(port_0_val, 15.0)

        # port 1 should not have a value
        port_1_val = metrics.port_data[time_idx, metric_idx, mesh_idx, y, x, 1]
        assert port_1_val == 0

        # only contribution from port 0
        xp_val = metrics.xp_data[time_idx, metric_idx, mesh_idx, y, x]
        assert np.isclose(xp_val, 15.0)

    def test_aggregation_multiple_time_and_metrics(self, mock_cmn):
        """Test that aggregatinos is metric independant"""
        data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 0.5, 1.0, 1.0],
            METRICS_COLUMN_NAME: pd.Categorical(["metric1", "metric2", "metric1", "metric2"]),
            NODE_COLUMN_NAME: [
                "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (100) at X=0 Y=0 Port=0",
                "HN-F (100) at X=0 Y=0 Port=0"
            ],
            VALUE_COLUMN_NAME: [10.0, 100.0, 20.0, 200.0]
        })

        metrics = CMNMetrics(mock_cmn, data, QPalette())

        time_idx_0 = metrics.time_stamps.tolist().index(0.5)
        time_idx_1 = metrics.time_stamps.tolist().index(1.0)
        metric_idx_1 = metrics.metric_id_map["metric1"]
        metric_idx_2 = metrics.metric_id_map["metric2"]
        mesh_idx = 0
        y, x, port = 0, 0, 0

        # Device data should match input
        dev_val_0_t_0 = metrics.device_data[time_idx_0, metric_idx_1, mesh_idx, y, x, port, 0]
        dev_val_1_t_0 = metrics.device_data[time_idx_0, metric_idx_2, mesh_idx, y, x, port, 0]
        dev_val_0_t_1 = metrics.device_data[time_idx_1, metric_idx_1, mesh_idx, y, x, port, 0]
        dev_val_1_t_1 = metrics.device_data[time_idx_1, metric_idx_2, mesh_idx, y, x, port, 0]
        assert np.isclose(dev_val_0_t_0, 10.0)
        assert np.isclose(dev_val_1_t_0, 100.0)
        assert np.isclose(dev_val_0_t_1, 20.0)
        assert np.isclose(dev_val_1_t_1, 200.0)

        # Values from different metrics should not mix
        port_val_0 = metrics.port_data[time_idx_0, metric_idx_1, mesh_idx, y, x, port]
        port_val_1 = metrics.port_data[time_idx_0, metric_idx_2, mesh_idx, y, x, port]
        xp_val_0 = metrics.xp_data[time_idx_0, metric_idx_1, mesh_idx, y, x]
        xp_val_1 = metrics.xp_data[time_idx_0, metric_idx_2, mesh_idx, y, x]
        port_val_0_t1 = metrics.port_data[time_idx_1, metric_idx_1, mesh_idx, y, x, port]
        port_val_1_t1 = metrics.port_data[time_idx_1, metric_idx_2, mesh_idx, y, x, port]
        xp_val_0_t1 = metrics.xp_data[time_idx_1, metric_idx_1, mesh_idx, y, x]
        xp_val_1_t1 = metrics.xp_data[time_idx_1, metric_idx_2, mesh_idx, y, x]

        assert np.isclose(port_val_0, 10.0)
        assert np.isclose(port_val_1, 100.0)
        assert np.isclose(xp_val_0, 10.0)
        assert np.isclose(xp_val_1, 100.0)
        assert np.isclose(port_val_0_t1, 20.0)
        assert np.isclose(port_val_1_t1, 200.0)
        assert np.isclose(xp_val_0_t1, 20.0)
        assert np.isclose(xp_val_1_t1, 200.0)


class TestCMNMetricsOutlierRemoval:
    """Tests for the outlier removal functionality."""

    @pytest.fixture
    def mock_cmn_simple(self):
        """Simple mock CMN for outlier tests."""
        mock_cmn = MagicMock(spec=CMN)
        mock_cmn.num_meshes = 1
        mock_meshes = np.zeros(1, dtype=mesh_dtype)
        mock_cmn.meshes = mock_meshes
        return mock_cmn

    def test_outlier_removal_basic(self, mock_cmn_simple):
        """Test basic outlier removal functionality."""
        # Create data with outliers
        data_with_outliers = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 5.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 10),
            NODE_COLUMN_NAME: ["Global"] * 10,
            VALUE_COLUMN_NAME: [10, 12, 11, 13, 9, 1000, 8, 14, 10, 12]
        })  # Outlier                              ^^^^

        metrics = CMNMetrics(mock_cmn_simple, data_with_outliers, QPalette())

        global_values = metrics.global_data[:, 0, 0]
        assert 1000 not in global_values

    def test_outlier_removal_extreme_values(self, mock_cmn_simple):
        """Test removal of extremely large values (>1e10)."""
        extreme_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 3.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 6),
            NODE_COLUMN_NAME: ["Global"] * 6,
            VALUE_COLUMN_NAME: [10, 12, 11, 1e15, 9, 13]
        })  # extreme value                 ^^^^

        metrics = CMNMetrics(mock_cmn_simple, extreme_data, QPalette())

        global_values = metrics.global_data[:, 0, 0]
        assert all(val < 1e10 for val in global_values)

    def test_outlier_removal_separate_metrics(self, mock_cmn_simple):
        """Test that outlier removal is done separately for each metric."""
        mixed_metrics_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 10.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(
                ["metric1"] * 10 + ["metric2"] * 10
            ),
            NODE_COLUMN_NAME: ["Global"] * 20,
            VALUE_COLUMN_NAME: [
                10, 12, 11, 13, 100, 9, 8, 14, 10, 12,
                #               ^^^ metric1 outlier
                100, 120, 101, 130, 1000, 90, 180, 140, 100, 102
                #                   ^^^^ metric2 outlier
            ]
        })

        metrics = CMNMetrics(mock_cmn_simple, mixed_metrics_data, QPalette())
        assert len(metrics.metric_names) == 2

        metric1_data = metrics.global_data[:, 0, 0]
        metric2_data = metrics.global_data[:, 1, 0]

        assert 100 not in metric1_data
        assert 1000 not in metric2_data

    def test_outlier_removal_insufficient_data(self, mock_cmn_simple):
        """Test behavior when there's insufficient data for outlier removal."""
        insufficient_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 1.0, 1.5],  # Only 3 data points
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 3),
            NODE_COLUMN_NAME: ["Global"] * 3,
            VALUE_COLUMN_NAME: [10, 1000, 12]  # One potential outlier
        })

        metrics = CMNMetrics(mock_cmn_simple, insufficient_data, QPalette())
        assert metrics is not None
        assert np.array_equal(metrics.global_data[:, 0, 0], np.array([10, 1000, 12]))

    def test_outlier_removal_global_vs_local(self, mock_cmn_simple):
        """Test that global and local metrics are processed separately."""
        mixed_node_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 10.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 20),
            NODE_COLUMN_NAME: (
                ["Global"] * 10 + ["XP at X=0 Y=0"] * 10
            ),
            VALUE_COLUMN_NAME: [
                10, 12, 11, 13, 100, 9, 8, 14, 10, 12,
                #               ^^^ Global outlier
                100, 120, 101, 130, 1000, 90, 180, 140, 100, 102
                #                   ^^^^ XP outlier
            ]
        })

        metrics = CMNMetrics(mock_cmn_simple, mixed_node_data, QPalette())
        XP_data = metrics.xp_data[:, :, 0, 0, 0]  # values for XP(0,0)

        assert 1000 not in XP_data
        assert 100 not in metrics.global_data
