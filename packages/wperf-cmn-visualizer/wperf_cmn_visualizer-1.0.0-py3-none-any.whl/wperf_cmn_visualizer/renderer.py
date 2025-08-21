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
from PySide6.QtWidgets import QWidget, QApplication, QGraphicsDropShadowEffect
from PySide6.QtGui import QPalette, QColor, QCursor
from PySide6.QtCore import Qt, QTimer
import numpy as np
from typing import Optional, Tuple, List
from enum import IntEnum

from wperf_cmn_visualizer.canvas import Canvas, ZoomPanCanvas
from wperf_cmn_visualizer.hit_test import HitTest
from wperf_cmn_visualizer.cmn import CMN
from wperf_cmn_visualizer.cmn_metrics import CMNMetrics
from wperf_cmn_visualizer.config import Config


class CMNRenderer:
    """
    Handles the rendering of a CMN onto a ZoomPanCanvas widget.
    Viewport-culling optimisation.
    Handles level of detail using zoom scale (more detail for higher zoom).
    Handles Mouse hover interaction.
    """
    dtc_color_map: List[QColor] = [
        QColor("#44AA99"),
        QColor("#549EC2"),
        QColor("#C5B45E"),
        QColor("#BE5D6D"),
        QColor("#117733"),
        QColor("#332288"),
        QColor("#B731A1"),
        QColor("#815911"),
    ]
    """
    Accessible Colour map for distinguishing DTC domains.
    Reference: https://davidmathlogic.com/colorblind
    """

    class CMNNodeType(IntEnum):
        NONE = 0
        XP = 1
        PORT = 2
        DEVICE = 3

    CMNNodeTypeData = np.dtype([
        ('type', np.uint8),
        ('x', np.uint8),
        ('y', np.uint8),
        ('port', np.uint8),
        ('device', np.uint8),
    ])

    def __init__(self, master: QWidget, palette: QPalette, cmn: CMN, cmn_metrics: Optional[CMNMetrics]):
        """
        Args:
            root (Qwidget): The parent window.
            cmn (CMN): The computational mesh network object containing mesh data.
            cmn_metrics (Optional[CMNMetrics]): Optional metrics data for coloring.
            palette (QPalette): QPalette for consistent theming.
        """
        self.cmn_idx: int = 0
        self.cmn: CMN = cmn
        self.palette: QPalette = palette
        self._setup_theme_colors()

        self.canvas: ZoomPanCanvas = ZoomPanCanvas(master, self._render_all, self._handle_hover)
        QTimer.singleShot(0, self._centre_and_render)

        self.hit_test: HitTest = HitTest(CMNRenderer.CMNNodeTypeData, 256)
        self._setup_tooltip()

        # cmn metrics initialisations
        self.cmn_metrics_time_idx: int = 0
        self.cmn_metrics_metric_id: int = 0
        self.cmn_metrics: Optional[CMNMetrics] = cmn_metrics

    def _setup_theme_colors(self) -> None:
        """Extract and setup theme colors from QPalette with proper dark/light mode handling."""
        window_color = self.palette.color(QPalette.ColorRole.Window)
        base_color = self.palette.color(QPalette.ColorRole.Base)
        text_color = self.palette.color(QPalette.ColorRole.Text)

        window_brightness = (window_color.red() + window_color.green() + window_color.blue()) / 3
        self.is_dark_mode = window_brightness < 128

        if self.is_dark_mode:
            self.grid_color = self.palette.color(QPalette.ColorRole.Light)
            self.outline_color = self.palette.color(QPalette.ColorRole.Light)
        else:
            self.grid_color = self.palette.color(QPalette.ColorRole.Dark)
            self.outline_color = self.palette.color(QPalette.ColorRole.Dark)

        self.text_color = text_color
        self.ui_bg_color = base_color
        self.black_color = QColor("black")
        self.white_color = QColor("white")

    def _setup_tooltip(self):
        """Initialise tooltip UI and state."""
        self.tooltip_canvas = Canvas(self.canvas)
        self.tooltip_canvas.setContentsMargins(0, 0, 0, 0)
        self.tooltip_canvas.hide()
        self.tooltip_canvas.raise_()
        self.tooltip_canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.tooltip_canvas.setStyleSheet(f"""
            background-color: {self.palette.color(QPalette.ColorRole.ToolTipBase).name()};
            color: {self.palette.color(QPalette.ColorRole.ToolTipText).name()};
            border-radius: 6px;
        """)
        shadow = QGraphicsDropShadowEffect(self.tooltip_canvas)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 255))
        shadow.setOffset(0, 0)
        self.tooltip_canvas.setGraphicsEffect(shadow)

        self._tooltip_delay = QApplication.style().styleHint(
            QApplication.style().StyleHint.SH_ToolTip_WakeUpDelay
        )
        self._tooltip_data = None  # currently hovered data
        self._tooltip_active = False
        self._tooltip_timer = QTimer(singleShot=True)
        self._tooltip_timer.timeout.connect(self._on_tooltip_timeout)

        self._tooltip_offset_x = 5
        self._tooltip_offset_y = -5

    @property
    def current_mesh(self) -> np.ndarray:
        """
        Returns:
            CMNMesh: The active mesh object from the CMN.
        """
        return self.cmn.meshes[self.cmn_idx]

    def _on_time_changed(self, time_idx: int):
        self.cmn_metrics_time_idx = time_idx
        self._render_all()

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
        canvas_right = (self.canvas.view.viewport().width() - self.canvas.offset_x) / self.canvas.zoom_scale
        canvas_top = (self.canvas.view.viewport().height() - self.canvas.offset_y) / self.canvas.zoom_scale

        # Add padding as a factor of the canvas size
        padding = max(canvas_right - canvas_left, canvas_top - canvas_bottom) // 4

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
        width = self.canvas.view.viewport().width()
        height = self.canvas.view.viewport().height()

        cell_size = self.canvas.get_dynamic_grid_cell_size()
        # Calculate total grid size in world coordinates
        grid_width: float = int(self.current_mesh["x_dim"]) * cell_size * self.canvas.zoom_scale
        grid_height: float = int(self.current_mesh["y_dim"]) * cell_size * self.canvas.zoom_scale
        # Center the grid
        self.canvas.offset_x = (width - grid_width) / 2
        self.canvas.offset_y = (height - grid_height) / 2

    def _handle_hover(self, wx: float, wy: float) -> None:
        """Process hover events with delayed show/hide logic."""
        new_data = self.hit_test.hit_test(wx, wy)

        if new_data == self._tooltip_data:
            return

        self._tooltip_data = new_data
        self._tooltip_timer.stop()

        if new_data:
            if self._tooltip_active:
                self._show_tooltip(new_data)
            else:
                self._tooltip_timer.start(self._tooltip_delay)
        else:
            if self._tooltip_active:
                self._tooltip_timer.start(self._tooltip_delay)
            else:
                self.tooltip_canvas.hide()

    def _on_tooltip_timeout(self):
        """Timer expiry — either show or hide tooltip."""
        if self._tooltip_data:
            self._tooltip_active = True
            self._show_tooltip(self._tooltip_data)
        else:
            self._tooltip_active = False
            self.tooltip_canvas.hide()

    def _show_tooltip(self, data):
        """Render and position tooltip with centered text using clean Canvas architecture."""
        if self.cmn_metrics is None:
            return

        # Extract value based on node type
        node_type = data["type"]
        if node_type == CMNRenderer.CMNNodeType.XP:
            value = self.cmn_metrics.xp_data[
                self.cmn_metrics_time_idx, self.cmn_metrics_metric_id, self.cmn_idx,
                data["y"], data["x"]
            ]
            text = f"{value:.6f}"

        elif node_type == CMNRenderer.CMNNodeType.PORT:
            value = self.cmn_metrics.port_data[
                self.cmn_metrics_time_idx, self.cmn_metrics_metric_id, self.cmn_idx,
                data["y"], data["x"], data["port"]
            ]
            text = f"{value:.6f}"

        elif node_type == CMNRenderer.CMNNodeType.DEVICE:
            value = self.cmn_metrics.device_data[
                self.cmn_metrics_time_idx, self.cmn_metrics_metric_id, self.cmn_idx,
                data["y"], data["x"], data["port"], data["device"]
            ]
            text = f"{value:.6f}"
        else:
            text = ""

        if not text:
            self.tooltip_canvas.hide()
            return

        # measure text to determine canvas size
        text_width = self.tooltip_canvas.get_text_width(text, Config.TOOLTIP_FONT_SIZE)
        text_height = self.tooltip_canvas.get_text_height(Config.TOOLTIP_FONT_SIZE)

        # set canvas size
        canvas_width = text_width + (Config.TOOLTIP_PADDING * 2)
        canvas_height = text_height + (Config.TOOLTIP_PADDING * 2)
        self.tooltip_canvas.resize(int(canvas_width), int(canvas_height))

        # clear canvas and draw text
        self.tooltip_canvas.scene.clear()
        self.tooltip_canvas.draw_text(canvas_width / 2, canvas_height / 2, text, self.text_color, Config.TOOLTIP_FONT_SIZE)

        # set position of tool tip and ensure it not slipping boundaries of window.
        cursor_pos = self.canvas.mapFromGlobal(QCursor.pos())
        tooltip_x = cursor_pos.x() + self._tooltip_offset_x
        tooltip_y = cursor_pos.y() + self._tooltip_offset_y
        canvas_rect = self.canvas.rect()
        if tooltip_x + canvas_width > canvas_rect.right():
            tooltip_x = cursor_pos.x() - canvas_width - self._tooltip_offset_x
        if tooltip_y + canvas_height > canvas_rect.bottom():
            tooltip_y = cursor_pos.y() - canvas_height - self._tooltip_offset_y
        tooltip_x = max(0, tooltip_x)
        tooltip_y = max(0, tooltip_y)

        # reveal tool tip
        self.tooltip_canvas.move(int(tooltip_x), int(tooltip_y))
        self.tooltip_canvas.show()

    def _render_all(self) -> None:
        """
        Render Callback Function.
        """
        if self.canvas.isVisible():
            self.canvas.scene.clear()
            self.hit_test.clear()
            self.tooltip_canvas.hide()
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
                color=self.grid_color,
                thickness=Config.GRID_LINE_WIDTH,
            )

        # Render horizontal lines
        for row in range(min_row, max_row + 1):
            _, y = self.grid_to_world(row, 0)
            x_start, _ = self.grid_to_world(0, min_col)
            x_end, _ = self.grid_to_world(0, max_col)

            self.canvas.draw_line(
                x_start, y, x_end, y,
                color=self.grid_color,
                thickness=Config.GRID_LINE_WIDTH,
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

    def _get_node_color(self, xp_x: int, xp_y: int, dtc: int) -> QColor:
        """Get the appropriate color for a node based on metrics or DTC domain."""
        if self.cmn_metrics is not None:
            return self.cmn_metrics.get_xp_colour(
                self.cmn_metrics_time_idx,
                self.cmn_metrics_metric_id,
                self.cmn_idx,
                xp_y,
                xp_x
            )
        else:
            return CMNRenderer.dtc_color_map[dtc % len(CMNRenderer.dtc_color_map)]

    def _get_port_color(self, xp_x: int, xp_y: int, port_index: int) -> QColor:
        """Get the appropriate color for a port based on metrics or default."""
        if self.cmn_metrics is not None:
            return self.cmn_metrics.get_port_colour(
                self.cmn_metrics_time_idx,
                self.cmn_metrics_metric_id,
                self.cmn_idx,
                xp_y,
                xp_x,
                port_index
            )
        else:
            return self.ui_bg_color

    def _get_device_color(self, xp_x: int, xp_y: int, port_index: int, device_index: int) -> QColor:
        """Get the appropriate color for a device based on metrics or default."""
        if self.cmn_metrics is not None:
            return self.cmn_metrics.get_device_colour(
                self.cmn_metrics_time_idx,
                self.cmn_metrics_metric_id,
                self.cmn_idx,
                xp_y,
                xp_x,
                port_index,
                device_index
            )
        else:
            return self.ui_bg_color

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
        - DTC-based colour assignment or heatmap colors.
        - Additional text annotations when zoomed in.
        """
        def draw_node(x, y, node_xp, isHovered):
            """
            +-------+
            |       |
            |     <- base_colour
            |       |
            +-------+ <- node
            """
            xp_x = node_xp["node_info"]["coord"]["x"]
            xp_y = node_xp["node_info"]["coord"]["y"]
            dtc = node_xp["dtc_domain"]
            node_colour = self._get_node_color(xp_x, xp_y, dtc)
            node_size_double = Config.XP_NODE_SQUARE_SIZE * 2
            self.canvas.draw_rectangle(
                x, y,
                node_size_double,
                node_size_double,
                node_colour,
                outline_color=self.outline_color,
                outline_thickness=Config.XP_OUTLINE_WIDTH,
            )
            self.hit_test.add_rect(x, y, node_size_double, node_size_double, (CMNRenderer.CMNNodeType.XP, xp_x, xp_y, 0, 0))

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
                self.black_color,
                scale_rate=0.5,
            )
            self.canvas.draw_text(
                coord_box_x, coord_box_y,
                coord_str,
                self.white_color, CMNRenderer.coord_str_font_size,
                scale_rate=0.5,
            )

            if empty_ports[0].size > 1:
                second_port_index = empty_ports[0][1]
                dx2, dy2 = CMNRenderer.offsets[second_port_index]
            else:
                dx2 = 0
                dy2 = -1

            node_id_box_x = x + dx2 * Config.XP_NODE_SQUARE_SIZE
            node_id_box_y = y + dy2 * Config.XP_NODE_SQUARE_SIZE

            node_id = f'{node_xp["node_info"]["nodeid"]}'
            height2 = self.canvas.get_text_height(4, scale_rate=0.5) + Config.XP_UI_PADDING
            width2 = self.canvas.get_text_width(node_id, 4, scale_rate=0.5) + Config.XP_UI_PADDING

            self.canvas.draw_rectangle(
                node_id_box_x, node_id_box_y,
                width2, height2,
                self.black_color,
                scale_rate=0.5,
            )
            self.canvas.draw_text(
                node_id_box_x, node_id_box_y,
                node_id,
                self.white_color, CMNRenderer.coord_str_font_size,
                scale_rate=0.5,
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
                self.text_color, Config.XP_LABEL_FONT_SIZE,
            )

        def draw_medium_zoom_ports(x, y, node_xp):
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
                    color=self.grid_color,
                    thickness=Config.GRID_LINE_WIDTH,
                )

                lx = -Config.XP_UI_PADDING * dx
                ly = -Config.XP_UI_PADDING * dy
                self.canvas.draw_text(
                    x + lx + (dx * Config.XP_NODE_SQUARE_SIZE),
                    y + ly + (dy * Config.XP_NODE_SQUARE_SIZE),
                    f"P{p}", self.text_color, Config.XP_DETAILS_FONT_SIZE,
                )

                port_type_str = port["type_str"]
                box_width = self.canvas.get_text_width(port_type_str, Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_height = self.canvas.get_text_height(Config.XP_DETAILS_FONT_SIZE) + Config.XP_UI_PADDING
                box_center_x = x1 + (dx * box_width / 2)
                box_center_y = y1 + (dy * box_height / 2)

                xp_x = node_xp["node_info"]["coord"]["x"]
                xp_y = node_xp["node_info"]["coord"]["y"]
                port_color = self._get_port_color(xp_x, xp_y, p)
                self.canvas.draw_rectangle(
                    box_center_x, box_center_y,
                    box_width, box_height,
                    port_color,
                    outline_color=self.outline_color,
                    outline_thickness=Config.XP_OUTLINE_WIDTH,
                )
                self.hit_test.add_rect(box_center_x, box_center_y, box_width, box_height, (CMNRenderer.CMNNodeType.PORT, xp_x, xp_y, p, 0))
                self.canvas.draw_text(
                    box_center_x, box_center_y,
                    port_type_str, self.text_color, Config.XP_DETAILS_FONT_SIZE,
                )

        def draw_full_zoom_ports(x, y, node_xp):
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
                devices = port["devices"][:port["num_devices"]]
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
                    self.ui_bg_color, outline_color=self.outline_color,
                    outline_thickness=Config.XP_OUTLINE_WIDTH,
                )

                xp_x = node_xp["node_info"]["coord"]["x"]
                xp_y = node_xp["node_info"]["coord"]["y"]
                port_box_center_y = box_center_y - (dy * ((box_height - text_height) / 2))
                port_color = self._get_port_color(xp_x, xp_y, p)
                self.canvas.draw_rectangle(
                    box_center_x, port_box_center_y,
                    box_width, text_height,
                    port_color,
                    outline_color=self.outline_color,
                    outline_thickness=Config.XP_OUTLINE_WIDTH,
                )
                self.hit_test.add_rect(box_center_x, port_box_center_y, box_width, text_height, (CMNRenderer.CMNNodeType.PORT, xp_x, xp_y, p, 0))
                self.canvas.draw_text(
                    box_center_x, port_box_center_y,
                    port_string, self.text_color, Config.XP_DETAILS_FONT_SIZE,
                )

                self.canvas.draw_line(
                    box_center_x - (dx * box_width / 2),
                    box_center_y - (dy * (box_height / 2 - text_height)),
                    box_center_x + (dx * box_width / 2),
                    box_center_y - (dy * (box_height / 2 - text_height)),
                    color=self.outline_color,
                    thickness=Config.GRID_LINE_WIDTH
                )

                left_edge = box_center_x - (box_width / 2)
                text_left_start = left_edge + text_height / 2

                for i, device_str in enumerate(device_strs):
                    text_center_x = text_left_start + (i * text_height)
                    text_center_y = box_center_y + (dy * (text_height / 2))

                    device_color = self._get_device_color(xp_x, xp_y, p, i)
                    self.canvas.draw_rectangle(
                        text_center_x, text_center_y,
                        text_height, max_str_width,
                        device_color,
                        outline_color=self.outline_color,
                        outline_thickness=1,
                    )
                    self.hit_test.add_rect(text_center_x, text_center_y, text_height, max_str_width, (CMNRenderer.CMNNodeType.DEVICE, xp_x, xp_y, p, i))

                    self.canvas.draw_text(
                        text_center_x, text_center_y,
                        device_str,
                        self.text_color, Config.XP_DETAILS_FONT_SIZE, angle=-90,
                    )
                    if i < port["num_devices"] - 1:
                        self.canvas.draw_line(
                            x1=text_center_x + text_height / 2, y1=text_center_y - (dy * max_str_width / 2),
                            x2=text_center_x + text_height / 2, y2=text_center_y + (dy * max_str_width / 2),
                            color=self.outline_color,
                            thickness=Config.GRID_LINE_WIDTH,
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

                draw_node(x, y, node_xp, False)

                if is_small_zoom:
                    draw_coord_node_id_labels(x, y, node_xp)

                if is_medium_zoom:
                    draw_medium_zoom_labels(x, y, node_xp)
                    draw_medium_zoom_ports(x, y, node_xp)

                if is_full_zoom:
                    draw_full_zoom_ports(x, y, node_xp)
