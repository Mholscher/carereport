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
from datetime import date, timedelta
import unittest
from PyQt6.QtCore import Qt
from carereport.views.care_app import mainwindow
from carereport.views.scripts_diet import CreateDiet
from carereport.views.diet_views import DietView


class TestCreateDietHeader(unittest.TestCase):

    def setUp(self):

        self.diet_form = mainwindow.centralWidget().DietPagesWidget
        self.full_form = mainwindow.centralWidget()
        self.header = CreateDiet(self.full_form)

    def tearDown(self):

        pass

    def test_created_header_has_view(self):
        """ Creating a header creates a diet header view """

        self.assertTrue(hasattr(self.header, "diet_view"),
                        "No attribute for diet header")
        self.assertEqual(type(self.header.diet_view),
                         DietView,
                         "Incorrect type for view")

    def test_update_header_view(self):
        """ Update the header view from the diet update window """

        CheckState = Qt.CheckState
        self.full_form.dietNameEdit.setText("Groente")
        self.full_form.permanentCheckBox.setCheckState(CheckState.Checked)
        self.header.update_diet_view()
        self.assertTrue(hasattr(self.header, "diet_view"),
                        "No header on diet")
        self.assertEqual(self.header.diet_view.diet_name,
                         self.full_form.dietNameEdit.text(),
                         "Diet name not filled")
        self.assertTrue(self.header.diet_view.permanent_diet,
                        "Diet not permanent")

    def test_update_dates_if_not_permanent(self):
        """ A non-permanent diet should update dates  """

        CheckState = Qt.CheckState
        self.full_form.dietNameEdit.setText("Arretjes cake")
        self.full_form.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.full_form.startDateEdit.setDate(date.today())
        self.full_form.endDateEdit.setDate(date.today() + timedelta(days=3))
        self.header.update_diet_view()
        self.assertEqual(self.header.start_date,
                         self.full_form.startDateEdit.date(),
                         "Start date not updated")
        self.assertEqual(self.header.end_date,
                         self.full_form.endDateEdit.date(),
                         "End date not updated")

    def test_start_date_must_be_before_end(self):
        """ A diet must end after a start """

        CheckState = Qt.CheckState
        self.full_form.dietNameEdit.setText("Groentevrij")
        self.full_form.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.full_form.startDateEdit.setDate(date.today())
        with self.assertRaises(ValueError):
            self.full_form.endDateEdit.setDate(date.today() + timedelta(days=-3))
            self.header.update_diet_view()
