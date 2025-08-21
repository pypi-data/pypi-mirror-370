import os
from typing import Optional

from AnyQt import QtWidgets
from AnyQt import QtGui
from AnyQt.QtCore import Qt, QPoint


class ImageViewer(QtWidgets.QGraphicsView):
    """Image viewer with panning and zooming"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorUnderMouse)
        self.setDragMode(self.ScrollHandDrag)
        self._last_mouse_pos: Optional[QPoint] = None

    def load_image(self, image_path: Optional[str]) -> None:
        """Load an image from file"""
        if image_path and os.path.isfile(image_path):
            pixmap = QtGui.QPixmap(image_path)
            self._scene.clear()
            self._scene.addPixmap(pixmap)
        else:
            self._scene.clear()

    def wheelEvent(self, event) -> None:
        """Zoom in or out with mouse wheel"""
        # Center on the mouse position
        view_pos = event.pos()
        scene_pos_before_scale = self.mapToScene(view_pos)
        self.centerOn(scene_pos_before_scale)

        # Scale
        factor = 1.1
        if event.angleDelta().y() < 0:
            factor = 0.9
        self.scale(factor, factor)

        # Shift in position due to scaling
        scene_pos_after_scale = self.mapToScene(view_pos)
        shift_by_scaling = scene_pos_after_scale - scene_pos_before_scale

        # Undo the shift due to scaling
        center_after_scale = self.mapToScene(self.viewport().rect().center())
        self.centerOn(center_after_scale - shift_by_scaling)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Store initial mouse position for panning"""
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """Clear last mouse position on release"""
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = None

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Pan the view with left mouse button pressed"""
        if event.buttons() != Qt.LeftButton or self._last_mouse_pos is None:
            return
        delta = event.pos() - self._last_mouse_pos
        self._last_mouse_pos = event.pos()

        hscrollbar = self.horizontalScrollBar()
        hpos = hscrollbar.value()
        hscrollbar.setValue(hpos - delta.x())

        vscrollbar = self.verticalScrollBar()
        vpos = vscrollbar.value()
        vscrollbar.setValue(vpos - delta.y())
