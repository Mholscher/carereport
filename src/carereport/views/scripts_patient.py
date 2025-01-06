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
                             QTreeWidgetItem)
from .patientdialog  import Ui_inputPatient
from .patient_views import PatientView


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

        self.update_patient_view()
        super().accept()


# Code for testing purposes
if __name__ == "__main__":
    app = QApplication([])
    main_window = PatientChanges(PatientView())
    main_window.show()
    sys.exit(app.exec())