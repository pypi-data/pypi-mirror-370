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

import pandas as pd
import pandas.testing as pdt
from unittest.mock import mock_open, patch
from wperf_cmn_visualizer.telemetry_loader import cmn_telemetry_loader
from wperf_cmn_visualizer.telemetry_loader import TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME


class TestTelemetryLoader:
    """Tests for the telemetry loader functionality."""

    def test_load_valid_csv_file(self):
        """Test loading a valid CSV telemetry file."""
        csv_content = """run,time,level,stage,group,metric,node,value,interrupted,units
1,0.500514296,2,0,,HNF SLC miss ratio with filters = hbt_lbt_filter.all_requests_selected,Global,45.3351605662493,No,Percentage
1,0.500514296,2,0,,HNF SLC miss ratio with filters = hbt_lbt_filter.all_requests_selected,HN-F (144) at X=1 Y=2 Port=0,48.247426210951204,No,Percentage"""

        expected_data = pd.DataFrame([
            {
                TIME_COLUMN_NAME: 0.500514296,
                METRICS_COLUMN_NAME: "HNF SLC miss ratio with filters = hbt_lbt_filter.all_requests_selected",
                NODE_COLUMN_NAME: "Global",
                VALUE_COLUMN_NAME: 45.3351605662493
            },
            {
                TIME_COLUMN_NAME: 0.500514296,
                METRICS_COLUMN_NAME: "HNF SLC miss ratio with filters = hbt_lbt_filter.all_requests_selected",
                NODE_COLUMN_NAME: "HN-F (144) at X=1 Y=2 Port=0",
                VALUE_COLUMN_NAME: 48.247426210951204
            }
        ])
        expected_data[METRICS_COLUMN_NAME] = expected_data[METRICS_COLUMN_NAME].astype("category")
        expected_data[NODE_COLUMN_NAME] = expected_data[NODE_COLUMN_NAME].astype("string")

        with patch("builtins.open", mock_open(read_data=csv_content)):
            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_file("test.csv")
            pdt.assert_frame_equal(loader.data.reset_index(drop=True), expected_data)

    def test_load_empty_csv_file(self):
        """Test loading an empty CSV file with headers only."""
        csv_content = "run,time,level,stage,group,metric,node,value,interrupted,units\n"

        with patch("builtins.open", mock_open(read_data=csv_content)):
            loader = cmn_telemetry_loader()
            loader.load_telemetry_from_file("empty.csv")
            assert loader.data.empty

    def test_load_nonexistent_file(self):
        """Test error handling when file doesn't exist."""
        loader = cmn_telemetry_loader()

        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with patch("builtins.print") as mock_print:
                loader.load_telemetry_from_file("nonexistent.csv")
                mock_print.assert_called_once_with("Error: File 'nonexistent.csv' not found.")
                assert loader.data.empty

    def test_initial_state(self):
        """Test the initial state of the loader."""
        loader = cmn_telemetry_loader()
        assert isinstance(loader.data, pd.DataFrame)
        assert loader.data.empty
