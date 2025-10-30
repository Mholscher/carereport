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
from carereport.models.medical import DietHeader, DietLines
from carereport.views.patient_views import PatientView
from carereport.views.diet_views import (DietView, DietLineView)


class TestDietViewFromToDiet(unittest.TestCase):

    def setUp(self):

        self.patient_view = PatientView(surname="Canafella",
                                        initials="R.U.",
                                        birthdate=date(2003, 12, 4),
                                        sex="F")
        self.patient_view.to_patient()
        self.patient1 = self.patient_view.patient
        self.diet = DietHeader(id=2101,
                               diet_name="Suikervrij",
                               permanent_diet=True,
                               start_date=None,
                               end_date=None,
                               patient=self.patient1)
        self.dietline1 = DietLines(id=12,
                                   food_name="Suiker",
                                   application_type="Niet gebruiken",
                                   description="Suikervrij betekent dat je"
                                   "nergens suiker in mag doen",
                                   diet=self.diet)
        session.add_all([self.diet, self.patient1])
        self.diet_view = DietView(id=None,
                                  diet_name="Fruit",
                                  permanent_diet=False,
                                  start_date=date(2025, 4, 12),
                                  end_date=None,
                                  patient=self.patient_view)
        session.flush()

    def tearDown(self):

        session.rollback()

    def test_create_view_from_diet(self):
        """ Create a view for a diet header """

        diet_view1 = DietView.create_from_diet(self.diet)
        self.assertEqual(diet_view1.id, self.diet.id,
                         "Id not copied to view")
        self.patient_view.id = diet_view1.patient.id 
        self.assertEqual(diet_view1.patient, self.patient_view,
                         "Patient not converted")

    def test_create_diet_from_view(self):
        """ Create a diet header from a diet view """

        diet_view1 = self.diet_view.to_diet()
        self.assertEqual(diet_view1.patient, self.patient1,
                         "Patient not converted")

    def test_diet_in_view(self):
        """ Creating a view from a diet should put the header in the view """

        diet_view = DietView.create_from_diet(self.diet)
        self.assertEqual(diet_view.diet_header, self.diet,
                         f"Diet {self.diet.diet_name} not in view")

    def test_update_diet_from_view(self):
        """ Update an existing view from the view """

        diet_view = DietView.create_from_diet(self.diet)
        diet_view.diet_name = "Zoutloos"
        diet_view.update_diet()
        self.assertEqual(diet_view.diet_name, self.diet.diet_name,
                         f"Name not changed in {self.diet.diet_name}")
        diet_view.permanent_diet = False
        diet_view.update_diet()
        self.assertFalse(diet_view.diet_header.permanent_diet,
                         "Permanent not changed")

    def test_create_diet_views(self):
        """ Create diet views for a patient """

        diets = DietView.diets_for_patient(self.patient_view)
        self.assertEqual(len(diets), 1,
                         f"Wrong number of diets: {len(diets)}")
        self.assertEqual(diets[0].id, 2101,
                         f"Wrong diet id: {diets[0].id}")

    def test_create_diet_line_views_for_diet(self):
        """ Get the lines for a diet """

        diet_line = DietLines(id=17,
                              food_name="Taart",
                              application_type="Niet gebruiken",
                              description="Taart bevat gewoonlijk"
                              " heel veel suiker",
                              diet=self.diet)
        diet_view = DietView.create_from_diet(self.diet)
        diet_lines = diet_view.lines()
        self.assertEqual(len(diet_lines), 2,
                         f"Wrong number of lines: {len(diet_lines)}")
        ids = [diet.id for diet in diet_lines]
        self.assertIn(12, ids, "At least one id not in lines")


class TestDietLineViewFromToLine(unittest.TestCase):

    def setUp(self):

        self.patient_view = PatientView(surname="Canafella",
                                        initials="R.U.",
                                        birthdate=date(2003, 12, 4),
                                        sex="F")
        self.patient_view.to_patient()
        self.patient1 = self.patient_view.patient
        self.diet = DietHeader(id=2101,
                               diet_name="Suikervrij",
                               permanent_diet=True,
                               start_date=None,
                               end_date=None,
                               patient=self.patient1)
        self.dietline1 = DietLines(id=12,
                                   food_name="Suiker",
                                   application_type="Niet gebruiken",
                                   description="Suikervrij betekent dat je"
                                   "nergens suiker in mag doen",
                                   diet=self.diet)
        session.add_all([self.diet, self.patient1])
        self.diet_view = DietView(id=None,
                                  diet_name="Fruit",
                                  permanent_diet=False,
                                  start_date=date(2025, 4, 12),
                                  end_date=None,
                                  patient=self.patient_view)
        self.diet_line_view = DietLineView(id=42,
                                           food_name="Peer",
                                           application_type="Eet regelmatig",
                                           description="De peer is een vrucht die we"
                                           "regelmatig mogen eten",
                                           diet_view=self.diet_view)
        session.flush()

    def tearDown(self):

        session.rollback()

    def test_create_view_form_diet_line(self):
        """ Create a line view from a diet line """

        diet_view1 = DietView.create_from_diet(self.diet)
        diet_line_view = DietLineView.create_from_diet_line(self.dietline1,
                                                            diet_view1)
        self.assertEqual(diet_line_view.diet_line, self.dietline1,
                         "View does not contain line (is"
                         f" {diet_line_view.diet_line}) ")

    def test_update_diet_line_from_view(self):
        """ Update  the line for a diet line view  """

        diet_view2 = DietView.create_from_diet(self.diet)
        diet_line_view2 = DietLineView.create_from_diet_line(self.dietline1,
                                                             diet_view2)
        diet_line_view2.application_type = "Geen suiker gebruiken"
        diet_line_view2.update_diet_line()
        self.assertEqual(diet_line_view2.application_type,
                         self.dietline1.application_type,
                         "Change not passed from view to model")

    def test_create_diet_line_from_view(self):
        """ Create a new diet line from a view """

        diet_header = self.diet_view.to_diet()
        diet_line = self.diet_line_view.to_diet_line(diet_header)
        self.assertEqual(diet_line.food_name, self.diet_line_view.food_name,
                         f"Food name {diet_line.food_name} not correct")
        self.assertEqual(diet_line.application_type,
                         self.diet_line_view.application_type,
                         f"Application type {diet_line.application_type}"
                         " not correct")
        self.assertEqual(diet_line.description,
                         self.diet_line_view.description,
                         f"Food name {diet_line.description} not correct")

    def test_check_line_view_is_in_diet_view(self):
        """ A created line should appear in the view of the diet """

        self.assertIn(self.diet_line_view, self.diet_view.lines_views,
                     "Line not in the view")
