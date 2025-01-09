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
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDate
from carereport import session
from carereport.views.patient_views import PatientView
from carereport.views.scripts_patient import PatientChanges

class TestCreatePatientInput(unittest.TestCase):

    def setUp(self):

        self.app = QApplication([])

    def rollback(self):

        session.reset()
        self.app.quit()

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
        self.app = QApplication([])
        self.patient_view =  PatientView(surname="Vanitator",
                                         initials="O.M.",
                                         birthdate=date(1966, 12, 6),
                                         sex="M")
        self.patient_form = PatientChanges(self.patient_view)

    def rollback(self):

        session.reset()
        self.app.quit()

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
