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
CMN metrics data structures and operations.
"""

import numpy as np
import pandas as pd
from typing import Dict
from .cmn import CMN_MAX_PORTS, CMN_MAX_CHILDS, CMN_MAX_MESH_WIDTH, CMN_MAX_MESH_HEIGHT
from .cmn import CMN
from .telemetry_loader import TIME_COLUMN_NAME, METRICS_COLUMN_NAME, NODE_COLUMN_NAME, VALUE_COLUMN_NAME


class CMNMetrics:
    """
    Handles CMN metrics by storing them in structured numpy arrays
    indexed by time, mesh, and coordinates within the mesh.

    TODO:
        - support the use of multiple metrics at the same time.
        - support Global metrics

    NOTE:
        -CMNMetrics only supports one mesh. This is because input data from \
            Telemetry Solution's `topdown-tool` only supports 1 mesh.

    Attributes:
        self.metric_names (np.ndarray[dtype=str]): Compact list of unique names indexed by metric ids.
        self.metric_id_map (Dict[str, int]): Map from metric string to metric id
        self.time_stamps (np.ndarray[dtype=f8]): 1d numpy array of unique time stamps which which data is available.
        self.num_time_stamps (int): number of time_stamps
        self.data (np.nradday): 4d numpy array, index with self.data[time_stamp, mesh_index, XP coord Y, XP coord X]
    """
    def __init__(self, cmn: CMN, metrics_data: pd.DataFrame) -> None:
        """
        Contruct CMNMesh object.
        Args:
            cmn (CMN): Read-only CMN object used to validate input data. Invalid input is ignored.
            metrics_data (pd.DataFrame): Data frame from pandas loaded from cmn_telemtry_loader.
        """

        # Metric names and corresponding IDs (categorical for compactness)
        self.metric_names: np.ndarray = metrics_data[METRICS_COLUMN_NAME].cat.categories.to_numpy(dtype=str)
        self.metric_id_map: Dict[str, int] = {name: idx for idx, name in enumerate(self.metric_names)}
        self.num_metrics: int = len(self.metric_names)

        # Extract coordinate and node info using regex from the 'node' column
        # node column has three formats:
        # 1> "global" which indicates the entire mesh
        # 2> "XP at X=0 Y=0" which indicates a specific XP at given coordinate
        # 3> HN-F (101) at X=0 Y=0 Port=0 which indicates a device on a specific XP and port. Device identified using nodeid.
        node_info: pd.DataFrame = metrics_data[NODE_COLUMN_NAME].str.extract(
            r"^(?:(?P<device>.+?) \((?P<nodeid>\d+)\) at X=(?P<x_device>\d+) Y=(?P<y_device>\d+) Port=(?P<port>\d+)"
            r"|(?P<device_xp>XP) at X=(?P<x_xp>\d+) Y=(?P<y_xp>\d+)"
            r"|(?P<global>Global))$"
        )
        # remove outliers
        metrics_data, node_info = self._remove_outliers_mean_std(metrics_data, node_info)

        self.time_stamps: np.ndarray = np.sort(metrics_data[TIME_COLUMN_NAME].unique())
        self.num_time_stamps: int = len(self.time_stamps)

        # data holding members: Global level, XP level, Port level, Device level
        self.global_data: np.ndarray = np.zeros(
            shape=(self.num_time_stamps, self.num_metrics, cmn.num_meshes),
            dtype="f8"
        )
        self.xp_data: np.ndarray = np.zeros(
            shape=(
                self.num_time_stamps, self.num_metrics, cmn.num_meshes,
                CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH
            ),
            dtype="f8"
        )
        self.port_data: np.ndarray = np.zeros(
            shape=(
                self.num_time_stamps, self.num_metrics, cmn.num_meshes,
                CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH,
                CMN_MAX_PORTS
            ),
            dtype="f8"
        )
        self.device_data: np.ndarray = np.zeros(
            shape=(
                self.num_time_stamps, self.num_metrics, cmn.num_meshes,
                CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH,
                CMN_MAX_PORTS, CMN_MAX_CHILDS
            ),
            dtype="f8"
        )

        time_indices = np.searchsorted(self.time_stamps, metrics_data[TIME_COLUMN_NAME].to_numpy())
        metric_ids = metrics_data[METRICS_COLUMN_NAME].cat.codes.to_numpy()
        metric_values = metrics_data[VALUE_COLUMN_NAME].to_numpy()

        self._load_global_data(node_info, time_indices, metric_ids, metric_values)
        self._load_device_data(node_info, cmn, time_indices, metric_ids, metric_values)
        self._load_xp_data(node_info, time_indices, metric_ids, metric_values)

        # cache for get_metric_min_max method
        self._last_metric_id = None
        self._last_mesh_idx = None
        self._last_min_max = (0.0, 0.0)

    def _remove_outliers_mean_std(
        self,
        df: pd.DataFrame, node_info: pd.DataFrame,
        std_multiplier: float = 2.0
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Properly removes outliers by filtering per-metric and per-node-type.
        Keeps values within [mean - N*std, mean + N*std] AND < 1e6.
        """
        keep_mask = pd.Series(False, index=df.index)

        global_mask = node_info["global"].notna()
        non_global_mask = ~global_mask

        for metric in self.metric_names:
            metric_mask = df[METRICS_COLUMN_NAME] == metric

            # GLOBAL
            subset_global = df[metric_mask & global_mask]
            subset_global = subset_global[subset_global[VALUE_COLUMN_NAME] < 1e10]

            if len(subset_global) >= 4:
                values = subset_global[VALUE_COLUMN_NAME]
                mean = values.mean()
                std = values.std()
                lower = mean - std_multiplier * std
                upper = mean + std_multiplier * std
                valid_mask = (values >= lower) & (values <= upper)
                keep_mask.loc[subset_global[valid_mask].index] = True
            else:
                keep_mask.loc[subset_global.index] = True

            # NON-GLOBAL
            subset_local = df[metric_mask & non_global_mask]
            subset_local = subset_local[subset_local[VALUE_COLUMN_NAME] < 1e10]

            if len(subset_local) >= 4:
                values = subset_local[VALUE_COLUMN_NAME]
                mean = values.mean()
                std = values.std()
                lower = mean - std_multiplier * std
                upper = mean + std_multiplier * std
                valid_mask = (values >= lower) & (values <= upper)
                keep_mask.loc[subset_local[valid_mask].index] = True
            else:
                keep_mask.loc[subset_local.index] = True

        filtered_df = df[keep_mask].reset_index(drop=True)
        filtered_node_info = node_info[keep_mask].reset_index(drop=True)

        return filtered_df, filtered_node_info

    def _load_global_data(self, node_info, time_indices, metric_ids, metric_values) -> None:
        global_mask = node_info["global"].notna()
        if global_mask.any():
            global_rows = np.where(global_mask)[0]
            global_t = time_indices[global_rows]
            global_m = np.zeros(len(global_rows), dtype=int)  # mesh = 0
            global_ids = metric_ids[global_rows]
            global_vals = metric_values[global_rows]
            self.global_data[global_t, global_ids, global_m] = global_vals

    def _load_xp_data(self, node_info, time_indices, metric_ids, metric_values) -> None:
        x_xp = node_info["x_xp"].astype("float")
        y_xp = node_info["y_xp"].astype("float")
        xp_mask = (
            x_xp.notna() & y_xp.notna()
            & (x_xp >= 0) & (x_xp < CMN_MAX_MESH_WIDTH)
            & (y_xp >= 0) & (y_xp < CMN_MAX_MESH_HEIGHT)
        )

        if xp_mask.any():
            xp_rows = np.where(xp_mask)[0]
            xp_t = time_indices[xp_rows]
            xp_m = np.zeros(len(xp_rows), dtype=int)
            xp_y = node_info.loc[xp_mask, "y_xp"].astype(int).to_numpy()
            xp_x = node_info.loc[xp_mask, "x_xp"].astype(int).to_numpy()
            xp_ids = metric_ids[xp_rows]
            xp_vals = metric_values[xp_rows]
            self.xp_data[xp_t, xp_ids, xp_m, xp_y, xp_x] = xp_vals

    def _load_device_data(self, node_info, cmn, time_indices, metric_ids, metric_values) -> None:
        x_dev = node_info["x_device"].astype("float")
        y_dev = node_info["y_device"].astype("float")
        port_dev = node_info["port"].astype("float")

        device_mask = (
            x_dev.notna() & y_dev.notna() & port_dev.notna()
            & (x_dev >= 0) & (x_dev < CMN_MAX_MESH_WIDTH)
            & (y_dev >= 0) & (y_dev < CMN_MAX_MESH_HEIGHT)
            & (port_dev >= 0) & (port_dev < CMN_MAX_PORTS)
        )

        if device_mask.any():
            dev_rows = np.where(device_mask)[0]
            dev_t = time_indices[dev_rows]
            dev_nodeids = node_info.loc[device_mask, "nodeid"].astype(int)
            dev_y = node_info.loc[device_mask, "y_device"].astype(int)
            dev_x = node_info.loc[device_mask, "x_device"].astype(int)
            dev_ports = node_info.loc[device_mask, "port"].astype(int)
            dev_ids = metric_ids[dev_rows]
            dev_vals = metric_values[dev_rows]

            for t, nodeid, y, x, port, mid, val in zip(
                dev_t, dev_nodeids, dev_y, dev_x, dev_ports, dev_ids, dev_vals
            ):
                for device_idx, device in enumerate(cmn.meshes[0]["xps"][y, x]["ports"][port]["devices"]):
                    if device["nodeid"] == nodeid:
                        self.device_data[t, mid, 0, y, x, port, device_idx] = val

            # aggregate metric values for each device onto its port
            non_zero_dev_mask = self.device_data != 0.0
            device_counts = np.count_nonzero(non_zero_dev_mask, axis=6, keepdims=False)
            device_sums = self.device_data.sum(axis=6)
            with np.errstate(divide='ignore', invalid='ignore'):
                port_means = np.where(
                    device_counts > 0,
                    device_sums / device_counts,
                    0.0
                )
            self.port_data = port_means

            # aggregate metrics values for each port onto its XP
            non_zero_port_mask = self.port_data != 0.0
            port_counts = np.count_nonzero(non_zero_port_mask, axis=5, keepdims=False)
            port_sums = self.port_data.sum(axis=5)
            with np.errstate(divide='ignore', invalid='ignore'):
                xp_means = np.where(
                    port_counts > 0,
                    port_sums / port_counts,
                    0.0
                )
            self.xp_data = xp_means

    def get_metric_min_max(self, metric_id: int, mesh_idx: int) -> tuple[float, float]:
        """
        Compute the minimum and maximum non-zero values for a given metric and mesh.
        Args:
            metric_id: Metric identifier to filter by.
            mesh_idx: Index of the mesh to extract from.
        Returns:
            A tuple containing (min_value, max_value) for the selected metric.
            If no non-zero values are found, returns (0.0, 0.0).
        """
        if metric_id == self._last_metric_id and mesh_idx == self._last_mesh_idx:
            return self._last_min_max

        metric_id = max(0, min(metric_id, self.num_metrics - 1))
        mesh_idx = max(0, min(mesh_idx, self.global_data.shape[2] - 1))

        min_val = np.inf
        max_val = -np.inf

        # XP level
        xp_vals = self.xp_data[:, metric_id, mesh_idx, :, :]
        xp_mask = xp_vals != 0.0
        if np.any(xp_mask):
            xp_filtered = xp_vals[xp_mask]
            min_val = min(min_val, xp_filtered.min())
            max_val = max(max_val, xp_filtered.max())

        # Port level
        port_vals = self.port_data[:, metric_id, mesh_idx, :, :, :]
        port_mask = port_vals != 0.0
        if np.any(port_mask):
            port_filtered = port_vals[port_mask]
            min_val = min(min_val, port_filtered.min())
            max_val = max(max_val, port_filtered.max())

        # Device level
        dev_vals = self.device_data[:, metric_id, mesh_idx, :, :, :, :]
        dev_mask = dev_vals != 0.0
        if np.any(dev_mask):
            dev_filtered = dev_vals[dev_mask]
            min_val = min(min_val, dev_filtered.min())
            max_val = max(max_val, dev_filtered.max())

        if min_val == np.inf:
            result = (0.0, 0.0)
        else:
            result = (float(min_val), float(max_val))

        self._last_metric_id = metric_id
        self._last_mesh_idx = mesh_idx
        self._last_min_max = result

        return result

    def _value_to_colour(self, value: float, vmin: float, vmax: float) -> str:
        """Normalise and convert value to a red-scale hex colour."""
        if vmax <= vmin:
            return "#FFFFFF"
        norm = (value - vmin) / (vmax - vmin)
        norm = np.clip(norm, 0.0, 1.0)
        r = 255
        g = int((1 - norm) * 255)
        b = int((1 - norm) * 255)
        return f"#{r:02X}{g:02X}{b:02X}"

    def get_xp_colour(self, time_idx: int, metric_id: int, mesh_idx: int, y: int, x: int) -> str:
        val = self.xp_data[time_idx, metric_id, mesh_idx, y, x]
        vmin, vmax = self.get_metric_min_max(metric_id, mesh_idx)
        return self._value_to_colour(val, vmin, vmax)

    def get_port_colour(self, time_idx: int, metric_id: int, mesh_idx: int, y: int, x: int, port: int) -> str:
        val = self.port_data[time_idx, metric_id, mesh_idx, y, x, port]
        vmin, vmax = self.get_metric_min_max(metric_id, mesh_idx)
        return self._value_to_colour(val, vmin, vmax)

    def get_device_colour(self, time_idx: int, metric_id: int, mesh_idx: int, y: int, x: int, port: int, device_idx: int) -> str:
        val = self.device_data[time_idx, metric_id, mesh_idx, y, x, port, device_idx]
        vmin, vmax = self.get_metric_min_max(metric_id, mesh_idx)
        return self._value_to_colour(val, vmin, vmax)
