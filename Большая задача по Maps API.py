import sys

from PyQt5.QtGui import QPixmap

from map_geo_coords_api import get_map_from_coords

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('graphic.ui', self)
        self.search_btn.clicked.connect(self.search)

    def search(self):
        image = get_map_from_coords(reversed(self.line_enter_coords.text().replace(" ", "").split(",")), type_in=list)
        pixmap = QPixmap()
        pixmap.loadFromData(image)
        self.map.setPixmap(pixmap)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
