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

from unittest.mock import Mock, patch
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPoint, QPointF, QEvent
from PySide6.QtGui import QMouseEvent, QDrag

from wperf_cmn_visualizer.tabbing import TabbedInterface, TabSection, DraggableTabBar, TabData


class TestTabData:
    """Tests for TabData class"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_tab_data_initialization(self):
        """Test TabData stores widget, title, and source section correctly"""
        widget = QWidget()
        title = "Extra Long Title"
        display_title = "Test Tab"
        section = Mock()

        tab_data = TabData(widget, title, display_title, section)

        assert tab_data.widget is widget
        assert tab_data.title == title
        assert tab_data.source_section is section


class TestDraggableTabBar:
    """Tests for DraggableTabBar class"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        """Set up test fixtures"""
        self.main_window = Mock()
        self.section = Mock()
        self.section.main_window = self.main_window
        self.tab_widget = Mock()
        self.tab_bar = DraggableTabBar(self.tab_widget, self.section)

    def teardown_method(self):
        """Clean up"""
        self.tab_bar.deleteLater()

    def test_initialization(self):
        """Test DraggableTabBar initializes correctly"""
        assert self.tab_bar.tab_widget is self.tab_widget
        assert self.tab_bar.section is self.section
        assert self.tab_bar.drag_start_pos is None
        assert self.tab_bar.acceptDrops() is True

    def test_mouse_press_sets_drag_start_pos(self):
        """
        Test mock mouse press event sets drag start position at correct place.
        """
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPoint(10, 20),
            QPoint(10, 20),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )

        self.tab_bar.mousePressEvent(event)
        assert self.tab_bar.drag_start_pos == QPoint(10, 20)

    def test_mouse_press_ignores_non_left_button(self):
        """
        Test mouse press with non-left button is ignored.
        """
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPoint(10, 20),
            QPoint(10, 20),
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier
        )

        self.tab_bar.mousePressEvent(event)
        assert self.tab_bar.drag_start_pos is None

    @patch.object(QApplication, 'startDragDistance', return_value=5)
    def test_mouse_move_starts_drag_when_distance_exceeded(self, mock_drag_distance):
        """
        Set mouse click at a point.
        Test mouse move starts drag when distance threshold exceeded.
        Mock drag threshold to known value.
        """
        self.tab_bar.drag_start_pos = QPointF(0, 0)
        with patch.object(self.tab_bar, 'start_drag') as mock_start_drag:
            event = QMouseEvent(
                QEvent.Type.MouseMove,
                QPoint(10, 0),  # threshold = 5, 10 > 5
                QPoint(10, 0),
                Qt.MouseButton.NoButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            )

            self.tab_bar.mouseMoveEvent(event)
            mock_start_drag.assert_called_once()  # ensure that start_drag method is called.

    @patch.object(QApplication, 'startDragDistance', return_value=20)
    def test_mouse_move_no_drag_when_distance_too_small(self, mock_drag_distance):
        """
        Set mouse click at a point.
        Test mouse move doesn't start drag when distance too small.
        """
        self.tab_bar.drag_start_pos = QPointF(0, 0)
        with patch.object(self.tab_bar, 'start_drag') as mock_start_drag:
            event = QMouseEvent(
                QEvent.Type.MouseMove,
                QPoint(5, 0),  # threshold = 20, 5 < 20
                QPoint(5, 0),
                Qt.MouseButton.NoButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            )

            self.tab_bar.mouseMoveEvent(event)
            mock_start_drag.assert_not_called()  # start_drag method should not be called.

    def test_start_drag_invalid_tab_index(self):
        """
        Ensure that dragging only occurs when started from a tab.
        start_drag method should returns early when tabAt returns invalid index
        """
        self.tab_bar.drag_start_pos = QPointF(10, 10)
        with patch.object(self.tab_bar, 'tabAt', return_value=-1), \
             patch.object(QDrag, 'exec', autospec=True) as mock_exec:

            self.tab_bar.start_drag()
            mock_exec.assert_not_called()

    @patch('wperf_cmn_visualizer.tabbing.QDrag')
    def test_start_drag_no_removal_when_same_section(self, mock_qdrag_class):
        """
        Test that dragging in the same section does NOT remove the tab.
        """
        self.tab_bar.drag_start_pos = QPointF(10, 10)

        mock_drag = Mock()
        mock_qdrag_class.return_value = mock_drag
        mock_drag.exec.return_value = Qt.DropAction.MoveAction

        with patch('wperf_cmn_visualizer.tabbing.TabData') as mock_tab_data_class:
            mock_tab_data_instance = Mock()
            mock_tab_data_instance.source_section = self.tab_bar.section
            mock_tab_data_class.return_value = mock_tab_data_instance

            test_widget = QWidget()
            self.tab_widget.widget.return_value = test_widget
            self.tab_widget.removeTab = Mock()
            self.tab_widget.addTab = Mock()

            with patch.object(self.tab_bar, 'tabAt', return_value=1), \
                 patch.object(self.tab_bar, 'tabText', return_value="Test Tab"):

                self.tab_bar.start_drag()

            mock_qdrag_class.assert_called_once_with(self.tab_bar)
            mock_drag.exec.assert_called_once_with(Qt.DropAction.MoveAction)
            self.tab_widget.removeTab.assert_not_called()  # should NOT remove tab since same section

    @patch('wperf_cmn_visualizer.tabbing.QDrag')
    def test_start_drag_removes_tab_when_different_section(self, mock_qdrag_class):
        """
        Test that dragging to a different section removes the tab.
        """
        self.tab_bar.drag_start_pos = QPointF(10, 10)

        mock_drag = Mock()
        mock_qdrag_class.return_value = mock_drag
        mock_drag.exec.return_value = Qt.DropAction.MoveAction

        with patch('wperf_cmn_visualizer.tabbing.TabData') as mock_tab_data_class:
            mock_tab_data_instance = Mock()
            mock_tab_data_instance.source_section = 'different_section'
            mock_tab_data_class.return_value = mock_tab_data_instance

            test_widget = QWidget()
            self.tab_widget.widget.return_value = test_widget
            self.tab_widget.removeTab = Mock()
            self.tab_widget.addTab = Mock()

            with patch.object(self.tab_bar, 'tabAt', return_value=1), \
                 patch.object(self.tab_bar, 'tabText', return_value="Test Tab"):

                self.tab_bar.start_drag()

            mock_qdrag_class.assert_called_once_with(self.tab_bar)
            mock_drag.exec.assert_called_once_with(Qt.DropAction.MoveAction)
            self.tab_widget.removeTab.assert_called_once_with(1)  # removed because different section


class TestTabSection:
    """Tests for TabSection class"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        """Set up test fixtures"""
        self.main_window = Mock()
        self.section = TabSection(self.main_window)

    def teardown_method(self):
        """Clean up"""
        self.section.deleteLater()

    def test_initialization(self):
        """Test TabSection initializes correctly"""
        assert self.section.main_window is self.main_window
        assert self.section.tabs is not None
        assert isinstance(self.section.tabs.tabBar(), DraggableTabBar)

    def test_add_tab(self):
        """Test adding a tab"""
        widget = QWidget()
        title = "Test Tab"

        index = self.section.add_tab(widget, title)

        assert index >= 0
        assert self.section.tabs.widget(index) is widget
        assert self.section.tabs.tabText(index) == title
        assert self.section.tabs.currentIndex() == index

    def test_close_tab(self):
        """Test closing a tab"""
        widget = QWidget()
        index = self.section.add_tab(widget, "Test Tab")

        with patch.object(widget, 'deleteLater') as mock_delete:
            self.section.close_tab(index)
            mock_delete.assert_called_once()

        assert self.section.tabs.widget(index) is None

    def test_close_tab_triggers_cleanup_when_empty(self):
        """
        Test closing last tab triggers cleanup.
        Empty Sections must not exist.
        """
        widget = QWidget()
        index = self.section.add_tab(widget, "Test Tab")
        self.section.close_tab(index)

        self.main_window.cleanup_after_tab_close.assert_called_once_with(self.section)

    def test_close_tab_no_cleanup_when_not_empty(self):
        """
        Test closing tab doesn't trigger cleanup when section not empty.
        Sections with tabs remaining should stay alive.
        """
        widget1 = QWidget()
        widget2 = QWidget()
        self.section.add_tab(widget1, "Tab 1")
        index2 = self.section.add_tab(widget2, "Tab 2")
        self.section.close_tab(index2)

        self.main_window.cleanup_after_tab_close.assert_not_called()

    def test_is_empty(self):
        """Simple test for is_empty method"""
        assert self.section.is_empty() is True

        widget = QWidget()
        self.section.add_tab(widget, "Test Tab")
        assert self.section.is_empty() is False

        self.section.close_tab(0)
        assert self.section.is_empty() is True


class TestTabbedInterface:
    """Tests for TabbedInterface class"""

    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setup_method(self):
        """Set up test fixtures"""
        self.interface = TabbedInterface()

    def teardown_method(self):
        """Clean up"""
        self.interface.deleteLater()

    def test_initialization(self):
        """Test TabbedInterface initializes with one section"""
        assert len(self.interface.sections) == 1
        assert isinstance(self.interface.sections[0], TabSection)
        assert self.interface.drop_info is None

    def test_add_section_at_end(self):
        """Test adding section at end"""
        initial_count = len(self.interface.sections)

        section = self.interface.add_section()
        assert len(self.interface.sections) == initial_count + 1
        assert self.interface.sections[-1] is section

    def test_add_section_at_position(self):
        """Test adding section at given position"""
        self.interface.add_section()  # Add second section

        section = self.interface.add_section(1)  # Insert at position 1
        assert len(self.interface.sections) == 3
        assert self.interface.sections[1] is section

    def test_remove_section(self):
        """Test removing a section"""
        section = self.interface.add_section()
        initial_count = len(self.interface.sections)

        with patch.object(section, 'deleteLater') as mock_delete:
            self.interface.remove_section(section)
            mock_delete.assert_called_once()

        assert len(self.interface.sections) == initial_count - 1
        assert section not in self.interface.sections

    def test_cleanup_after_successful_move_keeps_last_section(self):
        """
        Test cleanup doesn't remove section when there is only one.
        Minimum number of sections = 1
        """
        while len(self.interface.sections) > 1:
            self.interface.remove_section(self.interface.sections[-1])

        source_section = self.interface.sections[0]
        source_section.is_empty = Mock(return_value=True)

        with patch.object(self.interface, 'remove_section') as mock_remove:
            self.interface.cleanup_after_successful_move(source_section)
            mock_remove.assert_not_called()

    def test_get_drop_info_left_third(self):
        """
        Test get_drop_info returns 'left' for left third of section.
        Drop info must return left string.
        """
        section = self.interface.sections[0]
        section.setGeometry(0, 0, 300, 100)

        # Point in left third (x < 100)
        drop_info = self.interface.get_drop_info(QPointF(50, 50))
        assert drop_info == (0, 'left')

    def test_get_drop_info_right_third(self):
        """
        Test get_drop_info returns 'right' for right third of section
        """
        section = self.interface.sections[0]
        section.setGeometry(0, 0, 300, 100)

        # Point in right third (x > 200)
        drop_info = self.interface.get_drop_info(QPointF(250, 50))
        assert drop_info == (1, 'right')

    def test_get_drop_info_center(self):
        """
        Test get_drop_info returns 'center' for middle third of section
        """
        section = self.interface.sections[0]
        section.setGeometry(0, 0, 300, 100)

        # Point in center third
        drop_info = self.interface.get_drop_info(QPointF(150, 50))
        assert drop_info == (0, 'center')

    def test_handle_drop_center_adds_to_existing_section(self):
        """
        When a tab is dropped in the center of a section,
        it should dock into that section.
        """
        widget = QWidget()
        source_section = Mock()
        mime_data = TabData(widget, "Test Tab", "Test Tab", source_section)
        event = Mock()
        event.mimeData.return_value = mime_data
        event.acceptProposedAction = Mock()

        with patch.object(self.interface, 'get_drop_info', return_value=(0, 'center')), \
             patch.object(self.interface.sections[0], 'add_tab') as mock_add_tab:

            self.interface.handle_drop(event, QPointF(50, 50))
            mock_add_tab.assert_called_once_with(widget, "Test Tab")

    def test_handle_drop_side_creates_new_section(self):
        """
        Dropping tab towards left or right should create a new section.
        Dropped tab should be added to new section.
        """
        widget = QWidget()
        source_section = Mock()
        mime_data = TabData(widget, "Test Tab", "Test Tab", source_section)
        event = Mock()
        event.mimeData.return_value = mime_data
        event.acceptProposedAction = Mock()

        with patch.object(self.interface, 'get_drop_info', return_value=(0, 'left')), \
             patch.object(self.interface, 'add_section') as mock_add_section:

            mock_new_section = Mock()
            mock_add_section.return_value = mock_new_section

            self.interface.handle_drop(event, QPointF(50, 50))

            mock_add_section.assert_called_once_with(0)
            mock_new_section.add_tab.assert_called_once_with(widget, "Test Tab")
