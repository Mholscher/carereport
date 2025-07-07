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
from carereport.views.scripts_diet import (CreateDiet, UpdateDiet)
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
        self.assertEqual(self.header.diet_view.start_date,
                         self.full_form.startDateEdit.date(),
                         "Start date not updated")
        self.assertEqual(self.header.diet_view.end_date,
                         self.full_form.endDateEdit.date(),
                         "End date not updated")

    def test_start_date_must_be_before_end(self):
        """ A diet must end after a start """

        CheckState = Qt.CheckState
        self.full_form.dietNameEdit.setText("Groentevrij")
        self.full_form.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.full_form.startDateEdit.setDate(date.today())
        with self.assertRaises(ValueError):
            self.full_form.endDateEdit.setDate(date.today()
                                               + timedelta(days=-3))
            self.header.update_diet_view()

    def test_no_start_or_end_date_for_permanent(self):
        """ Start and end date on the view are empty for a permanent diet """

        CheckState = Qt.CheckState
        self.full_form.dietNameEdit.setText("Vetarm")
        self.full_form.permanentCheckBox.setCheckState(CheckState.Checked)
        self.full_form.startDateEdit.setDate(date.today())
        self.full_form.endDateEdit.setDate(date.today() + timedelta(days=-3))
        self.header.update_diet_view()
        self.assertFalse(self.header.diet_view.start_date,
                         "Start date not None")
        self.assertFalse(self.header.diet_view.end_date,
                         "End date not None")

    @unittest.skip
    def test_create_diet_from_view(self):
        """ Create a diet from the view """

        CheckState = Qt.CheckState
        self.full_form.dietNameEdit.setText("Lactose belast")
        self.full_form.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.full_form.startDateEdit.setDate(date.today() + timedelta(days=4))
        self.full_form.endDateEdit.setDate(date.today() + timedelta(days=8))
        self.header.update_diet_view()
        self.header.update_diet()
        self.assertEqual(self.header.diet_view.diet_header.diet_name,
                         self.header.diet_view.diet_name,
                         "Name in diet not set")


class TestUpdateDietHeader(unittest.TestCase):

    def setUp(self):

        # self.diet_form = mainwindow.centralWidget().DietPagesWidget
        self.full_form = mainwindow.centralWidget()
        self.view = DietView(diet_name="Brooddieet",
                             permanent_diet=False,
                             start_date=date.today(),
                             end_date=date.today()+timedelta(days=15))

    def tearDown(self):

        pass

    def test_fill_header_from_view(self):
        """ Fill the header form from the diet view """

        update_diet = UpdateDiet(self.view, self.full_form)
        self.assertEqual(update_diet.pages_widget.diet_name,
                         self.view.diet_name,
                         "Name not filled")
        self.assertEqual(update_diet.pages_widget.start_date,
                         self.view.start_date,
                         "Start date not filled")
        self.assertEqual(update_diet.pages_widget.permanent_diet,
                         self.view.permanent_diet,
                         "Permanent incorrect")

    def test_fill_change_view(self):
        """ Change some fields, update the diet view """

        CheckState = Qt.CheckState
        update_diet = UpdateDiet(self.view, self.full_form)
        diet_form = mainwindow.centralWidget()
        diet_form.permanentCheckBox.setCheckState(CheckState.Unchecked)
        diet_form.startDateEdit.setDate(self.view.start_date
                                        - timedelta(days=2))
        diet_form.endDateEdit.setDate(self.view.end_date + timedelta(days=7))
        update_diet.update_diet_view()
        self.assertEqual(self.view.start_date,
                         diet_form.startDateEdit.date(),
                         "Start date not changed")
        self.assertEqual(self.view.end_date,
                         diet_form.endDateEdit.date(),
                         "End date not changed")

    def test_set_permanent_ignores_dates(self):
        """ Setting a diet to permanent should ignore date changes """

        CheckState = Qt.CheckState
        update_diet = UpdateDiet(self.view, self.full_form)
        diet_form = mainwindow.centralWidget()
        diet_form.permanentCheckBox.setCheckState(CheckState.Checked)
        diet_form.startDateEdit.setDate(self.view.start_date
                                        + timedelta(days=2))
        diet_form.endDateEdit.setDate(self.view.end_date + timedelta(days=7))
        update_diet.update_diet_view()
        self.assertNotEqual(self.view.start_date,
                            diet_form.startDateEdit.date(),
                            "Start date changed")
        self.assertNotEqual(self.view.end_date,
                            diet_form.endDateEdit.date(),
                            "End date changed")

    def test_start_date_earlier_than_end_date(self):
        """ The start date must be before the end date """

        CheckState = Qt.CheckState
        update_diet = UpdateDiet(self.view, self.full_form)
        diet_form = mainwindow.centralWidget()
        diet_form.permanentCheckBox.setCheckState(CheckState.Unchecked)
        diet_form.startDateEdit.setDate(self.view.start_date
                                        + timedelta(days=2))
        with self.assertRaises(ValueError):
            diet_form.endDateEdit.setDate(self.view.start_date)
            update_diet.update_diet_view()
