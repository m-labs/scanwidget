import logging

from PyQt5 import QtGui, QtCore, QtWidgets
from numpy import linspace

from ticker import Ticker


logger = logging.getLogger(__name__)


class ScanAxis(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.proxy = None
        self.sizePolicy().setControlType(QtWidgets.QSizePolicy.ButtonBox)
        self.ticker = Ticker()
        qfm = QtGui.QFontMetrics(QtGui.QFont())
        lineSpacing = qfm.lineSpacing()
        descent = qfm.descent()
        self.setMinimumHeight(2*lineSpacing + descent + 5 + 5)

    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        qfm = QtGui.QFontMetrics(painter.font())
        avgCharWidth = qfm.averageCharWidth()
        lineSpacing = qfm.lineSpacing()
        descent = qfm.descent()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # The center of the slider handles should reflect what's displayed
        # on the spinboxes.
        painter.translate(self.proxy.slider.handleWidth()/2, self.height() - 5)
        painter.drawLine(0, 0, self.width(), 0)
        realLeft = self.proxy.pixelToReal(0)
        realRight = self.proxy.pixelToReal(self.width())
        ticks, prefix, labels = self.ticker(realLeft, realRight)
        painter.drawText(0, -5-descent-lineSpacing, prefix)

        pen = QtGui.QPen()
        pen.setWidth(2)
        painter.setPen(pen)

        for t, l in zip(ticks, labels):
            t = self.proxy.realToPixel(t)
            painter.drawLine(t, 0, t, -5)
            painter.drawText(t - len(l)/2*avgCharWidth, -5-descent, l)

        sliderStartPixel = self.proxy.realToPixel(self.proxy.realStart)
        sliderStopPixel = self.proxy.realToPixel(self.proxy.realStop)
        pixels = linspace(sliderStartPixel, sliderStopPixel,
                          self.proxy.numPoints)
        for p in pixels:
            p_int = int(p)
            painter.drawLine(p_int, 0, p_int, 5)
        ev.accept()


# Basic ideas from https://gist.github.com/Riateche/27e36977f7d5ea72cf4f
class ScanSlider(QtWidgets.QSlider):
    sigStartMoved = QtCore.pyqtSignal(int)
    sigStopMoved = QtCore.pyqtSignal(int)

    def __init__(self):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Horizontal)
        self.startPos = None  # Pos and Val can differ in event handling.
        # perhaps prevPos and currPos is more accurate.
        self.stopPos = None
        self.startVal = None
        self.stopVal = None
        self.offset = None
        self.position = None
        self.stopPressed = QtWidgets.QStyle.SC_None
        self.startPressed = QtWidgets.QStyle.SC_None
        self.firstMovement = False  # State var for handling slider overlap.
        self.blockTracking = False

        self.setRange(0, 4095)

        # We need fake sliders to keep around so that we can dynamically
        # set the stylesheets for drawing each slider later. See paintEvent.
        self.dummyStartSlider = QtWidgets.QSlider()
        self.dummyStopSlider = QtWidgets.QSlider()
        self.dummyStartSlider.setStyleSheet(
            "QSlider::handle {background:blue}")
        self.dummyStopSlider.setStyleSheet(
            "QSlider::handle {background:red}")

    # We basically superimpose two QSliders on top of each other, discarding
    # the state that remains constant between the two when drawing.
    # Everything except the handles remain constant.
    def initHandleStyleOption(self, opt, handle):
        self.initStyleOption(opt)
        if handle == "start":
            opt.sliderPosition = self.startPos
            opt.sliderValue = self.startVal
        elif handle == "stop":
            opt.sliderPosition = self.stopPos
            opt.sliderValue = self.stopVal

    # We get the range of each slider separately.
    def pixelPosToRangeValue(self, pos):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                         QtWidgets.QStyle.SC_SliderGroove,
                                         self)
        rangeVal = QtWidgets.QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), pos - gr.x(),
            self.effectiveWidth(), opt.upsideDown)
        return rangeVal

    def rangeValueToPixelPos(self, val):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        pixel = QtWidgets.QStyle.sliderPositionFromValue(
            self.minimum(), self.maximum(), val, self.effectiveWidth(),
            opt.upsideDown)
        return pixel

    # When calculating conversions to/from pixel space, not all of the slider's
    # width is actually usable, because the slider handle has a nonzero width.
    # We use this function as a helper when the axis needs slider information.
    def handleWidth(self):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        sr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                         QtWidgets.QStyle.SC_SliderHandle,
                                         self)
        return sr.width()

    def effectiveWidth(self):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                         QtWidgets.QStyle.SC_SliderGroove,
                                         self)
        return gr.width() - self.handleWidth()

    def handleMousePress(self, pos, control, val, handle):
        # If chosen slider at edge, treat it as non-interactive.
        v = self.startVal if handle == "start" else self.stopVal
        if v in (self.minimum(), self.maximum()):
            return QtWidgets.QStyle.SC_None

        opt = QtWidgets.QStyleOptionSlider()
        self.initHandleStyleOption(opt, handle)
        newControl = self.style().hitTestComplexControl(
            QtWidgets.QStyle.CC_Slider, opt, pos, self)
        sr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                         QtWidgets.QStyle.SC_SliderHandle,
                                         self)
        if newControl == QtWidgets.QStyle.SC_SliderHandle:
            # no pick()- slider orientation static
            self.offset = pos.x() - sr.topLeft().x()
            self.setSliderDown(True)
        # Needed?
        if newControl != control:
            self.update(sr)
        return newControl

    def drawHandle(self, painter, handle):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        self.initHandleStyleOption(opt, handle)
        opt.subControls = QtWidgets.QStyle.SC_SliderHandle
        painter.drawComplexControl(QtWidgets.QStyle.CC_Slider, opt)

    def setStartPosition(self, val):
        if val == self.startPos:
            return
        self.startPos = val
        if not self.hasTracking() or self.blockTracking:
            return
        # TODO: Is this necessary? QStyle::sliderPositionFromValue appears
        # to clamp already.
        low = min(max(self.minimum(), val), self.maximum())
        if low != self.startVal:
            self.startVal = low
            self.startPos = low
            self.update()

    def setStopPosition(self, val):
        if val == self.stopPos:
            return
        self.stopPos = val
        if not self.hasTracking() or self.blockTracking:
            return
        # TODO: Is this necessary? QStyle::sliderPositionFromValue appears
        # to clamp already.
        high = min(max(self.minimum(), val), self.maximum())
        if high != self.stopVal:
            self.stopVal = high
            self.stopPos = high
            self.update()

    def mousePressEvent(self, ev):
        if ev.buttons() ^ ev.button():
            ev.ignore()
            return

        # Prefer stopVal in the default case.
        self.stopPressed = self.handleMousePress(
            ev.pos(), self.stopPressed, self.stopVal, "stop")
        if self.stopPressed != QtWidgets.QStyle.SC_SliderHandle:
            self.startPressed = self.handleMousePress(
                ev.pos(), self.stopPressed, self.startVal, "start")

        # State that is needed to handle the case where two sliders are equal.
        self.firstMovement = True
        ev.accept()

    def mouseMoveEvent(self, ev):
        if (self.startPressed != QtWidgets.QStyle.SC_SliderHandle and
                self.stopPressed != QtWidgets.QStyle.SC_SliderHandle):
            ev.ignore()
            return

        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)

        # This code seems to be needed so that returning the slider to the
        # previous position is honored if a drag distance is exceeded.
        m = self.style().pixelMetric(QtWidgets.QStyle.PM_MaximumDragDistance,
                                     opt, self)
        newPos = self.pixelPosToRangeValue(ev.pos().x() - self.offset)

        if m >= 0:
            r = self.rect().adjusted(-m, -m, m, m)
            if not r.contains(ev.pos()):
                newPos = self.position

        if self.firstMovement:
            if self.startPos == self.stopPos:
                # StopSlider is preferred, except in the case where
                # start == max possible value the slider can take.
                if self.startPos == self.maximum():
                    self.startPressed = QtWidgets.QStyle.SC_SliderHandle
                    self.stopPressed = QtWidgets.QStyle.SC_None
                self.firstMovement = False

        if self.startPressed == QtWidgets.QStyle.SC_SliderHandle:
            self.setStartPosition(newPos)
            self.sigStartMoved.emit(self.startPos)

        if self.stopPressed == QtWidgets.QStyle.SC_SliderHandle:
            self.setStopPosition(newPos)
            self.sigStopMoved.emit(self.stopPos)

        ev.accept()

    def mouseReleaseEvent(self, ev):
        QtWidgets.QSlider.mouseReleaseEvent(self, ev)
        self.setSliderDown(False)  # AbstractSlider needs this
        self.startPressed = QtWidgets.QStyle.SC_None
        self.stopPressed = QtWidgets.QStyle.SC_None

    def paintEvent(self, ev):
        # Use QStylePainters to make redrawing as painless as possible.
        # Paint on the custom widget, using the attributes of the fake
        # slider references we keep around. setStyleSheet within paintEvent
        # leads to heavy performance penalties (and recursion?).
        # QPalettes would be nicer to use, since palette entries can be set
        # individually for each slider handle, but Windows 7 does not
        # use them. This seems to be the only way to override the colors
        # regardless of platform.
        startPainter = QtWidgets.QStylePainter(self, self.dummyStartSlider)
        stopPainter = QtWidgets.QStylePainter(self, self.dummyStopSlider)

        # Handles
        # Qt will snap sliders to 0 or maximum() if given a desired pixel
        # location outside the mapped range. So we manually just don't draw
        # the handles if they are at 0 or max.
        if self.minimum() < self.startVal < self.maximum():
            self.drawHandle(startPainter, "start")
        if self.minimum() < self.stopVal < self.maximum():
            self.drawHandle(stopPainter, "stop")


