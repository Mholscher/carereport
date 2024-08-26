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

""" This module holds the definitions for the medical data.

The medical data is what the diagnose and the treatment are and how the
medicals come to a decision what treatment to apply. It is e.g. concerned
with

    #. medication
    #. requested examinations
    #. results from said examinations
    #. the diagnose which was made
    #. the treatment selected for the diagnose

Things related to non-medical care (ward, diet) are not defined 
in this module.
"""

from datetime import date
from sqlalchemy import (String, Date, Integer, text, ForeignKey, Index,
                        select, event, Boolean)
from sqlalchemy.orm import (mapped_column, validates, relationship)
from carereport import (Base, session, validate_field_existance)


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


class ExaminationKindIsMandatoryError(ValueError):
    """ The examination kind must be present """

    pass


class ExamaningDepartmentIsMandatoryError(ValueError):
    """ There must be a department to execute the request """

    pass


class ExecutionBeforeRequestError(ValueError):
    """ Execution cannot be before request """

    pass


class RequesterIsMandatoryError(ValueError):
    """ Every request must have a requester """

    pass


class ExecutedCannotBeRefusedError(ValueError):
    """ An executed request cannot be refused """

    pass


class ExecutorMandatoryInResultError(ValueError):
    """ Executor is mandatory in examination result """

    pass


class ResultMustBeForRequestError(ValueError):
    """ An examination result must be in response to a request """

    pass


class PermanentDietWithStartDateError(ValueError):
    """ A permanent error cannot have start date """

    pass

class DietLinesFoodNameMissingError(ValueError):
    """ A name for a diet line is mandatory """

    pass


class DietLineNeedsHeaderError(ValueError):
    """ A dietline can only exist coupled to a header """

    pass


class DietLinesApplicationMissingError(ValueError):
    """ A diet line must have a way to apply it """

    pass


