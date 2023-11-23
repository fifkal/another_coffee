import sqlite3 as sql
from PyQt5 import uic
from PyQt5.QtWidgets import *
import sys
from PyQt5 import QtGui


class Coffee(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['id кофе', 'сорт',
                                                    'степень прожарки', 'молотый/растворимый', 'вкус',
                                                    'цена', 'объём упаковки'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.save_button.clicked.connect(self.save_results)
        self.delete_button.clicked.connect(self.remove)
        self.add.clicked.connect(self.add_row)
        self.modified = {}
        self.con = sql.connect("capuchino.db")
        self.cur = self.con.cursor()
        result = self.cur.execute(f"SELECT * FROM coffee").fetchall()
        if result:
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(len(result[0]))
            self.titles = [description[0] for description in self.cur.description]
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            que = "UPDATE coffee SET\n"
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += "WHERE id = ?"
            self.cur.execute(que, (self.id_box.text(),))
            self.con.commit()
            self.modified.clear()

    def remove(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM coffee WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
        self.update()

    def generate_id(self):
        self.cur.execute('SELECT max(id) FROM coffee')
        result = self.cur.fetchone()[0]

        if result is None:
            return 1
        else:
            return result + 1

    def add_row(self):
        id_new = self.generate_id()
        val = f"INSERT INTO coffee(id) VALUES(?);"
        self.cur.execute(val, (id_new, ))
        self.con.commit()
        self.update()

    def update(self):
        self.modified = {}
        self.con = sql.connect("capuchino.db")
        self.cur = self.con.cursor()
        result = self.cur.execute("SELECT * FROM coffee").fetchall()
        if result:
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(len(result[0]))
            self.titles = [description[0] for description in self.cur.description]
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.modified = {}


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec_())
