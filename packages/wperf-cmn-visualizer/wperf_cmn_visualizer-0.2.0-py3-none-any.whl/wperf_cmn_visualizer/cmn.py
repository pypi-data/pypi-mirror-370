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
CMN mesh data structures and operations.
"""

import numpy as np
from numpy import dtype as np_dtype
from typing import Dict, Any, List

CMN_MAX_PORTS: int = 6
CMN_MAX_CHILDS: int = 32
CMN_MAX_MESH_WIDTH: int = 12
CMN_MAX_MESH_HEIGHT: int = 12
CMN_TYPE_STR_MAX_LEN: int = 128
CMN_XP_DEVICE_ID: int = 6

coord_dtype = np_dtype(
    [
        ("x", "u1"),
        ("y", "u1"),
    ]
)

node_dtype = np_dtype(
    [
        ("coord", coord_dtype),
        ("nodeid", "u2"),
        ("logicalid", "u2"),
        ("type", "u2"),
        ("type_str", "U128"),
    ]
)

port_dtype = np_dtype(
    [
        ("type", "u1"),
        ("type_str", "U128"),
        ("cal", "b1"),
        ("num_devices", "u1"),
        ("devices", node_dtype, CMN_MAX_CHILDS),
    ]
)

xp_dtype = np_dtype(
    [
        ("node_info", node_dtype),
        ("dtc_domain", "u1"),
        ("num_device_ports", "u1"),
        ("ports", port_dtype, CMN_MAX_PORTS),
    ]
)

mesh_dtype = np_dtype(
    [
        ("x_dim", "u1"),
        ("y_dim", "u1"),
        ("xps", xp_dtype, (CMN_MAX_MESH_HEIGHT, CMN_MAX_MESH_WIDTH)),
    ]
)


class CMN:
    """
    Top-level CMN topology container managing multiple meshes.
    Attributes:
        num_meshes (int): Number of meshes in the topology
        meshes (np.ndarray): Array of mesh structures.
    """
    def __init__(self, topology: Dict[str, Any]) -> None:
        """
        Initialise CMN topology from JSON configuration.
        Args:
            topology (Dict[str, Any]): JSON configuration
        Raises:
            AssertionError: On invalid input
        """
        assert "elements" in topology, "topology data does not contain elements information"
        self.num_meshes: int = len(topology["elements"])
        assert self.num_meshes > 0, f"topology data contained {self.num_meshes} meshes"
        self.meshes = np.zeros(self.num_meshes, dtype=mesh_dtype)

        for i, element in enumerate(topology["elements"]):
            assert "config" in element, f"element idx: {i} does not contain configuration data"
            self._init_mesh(self.meshes[i], element["config"])

    def _init_mesh(self, mesh: np.ndarray, config: Dict[str, Any]) -> None:
        """
        Initialise a single mesh element.
        Args:
            mesh (np.ndarray): The structured array element to populate
            config (Dict[str, Any]): Configuration data for the mesh
        """
        x_val = config.get("X", 0)
        y_val = config.get("Y", 0)

        x_dim = int(x_val)
        y_dim = int(y_val)

        assert 0 < x_dim <= CMN_MAX_MESH_WIDTH, f"invalid x dimension on mesh, got: {x_dim}"
        assert 0 < y_dim <= CMN_MAX_MESH_HEIGHT, f"invalid y dimension on mesh, got: {y_dim}"

        mesh["x_dim"] = x_dim
        mesh["y_dim"] = y_dim

        assert "xps" in config, "no XP information on mesh"
        assert len(config["xps"]) > 0, "empty XP information on mesh"

        self._load_data(mesh, config["xps"], x_dim, y_dim)

    def _load_data(
        self,
        mesh: np.ndarray,
        xps_data: List[Dict[str, Any]],
        x_dim: int, y_dim: int
    ) -> None:
        """
        Load XP data into the mesh structure.
        Args:
            mesh (np.ndarray): Mesh structure
            xps_data (List[Dict[str, Any]]): List of XP data
            x_dim (int): Width of mesh
            y_dim (int): Height of mesh
        """
        for xp in xps_data:
            x = int(xp.get("X", 0))
            y = int(xp.get("Y", 0))

            if not (0 <= x < x_dim and 0 <= y < y_dim):
                continue

            node_xp = mesh["xps"][y, x]

            node_xp["node_info"]["coord"]["x"] = x
            node_xp["node_info"]["coord"]["y"] = y
            node_xp["node_info"]["nodeid"] = xp.get("id", 0)
            node_xp["node_info"]["logicalid"] = xp.get("logical_id", 0)
            node_xp["node_info"]["type"] = CMN_XP_DEVICE_ID
            node_xp["node_info"]["type_str"] = "XP"

            node_xp["dtc_domain"] = xp.get("dtc", 0)
            node_xp["num_device_ports"] = xp.get("n_ports", 0)

            for port in xp.get("ports", [])[:CMN_MAX_PORTS]:
                if "port" not in port or not (0 <= port["port"] < CMN_MAX_PORTS):
                    continue

                po = node_xp["ports"][port["port"]]
                po["type"] = port.get("type", 0)
                po["type_str"] = port.get("type_s", "unknown")[:CMN_TYPE_STR_MAX_LEN]
                po["cal"] = port.get("cal", False)

                devices_list = port.get("devices", [])[:CMN_MAX_CHILDS]
                po["num_devices"] = len(devices_list)

                for d, device in enumerate(devices_list):
                    dev = po["devices"][d]
                    dev["coord"]["x"] = x
                    dev["coord"]["y"] = y
                    dev["nodeid"] = device.get("id", 0)
                    dev["logicalid"] = device.get("logical_id", 0)
                    dev["type"] = device.get("type", 0)
                    dev["type_str"] = device.get("type_s", "unknown")[:CMN_TYPE_STR_MAX_LEN]

    def get_view(
        self,
        mesh_idx: int,
        min_row: int, max_row: int,
        min_col: int, max_col: int
    ):
        """
        Get a view of the mesh array for the visible region (NumPy array slicing).
        Args:
            mesh_idx (int): Mesh index
            min_row (int): Start row (inclusive)
            max_row (int): End row (inclusive)
            min_col (int): Start col (inclusive)
            max_col (int): End col (inclusive)
        Returns:
            NDArray[np.ndarray]: Sliced 2D view of the mesh XP array
        """
        mesh = self.meshes[mesh_idx]
        x_dim = mesh["x_dim"]
        y_dim = mesh["y_dim"]

        min_row = max(0, min_row)
        max_row = min(y_dim, max_row + 1)
        min_col = max(0, min_col)
        max_col = min(x_dim, max_col + 1)

        return mesh["xps"][min_row:max_row, min_col:max_col]
