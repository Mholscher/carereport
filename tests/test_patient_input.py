#    Copyright 2025 Menno Hölscher
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
import unittest
from datetime import date
from PyQt6.QtWidgets import QApplication, QTableWidgetSelectionRange
from PyQt6.QtCore import QDate
from carereport import session, app
from carereport.models.patient import Patient
from carereport.views.patient_views import PatientView
from carereport.views.scripts_patient import (PatientChanges,
                                              FindCreatePatient)


class TestCreatePatientInput(unittest.TestCase):

    def setUp(self):

        # self.app = QApplication([])
        pass

    def tearDown(self):

        session.reset()
        # self.app.quit()

    def test_create_for_view(self):
        """ The basics: create the screen for a view """

        patient_view = PatientView(surname="Scaffeljou",
                                   initials="K.M.N.",
                                   birthdate=date(1988, 6, 15),
                                   sex="F")
        patient_form = PatientChanges(patient_view)
        self.assertEqual(patient_form.patient_name_edit.text(),
                         "Scaffeljou", "Name not filled")
        self.assertEqual(patient_form.sex_box.currentText(),
                         "Vrouw", "Sex not filled correctly")
        self.assertEqual(patient_form.date_edit.date(),
                         QDate(1988, 6, 15),
                         "Date nor filled correctly")

    def test_update_view(self):
        """ Return the changed data to the view """

        patient_view = PatientView(surname="Bonifant",
                                   initials="T.M.",
                                   birthdate=date(1975, 8, 5),
                                   sex="M")
        patient_form = PatientChanges(patient_view)
        patient_form.patient_name_edit.setText("Bonnifant")
        patient_form.sex_box.setCurrentText("Vrouw")
        patient_form.date_edit.setDate(QDate(1975, 8, 15))
        patient_form.update_patient_view()
        self.assertEqual(patient_view.surname,
                         "Bonnifant", "Name not changed")
        self.assertEqual(patient_view.sex,
                         "F", "Sex not filled correctly")
        self.assertEqual(patient_view.birthdate,
                         date(1975, 8, 15),
                         "Date nor filled correctly")


class TestStandardInput(unittest.TestCase):

    def setUp(self):

        # self.app = QApplication([])
        self.patient_view = PatientView(surname="Vanitator",
                                        initials="O.M.",
                                        birthdate=date(1966, 12, 6),
                                        sex="M")
        self.patient_form = PatientChanges(self.patient_view)

    def tearDown(self):

        session.reset()
        # self.app.quit()

    def test_accept_input(self):
        """ Accepting input updates the view """

        self.patient_form.patient_name_edit.setText("Vanitatis")
        self.patient_form.initials_edit.setText("P.W.")
        self.patient_form.accept()
        self.assertEqual(self.patient_view.surname,
                         "Vanitatis",
                         "Name not set to view")
        self.assertEqual(self.patient_view.initials,
                         "P.W.",
                         "Initials not set to view")

    def test_ignore_input(self):
        """ Ignoring input updates the view """

        self.patient_form.patient_name_edit.setText("Vanitatis")
        self.patient_form.reject()
        self.assertNotEqual(self.patient_view.surname,
                            "Vanitatis",
                            "Name set to view")

    # @unittest.skip
    def test_empty_name_fails(self):
        """ Empty surname does not update """

        self.patient_form.patient_name_edit.setText("")
        self.patient_form.accept()
        self.assertEqual(self.patient_view.surname,
                         "Vanitator",
                         "Name changed")

    def test_empty_initials_fails(self):
        """ Empty initials does not update """

        self.patient_form.initials_edit.setText("")
        self.patient_form.accept()
        self.assertEqual(self.patient_view.initials,
                         "O.M.",
                         "Initials changed")


