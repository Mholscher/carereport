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
from carereport.models.patient import (Patient, Intake, IntakeResult)
from carereport.models.medical import (DietHeader, DietLines, Medication,
                                       ExaminationRequest)

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


class TestIntake(unittest.TestCase):

    def setUp(self):

        self.patient1 = Patient(surname="Scanda", initials="K.U.",
                               birthdate=date(1982, 10, 8), sex="F")
        self.patient2 = Patient(surname="Bandala", initials="W.",
                               birthdate=date(1953, 1, 28), sex="M")
        self.diethead1 = DietHeader(diet_name="Vega",
                                    permanent_diet = True)
        self.diethead2 = DietHeader(diet_name="Drink much",
                                    start_date = date(2024, 8, 7),
                                    end_date=None)
        self.diethead3 = DietHeader(diet_name="Carbo hydrate",
                                    start_date = date(2024, 7, 12),
                                    end_date=date(2025, 2, 17))
        self.dietline1 = DietLines(food_name="Water",
                                   application_type="One liter a day",
                                   description="Drink at least 1 liter"
                                               " of water a day",
                                    diet=self.diethead2)
        self.dietline2 = DietLines(food_name="Protein",
                                   application_type="50 grams a day",
                                   description="Should eat at least 50"
                                               " grams of proteins daily",
                                    diet=self.diethead1)
        self.dietline1 = DietLines(food_name="Cookies",
                                   application_type="Don't eat",
                                   description="Not now, not ever, never",
                                    diet=self.diethead3)
        self.intake1 = Intake(date_intake=date(2024, 8, 22),
                              result="Patient admitted",
                              patient=self.patient1)


    def tearDown(self):


        session.reset()
        cr.Base.metadata.drop_all(cr.engine)
        cr.Base.metadata.create_all(cr.engine)

    def test_intake_result_mandatory(self):
        """ An intake result is mandatory """

        with self.assertRaises(ValueError):
            self.intake1.result = ''
            session.flush()

    def test_intake_cannot_be_in_future(self):
        """ An intake cannot be in the future """

        with self.assertRaises(ValueError):
            intake2 = Intake(date_intake=date.today() + timedelta(days=1),
                             result="Flunks!")
            session.flush()

    def test_intake_can_be_today(self):
        """ An intake can take place today """

        intake2 = Intake(date_intake=date.today(),
                         result="succeeds",
                         patient=self.patient1)
        session.flush()
        self.assertEqual(intake2.date_intake, date.today(),
                         "Today changed or refused as date intake")


class TestIntakeResults(unittest.TestCase):

    def setUp(self):

        self.patient1 = Patient(surname="Scanda", initials="K.U.",
                               birthdate=date(1982, 10, 8), sex="F")
        self.patient2 = Patient(surname="Bandala", initials="W.",
                               birthdate=date(1953, 1, 28), sex="M")
        self.diethead1 = DietHeader(diet_name="Vega",
                                    permanent_diet = True)
        self.diethead2 = DietHeader(diet_name="Drink much",
                                    start_date = date(2024, 8, 7),
                                    end_date=None)
        self.diethead3 = DietHeader(diet_name="Carbo hydrate",
                                    start_date = date(2024, 7, 12),
                                    end_date=date(2025, 2, 17))
        self.dietline1 = DietLines(food_name="Water",
                                   application_type="One liter a day",
                                   description="Drink at least 1 liter"
                                               " of water a day",
                                    diet=self.diethead2)
        self.dietline2 = DietLines(food_name="Protein",
                                   application_type="50 grams a day",
                                   description="Should eat at least 50"
                                               " grams of proteins daily",
                                    diet=self.diethead1)
        self.dietline1 = DietLines(food_name="Cookies",
                                   application_type="Don't eat",
                                   description="Not now, not ever, never",
                                    diet=self.diethead3)
        self.intake1 = Intake(date_intake=date(2024, 8, 22),
                              result="Patient admitted",
                              patient=self.patient1)
        self.medication1 = Medication(medication="Asphacron 70mg",
                                 patient=self.patient1)
        self.exam_request = ExaminationRequest(examination_kind="Röntgen"
                                               " scan",
                                               examaning_department= "Radio",
                                               requester_name="Guillaume",
                                               patient=self.patient1)
        self.diethead1 = DietHeader(diet_name="Only fluid",
                                    start_date=date.today())
        session.flush()



    def tearDown(self):


        session.reset()
        cr.Base.metadata.drop_all(cr.engine)
        cr.Base.metadata.create_all(cr.engine)

    def test_can_link_intake_medication(self):
        """ We can create a link to medication """

        link_type, link_key = self.medication1.add_to_intake()
        self.intake1.add_result_for(link_type, link_key)
        session.flush()
        found = 0
        for intakeresult in self.intake1.results:
            if (intakeresult.link_type == "medi0001"
                and intakeresult.link_key == self.medication1.id):
                    found += 1
        self.assertTrue(found > 0, "No link found")

    def test_can_link_intake_examination(self):
        """ We can create a link to examination request from an intake """

        link_type, link_key = self.exam_request.add_to_intake()
        self.intake1.add_result_for(link_type, link_key)
        session.flush()
        found = 0
        for intakeresult in self.intake1.results:
            if (intakeresult.link_type == "exam0001"
                and intakeresult.link_key == self.exam_request.id):
                    found += 1
        self.assertTrue(found > 0, "No link found")

    def test_can_link_intake_diet(self):
        """ We can create a link to diet from an intake """

        link_type, link_key = self.diethead1.add_to_intake()
        self.intake1.add_result_for(link_type, link_key)
        session.flush()
        found = 0
        for intakeresult in self.intake1.results:
            if (intakeresult.link_type == "diet0001"
                and intakeresult.link_key == self.diethead1.id):
                    found += 1
        self.assertTrue(found > 0, "No link found")
