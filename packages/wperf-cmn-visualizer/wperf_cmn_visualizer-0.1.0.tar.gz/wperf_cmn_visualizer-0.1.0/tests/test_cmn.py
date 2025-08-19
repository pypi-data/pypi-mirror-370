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
from wperf_cmn_visualizer.cmn import CMN, CMN_MAX_MESH_WIDTH, CMN_MAX_MESH_HEIGHT
from wperf_cmn_visualizer.cmn import CMN_MAX_PORTS, CMN_MAX_CHILDS, CMN_XP_DEVICE_ID, CMN_TYPE_STR_MAX_LEN


class TestCMN:
    """Tests for the main CMN class."""

    def test_empty_mesh_data(self):
        """
        Test to ensure CMN constructor fails on empty input.
        """
        topology_data = {"elements": []}
        with pytest.raises(AssertionError):
            _ = CMN(topology_data)

    def test_mesh_dimension_validation(self):
        """Test mesh dimension validation."""
        # Test zero dimensions
        mesh_data = {"X": 0, "Y": 2, "xps": [{"X": 0, "Y": 0, "id": 100}]}
        topology_data = {"elements": [{"config": mesh_data}]}
        with pytest.raises(AssertionError):
            CMN(topology_data)

        mesh_data = {"X": 2, "Y": 0, "xps": [{"X": 0, "Y": 0, "id": 100}]}
        topology_data = {"elements": [{"config": mesh_data}]}
        with pytest.raises(AssertionError):
            CMN(topology_data)

        # Test oversized dimensions
        mesh_data = {"X": CMN_MAX_MESH_WIDTH + 1, "Y": 2, "xps": [{"X": 0, "Y": 0, "id": 100}]}
        topology_data = {"elements": [{"config": mesh_data}]}
        with pytest.raises(AssertionError):
            CMN(topology_data)

        mesh_data = {"X": 2, "Y": CMN_MAX_MESH_HEIGHT + 1, "xps": [{"X": 0, "Y": 0, "id": 100}]}
        topology_data = {"elements": [{"config": mesh_data}]}
        with pytest.raises(AssertionError):
            CMN(topology_data)

    def test_xp_data_loading_basic(self):
        """Test loading XP data into mesh structure."""
        mesh_data = {
            "X": 2, "Y": 2,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100, "logical_id": 200,
                    "dtc": 1, "n_ports": 2
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        xp = mesh["xps"][0, 0]
        assert xp["node_info"]["coord"]["x"] == 0
        assert xp["node_info"]["coord"]["y"] == 0
        assert xp["node_info"]["nodeid"] == 100
        assert xp["node_info"]["logicalid"] == 200
        assert xp["node_info"]["type"] == CMN_XP_DEVICE_ID
        assert xp["node_info"]["type_str"] == "XP"
        assert xp["dtc_domain"] == 1
        assert xp["num_device_ports"] == 2

    def test_xp_data_loading_out_of_bounds(self):
        """Test XP data loading ignores out-of-bounds coordinates."""
        mesh_data = {
            "X": 2, "Y": 2,
            "xps": [
                {"X": 0, "Y": 0, "id": 100},  # Valid
                {"X": 5, "Y": 5, "id": 200},  # Out of bounds
                {"X": -1, "Y": 0, "id": 300}  # Negative coords
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        # Valid XP should be loaded
        assert mesh["xps"][0, 0]["node_info"]["nodeid"] == 100
        # Out of bounds XPs should not affect the mesh
        # All other positions should have default values (0)
        assert mesh["xps"][0, 1]["node_info"]["nodeid"] == 0
        assert mesh["xps"][1, 0]["node_info"]["nodeid"] == 0
        assert mesh["xps"][1, 1]["node_info"]["nodeid"] == 0

    def test_port_data_loading(self):
        """Test loading port data with devices."""
        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100,
                    "ports": [
                        {
                            "port": 0, "type": 8, "type_s": "HN_T",
                            "cal": True,
                            "devices": [
                                {"id": 1, "logical_id": 2, "type": 4, "type_s": "HNI"},
                                {"id": 3, "logical_id": 4, "type": 1, "type_s": "DN"}
                            ]
                        }
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        assert port["type"] == 8
        assert port["type_str"] == "HN_T"
        assert port["cal"]
        assert port["num_devices"] == 2

        # Check first device
        device0 = port["devices"][0]
        assert device0["coord"]["x"] == 0
        assert device0["coord"]["y"] == 0
        assert device0["nodeid"] == 1
        assert device0["logicalid"] == 2
        assert device0["type"] == 4
        assert device0["type_str"] == "HNI"

        # Check second device
        device1 = port["devices"][1]
        assert device1["nodeid"] == 3
        assert device1["logicalid"] == 4
        assert device1["type"] == 1
        assert device1["type_str"] == "DN"

    def test_port_data_boundary_conditions(self):
        """Test port data loading with boundary conditions."""
        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100,
                    "ports": [
                        # Invalid port numbers should be ignored
                        {"port": -1, "type": 1, "type_s": "invalid"},
                        {"port": CMN_MAX_PORTS, "type": 2, "type_s": "invalid"},
                        {"port": 999, "type": 3, "type_s": "invalid"},
                        # Valid port
                        {"port": 0, "type": 8, "type_s": "HN_T"},
                        # Missing port key
                        {"type": 9, "type_s": "no_port"}
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        # Only the valid port should be loaded
        port = mesh["xps"][0, 0]["ports"][0]
        assert port["type"] == 8
        assert port["type_str"] == "HN_T"
        assert port["num_devices"] == 0
        # Other ports should have default values
        for i in range(1, CMN_MAX_PORTS):
            assert mesh["xps"][0, 0]["ports"][i]["type"] == 0
            assert mesh["xps"][0, 0]["ports"][i]["num_devices"] == 0

    def test_device_overflow_handling(self):
        """Test that excess devices are ignored."""
        # Create more devices than CMN_MAX_CHILDS
        devices = []
        for i in range(CMN_MAX_CHILDS + 1):
            devices.append({"id": i, "logical_id": i, "type": 1, "type_s": f"device_{i}"})

        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100,
                    "ports": [
                        {"port": 0, "type": 8, "type_s": "HN_T", "devices": devices}
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)  # should not assert

        mesh = cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        assert port["num_devices"] == CMN_MAX_CHILDS
        for i, device in enumerate(port["devices"]):
            assert device["nodeid"] == i
            assert device["type_str"] == f"device_{i}"

    def test_string_truncation(self):
        """Test that long strings are properly truncated."""
        long_string = "a" * (CMN_TYPE_STR_MAX_LEN + 10)  # Longer than CMN_TYPE_STR_MAX_LEN

        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100,
                    "ports": [
                        {
                            "port": 0, "type": 8, "type_s": long_string,
                            "devices": [
                                {"id": 1, "logical_id": 2, "type": 4, "type_s": long_string}
                            ]
                        }
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)  # should not fail

        mesh = cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        device = port["devices"][0]
        assert port["num_devices"] == 1
        # Strings should be truncated to CMN_TYPE_STR_MAX_LEN
        assert len(port["type_str"]) == CMN_TYPE_STR_MAX_LEN
        assert len(device["type_str"]) == CMN_TYPE_STR_MAX_LEN
        assert port["type_str"] == "a" * CMN_TYPE_STR_MAX_LEN
        assert device["type_str"] == "a" * CMN_TYPE_STR_MAX_LEN

    def test_missing_optional_fields(self):
        """Test handling of missing optional fields with default values."""
        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0,
                    # Missing: id, logical_id, dtc, n_ports
                    "ports": [
                        {
                            "port": 0,
                            # Missing: type, type_s, cal
                            "devices": [
                                {
                                    # Missing: id, logical_id, type, type_s
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        xp = mesh["xps"][0, 0]
        assert xp["node_info"]["nodeid"] == 0
        assert xp["node_info"]["logicalid"] == 0
        assert xp["dtc_domain"] == 0
        assert xp["num_device_ports"] == 0

        port = xp["ports"][0]
        assert port["type"] == 0
        assert port["type_str"] == "unknown"
        assert not port["cal"]
        assert port["num_devices"] == 1

        device = port["devices"][0]
        assert device["nodeid"] == 0
        assert device["logicalid"] == 0
        assert device["type"] == 0
        assert device["type_str"] == "unknown"

    def test_num_devices_empty_devices_list(self):
        """Test num_devices field with empty devices list."""
        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100,
                    "ports": [
                        {
                            "port": 0, "type": 8, "type_s": "HN_T",
                            "devices": []  # Empty devices list
                        }
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        assert port["num_devices"] == 0

    def test_num_devices_no_devices_field(self):
        """Test num_devices field when devices field is missing."""
        mesh_data = {
            "X": 1, "Y": 1,
            "xps": [
                {
                    "X": 0, "Y": 0, "id": 100,
                    "ports": [
                        {
                            "port": 0, "type": 8, "type_s": "HN_T"
                            # No devices field
                        }
                    ]
                }
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        mesh = cmn.meshes[0]
        port = mesh["xps"][0, 0]["ports"][0]
        assert port["num_devices"] == 0

    def test_cmn_initialization_single_mesh(self):
        """Test CMN initialization with a single mesh."""
        mesh_data = {
            "X": 2, "Y": 2,
            "xps": [
                {"X": 0, "Y": 0, "id": 100},
            ]
        }
        topology_data = {
            "elements": [
                {"config": mesh_data}
            ]
        }
        cmn = CMN(topology_data)

        assert cmn.num_meshes == 1
        assert cmn.meshes.shape == (1,)
        assert cmn.meshes[0]["x_dim"] == 2
        assert cmn.meshes[0]["y_dim"] == 2

    def test_cmn_initialization_multiple_meshes(self):
        """Test CMN initialization with multiple meshes."""
        mesh_data = {
            "X": 2, "Y": 2,
            "xps": [
                {"X": 0, "Y": 0, "id": 100},
            ]
        }
        topology_data = {
            "elements": [
                {"config": mesh_data},
                {"config": mesh_data},
                {"config": mesh_data}
            ]
        }
        cmn = CMN(topology_data)

        assert cmn.num_meshes == 3
        assert cmn.meshes.shape == (3,)

    def test_cmn_initialization_empty_elements(self):
        """Test CMN initialization with empty elements list fails."""
        topology_data = {"elements": []}
        with pytest.raises(AssertionError):
            _ = CMN(topology_data)

    def test_get_view_basic(self):
        """Test get_view basic functionality"""
        mesh_data = {
            "X": 3, "Y": 3,
            "xps": [
                {"X": 0, "Y": 0, "id": 1},
                {"X": 1, "Y": 0, "id": 2},
                {"X": 2, "Y": 0, "id": 3},
                {"X": 0, "Y": 1, "id": 4},
                {"X": 1, "Y": 1, "id": 5},
                {"X": 2, "Y": 1, "id": 6},
                {"X": 0, "Y": 2, "id": 7},
                {"X": 1, "Y": 2, "id": 8},
                {"X": 2, "Y": 2, "id": 9},
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        view = cmn.get_view(0, 0, 1, 0, 1)
        # Check shape
        assert view.shape == (2, 2)
        # Check ids of nodes in view are correct
        ids = [view[i, j]["node_info"]["nodeid"] for i in range(2) for j in range(2)]
        expected_ids = [1, 2, 4, 5]
        assert ids == expected_ids

    def test_get_view_out_of_bounds(self):
        """
        Test get_view with out of bounds access.
        Ensure returned values are clamped to bounds.
        """
        mesh_data = {
            "X": 2, "Y": 2,
            "xps": [
                {"X": 0, "Y": 0, "id": 10},
                {"X": 1, "Y": 0, "id": 20},
                {"X": 0, "Y": 1, "id": 30},
                {"X": 1, "Y": 1, "id": 40},
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)

        # Negative min_row and min_col get clamped to 0
        view = cmn.get_view(0, -5, 1, -5, 1)
        assert view.shape == (2, 2)
        assert view[0, 0]["node_info"]["nodeid"] == 10  # information check
        # max_row and max_col beyond dimensions get clamped
        view = cmn.get_view(0, 0, 10, 0, 10)
        assert view.shape == (2, 2)

    def test_get_view_inverted_ranges(self):
        """
        Test get_view return empty view for invalid range.
        """
        mesh_data = {
            "X": 2, "Y": 2,
            "xps": [
                {"X": 0, "Y": 0, "id": 1},
                {"X": 1, "Y": 0, "id": 2},
                {"X": 0, "Y": 1, "id": 3},
                {"X": 1, "Y": 1, "id": 4},
            ]
        }
        topology_data = {"elements": [{"config": mesh_data}]}
        cmn = CMN(topology_data)
        view = cmn.get_view(0, 1, 0, 1, 0)
        assert view.size == 0
