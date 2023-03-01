from PyQt5 import uic
import sqlite3 as sq
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QButtonGroup, QPushButton, QLineEdit, QPlainTextEdit, QRadioButton
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
        uic.loadUi('main.ui', self)

        self.table: QTableWidget
        self.table.itemSelectionChanged.connect(self.selectId)
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
        self.table.clear()
        self.con = sq.connect("coffee.sqlite")
        self.cur = self.con.execute("""
        SELECT * FROM coffee
        """)
        names = list(map(lambda x: x[0], self.cur.description))
        data = self.cur.fetchall()

        self.table.setColumnCount(7)
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(names)
        for i, row in enumerate(data):
            for j, string in enumerate(row):
                item = QTableWidgetItem()
                item.setText(str(string))
                self.table.setItem(i, j, item)

    def selectId(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        add.idInput.setText(selected[0].text())
        add.editRadioBtn.toggle()

    def closeEvent(self, event):
        add.deleteLater()
        return super().closeEvent(event)


class AdditionalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)

        self.formatSelect: QButtonGroup
        self.addRadioBtn: QRadioButton
        self.editRadioBtn: QRadioButton
        self.actionBtn: QPushButton
        self.idInput: QLineEdit
        self.sortInput: QLineEdit
        self.roastDegreeInput: QLineEdit
        self.typeInput: QLineEdit
        self.priceInput: QLineEdit
        self.volumeInput: QLineEdit
        self.tasteDescriptionInput: QPlainTextEdit

        self.formatSelect.buttonToggled.connect(self.changeState)
        self.idInput.textEdited.connect(self.changeSelection)
        self.idInput.textChanged.connect(self.replaceData)
        self.actionBtn.clicked.connect(self.doAction)

    def doAction(self):
        if self.addRadioBtn.isChecked():
            if not isfloat(self.priceInput.text()) or\
                    not isfloat(self.volumeInput.text()):
                return
            main.addNewLine((
                self.sortInput.text(),
                self.roastDegreeInput.text(),
                self.typeInput.text(),
                self.tasteDescriptionInput.toPlainText(),
                self.priceInput.text(),
                self.volumeInput.text()
            ))
        elif self.editRadioBtn.isChecked():
            if not isfloat(self.priceInput.text()) or\
                    not isfloat(self.volumeInput.text()):
                return
            main.editLine(self.idInput.text(), (
                self.sortInput.text(),
                self.roastDegreeInput.text(),
                self.typeInput.text(),
                self.tasteDescriptionInput.toPlainText(),
                self.priceInput.text(),
                self.volumeInput.text()
            ))

    def changeState(self):
        if self.addRadioBtn.isChecked():
            self.actionBtn.setText("Добавить")
            self.idInput.setText('')
            self.clearData()
            main.table.clearSelection()
        else:
            self.actionBtn.setText("Изменить")

    def changeSelection(self):
        try:
            main.table.selectRow(int(self.idInput.text()) - 1)
        except Exception:
            pass

    def clearData(self):
        for i in (
            self.sortInput,
            self.roastDegreeInput,
            self.typeInput,
            self.tasteDescriptionInput,
            self.priceInput,
            self.volumeInput
        ):
            i.clear()

    def replaceData(self):
        self.idInput.setStyleSheet('')
        id_ = self.idInput.text()
        row = main.cur.execute(
            'SELECT * FROM coffee WHERE ID LIKE ?', (id_,)
        ).fetchone()
        if not row:
            if id_:
                self.idInput.setStyleSheet('color: red;')
            return
        row = list(map(str, row))
        for i, x in enumerate((
            self.sortInput,
            self.roastDegreeInput,
            self.typeInput,
            self.tasteDescriptionInput,
            self.priceInput,
            self.volumeInput
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
