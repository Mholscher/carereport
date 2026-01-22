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
from PyQt6.QtCore import (Qt)
from PyQt6.QtWidgets import QTableWidgetSelectionRange
from carereport import (Patient, DietHeader, DietLines)
from carereport.views.care_app import mainwindow
from carereport.views.patient_views import (PatientView)
# from carereport.views.dietheader import Ui_DietHeaderWidget
from carereport.views.scripts_diet import (CreateDiet, UpdateDiet,
                                           UpdateDietLines, DietListWidget)
from carereport.views.diet_views import (DietView, DietLineView)


class TestCreateDietHeader(unittest.TestCase):

    def setUp(self):

        self.full_form = mainwindow.centralWidget()
        self.diet = CreateDiet(DietView())

    def tearDown(self):

        pass

    def test_created_header_has_view(self):
        """ Creating a header creates a diet header view """

        self.assertTrue(hasattr(self.diet, "diet_view"),
                        "No attribute for diet header")
        self.assertEqual(type(self.diet.diet_view),
                         DietView,
                         "Incorrect type for view")

    def test_update_header_view(self):
        """ Update the header view from the diet update window """

        CheckState = Qt.CheckState
        self.diet.dietNameEdit.setText("Groente")
        self.diet.permanentCheckBox.setCheckState(CheckState.Checked)
        self.diet.update_view()
        self.assertTrue(hasattr(self.diet, "diet_view"),
                        "No header on diet")
        self.assertEqual(self.diet.diet_view.diet_name,
                         self.diet.dietNameEdit.text(),
                         "Diet name not filled")
        self.assertTrue(self.diet.diet_view.permanent_diet,
                        "Diet not permanent")

    @unittest.skip("Cannot make test work with PyQt")
    def test_update_dates_if_not_permanent(self):
        """ A non-permanent diet should update dates  """

        CheckState = Qt.CheckState
        self.diet.show()
        # import pdb; pdb.set_trace()
        self.diet.dietNameEdit.setFocus()
        self.diet.dietNameEdit.setText("Arretjes cake")
        self.diet.permanentCheckBox.setFocus()
        self.diet.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.diet.startDateEdit.setFocus()
        self.diet.startDateEdit.setDate(date.today())
        self.diet.endDateEdit.setFocus()
        self.diet.endDateEdit.setDate(date.today() + timedelta(days=3))
        self.diet.dietNameEdit.setFocus()
        # self.diet.update_view()
        self.assertEqual(self.diet.diet_view.start_date,
                         self.diet.startDateEdit.date(),
                         "Start date not updated")
        self.assertEqual(self.diet.diet_view.end_date,
                         self.diet.endDateEdit.date(),
                         "End date not updated")
        self.assertIsInstance(self.diet.diet_view.start_date, date,
                              "Start date incorrect type")
        self.assertIsInstance(self.diet.diet_view.end_date, date,
                              "End date incorrect type")

    def test_start_date_must_be_before_end(self):
        """ A diet must end after a start """

        CheckState = Qt.CheckState
        self.diet.dietNameEdit.setText("Groentevrij")
        self.diet.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.diet.startDateEdit.setDate(date.today())
        with self.assertRaises(ValueError):
            self.diet.endDateEdit.setDate(date.today()
                                          + timedelta(days=-3))
            self.diet.update_view()

    def test_no_start_or_end_date_for_permanent(self):
        """ Start and end date on the view are empty for a permanent diet """

        CheckState = Qt.CheckState
        self.diet.dietNameEdit.setText("Vetarm")
        self.diet.permanentCheckBox.setCheckState(CheckState.Checked)
        self.diet.startDateEdit.setDate(date.today())
        self.diet.endDateEdit.setDate(date.today() + timedelta(days=-3))
        self.diet.update_view()
        self.assertFalse(self.diet.diet_view.start_date,
                         "Start date not None")
        self.assertFalse(self.diet.diet_view.end_date,
                         "End date not None")

    @unittest.skip
    def test_create_diet_from_view(self):
        """ Create a diet from the view """

        CheckState = Qt.CheckState
        self.diet.dietNameEdit.setText("Lactose belast")
        self.diet.permanentCheckBox.setCheckState(CheckState.Unchecked)
        self.diet.startDateEdit.setDate(date.today() + timedelta(days=4))
        self.diet.endDateEdit.setDate(date.today() + timedelta(days=8))
        self.diet.update_view()
        self.diet.update_diet()
        self.assertEqual(self.diet.diet_view.diet_header.diet_name,
                         self.diet.diet_view.diet_name,
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

        update_diet = UpdateDiet(self.view)
        self.assertEqual(update_diet.dietNameEdit.text(),
                         self.view.diet_name,
                         "Name not filled")
        self.assertEqual(update_diet.startDateEdit.date(),
                         self.view.start_date,
                         "Start date not filled")
        self.assertEqual(update_diet.permanentCheckBox.isChecked(),
                         self.view.permanent_diet,
                         "Permanent incorrect")

    def test_fill_change_view(self):
        """ Change some fields, update the diet view """

        CheckState = Qt.CheckState
        update_diet = UpdateDiet(self.view)
        update_diet.permanentCheckBox.setCheckState(CheckState.Unchecked)
        update_diet.startDateEdit.setDate(self.view.start_date
                                          - timedelta(days=2))
        update_diet.endDateEdit.setDate(self.view.end_date + timedelta(days=7))
        update_diet.update_view()
        self.assertEqual(self.view.start_date,
                         update_diet.startDateEdit.date(),
                         "Start date not changed")
        self.assertEqual(self.view.end_date,
                         update_diet.endDateEdit.date(),
                         "End date not changed")
        self.assertIsInstance(self.view.start_date, date,
                              "Start date incorrect type")
        self.assertIsInstance(self.view.end_date, date,
                              "End date incorrect type")

    def test_set_permanent_ignores_dates(self):
        """ Setting a diet to permanent should ignore date changes """

        CheckState = Qt.CheckState
        update_diet = UpdateDiet(self.view)
        update_diet.permanentCheckBox.setCheckState(CheckState.Checked)
        update_diet.startDateEdit.setDate(self.view.start_date
                                          + timedelta(days=2))
        update_diet.endDateEdit.setDate(self.view.end_date + timedelta(days=7))
        update_diet.update_view()
        self.assertNotEqual(self.view.start_date,
                            update_diet.startDateEdit.date(),
                            "Start date changed")
        self.assertNotEqual(self.view.end_date,
                            update_diet.endDateEdit.date(),
                            "End date changed")

    def test_start_date_earlier_than_end_date(self):
        """ The start date must be before the end date """

        CheckState = Qt.CheckState
        update_diet = UpdateDiet(self.view)
        update_diet.permanentCheckBox.setCheckState(CheckState.Unchecked)
        update_diet.startDateEdit.setDate(self.view.start_date
                                          + timedelta(days=2))
        with self.assertRaises(ValueError):
            update_diet.endDateEdit.setDate(self.view.start_date)
            update_diet.update_view()

    def test_end_date_can_be_high_date(self):
        """ The end date may be none """

        self.view.end_date = date(9999, 12, 31)
        update_diet = UpdateDiet(self.view)
        self.assertEqual(update_diet.endDateEdit.date(),
                         date(9999, 12, 31),
                         "End date is not high date")


class TestDietLineView(unittest.TestCase):

    def setUp(self):

        self.diet_view = DietView(diet_name="The actual diet",
                                  permanent_diet=False,
                                  start_date=date.today(),
                                  end_date=date.today()+timedelta(days=15))

    def tearDown(self):

        pass

    def test_create_diet_line_form(self):
        """ Create an diet line for a diet view """

        line = DietLineView(food_name="Cabbage",
                            description="You can eat this as you like",
                            application_type="irregularly",
                            diet_view=self.diet_view)
        diet_form = UpdateDietLines(self.diet_view)
        self.assertEqual(line.food_name,
                         diet_form.dietLineTable.item(0, 0).text(),
                         "Food name not correctly filled for line")

    def test_more_diet_lines(self):
        """ More than one line is inserted correctly """

        line1 = DietLineView(food_name="Potato",
                             description="You can eat this as you like",
                             application_type="often",
                             diet_view=self.diet_view)
        line2 = DietLineView(food_name="Mushroom",
                             description="You can eat this, when you"
                             " know it is not poisonous",
                             application_type="as you like",
                             diet_view=self.diet_view)
        diet_form = UpdateDietLines(self.diet_view)
        diet_form.show()
        self.assertEqual(diet_form.dietLineTable.rowCount(), 2,
                         "Incorrect number of lines:"
                         + str(diet_form.dietLineTable.rowCount()))
        self.assertEqual(diet_form.dietLineTable.item(1, 0).text(),
                         line2.food_name,
                         "Text not correct in table")
        self.assertEqual(diet_form.dietLineTable.item(0, 0).text(),
                         line1.food_name,
                         "Text not correct in table")

    def test_diet_lines_dialog_name(self):
        """ The diet line dialog should be named after the diet """

        diet_form = UpdateDietLines(self.diet_view)
        self.assertTrue(diet_form.windowTitle().startswith(self.diet_view.diet_name),
                        "Dialog title not starting with diet name")

    def test_create_line_unselects_previous(self):
        """ If you create a line while one is selected, unselect previous """

        diet_changes = UpdateDietLines(self.diet_view)
        row_count = diet_changes.dietLineTable.rowCount()
        self.assertEqual(row_count, 0,
                         f"Row count incorrect: {row_count}")
        diet_changes.insert_new_line()
        self.assertEqual(row_count, 0,
                         f"Row count incorrect: {row_count}")
        current_selections = diet_changes.dietLineTable.selectedRanges()
        self.assertEqual(len(current_selections), 1,
                         f"Wrong no of selections: {len(current_selections)}")
        self.assertEqual(current_selections[0].topRow(),
                         current_selections[0].bottomRow(),
                         "More than one row in selection")
        diet_changes.dietLineTable.insertRow(diet_changes.dietLineTable.rowCount())
        current_selections = diet_changes.dietLineTable.selectedRanges()
        self.assertEqual(len(current_selections), 1,
                         f"Wrong no of selections: {len(current_selections)}")
        first_range = diet_changes.dietLineTable.selectedRanges()[0]
        self.assertEqual(first_range.bottomRow(),
                         first_range.topRow(),
                         "More than one row in selection")


class TestDietChangeLines(unittest.TestCase):

    def setUp(self):

        self.diet_view = DietView(diet_name="Diet to change",
                                  permanent_diet=True,
                                  start_date=date.today(),
                                  end_date=date.today()+timedelta(days=15))

        self.diet_line1 = DietLineView(food_name="Vet vlees",
                                       application_type="minder dan 3x per "
                                       "week",
                                       description="Vet vlees is niet "
                                       "verboden, maar met is wel af te raden"
                                       " vaak te eten.",
                                       diet_view=self.diet_view)
        self.diet_line2 = DietLineView(food_name="Groente",
                                       application_type="minstens 250 gram "
                                       "dagelijks",
                                       description="Lekker en gezond!",
                                       diet_view=self.diet_view)
        self.update_dialog = UpdateDietLines(self.diet_view)

    def tearDown(self):

        pass

    def test_dialog_title_starts_with_diet_name(self):
        """ The update dialog has a title starting with diet name """

        title = self.diet_view.diet_name +\
            self.update_dialog.windowTitle()
        self.assertEqual(title[0:14], self.diet_view.diet_name,
                         "Title does not start with diet name")

    def test_select_line_fills_fields(self):
        """ Selecting a line in the table fills the fields with data """

        the_dialog = self.update_dialog
        range_line_2 = QTableWidgetSelectionRange(1, 0, 1, 1)
        the_dialog.dietLineTable.setRangeSelected(range_line_2, True)
        self.assertEqual(the_dialog.FoodNameEdit.text(),
                         the_dialog.dietLineTable.item(1, 0).text(),
                         "Food name not filled correctly")
        self.assertEqual(self.diet_line2.description,
                         the_dialog.DescriptionEdit.toPlainText(),
                         "Description not filled")

    def test_unselect_line_clears_fields(self):
        """ Unselecting a line in the table clears the fields """

        the_dialog = self.update_dialog
        range_line_2 = QTableWidgetSelectionRange(0, 0, 0, 1)
        the_dialog.dietLineTable.setRangeSelected(range_line_2, True)
        self.assertEqual(the_dialog.FoodNameEdit.text(),
                         the_dialog.dietLineTable.item(0, 0).text(),
                         "Food name not filled correctly")
        the_dialog.dietLineTable.setRangeSelected(range_line_2, False)
        self.assertEqual(the_dialog.FoodNameEdit.text(), "",
                         "Food name not cleared")
        self.assertEqual(the_dialog.DescriptionEdit.toPlainText(), "",
                         "Description not filled")

    def test_updates_to_view(self):
        """ Updates to field application type are passed to view """

        the_dialog = self.update_dialog
        range_line_2 = QTableWidgetSelectionRange(1, 0, 1, 1)
        the_dialog.dietLineTable.setRangeSelected(range_line_2, True)
        the_dialog.ApplicationTypeEdit.setText("dagelijks 250 gram")
        the_dialog.ApplicationTypeEdit.editingFinished.emit()
        the_dialog.dietLineTable.setRangeSelected(range_line_2, False)
        self.assertEqual(self.diet_line2.application_type,
                         "dagelijks 250 gram",
                         "Application type not filled correctly")

    def test_update_view_for_name(self):
        """ Updates to field food name are passed to view """

        the_dialog = self.update_dialog
        range_line_2 = QTableWidgetSelectionRange(1, 0, 1, 1)
        the_dialog.dietLineTable.setRangeSelected(range_line_2, True)
        the_dialog.FoodNameEdit.setText("Zaden en knollen")
        the_dialog.FoodNameEdit.editingFinished.emit()
        the_dialog.dietLineTable.setRangeSelected(range_line_2, False)
        self.assertEqual(self.diet_line2.food_name,
                         "Zaden en knollen",
                         "Food name not filled correctly")

    # @unittest.skip
    def test_update_view_for_description(self):
        """  Updates to field description are passed to the view """

        the_dialog = self.update_dialog
        # print("DescriptionEdit heeft type", type(the_dialog.DescriptionEdit))
        range_line_2 = QTableWidgetSelectionRange(1, 0, 1, 1)
        the_dialog.dietLineTable.setRangeSelected(range_line_2, True)
        the_dialog.show()
        the_dialog.DescriptionEdit.setFocus()
        the_dialog.DescriptionEdit.setPlainText("Dit is de nieuwe tekst")
        the_dialog.ApplicationTypeEdit.setFocus()
        the_dialog.dietLineTable.setRangeSelected(range_line_2, False)
        the_dialog.close()
        self.assertEqual(self.diet_line2.description,
                         "Dit is de nieuwe tekst",
                         "Description not filled correctly")

    def test_new_diet_line_inserts_row(self):
        """ Inserting a new row makes it appear in the table """

        the_dialog = self.update_dialog
        old_row_count = the_dialog.dietLineTable.rowCount()
        the_dialog.insert_new_line()
        self.assertEqual(the_dialog.dietLineTable.rowCount(),
                         old_row_count + 1,
                         "No row added to table")

    def test_adding_line_clears_inputs(self):
        """ Inserting a new diet line empties the input fields """

        the_dialog = self.update_dialog
        range_line_2 = QTableWidgetSelectionRange(1, 0, 1, 1)
        the_dialog.dietLineTable.setRangeSelected(range_line_2, True)
        # Make false positives less likely
        self.assertNotEqual(the_dialog.FoodNameEdit.text(),
                            "",
                            "Food name empty")
        the_dialog.insert_new_line()
        self.assertEqual(the_dialog.FoodNameEdit.text(),
                         "",
                         "Food name not empty")

    def test_each_line_unique_name(self):
        """ Each line in the test table must have a different food name """

        the_dialog = self.update_dialog
        self.assertNotEqual(the_dialog.dietLineTable.item(0, 0).text(),
                            the_dialog.dietLineTable.item(1, 0).text(),
                            "Row names equal!")

    def test_new_line_selected(self):
        """ A line just added is selected """

        the_dialog = self.update_dialog
        # for row in range(0, the_dialog.dietLineTable.rowCount()):
        #     print("Food name:", the_dialog.dietLineTable.item(row, 0).text())
        the_dialog.insert_new_line()
        # for row_nr in range(0, 3):
        #     print(row_nr, the_dialog.dietLineTable.item(row_nr, 0).text())
        # print("Row count:", the_dialog.dietLineTable.rowCount())
        self.assertIn(the_dialog.dietLineTable.item(
                          the_dialog.dietLineTable.rowCount() - 1, 0),
                      the_dialog.dietLineTable.selectedItems(),
                      "Food name edit not selected")


class TestDietHeaderWidgetList(unittest.TestCase):

    def setUp(self):

        self.patient1 = Patient(surname="Hakkebaart",
                                initials="J.F.Q.",
                                birthdate=date(1987, 6, 12),
                                sex="F")
        self.patient1_view = PatientView.from_patient(self.patient1)
        self.diet1 = DietHeader(diet_name="Glutenvrij",
                                permanent_diet=False,
                                start_date=date.today() - timedelta(days=250),
                                end_date=None,
                                patient=self.patient1)
        self.diet1_view = DietView.create_from_diet(self.diet1)
        self.dietline1_1 = DietLines(food_name="Brood",
                                     application_type="Nooit",
                                     description="Brood is gemaakt van "
                                     "tarwe, daar zit gluten in. "
                                     "Glutenvrij brood is geen brood, maar "
                                     "wel een vervanger",
                                     diet=self.diet1)
        self.dietline1_2 = DietLines(food_name="Pasta",
                                     application_type="Let op",
                                     description="De meeste pasta is gemaakt"
                                     " met tarwe, daar zit gluten in.",
                                     diet=self.diet1)

        self.diet2 = DietHeader(diet_name="Groente",
                                permanent_diet=False,
                                start_date=date.today() - timedelta(days=210),
                                end_date=None,
                                patient=self.patient1)
        self.diet2_view = DietView.create_from_diet(self.diet2)
        self.dietline2_1 = DietLines(food_name="Runderworst",
                                     application_type="Nooit",
                                     description="Runderworst is geen "
                                     "groente ",
                                     diet=self.diet2)
        self.dietline2_2 = DietLines(food_name="Pasta",
                                     application_type="Let op",
                                     description="De meeste pasta is gemaakt"
                                     "met tarwe, ook al geen groente",
                                     diet=self.diet2)

    def tearDown(self):

        pass

    def test_create_diet_tabs(self):
        """ Create a diet tab for a patient """

        diet_tab = DietListWidget(self.patient1_view)
        self.assertEqual(mainwindow.centralWidget().verticalLayoutDiet.count(),
                         2,
                         "Wrong no of items:"
                         f"{mainwindow.centralWidget().verticalLayoutDiet.count()}")
        layout = mainwindow.centralWidget().scrollAreaWidgetContents
        diet_views_from_interface = []
        for child in layout.children():
            if isinstance(child, UpdateDiet):
                diet_views_from_interface.append(child.diet_view)
        self.assertIn(self.diet1_view,
                      diet_views_from_interface,
                      "diet1_view not in group")
        self.assertIn(self.diet2_view,
                      diet_views_from_interface,
                      "diet2_view not in group")

    def test_open_line_dialog(self):
        """ Open the update lines dialog from a widget """

        diet_tab = DietListWidget(self.patient1_view)
        layout = mainwindow.centralWidget().scrollAreaWidgetContents
        diet_widgets_from_interface = []
        for child in layout.children():
            if isinstance(child, UpdateDiet):
                diet_widgets_from_interface.append(child)
        view0 = diet_widgets_from_interface[0]
        view0.changeLinesButton.click()
        self.assertIn(view0.lines_dialog, view0.children())

    def test_line_dialog_filled_correctly(self):
        """ The line dialog must be filled correctly """

        diet_tab = DietListWidget(self.patient1_view)
        layout = mainwindow.centralWidget().scrollAreaWidgetContents
        diet_widgets_from_interface = []
        for child in layout.children():
            if isinstance(child, UpdateDiet):
                diet_widgets_from_interface.append(child)
        view0 = diet_widgets_from_interface[0]
        view0.changeLinesButton.click()
        range_line = QTableWidgetSelectionRange(1, 0, 1, 1)
        view0.lines_dialog.dietLineTable.setRangeSelected(range_line, True)
        # print(view0.lines_dialog.dietLineTable.lines_views)
        self.assertIn(view0.lines_dialog.DescriptionEdit.toPlainText(),
                      [self.dietline1_1.description,
                       self.dietline1_2.description,
                       self.dietline2_2.description,
                       self.dietline2_1.description],
                      "Description not from lines")