class TestSearchCriterionsPatient(unittest.TestCase):

    def setUp(self):

        # self.app = QApplication([])
        self.search_dialog = FindCreatePatient()

    def tearDown(self):

        # self.app.quit()
        pass

    def test_create_search_criterions(self):
        """ Create criteria for a search of patient """

        self.search_dialog.birthdateEdit.setText("17-01-1976")
        self.search_dialog.SearchNameEdit.setText("Sanoussin")
        self.search_dialog.searchInitialsEdit.setText("Y.")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.search_params,
                         (date(1976, 1, 17),
                          "Sanoussin",
                          "Y."),
                         "Incorrect search_parameters")

    def test_part_search_criterion(self):
        """ Create a search criterion with empty field(s) """

        self.search_dialog.birthdateEdit.setText("17-01-1976")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.search_params,
                         (date(1976, 1, 17),
                          "",
                          ""),
                         "Incorrect search_parameters")

    def test_after_search_goto_results(self):
        """ After searching go to the result page """

        self.search_dialog.birthdateEdit.setText("19-11-1978")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.stackedWidget.currentIndex(),
                         1, "No page switch")

    def test_if_no_criteria_no_switch(self):
        """ Don't go to result page if wrong criteria """

        self.search_dialog.stackedWidget.setCurrentIndex(0)
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.stackedWidget.currentIndex(),
                         0, "Page switched")
        self.assertIn("één", self.search_dialog.statusLabel.text(),
                      "Status niet aangepast")


class TestDateInput(unittest.TestCase):

    def setUp(self):

        # self.app = QApplication([])
        self.search_dialog = FindCreatePatient()

    def tearDown(self):

        # self.app.quit()
        pass

    def test_full_date(self):
        """ Test that a date with all digits work """

        self.search_dialog.birthdateEdit.setText("12-11-1966")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.search_params[0].day,
                         12, "day not converted correctly")
        self.assertEqual(self.search_dialog.search_params[0].month,
                         11, "month not converted correctly")
        self.assertEqual(self.search_dialog.search_params[0].year,
                         1966, "year not converted correctly")

    def test_date_one_digit_day(self):
        """ A date with single digit day is converted  """

        self.search_dialog.birthdateEdit.setText("2-10-1998")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.search_params[0].day,
                         2, "day not converted correctly")
        self.assertEqual(self.search_dialog.search_params[0].month,
                         10, "month not converted correctly")
        self.assertEqual(self.search_dialog.search_params[0].year,
                         1998, "year not converted correctly")

    def test_date_one_digit_month(self):
        """ A date with single digit month is converted  """

        self.search_dialog.birthdateEdit.setText("12-3-1948")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.search_params[0].day,
                         12, "day not converted correctly")
        self.assertEqual(self.search_dialog.search_params[0].month,
                         3, "month not converted correctly")
        self.assertEqual(self.search_dialog.search_params[0].year,
                         1948, "year not converted correctly")

    # @unittest.skip
    def test_convert_invalid_date_fails(self):
        """ An invalid date inoputted fails """

        self.search_dialog.birthdateEdit.setText("12-31-1965")
        self.search_dialog.startSearchButton.clicked.emit()
        self.assertEqual(self.search_dialog.stackedWidget.currentIndex(),
                         0, "Page switched")


