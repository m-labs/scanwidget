import math

from PyQt5 import QtGui, QtCore, QtWidgets

# ScanAxis consists of a horizontal line extending indefinitely, major and
# minor ticks, and numbers over the major ticks. During a redraw, the width
# between adjacent ticks is recalculated, based on the new requested bounds.
#
# If the width is smaller than a certain threshold, the major ticks become
# minor ticks, and the minor ticks are deleted as objects.
class ScanAxis(QtWidgets.QGraphicsWidget):
    def __init__(self):
        QtWidgets.QGraphicsWidget.__init__(self)
        self.boundleft = 0
        self.boundright = 1

    def paint(self, painter, op, widget):
        # sceneRect = self.scene.sceneRect()
        pass


class DataPoint(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, pxSize = 2, color = QtGui.QColor(128,128,128,128)):
        QtWidgets.QGraphicsEllipseItem.__init__(self, 0, 0, pxSize, pxSize)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setBrush(color)
        self.setPen(color)


# class ScanModel(QO


# ScanScene holds all the objects, and controls how events are received to
# the ScanSliders (in particular, constraining movement to the x-axis).
# TODO: SceneRect only ever has to be as large in the Y-direction as the sliders.
class ScanScene(QtWidgets.QGraphicsScene):
    def __init__(self):
        QtWidgets.QGraphicsScene.__init__(self)

    def mouseMoveEvent(self, ev):
        
        QtWidgets.QGraphicsScene.mouseMoveEvent(self, ev)
        
    # def mouseClickEvent(self, ev):
    #     pass
    # 
    # def mouseDragEvent(self, ev):
    #     pass
    # 
    # def keyPressEvent(self, ev):

# Check for mouse events over the widget. If shift pressed and mouse click,
# change signal/event propogation to alter the number of points over which
# to scan. This widget should intercept mouse events/prevent events from
# reaching ScanSlider if shift is pressed.
class ScanBox(QtWidgets.QWidget):
    pass

# Houses the ScanAxis and Sliders in one row, buttons which auto-scale the view
# in another. Also 

# Needs to be subclassed from QGraphicsItem* b/c Qt will not send mouse events
# to GraphicsItems that do not reimplement mousePressEvent (How does Qt know?).
# Qt decides this while iterating to find which GraphicsItem should get control
# of the mouse. mousePressEvent is accepted by default.
# TODO: The slider that was most recently clicked should have z-priority.
# Qt's mouseGrab logic should implement this correctly.
# * Subclassed from QGraphicsObject to get signal functionality.
# ScanSlider assumes that it's parent is the scene.
class ScanSlider(QtWidgets.QGraphicsObject):
    sigPosChanged = QtCore.pyqtSignal(float)
    
    def __init__(self, pxSize = 20, color = QtGui.QColor(128,128,128,128)):
        QtWidgets.QGraphicsItem.__init__(self)
        self.xChanged.connect(self.emitSigPosChanged)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.pxSize = pxSize
        self.color = color
        
        # Make slider an equilateral triangle w/ sides pxSize pixels wide.
        altitude = math.ceil((pxSize/2)*math.sqrt(3))
        
        points = [QtCore.QPoint(-(self.pxSize/2), altitude), \
            QtCore.QPoint(0, 0), QtCore.QPoint((self.pxSize/2), altitude)]
        self.shape = QtGui.QPolygon(points)

    def boundingRect(self):
        penWidth = 1 # Not user-settable.
        # If bounding box does not cover whole polygon, trails will be left
        # when the object is moved.
        return QtCore.QRectF(-self.pxSize/2 - penWidth/2, 0 - penWidth/2, \
            self.pxSize + penWidth, self.pxSize + penWidth)

    def paint(self, painter, op, widget):
        painter.setBrush(self.color)
        painter.setPen(self.color)
        painter.drawConvexPolygon(self.shape)

    def mousePressEvent(self, ev):
        QtWidgets.QGraphicsItem.mousePressEvent(self, ev)

    def mouseMoveEvent(self, ev):
        QtWidgets.QGraphicsItem.mouseMoveEvent(self, ev)

    def emitSigPosChanged(self):
        self.sigPosChanged.emit(self.scenePos().x())

    # Constrain movement to X axis and ensure that the sliders (bounding box?)
    # do not leave the scene.
    # TODO: We need make sure the view doesn't recenter the scene in an attempt
    # to prevent adding scrollbars. Scene's X-axis should always be centered
    # at (0,0). 
    # TODO: Resize event for the scene should maintain current slider
    # positions or rescale the X-axis so the distance between
    # sliders and the edge of the scene remains proportional?
    def itemChange(self, change, val):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            newPos = val
            newPos.setY(0) # Constrain movement to X-axis of parent.
            return newPos
        return QtWidgets.QGraphicsItem.itemChange(self, change, val)
        


# The ScanWidget proper.
# TODO: Scene is centered on visible items by default when the scene is first
# viewed. We do not want this here; viewed portion of scene should be fixed.
# Items are moved/transformed within the fixed scene.
# TODO: On a resize, should the spinbox's default increment change?
class ScanWidget(QtWidgets.QGraphicsView):
    sigMinChanged = QtCore.pyqtSignal(float)
    sigMaxChanged = QtCore.pyqtSignal(float)
    sigNumChanged = QtCore.pyqtSignal(int)
    
    def __init__(self):
        self.scene = ScanScene()
        QtWidgets.QGraphicsView.__init__(self, self.scene)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.setSceneRect(self.frameGeometry()) # Ensure no scrollbars.
        
        self.minSlider = ScanSlider(color = QtGui.QColor(0,0,255,128))
        self.maxSlider = ScanSlider(color = QtGui.QColor(255,0,0,128))
        self.scene.addItem(self.minSlider)
        self.scene.addItem(self.maxSlider)
        self.minSlider.sigPosChanged.connect(self.sigMinChanged)
        self.maxSlider.sigPosChanged.connect(self.sigMaxChanged)

    def setMax(self, val):
        # emitting sigPosChanged might be moved to setPos. This will prevent
        # infinite recursion in that case.
        if val != self.maxSlider.scenePos(): # WARNING: COMPARING FLOATS! 
            self.maxSlider.setPos(QtCore.QPointF(val, 0))
        # self.update() # Might be needed, but paint seems to occur correctly.

    def setMin(self, val):
        if val != self.minSlider.scenePos(): # WARNING: COMPARING FLOATS! 
            self.minSlider.setPos(QtCore.QPointF(val, 0))

    def setNumPoints(self, val):
        pass

    def zoomOut(self):
        self.scale(1/1.2, 1)

    def zoomIn(self):
        self.scale(1.2, 1)

    def wheelEvent(self, ev):
        # if ev.delta() > 0: # TODO: Qt-4 specific.
        # TODO: If sliders are off screen after a zoom-in, what should we do?
        if ev.angleDelta().y() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    # Items in scene grab mouse in this function. If shift is pressed, skip
    # deciding which slider to grab and the view itself will get mouse Events.
    # This enables adding/deleting points.
    def mousePressEvent(self, ev):
        if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ShiftModifier:
            pass
        else:
            QtWidgets.QGraphicsView.mousePressEvent(self, ev)

    def mouseMoveEvent(self, ev):
        QtWidgets.QGraphicsView.mouseMoveEvent(self, ev)

    # def resizeEvent(self):
    #     pass
