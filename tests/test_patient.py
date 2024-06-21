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

class TestCreatePatient(unittest.TestCase):

    def setUp(self):

        pass

    def rollback(self):

        session.reset()
        

    def test_create_patient(self):
        """ Test creating a patient in the current session """

        patient = Patient()
        patient.surname = "Bogaert"
        patient.initials = "J.G.Th."
        patient.birthdate = date(1981, 4, 12)
        # print(patient.surname, patient.initials, patient.birthdate)
        # from time import sleep
        # sleep(3)
        session.add(patient)
        stmt = select(Patient).where(Patient.surname=="Bogaert")
        reread_patient = session.execute(stmt).all()
        self.assertTrue(reread_patient, f"Patient {patient.surname} not found")

    def test_patient_has_name(self):
        """ A patient must have a valid name """

        with self.assertRaises(ValueError):
            patient = Patient()
            patient.surname = ""
            patient.initials = "G.B."
            patient.birthdate = date(1972, 6, 7)

    def test_patient_name_none(self):
        """ A patients name needs to be filled """
 
        with self.assertRaises(ValueError):
            patient = Patient()
            patient.surname = None
            patient.initials = "J.B."
            patient.birthdate = date(1971, 7, 12)

    def test_birth_date_in_past(self):
        """ A birth date in the future is an error """

        with self.assertRaises(ValueError):
            patient = Patient()
            patient.surname = "Goofy"
            patient.initials = "P.L."
            today = date.today()
            patient.birthdate = today + timedelta(days=2)

    def test_born_today_is_OK(self):
        """ The patient may be born today """

        patient = Patient()
        patient.surname = "Zplots"
        patient.initials = "T.L."
        patient.birthdate = date.today()
        self.assertEqual(patient.birthdate, date.today(),
                         "Birthdate today not accepted")

    def test_sex_valid_works(self):
        """ All valid sex letters are accepted """

        patient1 = Patient()
        patient1.surname = "AMale"
        patient1.initials = "M."
        patient1.birthdate = date.today()
        patient1.sex = "M"
        self.assertEqual(patient1.sex, "M",
                         "sex male not accepted")
        patient2 = Patient()
        patient2.surname = "AFemale"
        patient2.initials = "F."
        patient2.birthdate = date.today()
        patient2.sex = "F"
        self.assertEqual(patient2.sex, "F",
                         "sex female not accepted")
        patient3 = Patient()
        patient3.surname = "Nonbinary"
        patient3.initials = "X."
        patient3.birthdate = date.today()
        patient3.sex = "X"
        self.assertEqual(patient3.sex, "X",
                         "sex non-binary not accepted")

    def test_invalid_sex_refused(self):
        """ Invalid sex code gives error """

        with self.assertRaises(ValueError):
            patient = Patient()
            patient.surname = "Unusable"
            patient.initials = "U."
            patient.birthdate = date.today()
            patient.sex = "U"