class TestPatientSelection(unittest.TestCase):

    def setUp(self):

        # self.app = QApplication([])
        self.search_dialog = FindCreatePatient()
        self.patient_views = [PatientView(id=3,
                                          surname="Chasselair",
                                          initials="Y.M.",
                                          birthdate=date(1987, 4, 3),
                                          sex="Vrouw"),
                              PatientView(id=7,
                                          surname="Chasselase",
                                          initials="T.Y.",
                                          birthdate=date(1987, 12, 17),
                                          sex="Vrouw"),
                              PatientView(id=12,
                                          surname="Chasselinome",
                                          initials="S.Y.",
                                          birthdate=date(1992, 2, 28),
                                          sex="Vrouw")]
        self.patient1 = Patient(surname="Scaffiy", initials="E.U.",
                                birthdate=date(1982, 10, 8), sex="F")
        session.add(self.patient1)
        self.patient2 = Patient(surname="Snately", initials="W.",
                                birthdate=date(1953, 1, 12), sex="M")
        session.add(self.patient2)
        self.patient3 = Patient(surname="Snatch", initials="E.I.M.",
                                birthdate=date(1973, 1, 12), sex="M")
        session.add(self.patient3)
        self.patient4 = Patient(surname="Frety", initials="F.R.",
                                birthdate=date(1992, 5, 30), sex="F")
        session.add(self.patient4)
        session.flush()

    def tearDown(self):

        # self.app.quit()
        session.rollback()
        # cr.Base.metadata.drop_all(cr.engine)
        # cr.Base.metadata.create_all(cr.engine)

    def test_show_patients(self):
        """ Show patients in views on table """

        self.search_dialog.load_patient_selection(self.patient_views)
        selected_count = self.search_dialog.patientTable.rowCount()
        names = [self.search_dialog.patientTable.item(row, 0).text()
                 for row in range(selected_count)]
        self.assertIn("Chasselair", names,
                      "Name Chasselair not found")
        self.assertIn("Chasselase", names,
                      "Name Chasselase not found")
        self.assertIn("Chasselinome", names,
                      "Name Chasselinome not found")

    def test_show_no_patients(self):
        """ Show no rows for empty selection """

        self.search_dialog.load_patient_selection([])
        selected_count = self.search_dialog.patientTable.rowCount()
        self.assertFalse(selected_count, "Showing **something")

    def test_return_patient_data(self):
        """ Requested data is returned """

        self.search_dialog.search_params = (None, "Snat", None)
        patients = self.search_dialog.select_patients_from_params()
        self.assertEqual(len(patients), 2,
                         "Incorrect no of patients returned")

    def test_to_selection_set_message(self):
        """ Getting to the patient result page """

        self.search_dialog.stackedWidget.setCurrentIndex(0)
        start_text = "Now on parameter set"
        self.search_dialog.statusLabel.setText(start_text)
        self.search_dialog.stackedWidget.setCurrentIndex(1)
        self.assertNotEqual(self.search_dialog.statusLabel.text(),
                            start_text,
                            "Status text not changed")

    def test_show_sex_translated(self):
        """ Show sex as a word, not a code """

        self.search_dialog.load_patient_selection(self.patient_views)
        # print(self.search_dialog.patientTable.item(1, 3).data(0))
        self.assertEqual(self.search_dialog.patientTable.item(1, 3).data(0),
                         "Vrouw", "Sex verkeerd")

    def test_change_search_criteria(self):
        """ Pressing the change search shows the criteria input """

        self.search_dialog.stackedWidget.setCurrentIndex(1)
        self.search_dialog.changeSearchButton.click()
        self.assertEqual(self.search_dialog.stackedWidget.currentIndex(), 0,
                         "Index not changed")

    @unittest.skip
    def test_cancel_search_from_selection(self):
        """ Cancel search from the selection stack pane """

        self.search_dialog.stackedWidget.setCurrentIndex(1)
        self.search_dialog.cancelButton.click()
        self.assertTrueś(self.search_dialog.isHidden(),
                         "Dialog visible changed")

    def test_existing_selected(self):
        """ When "Choose" is selected, the dialog signals accepted """

        self.search_dialog.load_patient_selection(self.patient_views)
        range = QTableWidgetSelectionRange(1, 0, 1, 3)
        self.search_dialog.patientTable.setRangeSelected(range, True)
        selection_ranges = self.search_dialog.patientTable.selectedRanges()
        self.assertEqual(selection_ranges[0].columnCount(),
                         4, "Wrong number of columns")

    def test_set_id_on_column_0(self):
        """ The id from patient_view is set on column 0 """

        self.search_dialog.load_patient_selection(self.patient_views)
        self.assertEqual(self.search_dialog.patientTable.item(1, 0).id,
                         self.patient_views[1].id,
                         "Incorrect Id set")

    def test_select_patient_as_current(self):
        """ A patient form the table is selected to be the cuurent one """

        self.search_dialog.load_patient_selection(self.patient_views)
        range = QTableWidgetSelectionRange(1, 0, 1, 3)
        self.search_dialog.patientTable.setRangeSelected(range, True)
        self.search_dialog.selected_patient()
        self.assertEqual(QApplication.instance().current_patient_view,
                         self.patient_views[1],
                         "Current_patient not set")
