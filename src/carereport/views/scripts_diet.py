#    Copyright 2025 Menno Hölscher
#
#    This file is part of carereport.

#    carereport is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    carereport is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.

#    You should have received a copy of the GNU Lesser General Public License
#    along with carereport.  If not, see <http://www.gnu.org/licenses/>.
""" This module contains the script(s) to handle the user interface for diets.

The diets are input through two input widgets that ar switching between each
other. One holds a list of diets (the headers that is) and the other one
enables creation and maintenance of diets and rules within a diet.
"""
import sys
from datetime import date
# from PyQt6.QtCore import QDate
# from PyQt6.QtCore import QLocale as Loc, pyqtSlot
from PyQt6.QtWidgets import (QWidget, QDialog, QTableWidgetItem,
                             QTableWidgetSelectionRange)
# from .widgetext import DescriptionWidget
from carereport import app
from .diet_views import DietView, DietLineView
from .dietline import Ui_dietLineDialog
from .dietheader import Ui_DietHeaderWidget
from .care_app import mainwindow
""" This module sets up diets. It takes care of creating new diets, updating
existing diets through diet views.
"""


def update_view_from_widget(instance):
    """ Update the view from a widget """

    instance.header_widget.update_view()


class _DietChanges(QWidget, Ui_DietHeaderWidget):
    """ This class contains shared functions for creating and updating  diet
    views from input."""

    def __init__(self, parent=None):

        super().__init__(parent=parent)

    def set_header_widget(self):
        """ Make sure each of the edits "knows" this widget """

        self.dietNameEdit.header_widget = self
        self.startDateEdit.header_widget = self
        self.endDateEdit.header_widget = self
        self.permanentCheckBox.header_widget = self

    def update_view(self):
        """ Update the values in a diet view """

        self.diet_view.diet_name = self.dietNameEdit.text()
        self.diet_view.permanent_diet =\
            self.permanentCheckBox.isChecked()
        if self.diet_view.permanent_diet:
            self.diet_view.start_date = None
            self.diet_view.end_date = None
        else:
            self.diet_view.start_date = self.startDateEdit.date()
            if self.endDateEdit.date() != date(9999, 12, 31):
                self.diet_view.end_date = self.endDateEdit.date()
            if self.diet_view.start_date and self.diet_view.end_date:
                self.diet_view.check_diet_dates()


class CreateDiet(_DietChanges):
    """ Create a new diet, using the view for diets.

    The view holds one header and as many lines (rules for the patient) as
    applicable for this diet.

    An example is a sugar limited diet. The diet has a header saying "sugar
    limited"  and rules like "Do not put sugar in your tea and coffee" or
    "No caramel"
    """

    def __init__(self, diet_view, parent=None):

        super().__init__(parent=parent)
        self.diet_view = DietView()
        self.setupUi(self)
        save_button = mainwindow.centralWidget().saveDataButton
        save_button.clicked.connect(self.update_view)
        self.set_header_widget()

    def update_diet(self):
        """ At this point in the script the diet for the database is created.

        The event to be processed is to save the diet.
        """

        self.diet_view.to_diet()


class UpdateDiet(_DietChanges):
    """ Change the data on an existing diet.

    Existing diets can be shown and changed. Examples are when a diet is made
    permanent, when an end date diet is altered, or a typing error is fixed.
    """

    def __init__(self, diet_view, parent=None, stretch=0):

        super().__init__(parent=parent)
        self.setupUi(self)
        # Fill the diet header
        self.dietNameEdit.setText(diet_view.diet_name)
        self.permanentCheckBox.setChecked(diet_view.permanent_diet)
        self.startDateEdit.setDate(diet_view.start_date)
        if diet_view.end_date:
            self.endDateEdit.setDate(diet_view.end_date)
        else:
            self.endDateEdit.setDate(date(9999, 12, 31))
        self.diet_view = diet_view
        save_button = mainwindow.centralWidget().saveDataButton
        save_button.clicked.connect(self.update_view)
        self.set_header_widget()

    def update_diet(self):
        """ The data in the view is released into the diet """

        self.diet_view.update_diet()

    def update_view(self):
        """ Update the view with changes from the window """

        view = self.diet_view
        if view.diet_name != self.dietNameEdit.text():
            view.diet_name = self.dietNameEdit.text()
        if view.permanent_diet != self.permanentCheckBox.isChecked():
            view.permanent_diet = self.permanentCheckBox.isChecked()
        if not view.permanent_diet:
            if view.start_date != self.startDateEdit.date():
                view.start_date = self.startDateEdit.date()
            if view.end_date != self.endDateEdit.date():
                if self.endDateEdit.date() == date(9999, 12, 31):
                    view.end_date = None
                else:
                    view.end_date = self.endDateEdit.date()
            if self.diet_view.start_date and self.diet_view.end_date:
                self.diet_view.check_diet_dates()


