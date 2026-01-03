from PyQt6.QtWidgets import QPlainTextEdit, QTableWidget
from PyQt6.QtCore import QEvent


class DescriptionWidget(QPlainTextEdit):

    def focusEvent(self, event):
        """ The focus out event sets the view to the value of the field """

        if event.type() == QEvent.Type.FocusAboutToChange:
            if self.save_to_view is not None:
                print("Going to save:", self.toPlainText())
                self.save_to_view()
        super().focusOutEvent(event)


class DietTableWidget(QTableWidget):

    def selectionChanged(self, selected, deselected):
        """ Take actions to be added to changing selection """

        if deselected:
            row = deselected.first().top()
            if self.item(row, 0):
                self.item(row, 0).setText(self.FoodNameEdit.text())
                self.FoodNameEdit.setText("")
            if self.item(row, 1):
                self.item(row, 1).setText(self.ApplicationTypeEdit.text())
                self.ApplicationTypeEdit.setText("")
            if self.item(row, 0):
                self.lines_views[row].description =\
                    self.DescriptionEdit.toPlainText()
                self.DescriptionEdit.setPlainText("")
        if selected:
            row = selected.first().top()
            if self.item(row, 0):
                self.FoodNameEdit.setText(self.item(row, 0).text())
            if self.item(row, 1):
                self.ApplicationTypeEdit.setText(self.item(row, 1).text())
            if row < len(self.lines_views):
                self.DescriptionEdit.setPlainText(
                    self.lines_views[row].description)
        super().selectionChanged(selected, deselected)
