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
import json
from unittest.mock import mock_open, patch
from wperf_cmn_visualizer.topology_loader import cmn_topology_loader


class TestTopologyLoader:
    """Tests for the topology loader functionality."""

    def test_load_valid_json_file(self):
        """Test loading a valid JSON topology file."""
        test_data = {"elements": [{"config": {"X": 2, "Y": 2}}]}
        json_content = json.dumps(test_data)
        # mock open files
        with patch("builtins.open", mock_open(read_data=json_content)):
            loader = cmn_topology_loader()
            loader.load_topology_from_file("test.json")
            assert loader.data == test_data

    def test_load_nonexistent_file(self):
        """Test error handling when file doesn't exist."""
        loader = cmn_topology_loader()
        with pytest.raises(FileNotFoundError):
            loader.load_topology_from_file("nonexistent.json")

    def test_load_invalid_json(self):
        """Test error handling for malformed JSON."""
        invalid_json = '{"elements": [invalid json}'

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            loader = cmn_topology_loader()
            with pytest.raises(ValueError):
                loader.load_topology_from_file("test.json")

    def test_load_empty_file(self):
        """Test error handling for empty JSON file."""
        with patch("builtins.open", mock_open(read_data="")):
            loader = cmn_topology_loader()
            with pytest.raises(ValueError):
                loader.load_topology_from_file("test.json")

    def test_load_null_data(self):
        """Test error handling for null JSON data."""
        with patch("builtins.open", mock_open(read_data="null")):
            loader = cmn_topology_loader()
            with pytest.raises(AssertionError):
                loader.load_topology_from_file("test.json")
