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
Zoomable and pannable canvas.
This will serve as the main body to which CMN objects are rendered.
"""

import tkinter as tk
import tkinter.font as tkFont
import ttkbootstrap as tb
from functools import lru_cache
from typing import Callable, Optional, Tuple, Any
from .config import Config


class ZoomPanCanvas(tk.Canvas):
    """
    A tkinter Canvas subclass that supports zooming and panning.
    This canvas allows users to zoom in and out and pan across the content.
    It maintains a zoom scale and offset to convert between world coordinates
    and screen coordinates.
    It also supports a hover callback for mouse movement in world coordinates.
    Also a redraw callback automaticalled called when redraw required.
    Attributes:
        zoom_scale : float
            The current zoom scale factor.
        offset_x : float
            Horizontal offset for panning.
        offset_y : float
            Vertical offset for panning.
        hover_callback : Optional[Callable[[float, float], None]]
            Optional callback for mouse hover events in world coordinates.
        redraw_callback : Callable[[], None]
            Callback to trigger canvas redraw; must take zero arguments.
    """
    def __init__(self, master: tb.Window, redraw_callback: Callable[[], None], **kwargs: Any) -> None:
        """
        Args:
        master : tb.Frame
            The parent tkinter root
        redraw_callback : Callable[[], None]
            A callback function that is called whenever the canvas
            needs to be redrawn, such as after panning or zooming.
            This function must take no parameters.
        kwargs : dict
            Additional keyword arguments to be passed to the base tk.Canvas.
        """
        super().__init__(master, **kwargs)
        self.zoom_scale: float = Config.DEFAULT_ZOOM
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self._pan_start_x: int = 0
        self._pan_start_y: int = 0
        self.hover_callback: Optional[Callable[[float, float], None]] = None
        self.redraw_callback: Callable[[], None] = redraw_callback
        self.font: tkFont.Font = tkFont.Font()
        self._setup_bindings()

    def get_dynamic_grid_cell_size(self) -> float:
        """Scale Current Grid Size."""
        return Config.GRID_CELL_SIZE * (1.0 + (self.zoom_scale - 1.0) * 0.3)

    def _setup_bindings(self) -> None:
        """Set up mouse and keyboard event bindings."""
        self.bind("<ButtonPress-1>", self._start_pan)
        self.bind("<B1-Motion>", self._do_pan)
        self.bind("<MouseWheel>", self._do_zoom)
        self.bind("<Configure>", self._on_resize)
        self.bind("<Motion>", self._on_mouse_move)
        self.bind_all("<Control-plus>", self._do_zoom)
        self.bind_all("<Control-equal>", self._do_zoom)
        self.bind_all("<Control-minus>", self._do_zoom)

    def _start_pan(self, event: tk.Event) -> None:
        """Start panning operation."""
        self._pan_start_x = event.x
        self._pan_start_y = event.y

    def _do_pan(self, event: tk.Event) -> None:
        """Handle panning motion."""
        dx = event.x - self._pan_start_x
        dy = event.y - self._pan_start_y
        self.offset_x += dx
        self.offset_y += dy
        self._pan_start_x = event.x
        self._pan_start_y = event.y
        self.redraw_callback()

    def _do_zoom(self, event: tk.Event) -> None:
        """Handle zoom operation from mouse wheel or keyboard shortcuts."""
        if event.type == tk.EventType.MouseWheel:
            if event.delta > 0 and self.zoom_scale >= Config.MAX_ZOOM:
                return
            if event.delta < 0 and self.zoom_scale <= Config.MIN_ZOOM:
                return
            factor = Config.ZOOM_FACTOR if event.delta > 0 else 1 / Config.ZOOM_FACTOR
            mouse_x = self.canvasx(event.x)
            mouse_y = self.canvasy(event.y)

        elif event.type == tk.EventType.KeyPress:
            key = event.keysym.lower()
            if key in ("equal", "plus") and self.zoom_scale < Config.MAX_ZOOM:
                factor = Config.ZOOM_FACTOR
            elif key == "minus" and self.zoom_scale > Config.MIN_ZOOM:
                factor = 1 / Config.ZOOM_FACTOR
            else:
                return
            mouse_x = self.canvasx(self.winfo_width() / 2)
            mouse_y = self.canvasy(self.winfo_height() / 2)
        else:
            return

        new_scale = max(Config.MIN_ZOOM, min(self.zoom_scale * factor, Config.MAX_ZOOM))
        if new_scale != self.zoom_scale:
            old_grid_size = self.get_dynamic_grid_cell_size()
            old_world_x = (mouse_x - self.offset_x) / self.zoom_scale
            old_world_y = (mouse_y - self.offset_y) / self.zoom_scale
            self.zoom_scale = new_scale
            new_grid_size = self.get_dynamic_grid_cell_size()
            grid_scale_factor = new_grid_size / old_grid_size
            new_world_x = old_world_x * grid_scale_factor
            new_world_y = old_world_y * grid_scale_factor
            self.offset_x = mouse_x - new_world_x * self.zoom_scale
            self.offset_y = mouse_y - new_world_y * self.zoom_scale

            self.redraw_callback()

    def _on_resize(self, event: tk.Event) -> None:
        """Handle canvas resize."""
        self.redraw_callback()

    def _on_mouse_move(self, event: tk.Event) -> None:
        """Handle mouse movement for hover effects."""
        if self.hover_callback:
            wx = (event.x - self.offset_x) / self.zoom_scale
            wy = (event.y - self.offset_y) / self.zoom_scale
            self.hover_callback(wx, wy)

    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        return x * self.zoom_scale + self.offset_x, y * self.zoom_scale + self.offset_y

    # Line thickness constants
    MIN_THICKNESS = 1
    MAX_THICKNESS = 3

    def draw_line(
            self,
            x1: float, y1: float,
            x2: float, y2: float,
            color: str, thickness: float = 1.0,
            scale_rate: float = 1.0,
            tag: str = "") -> int:
        """Draw a line in world coordinates."""

        sx1, sy1 = self.world_to_screen(x1, y1)
        sx2, sy2 = self.world_to_screen(x2, y2)
        effective_scale = self.zoom_scale ** scale_rate
        base_thickness = thickness * effective_scale
        scaled_thickness = max(self.MIN_THICKNESS, min(self.MAX_THICKNESS, base_thickness))
        return self.create_line(
            sx1, sy1, sx2, sy2,
            fill=color,
            width=scaled_thickness,
            tags=tag
        )

    def draw_rectangle(
            self,
            x: float, y: float,
            width: float, height: float,
            color: str, outline_color: str = "black",
            outline_thickness=1.0,
            scale_rate: float = 1.0,
            tag: str = "") -> int:
        """Draw a filled rectangle in world coordinates."""

        sx, sy = self.world_to_screen(x, y)
        effective_scale = self.zoom_scale ** scale_rate
        scaled_width = width * effective_scale
        scaled_height = height * effective_scale
        base_thickness = outline_thickness * effective_scale
        scaled_thickness = max(self.MIN_THICKNESS, min(self.MAX_THICKNESS, base_thickness))

        sx1 = sx - scaled_width / 2
        sy1 = sy - scaled_height / 2
        sx2 = sx + scaled_width / 2
        sy2 = sy + scaled_height / 2

        return self.create_rectangle(
            sx1, sy1, sx2, sy2,
            fill=color, outline=outline_color,
            width=scaled_thickness,
            tags=tag
        )

    def draw_outline_rectangle(
            self,
            x: float, y: float,
            width: float, height: float,
            outline_color: str, thickness: float = 1.0,
            scale_rate: float = 1.0,
            tag: str = "") -> int:
        """Draw an outline rectangle in world coordinates."""

        sx, sy = self.world_to_screen(x, y)
        effective_scale = self.zoom_scale ** scale_rate
        scaled_width = width * effective_scale
        scaled_height = height * effective_scale
        base_thickness = thickness * effective_scale
        scaled_thickness = max(self.MIN_THICKNESS, min(self.MAX_THICKNESS, base_thickness))

        sx1 = sx - scaled_width / 2
        sy1 = sy - scaled_height / 2
        sx2 = sx + scaled_width / 2
        sy2 = sy + scaled_height / 2

        return self.create_rectangle(
            sx1, sy1, sx2, sy2,
            fill="", outline=outline_color,
            width=scaled_thickness,
            tags=tag
        )

    def draw_text(
            self,
            x: float, y: float,
            text: str,
            color: str = "white", font_size: int = 12,
            angle: float = 0,
            scale_rate: float = 1.0,
            tag: str = "") -> int:
        """Draw text in world coordinates."""

        sx, sy = self.world_to_screen(x, y)
        effective_scale = self.zoom_scale ** scale_rate
        scaled_font_size = max(1, int(font_size * effective_scale))
        return self.create_text(
            sx, sy, text=text,
            fill=color, font=("", scaled_font_size),
            angle=angle,
            tags=tag
        )

    @staticmethod
    @lru_cache(maxsize=1024)
    def _get_font(scaled_size: int) -> tkFont.Font:
        """Cache Font objects"""
        return tkFont.Font(size=scaled_size)

    @staticmethod
    @lru_cache(maxsize=4096)
    def _measure_text_width_scaled(text: str, scaled_size: int) -> float:
        """Cache measuremeants"""
        f = ZoomPanCanvas._get_font(scaled_size)
        return f.measure(text)

    @staticmethod
    @lru_cache(maxsize=1024)
    def _measure_text_height_scaled(scaled_size: int) -> float:
        """Actual cached measurement with scaled font size"""
        f = ZoomPanCanvas._get_font(scaled_size)
        return f.metrics("linespace")

    def get_text_width(self, text: str, font_size: int, scale_rate: float = 1.0) -> float:
        zoom_scale = self.zoom_scale
        effective_scale = zoom_scale ** scale_rate
        scaled_size = max(1, int(font_size * effective_scale))
        width_px = ZoomPanCanvas._measure_text_width_scaled(text, scaled_size)
        return width_px / effective_scale

    def get_text_height(self, font_size: int, scale_rate: float = 1.0) -> float:
        zoom_scale = self.zoom_scale
        effective_scale = zoom_scale ** scale_rate
        scaled_size = max(1, int(font_size * effective_scale))
        height_px = ZoomPanCanvas._measure_text_height_scaled(scaled_size)
        return height_px / effective_scale
