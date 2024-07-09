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

from datetime import date
from sqlalchemy import (String, Date, Integer, text, ForeignKey, Index,
                        select)
from sqlalchemy.orm import (mapped_column, validates, relationship)
from carereport import Base, session
from carereport import Patient


class EndDateBeforeStartError(ValueError):
    """ The end date is before the start date """

    pass


class MedicationIsMandatoryError(ValueError):
    """ A medication cannot be empty """

    pass


class FrequencyMustHaveTypeError(ValueError):
    """ We should know what the frequency stands for """

    pass


class Medication(Base):
    """ Medication is one medication a patient is or was using.

    This is not a trigger to contact the pharmacist to deliver the medication,
    it is simply a medication prescribed.
    """

    __tablename__ = "medication"

    id = mapped_column(Integer, primary_key=True)
    medication = mapped_column(String(128))
    frequency = mapped_column(Integer, server_default="1")
    frequency_type = mapped_column(String(17), server_default="daily",
                                   nullable=False)
    start_date = mapped_column(Date, server_default=text('CURRENT_DATE()'))
    end_date = mapped_column(Date, nullable=True)
    patient_id = mapped_column(ForeignKey("patients.id"), index=True)
    patient = relationship("Patient", back_populates="medication")

    @classmethod
    def medication_for_patient(cls, patient):
        """ Return current medication for a patient """

        # print(patient.medication)
        return [medication for medication in patient.medication
                if medication.end_date is None 
                or medication.end_date >= date.today()]
        
    @validates("start_date")
    def validate_start_date(self, key, start_date):
        """ Validate that the start date is before the end date """
        
        if not self.end_date:
            return start_date
        if start_date >= self.end_date:
            raise EndDateBeforeStartError(f"Start date {start_date} is "
                                          f"after/equal end ({self.end_date})")
        return start_date

    @validates("end_date")
    def validate_end_date(self, key, end_date):
        """ Validate that the end date is after the start date """

        if not self.start_date:
            return end_date
        if end_date <= self.start_date:
            raise EndDateBeforeStartError(f"End date {end_date} is "
                                          f"before start ({self.start_date})")
        return end_date

    @validates("medication")
    def validate_medication(self, key, medication):
        """ Medication must be filled """

        if medication is None or medication == "":
            raise MedicationIsMandatoryError("A medication must be supplied")
        return medication

    @validates("frequency_type")
    def validate_frequncy_type(self, key, frequency_type):
        """ Frequency type must be filled """

        if frequency_type is None or frequency_type == "":
            raise FrequencyMustHaveTypeError("No type supplied for frequency")
        return frequency_type
