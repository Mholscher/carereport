#    Copyright 2024 Menno Hölscher
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
import unittest
from datetime import date
import carereport as cr
from carereport import session
from carereport.models.patient import Patient
from carereport.views.patient_views import PatientView


class TestCreatePatientView(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):

        session.reset()
        cr.Base.metadata.drop_all(cr.engine)
        cr.Base.metadata.create_all(cr.engine)

    def test_create_patient_view(self):
        """ Test creating a patient view of a patient in a session """

        patient = Patient()
        patient.surname = "Bogaert"
        patient.initials = "J.G.Th."
        patient.birthdate = date(1981, 4, 12)
        session.add(patient)
        patient_view = PatientView.from_patient(patient)
        self.assertEqual(patient_view.birthdate, patient.birthdate,
                         "Birthdate not filled correctly")
        self.assertEqual(patient_view.surname, patient.surname,
                         "Surname not filled correctly")

    def test_make_patient_from_view(self):
        """ Create a patient from a view """

        patient_view = PatientView(surname="Klanders",
                                   initials="T.V.",
                                   birthdate=date(2018, 5, 9),
                                   sex="M")
        patient = patient_view.to_patient()
        self.assertEqual(patient.birthdate, patient_view.birthdate,
                         "Birthdate not filled correctly")
        self.assertEqual(patient.surname, patient_view.surname,
                         "Surname not filled correctly")

    def test_view_no_sex_should_bcome_space(self):
        """ A patient should have a default sex of unknown """

        patient_view = PatientView(surname="Boresti",
                                   initials="V.",
                                   birthdate=date(2011, 2, 9),
                                   sex=None)
        patient = patient_view.to_patient()
        self.assertEqual(patient.sex, " ",
                         "Sex not defaulted correctly")


class TestUpdatePatientFromView(unittest.TestCase):

    def setUp(self):

        self.patient = Patient(id = 12,
                              surname="Lambavi",
                              initials="K.P.",
                              birthdate=date(1996, 2, 9),
                              sex="F")
        self.patient_view = PatientView(id=12,
                                        surname="Chibouste",
                                        initials="L.",
                                        birthdate=date(1995, 2, 13),
                                        sex="M")

    def tearDown(self):

        session.reset()

    def test_update_patient(self):
        """ Update the patient data from the view """

        self.patient_view.update_patient(self.patient)
        self.assertEqual(self.patient.surname, self.patient_view.surname,
                         "Surname not updated")
        self.assertEqual(self.patient.birthdate, self.patient_view.birthdate,
                         "Date of birth not updated")

    def test_ids_must_match(self):
        """ We must not overwrite data if ids differ """

        self.patient.id = 8
        with self.assertRaises(ValueError):
            self.patient_view.update_patient(self.patient)

    def test_unmatched_id_in_view_permitted(self):
        """ Can have not matching ids if in view is None """

        self.patient_view.id = None
        self.patient_view.update_patient(self.patient)
        self.assertEqual(self.patient.id, 12,
                         "id changed")


class TestViewsFromPatients(unittest.TestCase):

    def setUp(self):

        self.patient1 = Patient(
                          surname="Knalpot",
                          initials="H.",
                          birthdate=date(1956, 2, 19),
                          sex="M")
        session.add(self.patient1)
        self.patient2 = Patient(
                          surname="Linkeruitlaatpoort",
                          initials="K.",
                          birthdate=date(1977, 12, 3),
                          sex="F")
        session.add(self.patient2)
        self.patient_list = [self.patient1, self.patient2]
        session.flush()

    def tearDown(self):

        session.delete(self.patient1)
        session.delete(self.patient2)
        session.commit()
        session.reset()

    def test_create_list_of_views(self):
        """ Create a list of views from a list of patients """

        patient_view_list = PatientView.from_patient_list(self.patient_list)
        self.assertEqual(len(patient_view_list), len(self.patient_list),
                         "Lists do not have equal length")
        self.assertIn(self.patient1.surname, [patient_view_list[0].surname,
                                              patient_view_list[1].surname],
                      "Name not taken in views")

    def test_query_patients_and_create_list(self):
        """ Create a list of views from a search of patients """

        search_params = (None, "pot", None)
        patient_view_list = PatientView.get_patientlist_for_params(search_params)
        self.assertEqual(len(patient_view_list), 1,
                         "Wrong length of view list")
