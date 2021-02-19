import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from map_geo_coords_api import get_map_from_coords

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.spn = [0.0025, 0.0025]
        self.min_spn = [0.0005, 0.0005]

        uic.loadUi('graphic.ui', self)
        self.search_btn.clicked.connect(self.search)

    def search(self):
        image = get_map_from_coords(
            reversed(self.line_enter_coords.text().replace(" ", "").split(",")),
            type_in=list,
            spn=self.spn
        )
        pixmap = QPixmap()
        pixmap.loadFromData(image)
        self.map.setPixmap(pixmap)

    def keyPressEvent(self, event):

        if event.key() in [Qt.Key_PageUp, Qt.Key_Up]:
            self.spn[0] += 0.001
            self.spn[1] += 0.001
            self.search()
        elif event.key() in [Qt.Key_PageDown, Qt.Key_Down]:
            self.spn[0] = max(self.spn[0] - 0.001, self.min_spn[0])
            self.spn[1] = max(self.spn[1] - 0.001, self.min_spn[1])
            self.search()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
