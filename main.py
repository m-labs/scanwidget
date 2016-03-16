import asyncio
import atexit
import logging

from quamash import QApplication, QEventLoop, QtWidgets

from scanwidget import ScanWidget
from scientific_spinbox import ScientificSpinBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, server):
        QtWidgets.QMainWindow.__init__(self)
        self.exit_request = asyncio.Event()

    def closeEvent(self, *args):
        self.exit_request.set()


def main():
    logging.basicConfig(level=logging.INFO)
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    atexit.register(loop.close)

    win = MainWindow(app, None)

    container = QtWidgets.QWidget(win)
    layout = QtWidgets.QGridLayout()
    container.setLayout(layout)

    scanner = ScanWidget()
    scanner.setMinimumSize(300, 0)
    layout.addWidget(scanner, 0, 0, -1, 1)

    spinbox = ScientificSpinBox()
    spinbox.setStyleSheet("QDoubleSpinBox {color:blue}")
    spinbox.setMinimumSize(110, 0)
    layout.addWidget(spinbox, 0, 1)
    scanner.startChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(scanner.setStart)
    spinbox.setValue(-100)
    scanner.setStart(-100)

    spinbox = ScientificSpinBox()
    spinbox.setStyleSheet("QDoubleSpinBox {color:red}")
    layout.addWidget(spinbox, 2, 1)
    scanner.stopChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(scanner.setStop)
    spinbox.setValue(200)
    scanner.setStop(200)

    spinbox = QtWidgets.QSpinBox()
    spinbox.setMaximum((1 << 31) - 1)
    layout.addWidget(spinbox, 1, 1)
    scanner.numChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(scanner.setNum)
    spinbox.setValue(11)
    scanner.setNum(11)

    win.setCentralWidget(container)
    win.show()
    loop.run_until_complete(win.exit_request.wait())


if __name__ == "__main__":
    main()
