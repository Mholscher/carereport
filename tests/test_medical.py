#    Copyright 2024 Menno Hölscher
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
from datetime import date, timedelta
from sqlalchemy import select
import carereport as cr
from carereport import session
from carereport.models.patient import Patient
from carereport.models.medical import (Medication, ExaminationRequest)


class TestSetMedication(unittest.TestCase):

    def setUp(self):
        """ Setup patient to test with """

        self.patient = Patient(surname="Medtest", initials="A.N.",
                               birthdate=date(1981, 3, 6), sex="F")

    def tearDown(self):

        session.reset()
        cr.Base.metadata.drop_all(cr.engine)
        cr.Base.metadata.create_all(cr.engine)

    def test_one_medication(self):
        """ Create one medication line """

        medication = Medication()
        medication.medication = "Spariaton zalf 15mg"
        medication.frequency = 2
        medication.startdate = date(2024, 2, 4)
        medication.patient = self.patient
        session.add(medication)
        from_db = list(session.execute(select(Patient,Medication).
                                       join(Patient.medication).
                                       where(Patient.surname=="Medtest")))
        # print(from_db)
        nr_medication = len(from_db)
        self.assertEqual(nr_medication, 1,
                         "Wrong number of medication lines"
                         "({no_medication})")

    def test_more_medication(self):
        """ More medication is returned """

        medication1 = Medication(medication="Billenzalf Bicarbo 55mg",
                                 frequency=1,
                                 start_date=date(2024, 7, 5),
                                 patient=self.patient)
        medication2 = Medication(medication="Rikketik pil 50mg",
                                 frequency=4,
                                 start_date=date(2013, 11, 5),
                                 patient=self.patient)
        session.add(medication1)
        from_db = list(session.execute(select(Patient,Medication).
                                       join(Patient.medication).
                                       where(Patient.surname=="Medtest")))
        # print(from_db)
        nr_medication = len(from_db)
        self.assertEqual(nr_medication, 2,
                         "Wrong number of medication lines"
                         " ({nr_medication})")

    def test_patients_using_medication(self):
        """ Gather patients using a specific medicine """

        patient2 = Patient(surname = "AFemale",
                           initials = "F.",
                           birthdate = date(2001, 12, 7),
                           sex = "F")
        patient3 = Patient(surname = "NoMed",
                           initials = "H.M.",
                           birthdate = date(2007, 2,17),
                           sex = "F")
        session.add(patient3)
        medication1 = Medication(medication="Calderaton 12mg",
                                 frequency=1,
                                 start_date=date(2024, 8, 5),
                                 patient=self.patient)
        medication2 = Medication(medication="Calderaton Forte 18mg",
                                 frequency=2,
                                 start_date=date(2023, 11, 2),
                                 patient=patient2)
        session.add(medication1)
        session.add(medication2)
        session.flush()
        from_db =  list(session.execute(select(Patient,Medication).
                                       join(Patient.medication).
                                       where(Medication.medication.like("%Calderaton%"))))
        nr_medication = len(from_db)
        self.assertEqual(nr_medication, 2,
                         "Wrong number of  lines"
                         f" ({nr_medication})")
        self.assertNotEqual(from_db[0][0], from_db[1][0],
                            "Patients equal")

    def test_medication_mandatory(self):
        """ The medication field is mandatory """

        with self.assertRaises(ValueError):
            medication1 =  Medication(medication=None,
                                     frequency=1,
                                     start_date=date(2024, 12, 5),
                                     patient=self.patient)

        with self.assertRaises(ValueError):
            medication2 =  Medication(medication="",
                                     frequency=1,
                                     start_date=date(2024, 7, 3),
                                     patient=self.patient)

    def test_frequency_type_mandatory(self):
        """ A frequency type is mandatory """

        with self.assertRaises(ValueError):
            medication =  Medication(medication="Sparagon 110",
                                    frequency=1,
                                    frequency_type=None,
                                    start_date=date(2024, 7, 3),
                                    patient=self.patient)

    def test_frequency_is_number(self):
        """ The frequency must be an unsigned number """

        with self.assertRaises(ValueError):
            medication = Medication(medication="Asparosa 12 mg",
                                    frequency="2l",
                                    start_date=date(2024, 3, 12))


class TestMedicationLists(unittest.TestCase):

    def setUp(self):

        self.patient1 = Patient(surname="Medtest", initials="B.T.",
                               birthdate=date(1991, 3, 12), sex="F")
        self.patient2 = Patient(surname="NoList", initials="V.",
                               birthdate=date(1983, 11, 12), sex="M")

        self.medication1 = Medication(medication="Sandarati 200mg",
                                      frequency=4,
                                      start_date=date(2022, 8, 5),
                                      patient=self.patient1)
        self.medication2 = Medication(medication="Vloeibare Visirant 10mg",
                                      frequency=1,
                                      start_date=date(2021, 9, 5),
                                      end_date=date(2021, 9, 15),
                                      patient=self.patient1)
        self.medication3 = Medication(medication="Sandarati 80mg",
                                      frequency=4,
                                      start_date=date(2021, 9, 15),
                                      end_date=date.today()+timedelta(days=3),
                                      patient=self.patient1)
        self.medication4 = Medication(medication="NotAppear 40mg",
                                      frequency=1,
                                      start_date=date(2024, 3, 15),
                                      patient=self.patient2)
        
        session.add_all([self.patient1, self.patient2])
        session.flush()

    def tearDown(self):

        session.reset()
        cr.Base.metadata.drop_all(cr.engine)
        cr.Base.metadata.create_all(cr.engine)

    def test_current_medication_complete(self):
        """ All medication is returned in the list """

        medication_list = Medication.medication_for_patient(self.patient1)
        self.assertEqual(len(medication_list), 2,
                         "Incorrect number of medication")
        self.assertNotIn(self.medication2, medication_list,
                         f"{self.medication2.medication}"
                         " should not be in list")

    def test_start_before_end(self):
        """ Start date of a medication should be before end date """

        with self.assertRaises(ValueError):
            self.medication1.end_date = date(2022, 7, 22)

    def test_end_after_start(self):
        """ The end date must be after the start date """

        with self.assertRaises(ValueError):
            medication = Medication(medication="Scandafi 200mg",
                                      frequency=4,
                                      end_date=date(2022, 7, 22),
                                      patient=self.patient1)
            medication.start_date = date(2022, 8, 5)


