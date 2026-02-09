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
""" The patient views contains classes used for recording patient
data into the system. It serves to marshall data between the windows
of the system and the model for a patient.
"""

from dataclasses import dataclass
from datetime import date
from typing import (Optional, ClassVar)
from PyQt6.QtCore import QObject
from carereport import app, Patient  # , Medication, ExaminationRequest)
from .care_app import mainwindow
from .intake_views import IntakeView


class ChangingIdOfEntityError(ValueError):
    """ Do not change the id of a database entity from a view """

    pass


class SurnameCannotBeEmptyError(ValueError):
    """ Cannot create a patient without a surname """

    pass


class InitialsCannotBeEmptyError(ValueError):
    """ Cannot create a patient without initials """

    pass


class BirthdateInFutureError(ValueError):
    """ A birthdate cannot be in the future """

    pass


# class ChangePatientEmitter(QObject):
#     """ Class to be able to emit current patient change signal """
# 
#     newCurrentPatient = pyqtSignal()
# 
#     def __init__(self):
# 
#         QObject.__init__(self)
# 
#     def new_patient(self, new_patient):
#         """ Signal the setting of another patient as "current" """
# 
#         self.newCurrentPatient.emit(new_patient)


@dataclass
class PatientView():
    """ View class associated with the Patient class """

    id: Optional[int] = None
    surname: str = ""
    initials: str = ""
    birthdate: date = date(1990, 1, 1)
    sex: str = " "
    current_intake: IntakeView = None
    patient: Optional[Patient] = None
    # change_patient_emitter: ClassVar = ChangePatientEmitter()

    def to_patient(self):
        """ Create a patient in the model from this view """

        self.patient = Patient(id=self.id,
                               surname=self.surname,
                               initials=self.initials,
                               birthdate=self.birthdate,
                               sex=" " if self.sex is None else self.sex)
        self.set_current_patient()

    def update_patient(self):
        """ Update patient with data from this view """

        if self.id is not None and self.id != self.patient.id:
            raise ChangingIdOfEntityError("Programming error: "
                                          "Patient view is not for patient")
        if self.surname != self.patient.surname:
            self.patient.surname = self.surname
        if self.initials != self.patient.initials:
            self.patient.initials = self.initials
        if self.birthdate != self.patient.birthdate:
            self.patient.birthdate = self.birthdate
        if self.sex != self.patient.sex:
            self.patient.sex = " " if self.sex is None else self.sex
        self.set_current_patient()
        return self.patient

    @classmethod
    def from_patient(cls, patient):
        """ Create a view for the patient """

        return cls(id=patient.id,
                   surname=patient.surname,
                   initials=patient.initials,
                   birthdate=patient.birthdate,
                   sex=patient.sex,
                   patient=patient)

    @classmethod
    def from_patient_list(cls, patient_list):
        """ Create a list of patient views from a list of patients """

        return [cls.from_patient(patient) for patient in patient_list]

    @classmethod
    def get_patientlist_for_params(cls, search_params):
        """ Get a list of patients and create patient views  """

        return cls.from_patient_list(Patient.patient_search(search_params))

    def set_current_patient(self):
        """ The current patient for the application is set to this view """

        mainwindow.set_new_current_patient(self)
