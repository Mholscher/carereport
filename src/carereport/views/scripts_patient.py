#    Copyright 2024/2025 Menno Hölscher
#
#    This file is part of carereport.

#    carereport is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    carereport is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.

#    You should have received a copy of the GNU Lesser General Public License
#    along with carereport.  If not, see <http://www.gnu.org/licenses/>.

""" This module holds the scripting and user interface for the input of
patient data.

This entails the usage of Qt classes to create and process and the maintenance
of the views interfacing class, PatientView, for the interface to the model.
 """

import sys
from datetime import date
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QApplication, QDialog, QListWidget,
                             QTreeWidget, QLabel, QWidget,
                             QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QPushButton, 
                             QLineEdit, QTextEdit, QListWidgetItem,
                             QTreeWidgetItem, QTableWidgetItem)
from PyQt6.QtGui import QValidator
from .helpers import not_empty
from .patientdialog  import Ui_inputPatient
from .patientsearch import Ui_PatientSearchDialog
from .patient_views import PatientView

sex_translations = (("F", "Vrouw"), ("M", "Man"))

class PatientChanges(QDialog, Ui_inputPatient):
    """ This class handles creating and changing patient data

    It exchanges the data with the model through the patient view.
    """
    def __init__(self, patient_view):

        super().__init__()

        self.setupUi(self)
        self.patient_name_edit.setText(patient_view.surname)
        self.initials_edit.setText(patient_view.initials)
        self.sex_box.addItems(["Vrouw", "Man"])
        if patient_view.sex == "F":
            self.sex_box.setCurrentText("Vrouw")
        elif patient_view.sex == "M":
            self.sex_box.setCurrentText("Man")
        self.date_edit.setDate(QDate(patient_view.birthdate.year,
                                     patient_view.birthdate.month,
                                     patient_view.birthdate.day))
        self.date_edit.setMaximumDate(QDate.currentDate())
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.patient_name_edit.focusInEvent = self.focusOnName
        self.initials_edit.focusInEvent = self.focusOnInitials
        self.patient_view = patient_view

    def update_patient_view(self):
        """ Update the view with the current data from the dialog.

        This is a destructive operation on the attributes of the view.
        """

        self.patient_view.surname = self.patient_name_edit.text()
        self.patient_view.initials = self.initials_edit.text()
        if self.sex_box.currentText() == "Vrouw":
            self.patient_view.sex = "F"
        elif self.sex_box.currentText() == "Man":
            self.patient_view.sex = "M"
        edited_date = self.date_edit.date()
        self.patient_view.birthdate = date(edited_date.year(),
                                           edited_date.month(),
                                           edited_date.day())

    def accept(self):
        """ The input was OK-ed by the user """

        filled_name = not_empty(self.patient_name_edit)
        filled_initials = not_empty(self.initials_edit)
        if filled_name and filled_initials:
            self.update_patient_view()
            return super().accept()
        if not filled_name:
            self.nameerrorlabel.setText("*")
        if not filled_initials:
            self.initialserrorlabel.setText("*")
        return

    def focusOnName(self, event):
        """ Reset error label """

        self.nameerrorlabel.setText("")
        return self.focusInEvent(event)

    def focusOnInitials(self, event):
        """ Reset error label """

        self.initialserrorlabel.setText("")
        return self.focusInEvent(event)


class FindCreatePatient(QDialog, Ui_PatientSearchDialog):

    def __init__(self):

        super().__init__()

        self.setupUi(self)
        self.search_params = tuple()
        self.startSearchButton.clicked.connect(
            self.search_for_patients)
        self.cancelSearchButton.clicked.connect(self.done)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.currentChanged.connect(self.arrive_at_page)

    def search_for_patients(self, event):
        """ The parameters are entered, cast off the search

        The search is parametrized by the search_params, a tuple containing:

            :birthdate: the birthdate of thepatient to search for
            :surname: (part of) the surname of the patient
            :initials: (part of) the initials of the patient
    
        Not all of the items are required. One of them is enough 
        to start the search. Of course, the more fields are filled,
        the more precise the search, i.e. less results.
        """

        birthdate_text = self.birthdateEdit.text()
        birthdate_list = birthdate_text.split("-")
        if len(birthdate_list) != 3:
            self.statusLabel.setText(f"Datum {birthdate_text} ongeldig")
            return
        if any(birthdate_list):
            for seqno, datepart in enumerate(birthdate_list):
                try:
                    birthdate_list[seqno] = int(datepart)
                except ValueError:
                    self.statusLabel.setText(f"Datum {birthdate_text} ongeldig")
                    return
            try:
                birthdate = date(birthdate_list[2], birthdate_list[1],
                                 birthdate_list[0])
            except ValueError:
                # print(f"Datum {birthdate_text} ongeldig")
                self.statusLabel.setText(f"Datum {birthdate_text} ongeldig")
                return                
        else:
            birthdate = None
        name_part = self.SearchNameEdit.text()
        initials_part = self.searchInitialsEdit.text()
        self.search_params = (birthdate, name_part, initials_part)
        if any(self.search_params):
            patient_views = self.select_patients_from_params()
            self.load_patient_selection(patient_views)
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.statusLabel.setText("Vul minstens één veld!")

    def load_patient_selection(self, patient_views):
        """ Load the table with an iterable of patients """

        self.patientTable.setColumnCount(4)
        self.patientTable.setHorizontalHeaderLabels(["Naam",
                                                    "Voorletters",
                                                    "Geboortedatum",
                                                    "Sexe"])
        self.patientTable.setRowCount(len(patient_views))
        for row in range(len(patient_views)):
            for column in range(4):
                if column == 0:
                    the_field = patient_views[row].surname
                elif column == 1:
                    the_field = patient_views[row].initials
                elif column == 2:
                    the_field = str(patient_views[row].birthdate)
                elif column == 3:
                    for code, text in sex_translations:
                        if patient_views[row].sex == code:
                            the_field = text
                            break
                    else:
                        the_field = patient_views[row].sex
                the_item = QTableWidgetItem(the_field, type=4015)
                self.patientTable.setItem(row, column,the_item)

    def select_patients_from_params(self):
        """ Get patients from data for search parameters """

        return PatientView.get_patientlist_for_params(self.search_params)

    def arrive_at_page(self, page_index):
        """ Take any action when arriving at a page of the patient selection """

        if page_index == 1:
            self.statusLabel.setText("Kies patient of maak een nieuwe")
        return


# Code for testing purposes
if __name__ == "__main__":
    app = QApplication([])
    main_window = FindCreatePatient()
    main_window.open()
    sys.exit(app.exec())
