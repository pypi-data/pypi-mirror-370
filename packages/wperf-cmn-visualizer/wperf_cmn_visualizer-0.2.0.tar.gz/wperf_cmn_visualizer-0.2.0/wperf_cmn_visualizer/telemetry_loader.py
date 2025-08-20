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

TIME_COLUMN_NAME: str = "time"
METRICS_COLUMN_NAME: str = "metric"
NODE_COLUMN_NAME: str = "node"
VALUE_COLUMN_NAME: str = "value"


class cmn_telemetry_loader:
    def __init__(self):
        self.data: pd.DataFrame = pd.DataFrame()

    def load_telemetry_from_file(self, filename: str) -> None:
        """
        Load telemetry data from file using pandas.
        Interprets specific columns with defined data types.
        """
        try:
            self.data = pd.read_csv(
                filename,
                usecols=[TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME],
                dtype={
                    TIME_COLUMN_NAME: "f8",
                    METRICS_COLUMN_NAME: "category",
                    NODE_COLUMN_NAME: "string",
                    VALUE_COLUMN_NAME: "f8",
                }
            )
            self.data.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
            self.data.dropna(inplace=True)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Failed to load telemetry from '{filename}': {e}")
