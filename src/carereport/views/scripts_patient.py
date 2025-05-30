#    Copyright 2024/2025 Menno Hölscher
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

""" This module holds the scripting and user interface for the input of
patient data.

This entails the usage of Qt classes to create and process and the maintenance
of the views interfacing class, PatientView, for the interface to the model.
 """

import sys
from datetime import date
from PyQt6.QtCore import QDate
from PyQt6.QtCore import QLocale as Loc
from PyQt6.QtWidgets import (QApplication, QDialog, QTableWidgetItem)
from carereport import (app, session)
from .care_app import mainwindow
from .patientdialog import Ui_inputPatient
from .patientsearch import Ui_PatientSearchDialog
from .patient_views import PatientView
from .intake_views import IntakeView
# from PyQt6.QtTest import QSignalSpy

sex_translations = (("F", "Vrouw"), ("M", "Man"),
                    (" ", "Onbekend"))


class PatientChanges(QDialog, Ui_inputPatient):
    """ This class handles creating and changing patient data

    It exchanges the data with the model through the patient view.
    """
    def __init__(self, patient_view, parent=None):

        super().__init__(parent=parent)

        self.setupUi(self)
        self.setFixedSize(400, 336)
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
        self.accepted.connect(self.on_accept)  # type: ignore
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

    def update_patient(self):
        """ Update the patient with the data from the view.

        This should be the last thing done after all changes from the window
        have been put into the view.
        """

        patient = self.patient_view.patient
        if self.patient_view.surname != patient.surname:
            patient.surname = self.patient_view.surname
        if self.patient_view.initials != patient.initials:
            patient.initials = self.patient_view.initials
        if self.patient_view.birthdate != patient.birthdate:
            patient.birthdate = self.patient_view.birthdate
        if self.patient_view.sex != patient.sex:
            patient.sex = self.patient_view.sex

    def accept(self):
        """ Check if the data in the dialog is acceptable

        If it is, accept the data, else give message and stay on dialog.
        """

        problem_list = []
        if not self.patient_name_edit.text():
            problem_list.append("Achternaam kan niet leeg zijn")
        if not self.initials_edit.text():
            problem_list.append("Initialen kunnen niet leeg zijn")

        if problem_list:
            self.statusLabel.setText(";".join(problem_list))
        else:
            super(PatientChanges, self).accept()

    def on_accept(self):
        """ The input was OK-ed by the user """

        self.update_patient_view()
        if self.patient_view.id:
            self.update_patient()
        else:
            self.patient_view.to_patient()

    def focusOnName(self, event):
        """ Reset error label """

        self.nameerrorlabel.setText("")
        return self.focusInEvent(event)

    def focusOnInitials(self, event):
        """ Reset error label """

        self.initialserrorlabel.setText("")
        return self.focusInEvent(event)


class FindCreatePatient(QDialog, Ui_PatientSearchDialog):

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.setupUi(self)
        self.setFixedSize(434, 300)
        self.search_params = tuple()
        self.startSearchButton.clicked.connect(
            self.search_for_patients)
        self.cancelSearchButton.clicked.connect(self.done)
        self.cancelButton.clicked.connect(self.done)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.currentChanged.connect(self.arrive_at_page)
        self.changeSearchButton.clicked.connect(self.show_criteria_selection)
        self.patientSelectButton.clicked.connect(self.selected_patient)
        self.newPatientButton.clicked.connect(self.create_new_patient)
        self.patientTable.itemSelectionChanged.connect(
            self.on_selection_changed)

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
                    self.statusLabel.setText("Datum"
                                             f"{birthdate_text} ongeldig")
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
                    born = patient_views[row].birthdate
                    the_field = Loc().toString(QDate(born.year, born.month,
                                               born.day),
                                               Loc.FormatType.ShortFormat)
                elif column == 3:
                    for code, text in sex_translations:
                        if patient_views[row].sex == code:
                            the_field = text
                            break
                    else:
                        the_field = patient_views[row].sex
                the_item = QTableWidgetItem(the_field, type=4015)
                if column == 0:
                    the_item.id = patient_views[row].id
                self.patientTable.setItem(row, column, the_item)
        self.patient_views = patient_views

    def select_patients_from_params(self):
        """ Get patients from data for search parameters """

        return PatientView.get_patientlist_for_params(self.search_params)

    def arrive_at_page(self, page_index):
        """ Take action when arriving at a page of the patient selection """

        if page_index == 1:
            self.patientSelectButton.setEnabled(False)
            self.statusLabel.setText("Kies patiënt of maak een nieuwe")
        return

    def show_criteria_selection(self, event):
        """ Show the selection criteria for changing """

        self.stackedWidget.setCurrentIndex(0)
        self.statusLabel.setText("Pas zoekcriteria aan")

    def selected_patient(self):
        """ Set the selected patient form the table as the current one.

        TODO: refactor to use selectedranges
        """

        if self.patientTable.selectedRanges() == []:
            self.statusLabel.setText("Selecteer eerst een patiënt")
            return
        for row in range(self.patientTable.rowCount()):
            if self.patientTable.item(row, 0).isSelected():
                for patient_view in self.patient_views:
                    if patient_view.id == self.patientTable.item(row, 0).id:
                        app.current_patient_view = patient_view
                        break
                break
        self.accept()

    def create_new_patient(self):
        """ Create a new patient_view and make this current """

        QApplication.instance().current_patient_view = PatientView()
        self.accept()

    def on_selection_changed(self):
        """ If a selection is changed, we may enable/disable buttons """

        if self.patientTable.selectedRanges() != []:
            self.patientSelectButton.setEnabled(True)
        else:
            self.patientTable.patientSelectButton.setEnabled(False)


def NewIntake():
    """ Create a new intake for an existing or new patient

    The data and event handlers are in the
    :py:func:`FindCreateChangePatient`
    type
    """

    return FindCreateChangePatient()


class FindCreateChangePatient(object):
    """ Find or create a patient and change the data

    The user is allowed to enter some search criteria, and if the patient is
    found, select it as the current patient. After that the patient can be
    changed. The change will be saved to the database or rolled back.
    """

    def __init__(self):

        self.find_patient = FindCreatePatient(parent=mainwindow)
        mainwindow.find_or_create_patient = self
        self.find_patient.accepted.connect(self.patient_ready)
        self.ask_user()

    def ask_user(self):
        """ Find or create the patient using "my" find/create """

        self.find_patient.show()

    def patient_ready(self):
        """ Start the patient modify for intake """

        self.modify_patient = PatientChanges(app.current_patient_view)
        self.modify_patient.current_intake = IntakeView(
            patient=self.modify_patient)
        self.modify_patient.accepted.connect(self.update_patient_data)
        self.modify_patient.show()

    def update_patient_data(self):
        """ Update patient + add to session """

        if app.current_patient_view.id:
            self.modify_patient.update_patient()
        else:
            app.current_patient_view.to_patient()
            session.add(app.current_patient_view.patient)
        intake = self.modify_patient.current_intake.create_intake_from_view()
        session.add(intake)
        session.commit()
        mainwindow.find_or_create_patient = None


mainwindow.actionNieuw.triggered.connect(FindCreateChangePatient)

# Code for testing purposes
if __name__ == "__main__":
    patient_view = PatientView()
    # window = FindCreatePatient()
    window = PatientChanges(patient_view)
    window.show()
    sys.exit(app.exec())
