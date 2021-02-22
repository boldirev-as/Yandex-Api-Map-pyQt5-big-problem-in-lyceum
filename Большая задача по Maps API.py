import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from map_geo_coords_api import get_map, get_map_if_text, get_toponym, get_all_inf

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QCheckBox


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.spn = [0.0025, 0.0025]
        self.min_spn = [0.0005, 0.0005]
        self.place = [0, 0]
        self.postal_code = ""
        self.types_maps = {"спутник": "sat", "гибрид": "sat,skl", "схема": "map"}

        uic.loadUi('graphic.ui', self)
        self.search_btn.clicked.connect(self.clicked_btn_search)
        self.type_map_box.currentTextChanged.connect(self.search)
        self.search_text_btn.clicked.connect(self.clicked_btn_search_text)
        self.reboot_search_btn.clicked.connect(self.clear_pts)
        self.index_checkBox.clicked.connect(self.change_postal_code)

    def change_postal_code(self):
        print(self.postal_code)
        text = self.adress_view_label.text()
        if self.postal_code is not None and self.index_checkBox.isChecked():
            text += "\n" + self.postal_code
        elif not self.index_checkBox.isChecked() and self.postal_code is not None:
            parts = text.split("\n")
            text = parts[0]
        self.adress_view_label.setText(text)

    def clear_pts(self):
        self.search()
        self.adress_view_label.setText("")

    def set_address(self, address, postal_code):
        self.postal_code = postal_code
        postal_code = postal_code if postal_code is not None and self.index_checkBox.isChecked() else ""
        self.adress_view_label.setText(address + '\n' + postal_code)

    def set_image(self, img):
        pixmap = QPixmap()
        pixmap.loadFromData(img)
        self.map.setPixmap(pixmap)

    def clicked_btn_search_text(self):
        place = self.line_enter_keyword.text()

        request = get_map_if_text(place, self.types_maps[self.type_map_box.currentText()])

        self.spn = request["spn"]
        self.place = request["coords"]
        inf = get_all_inf(request["toponym"])
        self.set_address(inf["address"], inf["postal_code"])
        self.set_image(request["image"])

    def clicked_btn_search(self):
        try:
            self.place = \
                list(reversed(list(map(float, self.line_enter_coords.text().replace(" ", "").split(",")))))
        except Exception as e:
            print(e)

        image = get_map(self.place, self.spn, self.types_maps[self.type_map_box.currentText()],
                        f"{','.join(map(str, self.place))},pm2rdm1")

        inf = get_all_inf(get_toponym(self.place))
        self.set_address(inf["address"], inf["postal_code"])
        self.set_image(image)

    def search(self, set_new_address=False):
        image = get_map(self.place, self.spn, self.types_maps[self.type_map_box.currentText()],
                        f"{','.join(map(str, self.place))},pm2rdm1")
        self.set_image(image)
        if set_new_address:
            inf = get_all_inf(get_toponym(self.place))
            self.set_address(inf["address"], inf["postal_code"])

    def keyPressEvent(self, event):
        flag = False
        k_0 = self.spn[0] * 0.3
        k_1 = self.spn[1] * 0.3
        if event.key() == Qt.Key_PageUp:
            self.spn[0] += k_0
            self.spn[1] += k_1
        elif event.key() == Qt.Key_PageDown:
            self.spn[0] = max(self.spn[0] - k_0, self.min_spn[0])
            self.spn[1] = max(self.spn[1] - k_1, self.min_spn[1])
        else:
            flag = None

        if flag is None:
            flag = True
            if event.key() == Qt.Key_Down:
                self.place[1] -= k_1
            elif event.key() == Qt.Key_Up:
                self.place[1] += k_1
            elif event.key() == Qt.Key_Left:
                self.place[0] -= k_0
            elif event.key() == Qt.Key_Right:
                self.place[0] += k_0
            else:
                flag = None

        if flag is not None:
            self.search(flag)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