class TestExaminationRequest(unittest.TestCase):

    def setUp(self):

        self.patient1 = Patient(surname="Medtest", initials="B.T.",
                               birthdate=date(1991, 3, 12), sex="F")
        self.patient2 = Patient(surname="NoList", initials="V.",
                               birthdate=date(1983, 11, 12), sex="M")
        self.request1 = ExaminationRequest(date_request=date.today(),
                                           examination_kind="Scan",
                                           examaning_department="Radiology",
                                           requester_name="A.J. Jansen",
                                           requester_department="Cardiology",
                                           patient=self.patient1)
        self.request2 = ExaminationRequest(date_request=date.today(),
                                           examination_kind= "brain analysis",
                                           examaning_department="Psychology",
                                           requester_name="F.H. Snugsy",
                                           requester_department="Cardiology",
                                           patient=self.patient1)

        session.add_all([self.patient1, self.patient2])
        session.flush()
        self.request1_id = self.request1.id
        self.request2_id = self.request2.id

    def tearDown(self):

        session.reset()
        cr.Base.metadata.drop_all(cr.engine)
        cr.Base.metadata.create_all(cr.engine)

    def test_can_create_request(self):
        """ We can create an examination request """

        self.assertEqual(self.patient1.exam_requests[0], self.request1,
                         "Request cannot be seen from patient")

    def test_examination_kind_required(self):
        """ The examination kind is required """

        with self.assertRaises(ValueError):
            request = ExaminationRequest(date_request=date.today(),
                                         examination_kind= "",
                                         examaning_department="Internal",
                                         requester_name="F.J. Gansehuid",
                                         requester_department="Entomology",
                                         patient=self.patient1)

    def test_examining_department_required(self):
        """ The department executing the request is required """

        with self.assertRaises(ValueError):
            request = ExaminationRequest(date_request=date.today(),
                                         examination_kind= "Skin sample",
                                         examaning_department="",
                                         requester_name="H. Fodder",
                                         requester_department="Pathology",
                                         patient=self.patient1)

    def test_requester_name_required(self):
        """ The name of the requester is required """

        with self.assertRaises(ValueError):
            request = ExaminationRequest(date_request=date.today(),
                                         examination_kind= "Bacterial analysis",
                                         examaning_department="Urology",
                                         requester_name="",
                                         requester_department="Cardiology",
                                         patient=self.patient1)

    def test_execution_after_request(self):
        """ The execution date must be after the request date """

        request2 = ExaminationRequest(date_request=date.today(),
                                      examination_kind= "Bacterial analysis",
                                      examaning_department="Urology",
                                      requester_name="G. Vanvelders",
                                      requester_department="Cardiology",
                                      date_execution=date.today() +
                                      timedelta(days=2),
                                      patient=self.patient1)
        self.assertTrue(request2.date_execution > request2.date_request,
                        "Date not correctly updated")
        with self.assertRaises(ValueError):
            self.request1.date_execution = (date.today() + 
                                            timedelta(days=-2))

    def test_cannot_refuse_executed(self):
        """ If an examination is executed, it cannot be refused """

        self.request1.date_execution = date.today()
        session.flush()
        with self.assertRaises(ValueError):
            self.request1.request_refused = "No time"
            print(self.request1.date_execution, self.request1.request_refused)

    def test_open_requests_per_patient(self):
        """ List all outstanding examinations for a patient """

        open_requests = ExaminationRequest.open_requests_for_patient(
                            self.patient1)
        self.assertEqual(len(open_requests), 2, "No of requests incorrect")
        no_requests = ExaminationRequest.open_requests_for_patient(
                          self.patient2)

    def test_refused_not_listed(self):
        """ Refused examinations should not be listed """
        self.request2.request_refused = "Not appropriate"
        open_requests = ExaminationRequest.open_requests_for_patient(
                            self.patient1)
        self.assertNotIn(self.request2, list(open_requests),
                      "Refused request in open requests")

    def test_examination_in_past_omitted(self):
        """ An examination in the past should not be reported """

        self.request2.date_request = date.today() + timedelta(days=-10)
        self.request2.date_execution = date.today() + timedelta(days=-5)
        open_requests = ExaminationRequest.open_requests_for_patient(
                            self.patient1)
        self.assertNotIn(self.request2, list(open_requests),
                      "Past request in open requests")
        
    def test_requests_per_department(self):
        """ Report outstanding requests per department """

        request_list = ExaminationRequest.requests_for_department("diology")
        self.assertEqual(self.request1_id, request_list[0][0].id,
                      "Request that should appear not in list")
        self.assertEqual(len(request_list[0]), 1,
                         "More than the 1 entry expected")
