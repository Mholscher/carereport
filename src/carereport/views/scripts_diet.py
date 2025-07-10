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
""" This module contains the script(s) to handle the user interface for diets.

The diets are input through two input widgets that ar switching between each
other. One holds a list of diets (the headers that is) and the other one
enables creation and maintenance of diets and rules within a diet.
"""
from datetime import date
from PyQt6.QtCore import QDate
from PyQt6.QtCore import QLocale as Loc
from carereport import app
from .diet_views import DietView
""" This module sets up diets. It takes care of creating new diets, updating
existing diets through diet views.
"""


class _DietChanges():
    """ This class contains shared functions for creating and updating  diet
    views from input."""

    def update_diet_view(self):
        """ Update the values in a diet view """

        self.diet_view.diet_name = self.full_form.dietNameEdit.text()
        self.diet_view.permanent_diet =\
            self.full_form.permanentCheckBox.isChecked()
        if self.diet_view.permanent_diet:
            self.diet_view.start_date = None
            self.diet_view.end_date = None
        else:
            self.diet_view.start_date = self.full_form.startDateEdit.date()
            if self.full_form.endDateEdit.date():
                self.diet_view.end_date = self.full_form.endDateEdit.date()
            if self.diet_view.start_date and self.diet_view.end_date:
                self.diet_view.check_diet_dates()


class CreateDiet(_DietChanges):
    """ Create a new diet, using the view for diets.

    The view holds one header and as many lines (rules for the patient) as
    applicable for this diet.

    An example is a sugar limited diet. The diet has a header saying "sugar
    limited"  and rules like "Do not put sugar in your tea and coffee" or
    "No caramel"
    """

    def __init__(self, full_form):

        full_form.DietPagesWidget.setCurrentIndex(1)
        self.diet_view = DietView()
        self.full_form = full_form

    def update_diet(self):
        """ At this point in the script the diet for the database is created.

        The event to be processed is to save the diet.
        """

        self.diet_view.to_diet()


class UpdateDiet(_DietChanges):
    """ Change the data on an existing diet.

    Existing diets can be shown and changed. Examples are when a diet is made
    permanent, when an end date diet is altered, or a typing error is fixed.
    """

    def __init__(self, diet_view, full_form):

        self.pages_widget = full_form.DietPagesWidget
        the_widget = self.pages_widget
        the_widget.diet_name = diet_view.diet_name
        the_widget.permanent_diet = diet_view.permanent_diet
        the_widget.start_date = diet_view.start_date
        the_widget.end_date = diet_view.end_date
        self.diet_view = diet_view
        self.full_form = full_form

    def update_diet():
        """ The data in the view is released into the diet """

        self.diet_view.update_diet()
