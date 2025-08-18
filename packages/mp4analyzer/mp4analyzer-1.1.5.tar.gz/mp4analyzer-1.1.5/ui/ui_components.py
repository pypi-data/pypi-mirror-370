# UI component builders for MP4 Analyzer application.
from typing import Callable, Tuple, List
import html
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QWidget,
    QSlider,
    QPushButton,
    QSpinBox,
    QSizePolicy,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
)
from src.mp4analyzer import MP4Box
from ui.video_canvas import VideoDisplayCanvas
from ui.timeline_widget import TimelineBarGraph


class PlaybackControlWidget(QFrame):
    """Widget containing playback slider + navigation buttons."""

    def __init__(self, on_frame_changed: Callable[[int], None]):
        super().__init__()
        self.on_frame_changed = on_frame_changed

        # UI elements
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.previous_button = QPushButton("<")
        self.next_button = QPushButton(">")
        self.frame_counter_label = QLabel("0 / 0")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)

        # --- Title ---
        title = QLabel("Playback Control")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; border: none;")
        layout.addWidget(title)

        # --- Frame slider ---
        layout.addWidget(self.frame_slider)

        # --- Bottom row: counter + nav buttons ---
        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.frame_counter_label.setFixedSize(80, 25)
        self.frame_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(self.frame_counter_label)

        # Navigation buttons group
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 2, 0)
        for btn in [self.previous_button, self.next_button]:
            btn.setFixedSize(40, 25)
            btn.setStyleSheet("border: 1px solid #555; background: #333;")
        nav_layout.addWidget(self.previous_button)
        nav_layout.addWidget(self.next_button)
        bottom_layout.addWidget(nav, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addWidget(bottom)

        # Connect slider
        self.frame_slider.valueChanged.connect(self.on_frame_changed)

    def set_frame_range(self, max_frames: int):
        """Configure slider range based on total frames."""
        self.frame_slider.setRange(0, max(0, max_frames - 1))
        self.frame_slider.setValue(0)

    def set_current_frame(self, frame_index: int, total_frames: int):
        """Update counter label + slider position."""
        self.frame_counter_label.setText(f"{frame_index + 1} / {total_frames}")
        self.frame_slider.blockSignals(True)
        self.frame_slider.setValue(frame_index)
        self.frame_slider.blockSignals(False)


class LeftPanelWidget(QSplitter):
    """Left panel: metadata, MP4 boxes tree, log messages, and playback control."""

    def __init__(self, playback_control_widget: PlaybackControlWidget):
        super().__init__(Qt.Orientation.Vertical)

        # --- Metadata view ---
        self.metadata_view = QTextEdit()
        self.metadata_view.setPlaceholderText("MP4 Metadata")
        self.metadata_view.setReadOnly(True)

        metadata_container = QWidget()
        metadata_layout = QVBoxLayout(metadata_container)
        metadata_layout.setContentsMargins(0, 0, 0, 0)
        metadata_layout.addWidget(self.metadata_view)

        # --- Boxes tree section ---
        boxes_container = QWidget()
        boxes_layout = QVBoxLayout(boxes_container)
        boxes_layout.setContentsMargins(0, 0, 0, 0)

        # Header row with expand/collapse buttons
        boxes_header = QWidget()
        boxes_header.setFixedHeight(20)
        boxes_header_layout = QHBoxLayout(boxes_header)
        boxes_header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("MP4 Boxes")
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        title_label.setStyleSheet("font-weight: bold;")

        self.expand_button = QPushButton("+")
        self.collapse_button = QPushButton("-")
        for btn in [self.expand_button, self.collapse_button]:
            btn.setFixedSize(20, 20)
            btn.setStyleSheet("font-size: 12px;")

        boxes_header_layout.addWidget(
            title_label, alignment=Qt.AlignmentFlag.AlignVCenter
        )
        boxes_header_layout.addStretch()
        boxes_header_layout.addWidget(
            self.expand_button, alignment=Qt.AlignmentFlag.AlignVCenter
        )
        boxes_header_layout.addWidget(
            self.collapse_button, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        # Tree widget to display MP4 boxes
        self.boxes_tree = QTreeWidget()
        self.boxes_tree.setHeaderLabels(["Box", "Details"])
        self.boxes_tree.setTextElideMode(Qt.TextElideMode.ElideRight)

        boxes_layout.addWidget(boxes_header)
        boxes_layout.addWidget(self.boxes_tree)

        # Monospace font for metadata + tree
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.StyleHint.Monospace)
        self.metadata_view.setFont(monospace_font)
        self.boxes_tree.setFont(monospace_font)

        # Tree styling
        self.boxes_tree.setStyleSheet(
            """
            QTreeView::item {
                border-right: 1px solid #555;
            }
            QTreeView::item:last {
                border-right: none;
            }
            QTreeView::item:selected {
                background: purple;
                color: white;
            }
            """
        )

        # --- Log box ---
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Log Messages")

        # --- Add widgets to splitter ---
        self.addWidget(metadata_container)
        self.addWidget(boxes_container)
        self.addWidget(self.log_box)
        self.addWidget(playback_control_widget)
        self.setSizes([160, 440, 120, 80])

        # Expand/collapse actions
        self.expand_button.clicked.connect(
            lambda: (
                self.boxes_tree.expandAll(),
                self.boxes_tree.resizeColumnToContents(0),
                self.boxes_tree.resizeColumnToContents(1),
            )
        )
        self.collapse_button.clicked.connect(
            lambda: (
                self.boxes_tree.collapseAll(),
                self.boxes_tree.resizeColumnToContents(0),
                self.boxes_tree.resizeColumnToContents(1),
            )
        )

    def update_metadata(self, metadata_text: str):
        """Format and display metadata text in HTML."""
        lines = metadata_text.splitlines()
        html_lines: List[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped == "Video track(s) info":
                html_lines.append("<b>Video track(s) info:</b>")
            elif stripped == "Audio track(s) info":
                html_lines.append("<b>Audio track(s) info:</b>")
            else:
                html_lines.append(html.escape(line))
        html_content = "<pre style='margin:0'>{}</pre>".format("\n".join(html_lines))
        self.metadata_view.setHtml(html_content)

    def update_boxes(self, boxes: List[MP4Box]):
        """Populate MP4 box tree with parsed box hierarchy."""
        self.boxes_tree.clear()
        light_blue_brush = QBrush(QColor("#ADD8E6"))

        def _add_box(parent: QTreeWidgetItem, box: MP4Box, hierarchy: str = ""):
            props = box.properties()
            item = QTreeWidgetItem(parent)
            item.setText(1, hierarchy)

            # Label with type + optional name
            box_name = props.get("box_name", "")
            label_text = f"<span style='color:red'>{box.type}</span>"
            if box_name:
                label_text += f" <span style='color:gray'>({box_name})</span>"
            label = QLabel(label_text)
            label.setStyleSheet("background: transparent;")
            label.setFont(self.boxes_tree.font())
            self.boxes_tree.setItemWidget(item, 0, label)

            # Add properties
            for key, value in props.items():
                prop_item = QTreeWidgetItem(item, [key, str(value)])
                prop_item.setForeground(0, light_blue_brush)
                prop_item.setForeground(1, light_blue_brush)

            # Recurse into children
            child_hierarchy = (
                hierarchy + box.type + "/" if hierarchy or box.children else hierarchy
            )
            for child in box.children:
                _add_box(item, child, child_hierarchy)

        root = self.boxes_tree.invisibleRootItem()
        for box in boxes:
            _add_box(root, box)
        self.boxes_tree.expandToDepth(1)
        self.boxes_tree.resizeColumnToContents(0)
        self.boxes_tree.resizeColumnToContents(1)

    def add_log_message(self, message: str):
        """Append a message to the log box."""
        self.log_box.append(message)


class VideoControlBar(QWidget):
    """Control bar with file open, snapshot, zoom, and resolution display."""

    def __init__(
        self,
        on_open_file: Callable,
        on_save_snapshot: Callable,
        on_reset_zoom: Callable,
        on_zoom_changed: Callable[[int], None],
    ):
        super().__init__()

        # Controls
        self.open_button = QPushButton("Open")
        self.snapshot_button = QPushButton("Snapshot")
        self.reset_button = QPushButton("Reset")
        self.zoom_spinbox = QSpinBox()
        self.resolution_label = QLabel("--x--")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # File/zoom buttons
        for btn in [self.open_button, self.snapshot_button, self.reset_button]:
            btn.setStyleSheet("padding: 3px")

        layout.addWidget(self.open_button)
        layout.addWidget(self.snapshot_button)
        layout.addStretch()
        layout.addWidget(self.reset_button)

        # Zoom control spinbox
        self.zoom_spinbox.setRange(1, 500)
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setSuffix("%")
        self.zoom_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_spinbox.setStyleSheet("padding-bottom: 1px")
        layout.addWidget(self.zoom_spinbox)

        # Resolution text display
        self.resolution_label.setFixedSize(80, 25)
        self.resolution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.resolution_label)

        # Connect actions
        self.open_button.clicked.connect(on_open_file)
        self.snapshot_button.clicked.connect(on_save_snapshot)
        self.reset_button.clicked.connect(on_reset_zoom)
        self.zoom_spinbox.valueChanged.connect(on_zoom_changed)

    def set_resolution_text(self, resolution: str):
        """Update resolution label text."""
        self.resolution_label.setText(resolution)

    def reset_zoom_value(self):
        """Reset zoom to 100%."""
        self.zoom_spinbox.setValue(100)

    @property
    def current_zoom_percent(self) -> int:
        """Return current zoom value in percent."""
        return self.zoom_spinbox.value()


class RightPanelWidget(QSplitter):
    """Right panel: video canvas, control bar, and timeline graph."""

    def __init__(
        self,
        on_open_file: Callable,
        on_save_snapshot: Callable,
        on_reset_zoom: Callable,
        on_zoom_changed: Callable[[int], None],
        on_frame_selected: Callable[[int], None],
    ):
        super().__init__(Qt.Orientation.Vertical)

        # Subcomponents
        self.video_canvas = VideoDisplayCanvas()
        self.control_bar = VideoControlBar(
            on_open_file, on_save_snapshot, on_reset_zoom, on_zoom_changed
        )
        self.timeline_widget = TimelineBarGraph(on_frame_selected)

        # Scroll area for timeline
        self.timeline_scroll_area = QScrollArea()
        self.timeline_scroll_area.setWidget(self.timeline_widget)
        self.timeline_scroll_area.setWidgetResizable(False)
        self.timeline_scroll_area.setMinimumHeight(150)
        self.timeline_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.timeline_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.timeline_scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.timeline_widget.set_scroll_area(self.timeline_scroll_area)

        # Add to splitter
        self.addWidget(self.video_canvas)
        self.addWidget(self.control_bar)
        self.addWidget(self.timeline_scroll_area)

        self.setStretchFactor(0, 3)  # video area larger
        self.setStretchFactor(2, 1)  # timeline smaller


def create_main_layout(
    on_open_file: Callable,
    on_save_snapshot: Callable,
    on_reset_zoom: Callable,
    on_zoom_changed: Callable[[int], None],
    on_frame_changed: Callable[[int], None],
    on_frame_selected: Callable[[int], None],
) -> Tuple[QSplitter, PlaybackControlWidget, LeftPanelWidget, RightPanelWidget]:
    """Build the main window layout with left/right split panels."""
    main_splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel has metadata/log + playback control
    playback_control = PlaybackControlWidget(on_frame_changed)
    left_panel = LeftPanelWidget(playback_control)

    # Right panel has video canvas, control bar, and timeline
    right_panel = RightPanelWidget(
        on_open_file,
        on_save_snapshot,
        on_reset_zoom,
        on_zoom_changed,
        on_frame_selected,
    )

    main_splitter.addWidget(left_panel)
    main_splitter.addWidget(right_panel)
    main_splitter.setSizes([240, 960])  # initial size split

    return main_splitter, playback_control, left_panel, right_panel
