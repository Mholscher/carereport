from datetime import date
from PyQt6.QtWidgets import (QPlainTextEdit, QTableWidget,
                             QDateEdit, QLineEdit, QCheckBox)
""" This module holds widget extensions used to make small
additions to widgets, creating classes that can be used in the designer
promoting certain widgets.
"""


class DescriptionWidget(QPlainTextEdit):

    def focusOutEvent(self, event):
        """ The focus out event sets the view to the value of the field """

        # if event.type() == QEvent.Type.FocusAboutToChange:
        if hasattr(self.parent, "update_view"):
            print("Going to save:", self.toPlainText())
            self.parent.update_view()
        super().focusOutEvent(event)


class DietTableWidget(QTableWidget):
    """ This widget expands the working of the table widget

    The values in the input fields for the deselected row  are saved and the
    values of the newly selected row are put in the input fields.
    """

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
            self.FoodNameEdit.setReadOnly(False)
            self.ApplicationTypeEdit.setReadOnly(False)
            self.DescriptionEdit.setReadOnly(False)

        super().selectionChanged(selected, deselected)


class PyDateEdit(QDateEdit):
    """ Return a datetime.date from the edit

    The QDateEdit returns a QDate instance, but in Python we want a
    datime.date instance.
    """

    def date(self):
        """ Return the QDate instance as a date instance """

        qt_date = super().date()
        return date(qt_date.year(), qt_date.month(), qt_date.day())

    def focusOutEvent(self, event):
        """ If a date edit has a header widget,  update the view """

        if hasattr(self, "header_widget"):
            self.header_widget.update_view()
        super().focusOutEvent(event)


class PyLineEdit(QLineEdit):
    """ Instrument a text field for updating """

    def focusOutEvent(self, event):
        """ If a string field has a header widget, update the view """

        if hasattr(self, "header_widget"):
            self.header_widget.update_view()
        super().focusOutEvent(event)


class PyCheckBox(QCheckBox):
    """ Instrument a text field for updating """

    def focusOutEvent(self, event):
        """ If a checkbox field has a header widget, update the view """

        if hasattr(self, "header_widget"):
            self.header_widget.update_view()
        super().focusOutEvent(event)
