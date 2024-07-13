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
from carereport import (Base, session, validate_field_existance)
from carereport import Patient


class EndDateBeforeStartError(ValueError):
    """ The end date is before the start date """

    pass


class MedicationIsMandatoryError(ValueError):
    """ A medication cannot be empty """

    pass


class FrequencyMustBeANumber(ValueError):
    """ The frequency must be a positive number """

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

    @validates("frequency")
    def validate_frequency(self, key, frequency):
        """ Frequency must be an unsigned integer """

        if (not isinstance(frequency, int)
            or frequency < 1):
            raise FrequencyMustBeANumber("Frequency must be a positive number")
        return frequency

    @validates("frequency_type")
    def validate_frequncy_type(self, key, frequency_type):
        """ Frequency type must be filled """

        # if frequency_type is None or frequency_type == "":
        #     raise FrequencyMustHaveTypeError("No type supplied for frequency")
        return validate_field_existance(self, key, frequency_type,
                                        FrequencyMustHaveTypeError)


class ExaminationRequest(Base):
    """ An examination that has been requested for a patient.

    The request will have a description and a department to execute
    the request. The department will execute the request and create the
    examination result.

    If the department refuses the request, the reason for the refusal will
    be added to the request.
    """

    __tablename__ = "examrequest"

    id = mapped_column(Integer, primary_key=True)
    date_request = mapped_column(Date, default=date.today)
    examination_kind = mapped_column(String(128), nullable=False)
    examaning_department = mapped_column(String(56), nullable=False)
    requester_name = mapped_column(String(56), nullable=False)
    requester_department = mapped_column(String(56))
    date_execution = mapped_column(Date, nullable=True)
    request_refused = mapped_column(String(128))
    patient_id = mapped_column(ForeignKey("patients.id"), index=True)
    patient = relationship("Patient", back_populates="exam_requests")
