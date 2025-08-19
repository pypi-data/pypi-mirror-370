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
Main Renderer module for rendering CMN to main body.
"""

import ttkbootstrap as tb
import numpy as np
from typing import Optional, Tuple, List, Any
from wperf_cmn_visualizer.canvas import ZoomPanCanvas
from wperf_cmn_visualizer.cmn import CMN
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics
from wperf_cmn_visualizer.config import Config, Events


class CMNRenderer:
    """
    Handles the rendering of a CMN onto a ZoomPanCanvas widget.
    Viewport-culling optimisation.
    Handles level of detail using zoom scale (more detail for higher zoom).
    Handles Mouse hover interaction.
    """
    dtc_color_map: List[str] = [
        "#44AA99",
        "#88CCEE",
        "#DDCC77",
        "#CC6677",
        "#117733",
        "#332288",
        "#AA4499",
        "#815911",
    ]
    """
    Accessible Colour map for distinguishing DTC domains.
    Reference: https://davidmathlogic.com/colorblind
    """

    def __init__(self, root: tb.Window, style: tb.Style, cmn: CMN, cmn_metrics: Optional[CMNMetrics]):
        """
        Args:
            root (tb.Window): The parent window.
            cmn (CMN): The computational mesh network object containing mesh data.
        """
        self.cmn_idx: int = 0
        self.cmn: CMN = cmn
        self.style: Any = style  # type hint bypass
        self.canvas: ZoomPanCanvas = ZoomPanCanvas(
            root, self._render_all, bg=self.style.colors.bg, highlightthickness=0
        )
        self.canvas.pack(expand=True, fill="both",
                         padx=Config.CANVAS_PADDING,
                         pady=Config.CANVAS_PADDING)
        self.canvas.hover_callback = self._handle_hover
        self.hovered_node: Optional[Tuple[int, int]] = None
        self.canvas.after_idle(self._centre_and_render)

        # cmn metrics initialisations
        self.cmn_metrics_time_idx: int = 0
        self.cmn_metrics_metric_id: int = 0
        self.cmn_metrics: Optional[CMNMetrics] = cmn_metrics
        self.cmn_metrics_values: Optional[np.ndarray] = None
        if self.cmn_metrics is not None:
            self.cmn_metrics_values_min, self.cmn_metrics_values_max = \
                self.cmn_metrics.get_metric_min_max(self.cmn_metrics_metric_id, self.cmn_idx)
        else:
            self.cmn_metrics_values_min, self.cmn_metrics_values_max = 0.0, 0.0

        self._fetch_metrics_values()
        root.bind(Events.TIMESCRUB_EVT, self._fetch_metrics_values, add=True)

    def _fetch_metrics_values(self, _=None):
        """
        Event handler for timeline scrubbing event.
        Fetch metric values for timestamp and generate colouring data.
        """
        # fetch timestamp index
        if isinstance(Events.Data, int):
            self.cmn_metrics_time_idx = Events.Data

        if self.cmn_metrics is not None:
            # fetch values for timestamp index
            self.cmn_metrics_values = self.cmn_metrics.get_metric_values_mesh(
                self.cmn_metrics_time_idx, self.cmn_metrics_metric_id,
                self.cmn_idx
            )

            values = self.cmn_metrics_values["xp_metric"]["value"]

            if self.cmn_metrics_values_max <= self.cmn_metrics_values_min:
                shape = values.shape
                self.cmn_metrics_colour_grid = np.full(shape, '#FFFFFF', dtype='<U7')
            else:
                # normalise values between 0 and 1
                norm = (values - self.cmn_metrics_values_min) / (self.cmn_metrics_values_max - self.cmn_metrics_values_min)
                norm = np.clip(norm, 0, 1)

                # modulate red colour channel based on noramlised values
                r = np.full_like(norm, 255, dtype=np.uint8)
                g = ((1 - norm) * 255).astype(np.uint8)
                b = ((1 - norm) * 255).astype(np.uint8)

                # combine to hex string
                rgb_combined = (r.astype(np.uint32) << 16) | (g.astype(np.uint32) << 8) | b.astype(np.uint32)
                self.cmn_metrics_colour_grid = np.char.add(
                    '#',
                    np.char.zfill(np.char.upper(np.char.mod('%x', rgb_combined)), 6)
                )
            # trigger re-render
            self._render_all()

    @property
    def current_mesh(self) -> np.ndarray:
        """
        Returns:
            CMNMesh: The active mesh object from the CMN.
        """
        return self.cmn.meshes[self.cmn_idx]

    def grid_to_world(self, row: int, col: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates with dynamic cell size."""
        cell_size = self.canvas.get_dynamic_grid_cell_size()
        return (col * cell_size, (int(self.current_mesh["y_dim"]) - row) * cell_size)

    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates with dynamic cell size."""
        cell_size = self.canvas.get_dynamic_grid_cell_size()
        return (
            int(self.current_mesh["y_dim"]) - int(round(world_y / cell_size)),
            int(round(world_x / cell_size))
        )

    def find_node_at_world_pos(self, world_x: float, world_y: float, tolerance: float) -> Optional[Tuple[int, int]]:
        """
        Find the grid node closest to a given world position, within a distance tolerance.
        Args:
            world_x (float): World x-position.
            world_y (float): World y-position.
            tolerance (float): Maximum search radius.
        Returns:
            Optional[Tuple[int, int]]: Grid position if a node is found, otherwise None.
        """
        row, col = self.world_to_grid(world_x, world_y)

        # bounds check
        if not (0 <= row < self.current_mesh["y_dim"] and 0 <= col < int(self.current_mesh["x_dim"])):
            return None

        # Check if within tolerance
        actual_world_x, actual_world_y = self.grid_to_world(row, col)
        distance_squared = (world_x - actual_world_x)**2 + (world_y - actual_world_y)**2

        if distance_squared <= tolerance ** 2:
            return (row, col)

        return None

    def get_visible_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get the grid bounds of the currently visible viewport, with extra padding.
        Extra padding ensures elements near by are rendered and dont appear suddenly;
        This prevents any flickering (smoother zooming and panning experience)
        Returns:
            Tuple[int, int, int, int]: (min_row, max_row, min_col, max_col) bounds.
        """
        cell_size = self.canvas.get_dynamic_grid_cell_size()
        # Calculate visible bounds in world coordinates
        canvas_left = -self.canvas.offset_x / self.canvas.zoom_scale
        canvas_bottom = -self.canvas.offset_y / self.canvas.zoom_scale
        canvas_right = (self.canvas.winfo_width() - self.canvas.offset_x) / self.canvas.zoom_scale
        canvas_top = (self.canvas.winfo_height() - self.canvas.offset_y) / self.canvas.zoom_scale

        # Add padding as a factor of the canvas size
        padding = max(canvas_right - canvas_left, canvas_top - canvas_bottom) // 3

        # Convert to grid coordinates with bounds checking using dynamic cell size
        min_col = max(0, int((canvas_left - padding) / cell_size))
        max_col = min(int(self.current_mesh["x_dim"]) - 1, int((canvas_right + padding) / cell_size))
        max_row = min(
            int(self.current_mesh["y_dim"]) - 1,
            int(self.current_mesh["y_dim"]) - int((canvas_bottom - padding) / cell_size)
        )
        min_row = max(
            0,
            int(self.current_mesh["y_dim"]) - int((canvas_top + padding) / cell_size)
        )
        return min_row, max_row, min_col, max_col

    def _centre_and_render(self) -> None:
        """Centre the grid and render."""
        self._centre_grid()
        self._render_all()

    def _centre_grid(self) -> None:
        """Centre the grid in the canvas."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        # If called before window fully initialised, pause for 10ms and call again
        if width <= 1 or height <= 1:
            self.canvas.after(10, self._centre_and_render)
            return

        cell_size = self.canvas.get_dynamic_grid_cell_size()
        # Calculate total grid size in world coordinates
        grid_width: float = int(self.current_mesh["x_dim"]) * cell_size * self.canvas.zoom_scale
        grid_height: float = int(self.current_mesh["y_dim"]) * cell_size * self.canvas.zoom_scale
        # Center the grid
        self.canvas.offset_x = (width - grid_width) / 2
        self.canvas.offset_y = (height - grid_height) / 2

    def _handle_hover(self, wx: float, wy: float) -> None:
        """Handle mouse hover."""
        found = self.find_node_at_world_pos(wx, wy, Config.XP_NODE_SQUARE_SIZE)
        if found != self.hovered_node:
            self.hovered_node = found
            self._render_all()

    def _render_all(self) -> None:
        """
        Render Callback Function.
        """
        self.canvas.delete("all")
        self._render_grid_lines()
        self._render_nodes()

    def _render_grid_lines(self) -> None:
        """Render all grid lines (no viewport culling)."""
        min_row, max_row = 0, int(self.current_mesh["y_dim"]) - 1
        min_col, max_col = 0, int(self.current_mesh["x_dim"]) - 1

        # Render vertical lines
        for col in range(min_col, max_col + 1):
            x, _ = self.grid_to_world(0, col)
            _, y_start = self.grid_to_world(min_row, 0)
            _, y_end = self.grid_to_world(max_row, 0)

            self.canvas.draw_line(
                x, y_start, x, y_end,
                color=self.style.colors.dark,
                thickness=Config.GRID_LINE_WIDTH,
                tag="grid_line",
            )

        # Render horizontal lines
        for row in range(min_row, max_row + 1):
            _, y = self.grid_to_world(row, 0)
            x_start, _ = self.grid_to_world(0, min_col)
            x_end, _ = self.grid_to_world(0, max_col)

            self.canvas.draw_line(
                x_start, y, x_end, y,
                color=self.style.colors.dark,
                thickness=Config.GRID_LINE_WIDTH,
                tag="grid_line",
            )

    @staticmethod
    def darken_colour(hex_colour: str, factor: float = 1.2) -> str:
        """Darken a hex colour by dividing each RGB channel by `factor`."""
        hex_colour = hex_colour.lstrip("#")
        r = min(int(int(hex_colour[0:2], 16) / factor), 255)
        g = min(int(int(hex_colour[2:4], 16) / factor), 255)
        b = min(int(int(hex_colour[4:6], 16) / factor), 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def brighten_colour(hex_colour: str, factor: float = 1.3) -> str:
        """Brighten a hex colour by multiplying each RGB channel by `factor`."""
        hex_colour = hex_colour.lstrip("#")
        r = min(int(int(hex_colour[0:2], 16) * factor), 255)
        g = min(int(int(hex_colour[2:4], 16) * factor), 255)
        b = min(int(int(hex_colour[4:6], 16) * factor), 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    # static rendering constants cache
    offsets = {
        0: (-1, 1),   # south west
        1: (1, -1),   # north east
        2: (1, 1),    # south east
        3: (-1, -1),  # north west
    }
    label_offsets = {
        0: (2.5, -2.0),
        1: (-2.5, 2.0),
        2: (-2.5, -2.0),
        3: (2.5, 2.0),
    }
    len_div_sqrt2 = Config.XP_PORT_LINE_LEN / np.sqrt(2)
    coord_str_font_size = 4  # used for coordinate box and nodeid

    def _render_nodes(self) -> None:
        """
        Render all visible nodes within the viewport. Includes:
        - Square XP node rendering with hover highlighting.
        - DTC-based colour assignment.
        - Additional text annotations when zoomed in.
        """
        def draw_node(x, y, node_xp, node_colour):
            """
            +-------+
            |       |
            |     <- base_colour
            |       |
            +-------+ <- node
            """
            node_size_double = Config.XP_NODE_SQUARE_SIZE * 2
            self.canvas.draw_rectangle(
                x, y,
                node_size_double,
                node_size_double,
                node_colour,
                outline_color=self.style.colors.dark,
                outline_thickness=Config.XP_OUTLINE_WIDTH,
                tag="node",
            )

        def draw_coord_node_id_labels(x, y, node_xp):
            """
                     +-----+
            +--------|(0,0)| <- coord_string
            |        +-----+ <= coord_str box
            |           |
            |    XP     |
            |           |
            +-----------+
            Look through ports, find empty ports to draw
            either a box with coordinates or box with node-id.
            This is designed to remain persistent accross all zoom Levels so it uses slower scaling.
            """
            types = node_xp["ports"]["type"][:4]
            empty_ports = np.where(types == 0)

            if empty_ports[0].size > 0:
                port_index = empty_ports[0][0]
                dx, dy = CMNRenderer.offsets[port_index]
            else:
                dx = 0
                dy = 1

            coord_box_x = x + dx * Config.XP_NODE_SQUARE_SIZE
            coord_box_y = y + dy * Config.XP_NODE_SQUARE_SIZE
            coordx = node_xp["node_info"]["coord"]["x"]
            coordy = node_xp["node_info"]["coord"]["y"]
            coord_str = f"({coordx},{coordy})"
            width = self.canvas.get_text_width(coord_str, CMNRenderer.coord_str_font_size, scale_rate=0.5) + Config.XP_UI_PADDING
            height = self.canvas.get_text_height(CMNRenderer.coord_str_font_size, scale_rate=0.5) + Config.XP_UI_PADDING

            self.canvas.draw_rectangle(
                coord_box_x, coord_box_y,
                width, height,
                "black",
                scale_rate=0.5,
                tag="coord_str_box"
            )
            self.canvas.draw_text(
                coord_box_x, coord_box_y,
                coord_str,
                "white", CMNRenderer.coord_str_font_size,
                scale_rate=0.5,
                tag="coord_string"
            )

            if empty_ports[0].size > 1:
                second_port_index = empty_ports[0][1]
                dx2, dy2 = CMNRenderer.offsets[second_port_index]
            else:
                dx2 = 0
                dy2 = -1

            node_id_box_x = x + dx2 * Config.XP_NODE_SQUARE_SIZE
            node_id_box_y = y + dy2 * Config.XP_NODE_SQUARE_SIZE

            node_id = node_xp["node_info"]["nodeid"]
            height2 = self.canvas.get_text_height(4, scale_rate=0.5) + Config.XP_UI_PADDING
            width2 = self.canvas.get_text_width(node_id, 4, scale_rate=0.5) + Config.XP_UI_PADDING

            self.canvas.draw_rectangle(
                node_id_box_x, node_id_box_y,
                width2, height2,
                "black",
                scale_rate=0.5,
                tag="node_id_box"
            )
            self.canvas.draw_text(
                node_id_box_x, node_id_box_y,
                node_id,
                "white", CMNRenderer.coord_str_font_size,
                scale_rate=0.5,
                tag="node_id_string"
            )

        def draw_medium_zoom_labels(x, y, node_xp):
            """
            +---------+
            |         |
            |    XP   | <- XP_label
            |         |
            +---------+
            Draw XP label.
            """
            self.canvas.draw_text(
                x, y,
                "XP",
                "black", Config.XP_LABEL_FONT_SIZE,
                tag="XP_label"
            )

        def draw_medium_zoom_ports(x, y, node_xp, port_box_col):
            """
                     +--------------+
                     |    port      | <- port_string_medium
                     +--------------+ <- port_box_medium
                    / <- port_line
            -------+
                 P1| <- port_label
                   |
            Draw additional port information for medium zoom level
            """
            for p, port in enumerate(node_xp["ports"]):
                if port["type"] == 0 or p not in CMNRenderer.offsets:
                    continue
                dx, dy = CMNRenderer.offsets[p]
                x0 = x + dx * Config.XP_NODE_SQUARE_SIZE
                y0 = y + dy * Config.XP_NODE_SQUARE_SIZE
                x1 = x0 + dx * CMNRenderer.len_div_sqrt2
                y1 = y0 + dy * CMNRenderer.len_div_sqrt2

                self.canvas.draw_line(
                    x0, y0, x1, y1,
                    color=self.style.colors.dark,
                    thickness=Config.GRID_LINE_WIDTH,
                    tag="port_line"
                )

                lx = -Config.XP_UI_PADDING * dx
                ly = -Config.XP_UI_PADDING * dy
                self.canvas.draw_text(
                    x + lx + (dx * Config.XP_NODE_SQUARE_SIZE),
                    y + ly + (dy * Config.XP_NODE_SQUARE_SIZE),
                    f"P{p}", "black", Config.XP_DETAILS_FONT_SIZE,
                    tag="port_label"
                )

                port_type_str = port["type_str"]
                box_width = self.canvas.get_text_width(port_type_str, Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_center_x = x1 + (dx * box_width / 2)
                box_center_y = y1 + (dy * box_height / 2)

                self.canvas.draw_rectangle(
                    box_center_x, box_center_y,
                    box_width, box_height,
                    port_box_col, outline_color=self.style.colors.dark,
                    outline_thickness=Config.XP_OUTLINE_WIDTH,
                    tag="port_box_medium"
                )
                self.canvas.draw_text(
                    box_center_x, box_center_y,
                    port_type_str, "black", Config.XP_DETAILS_FONT_SIZE,
                    tag="port_string_medium"
                )

        def draw_full_zoom_ports(x, y, node_xp, port_box_col):
            """
                     |    |     |  d <- device_strs_table_text
                     |    |     |  e  |
                     |    |     |  v  | <- device_strs_table_divider
                     |    |     |  1  |
                     +----------------+
                     |  CAL ? port    | <- port_string_full
                     +----------------+ <- port_box_full
                    /
            -------+
                 P1|
                   |
            """
            for p, port in enumerate(node_xp["ports"]):
                if port["type"] == 0 or p not in CMNRenderer.offsets:
                    continue

                port_string = f"{'CAL - ' if port['cal'] else ''}{port['type_str']}"
                port_string_width = self.canvas.get_text_width(port_string, Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                devices = np.sort(port["devices"][:port["num_devices"]], order="type")
                if len(devices) == 0:
                    continue
                device_ids = np.vectorize(hex)(devices["nodeid"])
                device_strs = np.char.add(np.char.add(devices["type_str"], " - "), device_ids)
                str_widths = np.vectorize(self.canvas.get_text_width)(device_strs, Config.XP_DETAILS_FONT_SIZE)
                max_str_width = np.max(str_widths) + Config.XP_UI_PADDING

                text_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_width = max(port_string_width, text_height * port["num_devices"])

                dx, dy = CMNRenderer.offsets[p]
                x0 = x + dx * Config.XP_NODE_SQUARE_SIZE
                y0 = y + dy * Config.XP_NODE_SQUARE_SIZE
                x1 = x0 + dx * CMNRenderer.len_div_sqrt2
                y1 = y0 + dy * CMNRenderer.len_div_sqrt2

                box_center_x = x1 + (dx * box_width / 2)
                box_center_y = y1 + (dy * (max_str_width + text_height) / 2)
                box_height = max_str_width + text_height

                self.canvas.draw_rectangle(
                    box_center_x, box_center_y,
                    box_width, box_height,
                    port_box_col, outline_color=self.style.colors.dark,
                    outline_thickness=Config.XP_OUTLINE_WIDTH,
                    tag="port_box_full"
                )
                self.canvas.draw_text(
                    box_center_x, box_center_y - (dy * ((box_height - text_height) / 2)),
                    port_string, "black", Config.XP_DETAILS_FONT_SIZE,
                    tag="port_string_full"
                )

                self.canvas.draw_line(
                    box_center_x - (dx * box_width / 2),
                    box_center_y - (dy * (box_height / 2 - text_height)),
                    box_center_x + (dx * box_width / 2),
                    box_center_y - (dy * (box_height / 2 - text_height)),
                    color=self.style.colors.dark,
                    thickness=Config.GRID_LINE_WIDTH
                )

                left_edge = box_center_x - (box_width / 2)
                text_left_start = left_edge + text_height / 2

                for i, device_str in enumerate(device_strs):
                    text_center_x = text_left_start + (i * text_height)
                    text_center_y = box_center_y + (dy * (text_height / 2))
                    self.canvas.draw_text(
                        text_center_x, text_center_y,
                        device_str,
                        "black", Config.XP_DETAILS_FONT_SIZE, angle=90,
                        tag="device_strs_table_text"
                    )
                    if i < port["num_devices"] - 1:
                        self.canvas.draw_line(
                            x1=text_center_x + text_height / 2, y1=text_center_y - (dy * max_str_width / 2),
                            x2=text_center_x + text_height / 2, y2=text_center_y + (dy * max_str_width / 2),
                            color=self.style.colors.dark,
                            thickness=Config.GRID_LINE_WIDTH,
                            tag="device_strs_table_divider"
                        )

        # main loop over visible XPs
        # only obtain visible section from the full cmn mesh
        min_row, max_row, min_col, max_col = self.get_visible_bounds()
        visible_mesh: np.ndarray = self.cmn.get_view(self.cmn_idx, min_row, max_row, min_col, max_col)

        # zoom mode
        zoom_scale = self.canvas.zoom_scale
        is_small_zoom = zoom_scale >= 2.50
        is_medium_zoom = zoom_scale >= 5.0
        is_full_zoom = zoom_scale >= 7.50

        # nested loop over visible mesh only
        for local_row in range(visible_mesh.shape[0]):
            for local_col in range(visible_mesh.shape[1]):
                row = min_row + local_row
                col = min_col + local_col
                if row >= self.current_mesh["y_dim"] or col >= self.current_mesh["x_dim"]:
                    continue

                node_xp = visible_mesh[local_row, local_col]
                x, y = self.grid_to_world(row, col)
                if self.cmn_metrics_values is not None:
                    xp_x = node_xp["node_info"]["coord"]["x"]
                    xp_y = node_xp["node_info"]["coord"]["y"]
                    node_colour = self.cmn_metrics_colour_grid[xp_y, xp_x]
                    port_box_col = self.style.colors.light
                else:
                    node_colour = CMNRenderer.dtc_color_map[node_xp["dtc_domain"] % len(CMNRenderer.dtc_color_map)]
                    port_box_col = self.style.colors.light
                    if self.hovered_node == (row, col):
                        node_colour = CMNRenderer.darken_colour(node_colour)
                        port_box_col = CMNRenderer.darken_colour(port_box_col)

                draw_node(x, y, node_xp, node_colour)

                if is_small_zoom:
                    draw_coord_node_id_labels(x, y, node_xp)

                if is_medium_zoom:
                    draw_medium_zoom_labels(x, y, node_xp)
                    draw_medium_zoom_ports(x, y, node_xp, port_box_col)

                if is_full_zoom:
                    draw_full_zoom_ports(x, y, node_xp, port_box_col)
