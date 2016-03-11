import asyncio
import atexit
import logging

from quamash import QApplication, QEventLoop, QtCore, QtWidgets

import scanwidget
from scientific_spinbox import ScientificSpinBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app, server):
        QtWidgets.QMainWindow.__init__(self)
        self.exit_request = asyncio.Event()

    def closeEvent(self, *args):
        self.exit_request.set()

    def save_state(self):
        return bytes(self.saveGeometry())

    def restore_state(self, state):
        self.restoreGeometry(QtCore.QByteArray(state))


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
    scanner = scanwidget.ScanWidget()
    scanner.setMinimumSize(300, 0)
    layout.addWidget(scanner, 0, 0, -1, 1)

    spinboxes = [ScientificSpinBox(),
                 QtWidgets.QSpinBox(),
                 ScientificSpinBox()]
    spinboxes[0].setStyleSheet("QDoubleSpinBox {color:blue}")
    spinboxes[2].setStyleSheet("QDoubleSpinBox {color:red}")
    spinboxes[0].setMinimumSize(110, 0)
    spinboxes[2].setMinimumSize(110, 0)
    spinboxes[1].setMinimum(1)
    spinboxes[1].setMaximum((1 << 31) - 1)

    labels = [QtWidgets.QLabel(l) for l in "Start Stop Points".split()]
    labels[0].setStyleSheet("QLabel {color:blue}")
    labels[1].setStyleSheet("QLabel {color:red}")

    for i, (l, s) in enumerate(zip(labels, spinboxes)):
        layout.addWidget(s, i, 1)
        # layout.addWidget(l, 1, i*2)
        # layout.addWidget(s, 1, i*2 + 1)

    scanner.sigStartMoved.connect(spinboxes[0].setValue)
    scanner.sigNumChanged.connect(spinboxes[1].setValue)
    scanner.sigStopMoved.connect(spinboxes[2].setValue)
    spinboxes[0].valueChanged.connect(scanner.setStart)
    spinboxes[1].valueChanged.connect(scanner.setNumPoints)
    spinboxes[2].valueChanged.connect(scanner.setStop)

    spinboxes[0].setValue(-100)
    spinboxes[2].setValue(200)
    spinboxes[1].setValue(11)

    win.setCentralWidget(container)
    win.show()
    loop.run_until_complete(win.exit_request.wait())


if __name__ == "__main__":
    main()
