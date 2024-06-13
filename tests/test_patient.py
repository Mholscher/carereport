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
from datetime import date
from sqlalchemy import select
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
