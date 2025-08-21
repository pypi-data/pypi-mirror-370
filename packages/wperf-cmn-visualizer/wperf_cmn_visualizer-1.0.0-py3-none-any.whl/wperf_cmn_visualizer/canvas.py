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
Base Canvas class with drawing features.
Zoomable pannable class which inherits from Canvas.
Allows for user interaction with mouse.
"""

from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem
from PySide6.QtGui import QPaintEvent, QPainter, QWheelEvent, QMouseEvent, QResizeEvent, QPen, QBrush, QColor, QFont, QFontMetrics
from PySide6.QtCore import Qt, QObject, QRectF, QPointF, QSize, QEvent
from typing import cast, Callable, Tuple, Optional, Any
from functools import lru_cache

from .config import Config


class Canvas(QWidget):
    """
    A PySide6 QWidget subclass that serves as a pure drawing surface.
    It contains a QGraphicsScene and QGraphicsView, and provides
    methods for drawing shapes and text in scene coordinates.

    This is the base class for simple UI rendering like tooltips.
    No world coordinates, no transformations - just direct scene drawing.
    """

    # Line thickness constants
    MIN_THICKNESS = 1
    MAX_THICKNESS = 3

    def __init__(self, master: QWidget, **kwargs: Any) -> None:
        """
        Args:
            master : QWidget
                The parent container
            kwargs : dict
                Additional keyword arguments passed on to parent class
        """
        super().__init__(master, **kwargs)

        # Set up QGraphicsScene and QGraphicsView
        # Scene holds items to be rendered
        # View is what those items are rendered to
        self.scene: QGraphicsScene = QGraphicsScene(self)

        self.view: QGraphicsView = QGraphicsView(self.scene, self)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Cached pen/brush
        self._brush = QBrush(QColor("black"))
        self._pen = QPen()

    def resizeEvent(self, event: QResizeEvent):
        """Handle canvas resize."""
        super().resizeEvent(event)
        self.view.setGeometry(self.rect())
        new_size: QSize = event.size()
        self.scene.setSceneRect(0, 0, new_size.width(), new_size.height())

    def draw_line(self, x1: float, y1: float, x2: float, y2: float,
                  color: QColor, thickness: float = 1.0, scale_rate: float = 1.0,
                  data: Any = None) -> None:
        """Draw a line in scene coordinates."""
        self._pen.setColor(QColor(color))
        self._pen.setWidthF(thickness)
        item = self.scene.addLine(x1, y1, x2, y2, self._pen)
        if data is not None:
            item.setData(0, data)

    def draw_rectangle(self, x: float, y: float, width: float, height: float,
                       color: QColor, outline_color: QColor = QColor("black"),
                       outline_thickness: float = 1.0, scale_rate: float = 1.0,
                       data: Any = None) -> None:
        """Draw a filled rectangle in scene coordinates."""
        rect = QRectF(x - width / 2, y - height / 2, width, height)
        self._brush.setColor(color)
        self._pen.setColor(outline_color)
        self._pen.setWidthF(outline_thickness)
        item = self.scene.addRect(rect, self._pen, self._brush)
        if data is not None:
            item.setData(0, data)

    def draw_outline_rectangle(self, x: float, y: float, width: float, height: float,
                               outline_color: QColor, thickness: float = 1.0,
                               scale_rate: float = 1.0, data: Any = None) -> None:
        """Draw an outline rectangle in scene coordinates."""
        rect = QRectF(x - width / 2, y - height / 2, width, height)
        self._pen.setColor(outline_color)
        self._pen.setWidthF(thickness)
        item = self.scene.addRect(rect, self._pen)
        if data:
            item.setData(0, data)

    def draw_text(self, x: float, y: float, text: str, color: QColor = QColor("white"),
                  font_size: int = 12, angle: float = 0, scale_rate: float = 1.0,
                  data: Any = None) -> None:
        """Draw text using QGraphicsSimpleTextItem in scene coordinates."""
        item = QGraphicsSimpleTextItem(text)
        item.setFont(self._get_font(font_size))
        self._brush.setColor(color)
        item.setBrush(self._brush)

        self.scene.addItem(item)
        bounding = item.boundingRect()
        item.setPos(x - bounding.width() / 2, y - bounding.height() / 2)

        if angle != 0:
            item.setTransformOriginPoint(bounding.center())
            item.setRotation(angle)
        if data is not None:
            item.setData(0, data)

    @staticmethod
    @lru_cache(maxsize=128)
    def _get_font(font_size: int) -> QFont:
        """Cache Font objects"""
        font = QFont()
        font.setPointSize(font_size)
        return font

    def get_text_width(self, text: str, font_size: int, scale_rate: float = 1.0) -> float:
        """Get text width in scene coordinates."""
        # Note: scale_rate is ignored in base Canvas (no scaling)
        font = self._get_font(font_size)
        metrics = QFontMetrics(font)
        return float(metrics.horizontalAdvance(str(text)))

    def get_text_height(self, font_size: int, scale_rate: float = 1.0) -> float:
        """Get text height in scene coordinates."""
        # Note: scale_rate is ignored in base Canvas (no scaling)
        font = self._get_font(font_size)
        metrics = QFontMetrics(font)
        return float(metrics.height())


class ZoomPanCanvas(Canvas):
    """
    A PySide6 QWidget subclass that supports zooming and panning.
    This canvas allows users to zoom in and out and pan across the content.
    Attributes:
        zoom_scale : float
            The current zoom scale factor.
        offset_x : float
            Horizontal offset for panning.
        offset_y : float
            Vertical offset for panning.
        redraw_callback : Callable[[], None]
            Callback to trigger canvas redraw; must take zero arguments.
    """
    def __init__(self, master: QWidget, redraw_callback: Callable[[], None],
                 hover_callback: Callable[[float, float], None], **kwargs: Any) -> None:
        """
        Args:
            master : QWidget
                The parent container
            redraw_callback : Callable[[], None]
                A callback function that is called whenever the canvas
                needs to be redrawn, such as after panning or zooming.
                This function must take no parameters.
            hover_callback: Callable[[float, float], None]
                A callback function that is called whenever the mouse
                hovers over the canvas. Called with the world x and world y
                coordinates.
            kwargs : dict
                Additional keyword arguments passed on to parent class
        """
        super().__init__(master, **kwargs)
        self._zoom_scale: float = Config.DEFAULT_ZOOM
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self._pan_start: Optional[QPointF] = None
        self.redraw_callback: Callable[[], None] = redraw_callback
        self.hover_callback: Callable[[float, float], None] = hover_callback

        self.scene.setSceneRect(-500000, -500000, 1000000, 1000000)
        self.view.setMouseTracking(True)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

        # Event handlers
        self.view.viewport().installEventFilter(self)

    @property
    def zoom_scale(self) -> float:
        return self._zoom_scale

    @zoom_scale.setter
    def zoom_scale(self, value: float) -> None:
        self._zoom_scale = max(Config.MIN_ZOOM, min(value, Config.MAX_ZOOM))

    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        return x * self.zoom_scale + self.offset_x, y * self.zoom_scale + self.offset_y

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return (sx - self.offset_x) / self.zoom_scale, (sy - self.offset_y) / self.zoom_scale

    def get_dynamic_grid_cell_size(self) -> float:
        """Scale Current Grid Size."""
        return Config.GRID_CELL_SIZE * (1.0 + (self.zoom_scale - 1.0) * 0.3)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float,
                  color: QColor, thickness: float = 1.0, scale_rate: float = 1.0,
                  data: Any = None) -> None:
        """Draw a line in world coordinates."""
        sx1, sy1 = self.world_to_screen(x1, y1)
        sx2, sy2 = self.world_to_screen(x2, y2)
        effective_scale = self.zoom_scale ** scale_rate
        base_thickness = thickness * effective_scale
        scaled_thickness = max(self.MIN_THICKNESS, min(self.MAX_THICKNESS, base_thickness))

        super().draw_line(sx1, sy1, sx2, sy2, color, scaled_thickness, data)

    def draw_rectangle(self, x: float, y: float, width: float, height: float,
                       color: QColor, outline_color: QColor = QColor("black"),
                       outline_thickness: float = 1.0, scale_rate: float = 1.0,
                       data: Any = None) -> None:
        """Draw a filled rectangle in world coordinates."""
        sx, sy = self.world_to_screen(x, y)
        effective_scale = self.zoom_scale ** scale_rate
        scaled_width = width * effective_scale
        scaled_height = height * effective_scale
        base_thickness = outline_thickness * effective_scale
        scaled_thickness = max(self.MIN_THICKNESS, min(self.MAX_THICKNESS, base_thickness))

        super().draw_rectangle(sx, sy, scaled_width, scaled_height,
                               color, outline_color, scaled_thickness, data)

    def draw_outline_rectangle(self, x: float, y: float, width: float, height: float,
                               outline_color: QColor, thickness: float = 1.0,
                               scale_rate: float = 1.0, data: Any = None) -> None:
        """Draw an outline rectangle in world coordinates."""
        sx, sy = self.world_to_screen(x, y)
        effective_scale = self.zoom_scale ** scale_rate
        scaled_width = width * effective_scale
        scaled_height = height * effective_scale
        base_thickness = thickness * effective_scale
        scaled_thickness = max(self.MIN_THICKNESS, min(self.MAX_THICKNESS, base_thickness))

        super().draw_outline_rectangle(sx, sy, scaled_width, scaled_height,
                                       outline_color, scaled_thickness, data)

    def draw_text(self, x: float, y: float, text: str, color: QColor = QColor("white"),
                  font_size: int = 12, angle: float = 0, scale_rate: float = 1.0,
                  data: Any = None) -> None:
        """Draw text in world coordinates."""
        sx, sy = self.world_to_screen(x, y)
        effective_scale = self.zoom_scale ** scale_rate
        scaled_font_size = max(1, int(font_size * effective_scale))

        super().draw_text(sx, sy, text, color, scaled_font_size, angle, data)

    # Override text measurement methods for world coordinates
    def get_text_width(self, text: str, font_size: int, scale_rate: float = 1.0) -> float:
        """Get text width in world coordinates."""
        effective_scale = self.zoom_scale ** scale_rate
        scaled_size = max(1, int(font_size * effective_scale))
        width_px = super().get_text_width(text, scaled_size)
        return width_px / effective_scale

    def get_text_height(self, font_size: int, scale_rate: float = 1.0) -> float:
        """Get text height in world coordinates."""
        effective_scale = self.zoom_scale ** scale_rate
        scaled_size = max(1, int(font_size * effective_scale))
        height_px = super().get_text_height(scaled_size)
        return height_px / effective_scale

    def _start_pan(self, event: QMouseEvent) -> None:
        """Start panning operation."""
        self._pan_start = event.position()

    def _do_pan(self, event: QMouseEvent) -> None:
        """Handle panning motion."""
        if not self._pan_start:
            return

        dx = event.position().x() - self._pan_start.x()
        dy = event.position().y() - self._pan_start.y()
        self.offset_x += dx
        self.offset_y += dy
        self._pan_start = event.position()
        self.redraw_callback()

    def _do_zoom(self, event: QWheelEvent) -> None:
        """Handle zoom operation from mouse wheel."""
        angle_delta = event.angleDelta().y()
        if angle_delta == 0:
            return

        factor = Config.ZOOM_FACTOR if angle_delta > 0 else 1 / Config.ZOOM_FACTOR
        mouse_x = event.position().x()
        mouse_y = event.position().y()

        old_zoom = self.zoom_scale
        old_grid_size = self.get_dynamic_grid_cell_size()
        old_world_x = (mouse_x - self.offset_x) / self.zoom_scale
        old_world_y = (mouse_y - self.offset_y) / self.zoom_scale

        self.zoom_scale = self.zoom_scale * factor
        if self.zoom_scale != old_zoom:
            new_grid_size = self.get_dynamic_grid_cell_size()
            grid_scale_factor = new_grid_size / old_grid_size
            new_world_x = old_world_x * grid_scale_factor
            new_world_y = old_world_y * grid_scale_factor
            self.offset_x = mouse_x - new_world_x * self.zoom_scale
            self.offset_y = mouse_y - new_world_y * self.zoom_scale

            self.redraw_callback()

    def paintEvent(self, event: QPaintEvent) -> None:
        self.redraw_callback()
        return super().paintEvent(event)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        """Handle all mouse and keyboard events."""
        if source is self.view.viewport():
            if event.type() == event.Type.Wheel:
                self._do_zoom(cast(QWheelEvent, event))
                return True

            elif event.type() == event.Type.MouseButtonPress:
                event = cast(QMouseEvent, event)
                if event.button() == Qt.MouseButton.LeftButton:
                    self._start_pan(event)
                    return True

            elif event.type() == event.Type.MouseMove:
                if self._pan_start:
                    self._do_pan(cast(QMouseEvent, event))
                else:
                    event = cast(QMouseEvent, event)
                    world_pos: QPointF = (event.position() - QPointF(self.offset_x, self.offset_y)) / self.zoom_scale  # type: ignore
                    self.hover_callback(world_pos.x(), world_pos.y())
                return True

            elif event.type() == event.Type.MouseButtonRelease:
                event = cast(QMouseEvent, event)
                if event.button() == Qt.MouseButton.LeftButton:
                    self._pan_start = None
                    return True
        return super().eventFilter(source, event)
