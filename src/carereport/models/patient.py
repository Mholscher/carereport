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
from sqlalchemy import (String, Date, Integer, Index, ForeignKey,
                        Index)
from sqlalchemy.orm import (mapped_column, validates, relationship,
                            Mapped)
from carereport import (Base, validate_field_existance)
from .medical import DietHeader

class EmptyNameError(ValueError):
    """ A patient must have a name """

    pass


class BirthdateMustBeInPastError(ValueError):
    """ A birth day cannot be in the future """

    pass


class SexInvalidError(ValueError):
    """ A sex must be in the valid sex dictionary """

    pass


class IntakeResultIsMandatoryError(ValueError):
    """ An intake must have a result """

    pass


class IntakeCannotBeInFutureError(ValueError):
    """ An intake cannot be in the future """

    pass


class Patient(Base):
    """ The class representing a pati4ent in care

    The patient is a class linked to be any medical entity in the system.
    It has but the least of conceivable attributes

    the attributes are:

        :surname: The surname of the patient
        :initials: The initials of the patient
        :birthdate: The day the patient was born
        :sex: An optional field to hold the sex of the patient

    """

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
    intakes:Mapped[List["Intake"]] =\
        relationship(back_populates="patient")
    diagnoses:Mapped[List["Diagnose"]] =\
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

    def get_diets(self, for_date=date.today()):
        """ Return the diet lines for the date for_date """

        return DietHeader.get_diets(self, for_date)


class Intake(Base):
    """ An intake has taken place. This is the result. 

    The intake is simply a human readable text. It is meant to tellwhat the end result was for the intake (think admitted, sent home, gave medication).

    Fields are

        :date_intake: The date the intake was done or completed
        :result: The human readable result of this intake

    """

    __tablename__ = "intakes"

    id = mapped_column(Integer, primary_key=True)
    date_intake = mapped_column(Date)
    result = mapped_column(String(256))
    results = relationship("IntakeResult", back_populates="intake")
    patient_id = mapped_column(ForeignKey("patients.id"), index=True)
    patient = relationship("Patient", back_populates="intakes")

    @validates("result")
    def validate_intake_result(self, key, result):
        """ Result of the intake is mandatory """

        return validate_field_existance(self, key, result,
                                        IntakeResultIsMandatoryError)

    @validates("date_intake")
    def validate_date_intake(self, key, date_intake):
        """ The date of an intake must be in the past """

        if date_intake > date.today():
            raise IntakeCannotBeInFutureError(f"{date_intake} is in future")
        return date_intake

    def add_result_for(self, link_type, link_key):
        """ Add a intake result for the type and key """

        intake_result = IntakeResult(link_type=link_type,
                                     link_key=link_key)
        self.results.append(intake_result)
        return


class IntakeResult(Base):
    """ Links to items created as a result of the intake.

    These links answer questions like "what medication was prescribed
    as a result of this intake?"
    """

    __tablename__ = "intakeresults"

    id = mapped_column(Integer, primary_key=True)
    link_type = mapped_column(String(10), nullable=False)
    link_key = mapped_column(Integer)
    intake_id = mapped_column(ForeignKey("intakes.id"), index=True)
    intake = relationship("Intake", back_populates="results")

    __table_args__=(Index("by_link", "link_type",
                          "link_key"),)
