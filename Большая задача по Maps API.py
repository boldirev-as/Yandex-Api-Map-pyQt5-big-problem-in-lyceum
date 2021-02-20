import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from map_geo_coords_api import get_map_from_coords, get_size_toponym, get_map_from_text

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.spn = [0.0025, 0.0025]
        self.min_spn = [0.0005, 0.0005]
        self.place = [0, 0]
        self.pts = []
        self.types_maps = {"спутник": "sat", "гибрид": "sat,skl", "схема": "map"}
        self.first_search = True

        uic.loadUi('graphic.ui', self)
        self.search_btn.clicked.connect(self.clicked_btn_search)
        self.type_map_box.currentTextChanged.connect(self.search)
        self.search_text_btn.clicked.connect(self.clicked_btn_search_text)
        self.reboot_search_btn.clicked.connect(self.clear_pts)

    def clear_pts(self):
        self.pts = []
        self.search()

    def clicked_btn_search_text(self):
        try:
            self.place = self.line_enter_keyword.text()
        except Exception as e:
            print(e)

        request = get_map_from_text(self.place,
                                    l=self.types_maps[self.type_map_box.currentText()],
                                    pt=None)

        self.spn = get_size_toponym(request[1])
        self.place = request[2]
        self.pts = [f"{self.place[0]},{self.place[1]},pm2rdm1"]
        pixmap = QPixmap()
        pixmap.loadFromData(request[0])
        self.map.setPixmap(pixmap)

    def clicked_btn_search(self):
        try:
            self.place = \
                list(reversed(list(map(float, self.line_enter_coords.text().replace(" ", "").split(",")))))
        except Exception as e:
            print(e)
        self.search()

    def search(self):
        print(self.pts)
        image = get_map_from_coords(
            self.place,
            spn=self.spn,
            l=self.types_maps[self.type_map_box.currentText()],
            pt=self.pts
        )
        pixmap = QPixmap()
        pixmap.loadFromData(image)
        self.map.setPixmap(pixmap)

    def keyPressEvent(self, event):
        flag = True
        k_0 = self.spn[0] * 0.3
        k_1 = self.spn[1] * 0.3
        if event.key() == Qt.Key_PageUp:
            self.spn[0] += k_0
            self.spn[1] += k_1
        elif event.key() == Qt.Key_PageDown:
            self.spn[0] = max(self.spn[0] - k_0, self.min_spn[0])
            self.spn[1] = max(self.spn[1] - k_1, self.min_spn[1])
        elif event.key() == Qt.Key_Down:
            self.place[1] -= k_1
        elif event.key() == Qt.Key_Up:
            self.place[1] += k_1
        elif event.key() == Qt.Key_Left:
            self.place[0] -= k_0
        elif event.key() == Qt.Key_Right:
            self.place[0] += k_0
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
