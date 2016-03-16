import logging

from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np

from ticker import Ticker


logger = logging.getLogger(__name__)


class ScanWidget(QtWidgets.QSlider):
    startChanged = QtCore.pyqtSignal(float)
    stopChanged = QtCore.pyqtSignal(float)
    numChanged = QtCore.pyqtSignal(int)

    def __init__(self, zoomFactor=1.05, zoomMargin=.1, dynamicRange=1e9):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Horizontal)
        self.zoomMargin = zoomMargin
        self.dynamicRange = dynamicRange
        self.zoomFactor = zoomFactor

        self.ticker = Ticker()

        self.menu = QtWidgets.QMenu(self)
        action = QtWidgets.QAction("&View Range", self)
        action.triggered.connect(self.viewRange)
        self.menu.addAction(action)
        action = QtWidgets.QAction("&Snap Range", self)
        action.triggered.connect(self.snapRange)
        self.menu.addAction(action)

        self.setRange(0, 4095)

        self._start, self._stop, self._num = None, None, None
        self._axisView, self._sliderView = None, None
        self._offset, self._pressed, self._dragLeft = None, None, None

    def contextMenuEvent(self, ev):
        self.menu.popup(ev.globalPos())

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        qfm = QtGui.QFontMetrics(self.font())
        return QtCore.QSize(5*10*qfm.averageCharWidth(),
                            4*qfm.lineSpacing())

    def _axisToPixel(self, val):
        a, b = self._axisView
        return a + val*b

    def _pixelToAxis(self, val):
        a, b = self._axisView
        return (val - a)/b

    def _setView(self, axis_left, axis_scale):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        g = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                        QtWidgets.QStyle.SC_SliderGroove,
                                        self)
        h = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                        QtWidgets.QStyle.SC_SliderHandle,
                                        self)
        slider_left = g.x() + h.width()/2
        slider_scale = (self.maximum() - self.minimum())/(
            g.width() - h.width())

        self._axisView = axis_left, axis_scale
        self._sliderView = ((axis_left - slider_left)*slider_scale,
                            axis_scale*slider_scale)
        self.update()

    def setStart(self, val):
        if self._start == val:
            return
        self._start = val
        self.update()
        self.startChanged.emit(val)

    def setStop(self, val):
        if self._stop == val:
            return
        self._stop = val
        self.update()
        self.stopChanged.emit(val)

    def setNum(self, val):
        if self._num == val:
            return
        self._num = val
        self.update()
        self.numChanged.emit(val)

    def viewRange(self):
        center = (self._stop + self._start)/2
        scale = self.width()*(1 - 2*self.zoomMargin)
        if self._stop != self._start:
            scale /= abs(self._stop - self._start)
            if center:
                scale = min(scale, self.dynamicRange/abs(center))
        else:
            scale = self.dynamicRange
            if center:
                scale /= abs(center)
        left = self.width()/2 - center*scale
        self._setView(left, scale)

    def snapRange(self):
        self.setStart(self._pixelToAxis(self.zoomMargin*self.width()))
        self.setStop(self._pixelToAxis((1 - self.zoomMargin)*self.width()))

    def _getStyleOptionSlider(self, val):
        a, b = self._sliderView
        val = a + val*b
        if not (self.minimum() <= val <= self.maximum()):
            return None
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        rect = self.rect()
        qfm = QtGui.QFontMetrics(self.font())
        opt.rect = QtCore.QRect(0, 3*qfm.lineSpacing(), rect.width(),
                                qfm.lineSpacing())
        opt.sliderPosition = val
        opt.sliderValue = val
        opt.subControls = QtWidgets.QStyle.SC_SliderHandle
        return opt

    def _hitHandle(self, pos, val):
        opt = self._getStyleOptionSlider(val)
        if not opt:
            return False
        control = self.style().hitTestComplexControl(
            QtWidgets.QStyle.CC_Slider, opt, pos, self)
        if control != QtWidgets.QStyle.SC_SliderHandle:
            return False
        sr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt,
                                         QtWidgets.QStyle.SC_SliderHandle,
                                         self)
        self._offset = pos.x() - sr.center().x()
        self.setSliderDown(True)
        return True

    def mousePressEvent(self, ev):
        if ev.buttons() ^ ev.button():
            ev.ignore()
            return
        if self._hitHandle(ev.pos(), self._stop):
            self._pressed = "stop"
        elif self._hitHandle(ev.pos(), self._start):
            self._pressed = "start"
        else:
            self._pressed = "axis"
            self._offset = ev.x()
            self._dragLeft = self._axisView[0]

    def mouseMoveEvent(self, ev):
        if not self._pressed:
            ev.ignore()
            return
        if self._pressed == "stop":
            self._stop = self._pixelToAxis(ev.x() - self._offset)
            self.update()
            if self.hasTracking():
                self.stopChanged.emit(self._stop)
        elif self._pressed == "start":
            self._start = self._pixelToAxis(ev.x() - self._offset)
            self.update()
            if self.hasTracking():
                self.startChanged.emit(self._start)
        elif self._pressed == "axis":
            self._setView(self._dragLeft + ev.x() - self._offset,
                          self._axisView[1])

    def mouseReleaseEvent(self, ev):
        QtWidgets.QSlider.mouseReleaseEvent(self, ev)
        self.setSliderDown(False)
        if self._pressed == "start":
            self.startChanged.emit(self._start)
        elif self._pressed == "stop":
            self.stopChanged.emit(self._stop)
        self._pressed = None

    def _zoom(self, z, x):
        a, b = self._axisView
        scale = z*b
        left = x - z*(x - a)
        if z > 1 and abs(left - self.width()/2) > self.dynamicRange:
            return
        self._setView(left, scale)

    def wheelEvent(self, ev):
        y = ev.angleDelta().y()/120.
        if ev.modifiers() & QtCore.Qt.ShiftModifier:
            if y:
                self.setNum(max(1, self._num + y))
        elif ev.modifiers() & QtCore.Qt.ControlModifier:
            if y:
                self._zoom(self.zoomFactor**y, ev.x())
        else:
            ev.ignore()

    def resizeEvent(self, ev):
        if not ev.oldSize().isValid():
            self.viewRange()
            return
        a, b = self._axisView
        scale = b*ev.size().width()/ev.oldSize().width()
        center = (self._stop + self._start)/2
        if center:
            scale = min(scale, self.dynamicRange/abs(center))
        left = a*scale/b
        self.ticker.min_ticks = int(ev.size().width()/100)
        self._setView(left, scale)

    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        qfm = QtGui.QFontMetrics(painter.font())
        avgCharWidth = qfm.averageCharWidth()
        lineSpacing = qfm.lineSpacing()
        descent = qfm.descent()
        painter.translate(0, lineSpacing)

        ticks, prefix, labels = self.ticker(self._pixelToAxis(0),
                                            self._pixelToAxis(self.width()))
        painter.drawText(0, 0, prefix)
        painter.translate(0, lineSpacing)

        painter.setPen(QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine))
        for t, l in zip(ticks, labels):
            t = self._axisToPixel(t)
            painter.drawText(t - len(l)/2*avgCharWidth, 0, l)
            painter.drawLine(t, descent, t, (lineSpacing + descent)/2)
        painter.translate(0, (lineSpacing + descent)/2)

        painter.drawLine(0, 0, self.width(), 0)

        for p in np.linspace(self._axisToPixel(self._start),
                             self._axisToPixel(self._stop),
                             self._num):
            painter.drawLine(p, 0, p, (lineSpacing - descent)/2)
        painter.translate(0, (lineSpacing - descent)/2)

        for x, c in (self._start, QtCore.Qt.blue), (self._stop, QtCore.Qt.red):
            x = self._axisToPixel(x)
            if self.minimum() <= x <= self.maximum():
                painter.setPen(c)
                painter.setBrush(c)
                painter.drawPolygon(*(QtCore.QPointF(*i) for i in [
                    (x, 0), (x - lineSpacing/2, lineSpacing),
                    (x + lineSpacing/2, lineSpacing)]))