class DietHeaderMustHaveLinesError(AttributeError):
    """ A diet must contain rules """

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
    frequency_type = mapped_column(String(17), server_default="per dag",
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
    result = relationship("ExaminationResult", back_populates="request")

    __table_args__ = (Index("bydepdate", "examaning_department",
          "date_request"),)

    @validates("examination_kind")
    def validate_examination_kind(self, key, examination_kind):
        """ Examination kind must have a value """

        return validate_field_existance(self, key, examination_kind,
                                        ExaminationKindIsMandatoryError)

    @validates("examaning_department")
    def validate_examaning_department(self, key, department):
        """ Examination kind must have a value """

        return validate_field_existance(self, key, department,
                                        ExamaningDepartmentIsMandatoryError)

    @validates("requester_name")
    def validate_requester_name(self, key, requester_name):
        """ Examination kind must have a value """

        return validate_field_existance(self, key, requester_name,
                                        RequesterIsMandatoryError)

    @validates("date_execution")
    def validate_date_execution(self, key, date_execution):
        """ Date of execution must be empty or after date of request """

        if date_execution is None:
            return date_execution
        if date_execution < self.date_request:
            raise ExecutionBeforeRequestError("execution cannot"
                                             " be before request")
        return date_execution

    @validates("request_refused")
    def validate_request_refused(self, key, request_refused):
        """ A request can only be refused if it is not executed """

        if request_refused and self.date_execution:
            raise ExecutedCannotBeRefusedError("You cannot refuse" 
                                                " an executed request")
        return request_refused

    @staticmethod
    def open_requests_for_patient(patient):
        """ List open examination requests for a patient """

        current_date = date.today()
        return [request for request in patient.exam_requests
                if (not request.date_execution
                or request.date_execution >= current_date)
                and not request.request_refused]

    @staticmethod
    def requests_for_department(department):
        """ List outstanding requests per department. 

        The department variable may be part (substring) of a department
        name.
        """

        selection = select(ExaminationRequest).where(
            ExaminationRequest.examaning_department.like(
            "%" + department + "%")).order_by(
                ExaminationRequest.date_request.asc())
        return list(session.execute(selection))


class ExaminationResult(Base):
    """ The result of an examination

    This is the result of an examination requested by a 
    different department. There will be a request for it, and the 
    result will link to this request.
    """

    __tablename__ = "examresult"

    id = mapped_column(Integer, primary_key=True)
    examination_executor = mapped_column(String(56), nullable=False)
    examination_result = mapped_column(String(256))
    request_id = mapped_column(ForeignKey("examrequest.id"), index=True)
    request = relationship("ExaminationRequest", back_populates="result")

    @validates("examination_executor")
    def validate_executor(self, key, executor):
        """ The executor is mandatory for a result """

        return validate_field_existance(self, key, executor,
                                        ExecutorMandatoryInResultError)

    def is_request_set(self, session):
        """ A result must have a request """

        if not self.request:
            raise ResultMustBeForRequestError(
                "Examination result must have request")


class DietHeader(Base):
    """ The general data belonging to a diet

    Diets consist of a general header (this object) and a list
    of "prescriptions" that form the rules of the diet.

    Diet is an atypical item in the system. It may be a medical item 
    (this patient should have a sugar limited diet for diabetes) or
    a lifestyle/care item (I am vegan). We make no difference.
    """

    __tablename__ = "dietheader"

    id = mapped_column(Integer, primary_key=True)
    diet_name = mapped_column(String(56), nullable=False)
    permanent_diet = mapped_column(Boolean, default=False)
    start_date = mapped_column(Date, nullable=True)
    end_date = mapped_column(Date, nullable=True)
    diet_lines = relationship("DietLines", back_populates="diet")
    patient_id = mapped_column(ForeignKey("patients.id"), index=True)
    patient = relationship("Patient", back_populates="diets")
 
    @validates("start_date")
    def validate_start_date(self, key, start_date):
        """ A start date is only permitted on a temporary diet """

        if start_date and self.permanent_diet:
            raise PermanentDietWithStartDateError("Start date not valid on"
                                                  " permanent diet")
        return start_date

    @validates("end_date")
    def validate_end_date(self, key, end_date):
        """ A start date is only permitted on a temporary diet """

        if end_date and self.permanent_diet:
            raise PermanentDietWithStartDateError("End date not valid on"
                                                  " permanent diet")
        return end_date

    @validates("permanent_diet")
    def validate_diet_is_permanent(self, key, permanent_diet):
        """ No permanent diet can have start/end date """
        if permanent_diet and (self.start_date or self.end_date):
            raise PermanentDietWithStartDateError("Cannot make diet"
                                                  " permanent with start or"
                                                  " end date")
        return permanent_diet

    def has_lines(self):
        """ Check if this header has at least one line attached """

        if len(self.diet_lines) == 0:
            raise DietHeaderMustHaveLinesError(f"Diet {self.diet_name}" 
                                               f"must have lines")
        return True

    @staticmethod
    def _current_diet(patient, for_date):
        """ Return current diets for patient as a list

        TODO: replace with a generator
        """
        return [diet_header for diet_header in patient.diets
                if diet_header.permanent_diet
                or (diet_header.start_date <= for_date
                and (diet_header.end_date is None
                     or diet_header.end_date > for_date))]

    @staticmethod
    def get_diets(patient, for_date):
        """ Return the diet lines for patient for the date for_date """

        diet_list = []
        for diet in DietHeader._current_diet(patient, for_date):
            for line in diet.diet_lines:
                diet_list.append(line)
        return diet_list


class DietLines(Base):
    """ Instructions for individual elements of a diet 

    Each line contains a rule to be considered for a diet.
    Think of "Patient should not have any sugar"
    The ensemble of lines plus a DietHeader make up the diet
    """

    __tablename__ = "dietline"

    id = mapped_column(Integer, primary_key=True)
    food_name = mapped_column(String(56), nullable=False)
    application_type = mapped_column(String(56), nullable=False)
    description = mapped_column(String(256))
    diet_id = mapped_column(ForeignKey("dietheader.id"), index=True)
    diet = relationship("DietHeader", back_populates="diet_lines")

    @validates("food_name")
    def validate_food_name(self, key, food_name):
        """ A food name is mandatory """

        return validate_field_existance(self, key, food_name,
                                        DietLinesFoodNameMissingError)

    @validates("application_type")
    def validate_application(self, key, application_type):
        """ The application type is mandatory """

        return validate_field_existance(self, key, application_type,
                                        DietLinesApplicationMissingError)

    @validates("diet")
    def validate_diet(self, key, diet):
        """ A food name is mandatory """

        return validate_field_existance(self, key, diet,
                                        DietLineNeedsHeaderError)



@event.listens_for(session, "before_flush")
def before_flush(session, flush_context, instances):
    """ Execute entity level checks before saving """

    for instance in session.dirty | session.new:
        if isinstance(instance, ExaminationResult):
            instance.is_request_set(session)
        if isinstance(instance, DietHeader):
            instance.has_lines()
