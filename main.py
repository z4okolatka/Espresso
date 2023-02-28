from PyQt5 import uic
import sqlite3 as sq
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
import sys


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.table: QTableWidget
        self.loadTable()

    def loadTable(self):
        con = sq.connect("coffee.sqlite")
        cur = con.execute("""
        SELECT * FROM coffee
        """)
        names = list(map(lambda x: x[0], cur.description))
        data = cur.fetchall()

        self.table.setColumnCount(7)
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(names)
        for i, row in enumerate(data):
            for j, string in enumerate(row):
                item = QTableWidgetItem()
                item.setText(str(string))
                self.table.setItem(i, j, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
