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

from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import mapped_column, validates
from carereport import Base

class EmptyNameError(ValueError):
    """ A patient must have a name """

    pass


class Patient(Base):

    __tablename__ = "patients"

    id = mapped_column(Integer, primary_key=True)
    surname = mapped_column(String(45), nullable=False)
    initials = mapped_column(String(10), nullable=False)
    birthdate = mapped_column(Date)
    sexe = mapped_column(String(1), nullable=True, server_default='')

    @validates("surname")
    def validate_name(self, key, surname):
        """ A name cannot be empty """

        if surname is None:
            raise EmptyNameError("Name cannot be empty")
        if surname == "":
            raise EmptyNameError("Name cannot be empty")
        return surname
