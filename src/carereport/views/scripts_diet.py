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
from .diet_views import DietView


class CreateDiet():

    def __init__(self, full_form):

        full_form.DietPagesWidget.setCurrentIndex(1)
        self.diet_view = DietView()
        self.full_form = full_form

    def update_diet_view(self):
        """ Update the values in a diet view """

        self.diet_view.diet_name = self.full_form.dietNameEdit.text()
        self.diet_view.permanent_diet =\
            self.full_form.permanentCheckBox.isChecked()
        self.start_date = self.full_form.startDateEdit.date()
        if self.full_form.endDateEdit.date():
            self.end_date = self.full_form.endDateEdit.date()
