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
from carereport.models.medical import Medication


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
