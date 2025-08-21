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
Telemetry loading abstraction layer.
"""
import pandas as pd
import os
import glob
import re

TIME_COLUMN_NAME: str = "time"
MESH_COLUMN_NAME: str = "mesh"
METRICS_COLUMN_NAME: str = "metric"
NODE_COLUMN_NAME: str = "node"
VALUE_COLUMN_NAME: str = "value"
NODEID_COLUMN_NAME: str = "nodeid"


class cmn_telemetry_loader:
    def __init__(self):
        self.data: pd.DataFrame = pd.DataFrame()

    def load_telemetry_from_path(self, path: str) -> None:
        """
        Load telemetry data from directory.
        Scans directory for CSV files matching the pattern:
        cmn<string>_<mesh_idx>_<timestamp>.csv.
        """
        if not os.path.isdir(path):
            return
        # fetch csv filess which match pattern
        csv_files = glob.glob(os.path.join(path, "cmn*_*_*.csv"))
        if not csv_files:
            return

        files_processed = 0
        files_failed = 0
        pattern = re.compile(r'cmn.*?_(\d+)_(\d+)\.csv$')

        for file_path in csv_files:
            try:
                # parse file name
                filename = os.path.basename(file_path)
                match = pattern.match(filename)
                if match:
                    mesh_idx = int(match.group(1))
                    timestamp = int(match.group(2)) / 1000
                else:
                    files_failed += 1
                    continue

                # Load the CSV file
                df = pd.read_csv(
                    file_path,
                    usecols=[METRICS_COLUMN_NAME, NODE_COLUMN_NAME, NODEID_COLUMN_NAME, VALUE_COLUMN_NAME],
                    dtype={
                        METRICS_COLUMN_NAME: "category",
                        NODE_COLUMN_NAME: "string",
                        NODEID_COLUMN_NAME: "UInt16",
                        VALUE_COLUMN_NAME: "f8",
                    }
                )

                if df.empty:
                    files_failed += 1
                    continue

                # Add the timestamp and mesh index columns from filename
                df[TIME_COLUMN_NAME] = timestamp
                df[MESH_COLUMN_NAME] = mesh_idx

                # Clean the data - replace empty strings with NaN
                df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)

                # drop NAs based on conditions
                # When Node column == Global, the nodeid maybe be empty
                df = df.loc[
                    df[NODE_COLUMN_NAME].notna()
                    & df[METRICS_COLUMN_NAME].notna()
                    & df[VALUE_COLUMN_NAME].notna()
                    & ((df[NODE_COLUMN_NAME] == "Global") | df[NODEID_COLUMN_NAME].notna())
                ]

                # Check if we have any data left after cleaning
                if df.empty:
                    files_failed += 1
                    continue

                self.data = df if self.data.empty else pd.concat([self.data, df], ignore_index=True)
                files_processed += 1
            except Exception:
                files_failed += 1
                continue
