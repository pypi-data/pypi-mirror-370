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
Tabbing Module.
Main exposed module is TabbedInterface. Easily add Tabs with rendered content.
Enables Docking, Split Windowing as well as drag and drop of tabs.
"""

from PySide6.QtCore import (
    Qt, QMimeData, QPointF, QObject, QEvent
)
from PySide6.QtGui import (
    QDrag, QPainter, QPen, QColor, QMouseEvent,
    QDragEnterEvent, QDragMoveEvent, QDropEvent
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QSplitter,
    QTabWidget, QTabBar,
)
from typing import Optional, Tuple, cast


class TabData(QMimeData):
    """
    A subclass of QMimeData to carry information about a draggable tab.
    Attributes:
        widget (QWidget): The widget contained in the tab.
        title (str): The tab's original full title (not truncated).
        display_title (str): The tab's display title (potentially truncated).
        source_section (TabSection): The TabSection where the drag originated.
    """
    def __init__(self, widget: QWidget, title: str, display_title: str, source_section: 'TabSection') -> None:
        """
        Initialise TabData with the widget, titles, and source section.
        Args:
            widget (QWidget): The widget inside the tab.
            title (str): The tab's original full title.
            display_title (str): The tab's display title (potentially truncated).
            source_section (TabSection): The section from which the drag started.
        """
        super().__init__()
        self.widget: QWidget = widget
        self.title: str = title  # Original full title
        self.display_title: str = display_title  # Display title (potentially truncated)
        self.source_section: TabSection = source_section


class DraggableTabBar(QTabBar):
    """
    A QTabBar subclass that allows for tabs to be dragged.
    This class initiates the tab drag and attached `TabData` to drag.
    Attributes:
        tab_widget (QTabWidget): The parent tab widget.
        section (TabSection): The TabSection this tab bar belongs to.
        drag_start_pos (Optional[QPointF]): Position where the drag started.
    """
    def __init__(self, tab_widget: QTabWidget, section: 'TabSection') -> None:
        """
        Initialise DraggableTabBar.
        Args:
            tab_widget (QTabWidget): The tab widget to manage.
            section (TabSection): The owning TabSection.
        """
        super().__init__()
        self.tab_widget: QTabWidget = tab_widget
        self.section: TabSection = section
        self.drag_start_pos: Optional[QPointF] = None
        self.setAcceptDrops(True)
        self.installEventFilter(self)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Record the position where the left mouse button was pressed.
        Args:
            event (QMouseEvent): The mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Initiate drag if mouse drag was enough to trigger a drag.
        Drag Threshold is set by PySide::QApplication.
        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.drag_start_pos is not None and (event.position() - self.drag_start_pos).manhattanLength() >= \
                QApplication.startDragDistance():
            self.start_drag()
        else:
            super().mouseMoveEvent(event)

    def start_drag(self) -> None:
        """
        Create and start a QDrag operation for the tab under the drag start position.
        Removes the tab only if moved to a different section.
        Now preserves the original full title.
        """
        # early returns for invalid drags
        if not self.drag_start_pos:
            return
        index = self.tabAt(self.drag_start_pos.toPoint())
        if index < 0:
            return

        widget = self.tab_widget.widget(index)
        display_title = self.tabText(index)
        original_title = self.section.get_original_title(index)  # Get the original full title

        mime_data = TabData(widget, original_title, display_title, self.section)
        drag = QDrag(self)
        drag.setMimeData(mime_data)

        result = drag.exec(Qt.DropAction.MoveAction)

        if result == Qt.DropAction.MoveAction and mime_data.source_section != self.section:
            self.tab_widget.removeTab(index)


class TabSection(QWidget):
    """
    A container widget representing a section containing tabs.
    Attributes:
        main_window (TabbedInterface): The main interface containing this section.
        tabs (QTabWidget): The tab widget managing tabs within the section.
    """

    TAB_TITLE_SOFT_LIMIT = 35
    TAB_TITLE_HARD_LIMIT = 40

    def __init__(self, main_window: 'TabbedInterface') -> None:
        """
        Initialise a TabSection.
        Args:
            main_window (TabbedInterface): The main parent widget.
        """
        super().__init__()
        self.main_window: TabbedInterface = main_window

        self._original_titles: dict[int, str] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs: QTabWidget = QTabWidget()
        self.tabs.setTabBar(DraggableTabBar(self.tabs, self))
        self.tabs.tabCloseRequested.connect(self.close_tab)

        layout.addWidget(self.tabs)

    def truncate_title(self, title: str) -> tuple[str, str]:
        """
        Truncate title if needed and return display title and full title for tooltip.
        Args:
            title (str): Original title
        Returns:
            tuple[str, str]: (display_title, tooltip_title)
        """
        if len(title) <= self.TAB_TITLE_SOFT_LIMIT:
            return title, title
        elif len(title) <= self.TAB_TITLE_HARD_LIMIT:
            return title, title
        else:
            truncated = title[:self.TAB_TITLE_SOFT_LIMIT - 3] + "..."
            return truncated, title

    def add_tab(self, widget: QWidget, title: str) -> int:
        """
        Add a new tab with the given widget and title.
        Handles title truncation and tooltip setup.
        Args:
            widget (QWidget): The widget to be displayed in the new tab.
            title (str): The tab's original full title.
        Returns:
            int: The index of the newly added tab.
        """
        display_title, tooltip_title = self.truncate_title(title)
        index = self.tabs.addTab(widget, display_title)

        # Store the original title
        self._original_titles[index] = title

        # Set tooltip if title was truncated
        if display_title != tooltip_title:
            self.tabs.tabBar().setTabToolTip(index, tooltip_title)

        self.tabs.setCurrentIndex(index)
        return index

    def get_original_title(self, index: int) -> str:
        """
        Get the original full title for a tab at the given index.
        Args:
            index (int): The tab index.
        Returns:
            str: The original full title, or the display title if not found.
        """
        return self._original_titles.get(index, self.tabs.tabText(index))

    def close_tab(self, index: int) -> None:
        """
        Close the tab at the specified index and clean up if section becomes empty.
        Args:
            index (int): The index of the tab to close.
        """
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()

        # Update title tracking data structure
        if index in self._original_titles:
            del self._original_titles[index]
        updated_titles = {}
        for tab_index, original_title in self._original_titles.items():
            if tab_index > index:
                updated_titles[tab_index - 1] = original_title
            else:
                updated_titles[tab_index] = original_title
        self._original_titles = updated_titles

        self.tabs.removeTab(index)

        if self.is_empty():
            self.main_window.cleanup_after_tab_close(self)

    def is_empty(self) -> bool:
        """
        Check if the section has no tabs.
        Returns:
            bool: True if no tabs exist, False otherwise.
        """
        return self.tabs.count() == 0


class DropTargetHighlight(QWidget):
    """
    An widget to visually indicate drop targets during drag-and-drop.
    Attributes:
        drop_info (Optional[Tuple[int, str]]): The current drop target info (section index, position).
        sections (list[TabSection]): The list of TabSections.
    """
    PEN_WIDTH: int = 5

    def __init__(self, parent: QWidget) -> None:
        """
        Initialise the overlay.
        Args:
            parent (QWidget): The parent widget (usually the TabbedInterface).
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.drop_info: Optional[Tuple[int, str]] = None
        self.sections: list[TabSection] = []

    def set_sections(self, sections: list[TabSection]) -> None:
        """
        Set the list of TabSections the overlay is tracking.
        Args:
            sections (list[TabSection]): List of current sections.
        """
        self.sections = sections

    def set_drop_info(self, drop_info: Optional[Tuple[int, str]]) -> None:
        """
        Update the drop indicator position and trigger repaint.
        Args:
            drop_info (Optional[Tuple[int, str]]): Tuple containing section index and position ('left', 'right', 'center').
        """
        self.drop_info = drop_info
        self.update()

    def paintEvent(self, event) -> None:
        """
        Paint the drop indicator depending on drop_info.
        If central drop, highlight the full section.
        If right/left drop, highlight drop direction.
        Args:
            event (QPaintEvent): Paint event.
        """
        if self.drop_info is None:
            return
        painter = QPainter(self)
        pen = QPen(QColor(0, 120, 215), DropTargetHighlight.PEN_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        section_index, position = self.drop_info
        if position == 'center' and section_index < len(self.sections):
            section_rect = self.sections[section_index].geometry()
            painter.drawRect(section_rect.adjusted(DropTargetHighlight.PEN_WIDTH, DropTargetHighlight.PEN_WIDTH, -DropTargetHighlight.PEN_WIDTH, -DropTargetHighlight.PEN_WIDTH))
        else:
            x = self.width() - 2 if section_index >= len(self.sections) else self.sections[section_index].geometry().x()
            painter.drawLine(x, DropTargetHighlight.PEN_WIDTH, x, self.height() - DropTargetHighlight.PEN_WIDTH)


class TabbedInterface(QWidget):
    """
    The main widget containing multiple TabSections with draggable tabs.
    Attributes:
        sections (list[TabSection]): The list of TabSections.
        drop_info (Optional[Tuple[int, str]]): Current drop target info.
        _highlight (DropTargetHighlight): The overlay widget showing drop targets.
        splitter (QSplitter): Splitter managing sections horizontally.
    """

    def __init__(self) -> None:
        """
        Initialise the TabbedInterface.
        """
        super().__init__()
        self.sections: list[TabSection] = []
        self.drop_info: Optional[Tuple[int, str]] = None
        self.setup_ui()
        self.installEventFilter(self)

    def setup_ui(self) -> None:
        """
        Setup the UI elements: splitter, _highlight, and initial section.
        """
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setHandleWidth(0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self._highlight: DropTargetHighlight = DropTargetHighlight(self)
        self._highlight.setGeometry(self.rect())
        self._highlight.set_sections(self.sections)
        self._highlight.show()
        self._highlight.raise_()

        self.add_section()

    def resizeEvent(self, event) -> None:
        """
        Ensure _highlight resizes with the main widget.
        Args:
            event (QResizeEvent): Resize event.
        """
        super().resizeEvent(event)
        self._highlight.setGeometry(self.rect())

    def add_section(self, position: int = -1) -> TabSection:
        """
        Add a new TabSection at the specified position.
        Args:
            position (int): Index at which to insert the new section. Defaults to -1 (append).
        Returns:
            TabSection: The newly created TabSection.
        """
        section = TabSection(self)
        if position == -1 or position > len(self.sections):
            position = len(self.sections)
        self.sections.insert(position, section)
        self.splitter.insertWidget(position, section)
        self.install_event_filters(section)
        self._highlight.set_sections(self.sections)
        return section

    def install_event_filters(self, widget: QWidget) -> None:
        """
        Install event filters on a widget and all its child widgets.
        Allows for pass through of Drag/Drop
        Args:
            widget (QWidget): The widget to install filters on.
        """
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def remove_section(self, section: TabSection) -> None:
        """
        Remove a TabSection from the interface and delete it.
        Args:
            section (TabSection): The section to remove.
        """
        if section in self.sections:
            self.sections.remove(section)
            section.deleteLater()
            self._highlight.set_sections(self.sections)

    def cleanup_after_successful_move(self, source_section: TabSection) -> None:
        """
        Remove section if it is empty and multiple sections exist.
        Args:
            source_section (TabSection): Section from which a tab was moved.
        """
        if source_section.is_empty() and len(self.sections) > 1:
            self.remove_section(source_section)

    def cleanup_after_tab_close(self, section: TabSection) -> None:
        """
        Remove section if it becomes empty after tab closure and multiple sections exist.
        Args:
            section (TabSection): The section where a tab was closed.
        """
        if section.is_empty() and len(self.sections) > 1:
            self.remove_section(section)

    def get_drop_info(self, pos: QPointF) -> Optional[Tuple[int, str]]:
        """
        Determine the drop target section and position based on mouse position.
        Args:
            pos (QPointF): Position relative to the TabbedInterface.
        Returns:
            Optional[Tuple[int, str]]: The target section index and position ('left', 'right', 'center').
        """
        global_pos = self.mapToGlobal(pos.toPoint())
        local_pos = self.mapFromGlobal(global_pos)
        # hit test each section
        for i, section in enumerate(self.sections):
            section_rect = section.geometry()
            if section_rect.contains(local_pos):
                relative_x = local_pos.x() - section_rect.x()
                section_width = section_rect.width()
                if relative_x < section_width * 0.33:
                    return (i, 'left')
                elif relative_x > section_width * 0.67:
                    return (i + 1, 'right')
                else:
                    return (i, 'center')

        return None

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Handle drag-and-drop events and update drop indicators.
        Args:
            obj (QObject): Object receiving the event.
            event (QEvent): The event.
        Returns:
            bool: True if event handled, otherwise False.
        """
        if event.type() == QEvent.Type.DragEnter:
            drag_event = cast(QDragEnterEvent, event)
            if isinstance(drag_event.mimeData(), TabData):
                drag_event.acceptProposedAction()
                return True

        elif event.type() == QEvent.Type.DragMove:
            drag_event = cast(QDragMoveEvent, event)
            if isinstance(drag_event.mimeData(), TabData):
                child_pos = drag_event.position()
                global_pos = cast(QWidget, obj).mapToGlobal(child_pos.toPoint())
                local_pos = QPointF(self.mapFromGlobal(global_pos))
                self.drop_info = self.get_drop_info(local_pos)
                self._highlight.set_drop_info(self.drop_info)
                drag_event.acceptProposedAction()
                return True

        elif event.type() == QEvent.Type.Drop:
            drop_event = cast(QDropEvent, event)
            if isinstance(drop_event.mimeData(), TabData):
                child_pos = drop_event.position()
                global_pos = cast(QWidget, obj).mapToGlobal(child_pos.toPoint())
                local_pos = QPointF(self.mapFromGlobal(global_pos))
                self.handle_drop(drop_event, local_pos)
                return True

        elif event.type() == QEvent.Type.DragLeave:
            self.drop_info = None
            self._highlight.set_drop_info(None)
            return True

        return super().eventFilter(obj, event)

    def handle_drop(self, event: QDropEvent, pos: QPointF) -> None:
        """
        Process the drop event.
        Add Tab into section if central drop.
        Else create new section and add tab into new section.
        Args:
            event (QDropEvent): The drop event.
            pos (QPointF): Position where the drop occurred.
        """
        mime_data = event.mimeData()
        if not isinstance(mime_data, TabData):
            return
        drop_info = self.get_drop_info(pos)
        if not drop_info:
            return

        section_index, position = drop_info

        if position == 'center':
            if section_index < len(self.sections):
                self.sections[section_index].add_tab(mime_data.widget, mime_data.title)
        else:
            new_section = self.add_section(section_index)
            new_section.add_tab(mime_data.widget, mime_data.title)

        self.cleanup_after_successful_move(mime_data.source_section)
        self.drop_info = None
        self._highlight.set_drop_info(None)
        event.acceptProposedAction()

    def add_tab(self, widget: QWidget, title: str, section_index: int = 0) -> int:
        """
        Add a new tab to a specified section, creating the section if none exist.
        Args:
            widget (QWidget): The widget to add as a tab.
            title (str): The tab's title.
            section_index (int): The index of the section to add the tab to.
        Returns:
            int: The index of the added tab within the section.
        """
        if not self.sections:
            self.add_section()
        section_index = min(section_index, len(self.sections) - 1)
        result = self.sections[section_index].add_tab(widget, title)
        self.install_event_filters(widget)
        return result
