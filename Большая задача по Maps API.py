import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from map_geo_coords_api import get_map, get_map_if_text, get_toponym, get_all_inf, get_organizations

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('graphic.ui', self)

        self.spn = [0.0025, 0.0025]
        self.min_spn = [0.0005, 0.0005]
        self.place = [0, 0]
        self.postal_code = ""
        self.pt = ""
        self.coords_pt = [0, 0]
        self.types_maps = {"спутник": "sat", "гибрид": "sat,skl", "схема": "map"}

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
            text = parts[:-1]
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
        self.pt = f"{','.join(map(str, self.place))},pm2rdm1"
        self.coords_pt = self.place

    def clicked_btn_search(self):
        try:
            self.place = \
                list(reversed(list(map(float, self.line_enter_coords.text().replace(" ", "").split(",")))))
        except Exception as e:
            print(e)

        self.pt = f"{','.join(map(str, self.place))},pm2rdm1"
        self.coords_pt = self.place
        image = get_map(self.place, self.spn, self.types_maps[self.type_map_box.currentText()],
                        self.pt)

        inf = get_all_inf(get_toponym(self.place))
        self.set_address(inf["address"], inf["postal_code"])
        self.set_image(image)

    def search(self, set_new_address=False):
        image = get_map(self.place, self.spn, self.types_maps[self.type_map_box.currentText()],
                        self.pt)
        self.set_image(image)
        if set_new_address:
            inf = get_all_inf(get_toponym(self.coords_pt))
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

    def mousePressEvent(self, event):  # 450 450
        # spn_x = place[0] / 300 * (event.x() - x1)
        # spn_y = place[1] / 300 * (event.y() - y1)
        # ekb 300 220          60.597465, 56.838011
        # place[0] - x

        x1, x2 = self.map.pos().x(), self.map.pos().x() + 450
        y1, y2 = self.map.pos().y(), self.map.pos().y() + 450

        if x1 <= event.x() <= x2 and y1 <= event.y() <= y2:
            spn_x = self.spn[0] / 300 * (event.x() - x1)
            spn_y = self.spn[1] / 220 * (event.y() - y1)

            place = [self.place[0] - self.spn[0] + spn_x,
                     self.place[1] + self.spn[1] - spn_y]

            if event.button() == Qt.LeftButton:
                self.pt = f"{','.join(map(str, place))},pm2rdm1"
                self.coords_pt = place
                self.search(True)
            elif event.button() == Qt.RightButton:
                org = get_organizations(place)
                if org is not None:
                    self.pt = f"{','.join(map(str, org['coords']))},pm2rdm1"
                    self.coords_pt = org["coords"]
                    self.adress_view_label.setText(org["address"] + "\n" + org["name"])
                    self.search()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
