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
    layout.addWidget(scanner, 0, 0, -1, 1)

    spinbox = ScientificSpinBox()
    spinbox.setStyleSheet("QDoubleSpinBox {color:blue}")
    spinbox.setMinimumSize(110, 0)
    layout.addWidget(spinbox, 0, 1)
    scanner.startChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(scanner.setStart)
    scanner.setStart(-100)

    spinbox = ScientificSpinBox()
    spinbox.setStyleSheet("QDoubleSpinBox {color:red}")
    layout.addWidget(spinbox, 2, 1)
    scanner.stopChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(scanner.setStop)
    scanner.setStop(200)

    spinbox = QtWidgets.QSpinBox()
    spinbox.setMinimum(1)
    spinbox.setMaximum((1 << 31) - 1)
    layout.addWidget(spinbox, 1, 1)
    scanner.numChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(scanner.setNum)
    scanner.setNum(11)

    win.setCentralWidget(container)
    win.show()
    loop.run_until_complete(win.exit_request.wait())


if __name__ == "__main__":
    main()
