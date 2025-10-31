#    Copyright 2024 Menno Hölscher
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
""" The diet views contains classes used for the diets of
patients.

Diet views come in 2 parts, a header describing the "general nature" of
the diet ("sugarfree") and specific rules (lines) for different types
of food.

These views serve to marshall data between the windows of the system and
the model.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from ..models.medical import DietHeader, DietLines
from .patient_views import PatientView


class DietEndBeforeStart(ValueError):
    """ A diet's end date must be on or after start date """

    pass


@dataclass
class DietView():
    """ The view for a dietheader plus its lines.

    The :py:class:`DietHeader` appears exactly once, while there can be more
    lines in the header, each for a :py:class:`DietLine` of the diet.

        :id: The id of the header of this diet
        :diet_name: a name for the diet. It is not assumed to be unique, or
                        required, but making it unique helps communication
        :permanent_diet: Is this a permanent diet (like vegan)?
        :start_date: The date the patient started or must start this diet. Not
                        for permanent diets.
        :end_date: The date the patient can stop following this diet. Not
                       for permanent diets.
        :patient: The patient this diet is for.
        :diet_lines: The view for lines for the diet.

    """

    id: Optional[int] = None
    diet_name: str = ''
    permanent_diet: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    patient: Optional[PatientView] = None
    diet_header: Optional[DietHeader] = None

    @classmethod
    def create_from_diet(cls, diet):
        """ Create a new diet view from a diet header """

        diet_view = cls(id=diet.id,
                        diet_name=diet.diet_name,
                        permanent_diet=diet.permanent_diet,
                        start_date=diet.start_date,
                        end_date=diet.end_date,
                        patient=PatientView.from_patient(diet.patient),
                        diet_header=diet)
        return diet_view

    def __post_init__(self):
        """ Set the lines up; cannot do that the usual way """

        self.lines_views = []

    def to_diet(self):
        """ Create a diet from this view """

        return DietHeader(id=self.id,
                          diet_name=self.diet_name,
                          permanent_diet=self.permanent_diet,
                          start_date=self.start_date,
                          end_date=self.end_date,
                          patient=self.patient.patient)

    def update_diet(self):
        """ Update the diet from the changed data in the view """

        if self.diet_name != self.diet_header.diet_name:
            self.diet_header.diet_name = self.diet_name
        if self.permanent_diet != self.diet_header.permanent_diet:
            self.diet_header.permanent_diet = self.permanent_diet
        if self.start_date != self.diet_header.start_date:
            self.diet_header.start_date = self.start_date
        if self.end_date != self.diet_header.end_date:
            self.diet_header.end_date = self.end_date

    def lines(self):
        """ Create a list of diet line views for this header """
 
        line_views = []
        for diet_line in self.diet_header.diet_lines:
            line_views.append(DietLineView.create_from_diet_line(diet_line,
                                                                 self))
        return line_views

    def check_diet_dates(self):
        """ Check if the start and end dates are acceptable """

        if self.permanent_diet:
            return
        if self.end_date < self.start_date:
            raise DietEndBeforeStart("End date can not be before startdate")

    @staticmethod
    def diets_for_patient(patient_view):
        """ Create a list of diet views for a patient  """

        diet_views = []
        patient = patient_view.patient
        for diet in patient.diets:
            diet_views.append(DietView.create_from_diet(diet))
        return diet_views


@dataclass
class DietLineView():
    """ A single diet line view (rule) for a diet.

    Diet lines are lifestyle rules, belonging toa diet, modelled
    by a diet header. This the view for those lines.

        :id: the id for this diet line
        :food_name: The name of a type of food or food product this line
                        applies to.
        :application_type: how this rule is to be applied, like do not use.
        :description: An human readable explanation fo the rule.
        :diet_view: the view of the diet this is a line to
        :diet_line: The diet line this view is for

    """

    diet_view: DietView
    id: Optional[int] = None
    food_name: str = ""
    description: str = ""
    application_type: str = "Daily"
    diet_line: Optional[DietLines] = None

    @classmethod
    def create_from_diet_line(cls, diet_line, diet_view):
        """ Create a view for a diet line """

        return cls(diet_view=diet_view,
                   id=diet_line.id,
                   food_name=diet_line.food_name,
                   description=diet_line.description,
                   application_type=diet_line.application_type,
                   diet_line=diet_line)

    def __post_init__(self):

        self.diet_view.lines_views.append(self)

    def update_diet_line(self):
        """ Pass any changes to the view into the line """

        if self.food_name != self.diet_line.food_name:
            self.diet_line.food_name = self.food_name
        if self.description != self.diet_line.description:
            self.diet_line.description = self.description
        if self.application_type != self.diet_line.application_type:
            self.diet_line.application_type = self.application_type

    def to_diet_line(self, diet):
        """ Create a fresh diet line for a diet from this view """

        return DietLines(id=self.id,
                         food_name=self.food_name,
                         description=self.description,
                         application_type=self.application_type,
                         diet=diet)
