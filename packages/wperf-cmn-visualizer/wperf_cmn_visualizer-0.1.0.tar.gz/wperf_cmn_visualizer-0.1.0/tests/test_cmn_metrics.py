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
from unittest.mock import MagicMock
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

    def test_metrics_initialization_basic(self, mock_cmn, sample_metrics_data):
        """Test basic CMNMetrics initialization."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data)

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
        assert metrics.global_data.shape == (2, 1)

    def test_xp_data_loading(self, mock_cmn, sample_metrics_data):
        """Test loading XP metric data."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data)

        # Check XP at X=0 Y=0, time=0.5, metric1
        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["metric_id"] == 0  # metric1
        assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["value"] == 10.5

        # Check XP at X=1 Y=0, time=0.5, metric2
        y, x = 0, 1
        assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["metric_id"] == 1  # metric2
        assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["value"] == 20.3

        # Check XP at X=0 Y=1, time=1.0, metric1
        time_idx = 1
        y, x = 1, 0
        assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["metric_id"] == 0  # metric1
        assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["value"] == 15.2

    def test_global_data_loading(self, mock_cmn, sample_metrics_data):
        """Test loading global metric data."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data)

        time_idx = 1
        mesh_idx = 0
        assert metrics.global_data["metric_id"][time_idx, mesh_idx] == 2  # metric3
        assert metrics.global_data["value"][time_idx, mesh_idx] == 40.1

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

        metrics = CMNMetrics(mock_cmn, edge_case_data)

        time_idx = 0
        mesh_idx = 0

        # Check global data
        assert metrics.global_data["value"][time_idx, mesh_idx] == 1.0

        # Check valid XP
        assert metrics.data[time_idx, mesh_idx, 0, 0]["xp_metric"]["value"] == 2.0

        # Check valid device
        assert metrics.data[time_idx, mesh_idx, 0, 0]["port_devices"][0, 0]["value"] == 4.0

        # Check out of bounds XP is not loaded (should remain 0)
        for y in range(CMN_MAX_MESH_HEIGHT):
            for x in range(CMN_MAX_MESH_WIDTH):
                if y == 0 and x == 0:
                    continue  # Skip the valid one
                assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["value"] == 0.0

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

        metrics = CMNMetrics(mock_cmn, invalid_port_data)

        # Only valid port should be loaded
        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0

        # Valid port should have data
        assert metrics.data[time_idx, mesh_idx, y, x]["port_devices"][0, 0]["value"] == 10.0

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

        metrics = CMNMetrics(mock_cmn, nodeid_data)

        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        port = 0

        assert metrics.data[time_idx, mesh_idx, y, x]["port_devices"][port, 0]["value"] == 10.0
        assert metrics.data[time_idx, mesh_idx, y, x]["port_devices"][port, 1]["value"] == 20.0
        assert metrics.data[time_idx, mesh_idx, y, x]["port_devices"][port, 2]["value"] == 30.0

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

        metrics = CMNMetrics(mock_cmn, multi_time_data)

        assert len(metrics.time_stamps) == 3
        assert metrics.time_stamps[0] == 0.5
        assert metrics.time_stamps[1] == 1.0
        assert metrics.time_stamps[2] == 1.5

        # Check data at different time stamps
        mesh_idx = 0

        # XP at X=0 Y=0, metric1
        assert metrics.data[0, mesh_idx, 0, 0]["xp_metric"]["value"] == 10.0
        assert metrics.data[1, mesh_idx, 0, 0]["xp_metric"]["value"] == 20.0
        assert metrics.data[2, mesh_idx, 0, 0]["xp_metric"]["value"] == 30.0

        # XP at X=1 Y=0, metric2
        assert metrics.data[0, mesh_idx, 0, 1]["xp_metric"]["value"] == 15.0
        assert metrics.data[1, mesh_idx, 0, 1]["xp_metric"]["value"] == 25.0
        assert metrics.data[2, mesh_idx, 0, 1]["xp_metric"]["value"] == 35.0

    def test_empty_metrics_data(self, mock_cmn):
        """Test handling of empty metrics DataFrame."""
        empty_data = pd.DataFrame({
            TIME_COLUMN_NAME: pd.Series([], dtype='float64'),
            METRICS_COLUMN_NAME: pd.Categorical([]),
            NODE_COLUMN_NAME: pd.Series([], dtype='string'),
            VALUE_COLUMN_NAME: pd.Series([], dtype='float64')
        })

        metrics = CMNMetrics(mock_cmn, empty_data)

        assert len(metrics.metric_names) == 0
        assert len(metrics.metric_id_map) == 0
        assert len(metrics.time_stamps) == 0
        assert metrics.num_time_stamps == 0

        # Data array should still be initialized but empty in time dimension
        assert metrics.data.shape[0] == 0
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

        metrics = CMNMetrics(mock_cmn, malformed_data)

        # Only the valid XP should be loaded
        time_idx = 0
        mesh_idx = 0
        assert metrics.data[time_idx, mesh_idx, 0, 0]["xp_metric"]["value"] == 10.0

        # All other positions should remain at default values
        for y in range(CMN_MAX_MESH_HEIGHT):
            for x in range(CMN_MAX_MESH_WIDTH):
                if y == 0 and x == 0:  # ignore valid case
                    continue
                assert metrics.data[time_idx, mesh_idx, y, x]["xp_metric"]["value"] == 0.0

    def test_metrics_hash_consistency(self, mock_cmn, sample_metrics_data):
        """Test that metrics hash is consistent with metrics array."""
        metrics = CMNMetrics(mock_cmn, sample_metrics_data)

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

        metrics = CMNMetrics(mock_cmn, unsorted_time_data)

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

        metrics = CMNMetrics(mock_cmn, device_data)  # should not crash

        time_idx = 0
        mesh_idx = 0
        y, x = 0, 0
        port_idx = 0

        for i in range(CMN_MAX_CHILDS):
            assert metrics.data[time_idx, mesh_idx, y, x]["port_devices"][port_idx, i]["value"] == i


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

        metrics = CMNMetrics(mock_cmn_simple, data_with_outliers)

        global_values = metrics.global_data["value"][metrics.global_data["value"] != 0]
        assert 1000 not in global_values

    def test_outlier_removal_extreme_values(self, mock_cmn_simple):
        """Test removal of extremely large values (>1e10)."""
        extreme_data = pd.DataFrame({
            TIME_COLUMN_NAME: list(np.arange(0.5, 3.5, 0.5)),
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 6),
            NODE_COLUMN_NAME: ["Global"] * 6,
            VALUE_COLUMN_NAME: [10, 12, 11, 1e15, 9, 13]
        })  # extreme value                 ^^^^

        metrics = CMNMetrics(mock_cmn_simple, extreme_data)

        global_values = metrics.global_data["value"][metrics.global_data["value"] != 0]
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

        metrics = CMNMetrics(mock_cmn_simple, mixed_metrics_data)
        assert len(metrics.metric_names) == 2

        metric1_data = metrics.global_data[metrics.global_data["metric_id"] == 0]
        metric2_data = metrics.global_data[metrics.global_data["metric_id"] == 1]

        assert 100 not in metric1_data["value"]
        assert 1000 not in metric2_data["value"]

    def test_outlier_removal_insufficient_data(self, mock_cmn_simple):
        """Test behavior when there's insufficient data for outlier removal."""
        insufficient_data = pd.DataFrame({
            TIME_COLUMN_NAME: [0.5, 1.0, 1.5],  # Only 3 data points
            METRICS_COLUMN_NAME: pd.Categorical(["metric1"] * 3),
            NODE_COLUMN_NAME: ["Global"] * 3,
            VALUE_COLUMN_NAME: [10, 1000, 12]  # One potential outlier
        })

        metrics = CMNMetrics(mock_cmn_simple, insufficient_data)
        assert metrics is not None
        assert np.array_equal(metrics.global_data["value"].flatten(), np.array([10, 1000, 12]))

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

        metrics = CMNMetrics(mock_cmn_simple, mixed_node_data)
        XP_data = metrics.data[:, 0, 0, 0]["xp_metric"]["value"]  # values for XP(0,0)

        assert 1000 not in XP_data
        assert 100 not in metrics.global_data["value"]
