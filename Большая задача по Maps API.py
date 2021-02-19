import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from map_geo_coords_api import get_map_from_coords

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.spn = [0.0025, 0.0025]
        self.min_spn = [0.0005, 0.0005]
        self.place = [int, [0, 0]]
        self.types_maps = {"спутник": "sat", "гибрид": "sat,skl", "схема": "map"}

        uic.loadUi('graphic.ui', self)
        self.search_btn.clicked.connect(self.clicked_btn_search)
        self.type_map_box.currentTextChanged.connect(self.search)

    def get_new_coords(self):
        self.place[1] = \
            list(reversed(list(map(float, self.line_enter_coords.text().replace(" ", "").split(",")))))

    def clicked_btn_search(self):
        try:
            self.get_new_coords()
        except Exception as e:
            print(e)
        self.search()

    def search(self):
        image = get_map_from_coords(
            self.place[1],
            type_in=self.place[0],
            spn=self.spn,
            l=self.types_maps[self.type_map_box.currentText()]
        )
        pixmap = QPixmap()
        pixmap.loadFromData(image)
        self.map.setPixmap(pixmap)

    def keyPressEvent(self, event):
        flag = True
        if event.key() == Qt.Key_PageUp:
            self.spn[0] += 0.001
            self.spn[1] += 0.001
        elif event.key() == Qt.Key_PageDown:
            self.spn[0] = max(self.spn[0] - 0.001, self.min_spn[0])
            self.spn[1] = max(self.spn[1] - 0.001, self.min_spn[1])
        elif event.key() == Qt.Key_Down:
            self.place[1][1] -= 0.001
        elif event.key() == Qt.Key_Up:
            self.place[1][1] += 0.001
        elif event.key() == Qt.Key_Left:
            self.place[1][0] -= 0.001
        elif event.key() == Qt.Key_Right:
            self.place[1][0] += 0.001
        else:
            flag = False

        if flag:
            self.search()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
