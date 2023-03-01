from PyQt5 import uic
import sqlite3 as sq
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QButtonGroup, QPushButton, QLineEdit, QPlainTextEdit, QRadioButton
from ui.addUI import Ui_MainWindow as Ui_Add
from ui.mainUI import Ui_MainWindow as Ui_Main
import sys


def isfloat(x):
    try:
        float(x)
        return True
    except Exception:
        return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Main()
        self.ui.setupUi(self)

        self.ui.table.itemSelectionChanged.connect(self.selectId)
        self.loadTable()

    def addNewLine(self, row):
        self.cur.execute(
            "INSERT INTO coffee (sort,roastDegree,type,tasteDescription,price,volume) VALUES(?,?,?,?,?,?)",
            row
        )
        self.con.commit()
        self.loadTable()

    def editLine(self, id_, row):
        self.cur.execute(
            "UPDATE coffee SET sort=?,roastDegree=?,type=?,tasteDescription=?,price=?,volume=? WHERE ID LIKE ?",
            (*row, id_)
        )
        self.con.commit()
        self.loadTable()

    def loadTable(self):
        self.ui.table.clear()
        self.con = sq.connect("data/coffee.sqlite")
        self.cur = self.con.execute("""
        SELECT * FROM coffee
        """)
        names = list(map(lambda x: x[0], self.cur.description))
        data = self.cur.fetchall()

        self.ui.table.setColumnCount(7)
        self.ui.table.setRowCount(len(data))
        self.ui.table.setHorizontalHeaderLabels(names)
        for i, row in enumerate(data):
            for j, string in enumerate(row):
                item = QTableWidgetItem()
                item.setText(str(string))
                self.ui.table.setItem(i, j, item)

    def selectId(self):
        selected = self.ui.table.selectedItems()
        if not selected:
            return
        add.ui.idInput.setText(selected[0].text())
        add.ui.editRadioBtn.toggle()

    def closeEvent(self, event):
        add.deleteLater()
        return super().closeEvent(event)


class AdditionalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Add()
        self.ui.setupUi(self)

        self.ui.formatSelect.buttonToggled.connect(self.changeState)
        self.ui.idInput.textEdited.connect(self.changeSelection)
        self.ui.idInput.textChanged.connect(self.replaceData)
        self.ui.actionBtn.clicked.connect(self.doAction)

    def doAction(self):
        if self.ui.addRadioBtn.isChecked():
            if not isfloat(self.ui.priceInput.text()) or\
                    not isfloat(self.ui.volumeInput.text()):
                return
            main.addNewLine((
                self.ui.sortInput.text(),
                self.ui.roastDegreeInput.text(),
                self.ui.typeInput.text(),
                self.ui.tasteDescriptionInput.toPlainText(),
                self.ui.priceInput.text(),
                self.ui.volumeInput.text()
            ))
        elif self.ui.editRadioBtn.isChecked():
            if not isfloat(self.ui.priceInput.text()) or\
                    not isfloat(self.ui.volumeInput.text()):
                return
            main.editLine(self.idInput.text(), (
                self.ui.sortInput.text(),
                self.ui.roastDegreeInput.text(),
                self.ui.typeInput.text(),
                self.ui.tasteDescriptionInput.toPlainText(),
                self.ui.priceInput.text(),
                self.ui.volumeInput.text()
            ))

    def changeState(self):
        if self.ui.addRadioBtn.isChecked():
            self.ui.actionBtn.setText("Добавить")
            self.ui.idInput.setText('')
            self.clearData()
            main.ui.table.clearSelection()
        else:
            self.ui.actionBtn.setText("Изменить")

    def changeSelection(self):
        try:
            main.ui.table.selectRow(int(self.idInput.text()) - 1)
        except Exception:
            pass

    def clearData(self):
        for i in (
            self.ui.sortInput,
            self.ui.roastDegreeInput,
            self.ui.typeInput,
            self.ui.tasteDescriptionInput,
            self.ui.priceInput,
            self.ui.volumeInput
        ):
            i.clear()

    def replaceData(self):
        self.ui.idInput.setStyleSheet('')
        id_ = self.ui.idInput.text()
        row = main.cur.execute(
            'SELECT * FROM coffee WHERE ID LIKE ?', (id_,)
        ).fetchone()
        if not row:
            if id_:
                self.ui.idInput.setStyleSheet('color: red;')
            return
        row = list(map(str, row))
        for i, x in enumerate((
            self.ui.sortInput,
            self.ui.roastDegreeInput,
            self.ui.typeInput,
            self.ui.tasteDescriptionInput,
            self.ui.priceInput,
            self.ui.volumeInput
        ), start=1):
            if isinstance(x, QLineEdit):
                x.setText(row[i])
            else:
                x.setPlainText(row[i])

    def closeEvent(self, event):
        main.deleteLater()
        return super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    add = AdditionalWindow()
    add.show()
    sys.exit(app.exec())
