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

import tempfile
from pathlib import Path

from wperf_cmn_visualizer.telemetry_loader import cmn_telemetry_loader
from wperf_cmn_visualizer.telemetry_loader import (
    TIME_COLUMN_NAME,
    MESH_COLUMN_NAME,
    METRICS_COLUMN_NAME,
    NODE_COLUMN_NAME,
    VALUE_COLUMN_NAME,
    NODEID_COLUMN_NAME
)


class TestTelemetryLoader:
    """Simple tests for the telemetry loader."""

    def test_initial_state(self):
        """Test the initial state of the loader."""
        loader = cmn_telemetry_loader()
        assert loader.data.empty

    def test_nonexistent_directory(self):
        """Test loading from directory that doesn't exist."""
        loader = cmn_telemetry_loader()
        loader.load_telemetry_from_path("/nonexistent/path")
        assert loader.data.empty

    def test_empty_directory(self):
        """Test loading from empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_path(temp_dir)
            assert loader.data.empty

    def test_directory_without_csvs(self):
        """Test loading from directory with no CSV files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "readme.txt").write_text("not a csv")

            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_path(temp_dir)
            assert loader.data.empty

    def test_directory_without_matching_pattern(self):
        """Test loading from directory with CSVs that don't match the pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "data.csv").write_text("header\nvalue")
            Path(temp_dir, "other_file.csv").write_text("header\nvalue")

            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_path(temp_dir)
            assert loader.data.empty

    def test_single_valid_csv_file(self):
        """Test loading a single valid CSV file."""
        csv_content = f"""{METRICS_COLUMN_NAME},{NODE_COLUMN_NAME},{NODEID_COLUMN_NAME},{VALUE_COLUMN_NAME}
metric1,Global,,10.5
metric1,Node1,1,20.5"""

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_file = Path(temp_dir, "cmn_test_1_1234567890000.csv")
            csv_file.write_text(csv_content)

            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_path(temp_dir)

            assert len(loader.data) == 2
            assert loader.data[TIME_COLUMN_NAME].iloc[0] == 1234567890.0
            assert loader.data[MESH_COLUMN_NAME].iloc[0] == 1
            assert "metric1" in loader.data[METRICS_COLUMN_NAME].values
            assert "Global" in loader.data[NODE_COLUMN_NAME].values

    def test_multiple_csv_files(self):
        """Test loading multiple valid CSV files."""
        csv_content1 = f"""{METRICS_COLUMN_NAME},{NODE_COLUMN_NAME},{NODEID_COLUMN_NAME},{VALUE_COLUMN_NAME}
metric1,Global,,10.5
"""
        csv_content2 = f"""{METRICS_COLUMN_NAME},{NODE_COLUMN_NAME},{NODEID_COLUMN_NAME},{VALUE_COLUMN_NAME}
metric2,Node1,1,20.5
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "cmn_test_1_1000.csv").write_text(csv_content1)
            Path(temp_dir, "cmn_test_2_20000.csv").write_text(csv_content2)

            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_path(temp_dir)

            # check data from both files
            assert len(loader.data) == 2
            assert 1.0 in loader.data[TIME_COLUMN_NAME].values
            assert 20.0 in loader.data[TIME_COLUMN_NAME].values
            assert 1 in loader.data[MESH_COLUMN_NAME].values
            assert 2 in loader.data[MESH_COLUMN_NAME].values

    def test_multiple_files_with_invalid_and_ignored(self):
        """Test loading from directory with valid and invalid files."""
        valid_csv = f"""{METRICS_COLUMN_NAME},{NODE_COLUMN_NAME},{NODEID_COLUMN_NAME},{VALUE_COLUMN_NAME}
metric1,Global,,10.5
"""
        invalid_csv = "this,is,not,valid,csv,data"

        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "cmn_valid_1_1000000000000.csv").write_text(valid_csv)
            Path(temp_dir, "cmn_invalid_2_2000000000000.csv").write_text(invalid_csv)
            Path(temp_dir, "not_matching_pattern.csv").write_text(valid_csv)

            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_path(temp_dir)

            # Should only load the valid file
            assert len(loader.data) == 1
            assert loader.data[MESH_COLUMN_NAME].iloc[0] == 1
            assert loader.data[TIME_COLUMN_NAME].iloc[0] == 1000000000.0