class UpdateDietLines(QDialog, Ui_dietLineDialog):
    """ Create and update lines for one diet.

    Both new and existing diets can have diet lines added and changed. We
    do not support deletion.
    """

    def __init__(self, diet_view, parent=None):

        super().__init__(parent=parent)
        self.setupUi(self)
        self.dietLineTable.setHorizontalHeaderLabels(["Voeding",
                                                      "Gebruikregel"])
        # self.dietLineTable.itemSelectionChanged.connect(self.changed_line_selection)
        self.dietLineTable.FoodNameEdit = self.FoodNameEdit
        self.FoodNameEdit.editingFinished.connect(
            self.on_editing_finished_food_name)
        self.dietLineTable.ApplicationTypeEdit = self.ApplicationTypeEdit
        self.ApplicationTypeEdit.editingFinished.connect(
            self.on_editing_finished_application_type)
        self.dietLineTable.DescriptionEdit = self.DescriptionEdit
        self.newLineButton.clicked.connect(self.insert_new_line)
        self.diet_view = diet_view
        self.setWindowTitle(diet_view.diet_name + self.windowTitle())
        self.line_widgets = []
        self.dietLineTable.lines_views = diet_view.lines_views
        for line in diet_view.lines_views:
            self.dietLineTable.insertRow(self.dietLineTable.rowCount())
            lineno = self.dietLineTable.rowCount() - 1
            food_name_item = QTableWidgetItem(line.food_name)
            self.dietLineTable.setItem(lineno, 0,
                                       food_name_item)
            application_item = QTableWidgetItem(line.application_type)
            self.dietLineTable.setItem(lineno, 1, application_item)
            self.line_widgets.append((food_name_item, application_item))
        self.FoodNameEdit.setReadOnly(True)
        self.ApplicationTypeEdit.setReadOnly(True)
        self.DescriptionEdit.setReadOnly(True)

    def insert_new_line(self, initial_values=None):
        """ Insert a new line in the collection.

        All values in the edit fields are set to empty, but in the table the
        values are set to placeholders. Editing replaces the placeholders
        with actual values.
        """

        self.dietLineTable.insertRow(self.dietLineTable.rowCount())
        current_row = self.dietLineTable.rowCount() - 1
        food_name_item = QTableWidgetItem("< Vul de voeding >")
        application_type_item = QTableWidgetItem("< Geef de regel >")
        self.dietLineTable.setItem(current_row, 0,
                                   food_name_item)
        self.dietLineTable.setItem(current_row, 1,
                                   application_type_item)
        if self.dietLineTable.selectedRanges():
            self.dietLineTable.setRangeSelected(
                self.dietLineTable.selectedRanges()[0],
                False)
        new_line_range = QTableWidgetSelectionRange(current_row, 0,
                                                    current_row, 1)
        self.dietLineTable.setRangeSelected(new_line_range, True)
        self.line_view = DietLineView(self.diet_view)
        self.ApplicationTypeEdit.setText("")
        self.DescriptionEdit.setPlainText("")
        self.FoodNameEdit.setText("")

    def save_description_to_view(self):
        """ Save the inputted text in description to view """

        if self.DescriptionEdit.toPlainText() != self.line_view.description:
            self.line_view.description = self.DescriptionEdit.toPlainText()

    def on_editing_finished_application_type(self):
        """ This is the handler for the focus out of ApplicationTypeEdit

        It synchronizes the view to the latest input in the text line.
        """

        range_selected = self.dietLineTable.selectedRanges()[0]
        if not range_selected:
            return
        row = range_selected.topRow()
        if self.diet_view.lines_views[row].application_type !=\
                self.ApplicationTypeEdit.text():
            self.diet_view.lines_views[row].application_type =\
                self.ApplicationTypeEdit.text()
        self.dietLineTable.selectedItems()[1].setText(
            self.ApplicationTypeEdit.text())

    def on_editing_finished_food_name(self):
        """ This is the handler for the focus out of FoodNameEdit

        It synchronizes the view to the latest input in the text line.
        """

        range_selected = self.dietLineTable.selectedRanges()[0]
        if not range_selected:
            return
        row = range_selected.topRow()
        if self.diet_view.lines_views[row].food_name != self.FoodNameEdit.text():
            self.diet_view.lines_views[row].food_name = self.FoodNameEdit.text()
        self.dietLineTable.selectedItems()[0].setText(
            self.FoodNameEdit.text())


class DietListWidget(QWidget):
    """ DietTab maintains a tab for diet headers.

    The diet tab is at the patient level, it will show all diets a patient
    follows. The details (like what it means for different types of food)
    are not shown, you can switch to a details screen to be shown those.
    """

    def __init__(self, patient_view):

        super().__init__()
        for diet in patient_view.patient.diets:
            diet_view = DietView.create_from_diet(diet)
            update_diet = UpdateDiet(diet_view)
            diet_tab = mainwindow.centralWidget()
            diet_tab.verticalLayoutDiet.addWidget(update_diet)


if __name__ == "__main__":
    diet_view = DietView(diet_name="Test dieet",
                         permanent_diet=False,
                         start_date=date(2026, 1, 15),
                         end_date=date(9999, 12, 31))
    # window = UpdateDietLines(diet_view)
    window = UpdateDiet(diet_view)
    window.show()
    sys.exit(app.exec())