# real (Sliders) => pixel (one pixel movement of sliders would increment by X)
# => range (minimum granularity that sliders understand).
class ScanWidget(QtWidgets.QWidget):
    sigStartMoved = QtCore.pyqtSignal(float)
    sigStopMoved = QtCore.pyqtSignal(float)
    sigNumChanged = QtCore.pyqtSignal(int)

    def __init__(self, zoomFactor=1.05, zoomMargin=.1, dynamicRange=1e9):
        QtWidgets.QWidget.__init__(self)
        self.slider = slider = ScanSlider()
        self.axis = axis = ScanAxis()
        axis.proxy = self

        # Layout.
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(axis)
        layout.addWidget(slider)
        self.setLayout(layout)

        # Context menu entries
        self.menu = QtWidgets.QMenu(self)
        viewRangeAct = QtWidgets.QAction("&View Range", self)
        viewRangeAct.triggered.connect(self.viewRange)
        self.menu.addAction(viewRangeAct)
        snapRangeAct = QtWidgets.QAction("&Snap Range", self)
        snapRangeAct.triggered.connect(self.snapRange)
        self.menu.addAction(snapRangeAct)

        self.realStart = None
        self.realStop = None
        self.numPoints = None
        self.zoomMargin = zoomMargin
        self.dynamicRange = dynamicRange
        self.zoomFactor = zoomFactor

        self.realToPixelTransform = -self.axis.width()/2, 1.

        # Connect event observers.
        axis.installEventFilter(self)
        slider.installEventFilter(self)
        slider.sigStopMoved.connect(self.handleStopMoved)
        slider.sigStartMoved.connect(self.handleStartMoved)

    def contextMenuEvent(self, ev):
        self.menu.popup(ev.globalPos())

    # pixel vals for sliders: 0 to slider_width - 1
    def realToPixel(self, val):
        a, b = self.realToPixelTransform
        rawVal = b*(val - a)
        # Clamp pixel values to 32 bits, b/c Qt will otherwise wrap values.
        rawVal = min(max(-(1 << 31), rawVal), (1 << 31) - 1)
        return rawVal

    def pixelToReal(self, val):
        a, b = self.realToPixelTransform
        return val/b + a

    def rangeToReal(self, val):
        pixelVal = self.slider.rangeValueToPixelPos(val)
        return self.pixelToReal(pixelVal)

    def realToRange(self, val):
        pixelVal = self.realToPixel(val)
        return self.slider.pixelPosToRangeValue(pixelVal)

    def setView(self, left, scale):
        self.realToPixelTransform = left, scale
        sliderX = self.realToRange(self.realStop)
        self.slider.setStopPosition(sliderX)
        sliderX = self.realToRange(self.realStart)
        self.slider.setStartPosition(sliderX)
        self.axis.update()

    def setStop(self, val):
        if self.realStop == val:
            return
        sliderX = self.realToRange(val)
        self.slider.setStopPosition(sliderX)
        self.realStop = val
        self.axis.update()  # Number of points ticks changed positions.
        self.sigStopMoved.emit(val)

    def setStart(self, val):
        if self.realStart == val:
            return
        sliderX = self.realToRange(val)
        self.slider.setStartPosition(sliderX)
        self.realStart = val
        self.axis.update()
        self.sigStartMoved.emit(val)

    def setNumPoints(self, val):
        if self.numPoints == val:
            return
        self.numPoints = val
        self.axis.update()
        self.sigNumChanged.emit(val)

    def handleStopMoved(self, rangeVal):
        val = self.rangeToReal(rangeVal)
        self.realStop = val
        self.axis.update()
        self.sigStopMoved.emit(val)

    def handleStartMoved(self, rangeVal):
        val = self.rangeToReal(rangeVal)
        self.realStart = val
        self.axis.update()
        self.sigStartMoved.emit(val)

    def handleZoom(self, zoomFactor, mouseXPos):
        newScale = self.realToPixelTransform[1] * zoomFactor
        refReal = self.pixelToReal(mouseXPos)
        newLeft = refReal - mouseXPos/newScale
        newZero = newLeft*newScale + self.slider.effectiveWidth()/2
        if zoomFactor > 1 and abs(newZero) > self.dynamicRange:
            return
        self.setView(newLeft, newScale)

    def viewRange(self):
        newScale = self.slider.effectiveWidth()/abs(
            self.realStop - self.realStart)
        newScale *= 1 - 2*self.zoomMargin
        newCenter = (self.realStop + self.realStart)/2
        if newCenter:
            newScale = min(newScale, self.dynamicRange/abs(newCenter))
        newLeft = newCenter - self.slider.effectiveWidth()/2/newScale
        self.setView(newLeft, newScale)

    def snapRange(self):
        lowRange = self.zoomMargin
        highRange = 1 - self.zoomMargin
        newStart = self.pixelToReal(lowRange * self.slider.effectiveWidth())
        newStop = self.pixelToReal(highRange * self.slider.effectiveWidth())
        self.setStart(newStart)
        self.setStop(newStop)

    def wheelEvent(self, ev):
        y = ev.angleDelta().y()
        if y:
            if ev.modifiers() & QtCore.Qt.ShiftModifier:
                # If shift+scroll, modify number of points.
                # TODO: This is not perfect. For high-resolution touchpads you
                # get many small events with y < 120 which should accumulate.
                # That would also match the wheel behavior of an integer
                # spinbox.
                z = int(y / 120.)
                self.setNumPoints(max(1, self.numPoints + z))
                ev.accept()
            elif ev.modifiers() & QtCore.Qt.ControlModifier:
                z = self.zoomFactor**(y / 120.)
                # Remove the slider-handle shift correction, b/c none of the
                # other widgets know about it. If we have the mouse directly
                # over a tick during a zoom, it should appear as if we are
                # doing zoom relative to the ticks which live in axis
                # pixel-space, not slider pixel-space.
                self.handleZoom(z, ev.x() - self.slider.handleWidth()/2)
                ev.accept()
            else:
                ev.ignore()

    def eventFilter(self, obj, ev):
        if ev.type() == QtCore.QEvent.Wheel:
            self.wheelEvent(ev)
            return True
        if not (obj is self.axis and ev.type() == QtCore.QEvent.Resize):
            return False
        if ev.oldSize().isValid():
            oldLeft = self.pixelToReal(0)
            refWidth = ev.oldSize().width() - self.slider.handleWidth()
            refRight = self.pixelToReal(refWidth)
            newWidth = ev.size().width() - self.slider.handleWidth()
            newScale = newWidth/(refRight - oldLeft)
            center = (self.realStop + self.realStart)/2
            if center:
                newScale = min(newScale, self.dynamicRange/abs(center))
            self.setView(oldLeft, newScale)
        else:
            self.viewRange()
        return False
