#    Copyright 2025 Menno Hölscher
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
from carereport import (app, session, Intake, Patient)
from carereport.views.patient_views import PatientView
from carereport.views.intake_views import (IntakeView, NoCurrentPatientError)


class TestViewFromToIntake(unittest.TestCase):

    def setUp(self):

        self.patient = Patient(surname="Kanfello",
                               initials="O.F.",
                               birthdate=date(1987, 4, 12))
        session.add(self.patient)
        self.patient_view = PatientView.from_patient(self.patient)
        app.current_patient_view = self.patient_view
        self.intake = Intake(date_intake=date.today(),
                             patient=self.patient)
        session.add(self.intake)

    def tearDown(self):

        session.reset()
        # self.app.quit()

    def test_create_view_from_intake(self):
        """ Create a view from an intake """

        view = IntakeView.create_view_from_intake(self.intake)
        self.assertEqual(view.patient, self.patient_view,
                         "Incorrect/no patient in intake")

    def test_patient_view_has_current_intake(self):
        """ a created intake view is attached to the patient view """

        view = IntakeView.create_view_from_intake(self.intake)
        self.assertEqual(self.patient_view.current_intake, view,
                         "Current intake not in patient view")

    def test_create_intake_from_view(self):
        """ Create an intake from the view """

        intake_view = IntakeView(patient=self.patient_view,
                                 date_intake=date(2025, 1, 12))
        intake = intake_view.create_intake_from_view()
        self.assertEqual(intake.date_intake, intake_view.date_intake,
                         "Data not transferred correctly")

    def test_no_intake_wo_patient(self):
        """ An intake can only be created if there is current patient """

        del app.current_patient_view
        with self.assertRaises(NoCurrentPatientError):
            IntakeView.create_view_from_intake(self.intake)
