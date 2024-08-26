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

"""  This module has the basic partient data, like surname, birth date
and the like. It does not have medical data nor hospitalization info
"""

from datetime import date
from typing import List
from sqlalchemy import String, Date, Integer, Index
from sqlalchemy.orm import (mapped_column, validates, relationship,
                            Mapped)
from carereport import Base, validate_field_existance

class EmptyNameError(ValueError):
    """ A patient must have a name """

    pass


class BirthdateMustBeInPastError(ValueError):
    """ A birth day cannot be in the future """

    pass


class SexInvalidError(ValueError):
    """ A sex must be in the valid sex dictionary """

    pass


class Patient(Base):

    __tablename__ = "patients"

    id = mapped_column(Integer, primary_key=True)
    surname = mapped_column(String(45), nullable=False)
    initials = mapped_column(String(10), nullable=False)
    birthdate = mapped_column(Date)
    sex = mapped_column(String(1), nullable=True, server_default='')
    medication:Mapped[List["Medication"]] = relationship(back_populates="patient")
    exam_requests:Mapped[List["ExaminationRequest"]] =\
        relationship(back_populates="patient")
    diets:Mapped[List["DietHeader"]] =\
        relationship(back_populates="patient")


    __table_args__= (Index("byname", "surname"),
                     Index("bybirthdate", "birthdate"))

    valid_sex = {"F" : "female",
                 "M" : "male",
                 "X" : "non-binary",
                 " " : "unknown"}

    @validates("surname")
    def validate_name(self, key, surname):
        """ A name cannot be empty """

        return validate_field_existance(self, key, surname, EmptyNameError)

    @validates("birthdate")
    def validate_birthdate(self, key, birthdate):
        """ A birthdate must be in the past  """

        if birthdate > date.today():
            raise BirthdateMustBeInPastError(f"{birthdate} is not in the past")
        return birthdate

    @validates("sex")
    def validate_sex(self, key, sex):
        """ A birthdate must be in the past  """

        if sex not in self.valid_sex:
            raise SexInvalidError(f"{sex} is not in a valid sex")
        return sex

    def _current_diet(self, for_date):
        """ Return current diets as a list

        TODO: replace with a generator
        """
        return [diet_header for diet_header in self.diets
                if diet_header.permanent_diet
                or (diet_header.start_date <= for_date
                and (diet_header.end_date is None
                     or diet_header.end_date > for_date))]

    def get_diets(self, for_date=date.today()):
        """ Return the diet lines for the date for_date """

        diet_list = []
        for diet in self._current_diet(for_date):
            for line in diet.diet_lines:
                diet_list.append(line)
        return diet_list
