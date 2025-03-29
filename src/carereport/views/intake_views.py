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
""" The intake views contains intake classes used for the intake of new
patients into the system. It serves to marshall data between the windows
of the system and the model for an intake.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
# from PyQt6.QtCore import pyqtSignal
from carereport import (app, Intake, Medication, ExaminationRequest)


class NoCurrentPatientError(BaseException):
    """ There must be a current patient for the requested operation """

    pass


@dataclass
class IntakeView():
    """ The class holds all data that can or should be produced for an intake
    of a patient.

    The intake may involve creating a new patient, that is
    taken care of by a separate script, there you can find the data you
    needed for a patient.

        :patient: The patient the intake was for; None means new patient
        :date_intake: The day this intake is being done. Default: today.
        :medication: Medication for the patient. Maybe previously prescribed or
                        newly prescribed
        :examinations: Examinations requested from the immediate intake

    """

    patient: Optional["PatientView"] = None
    date_intake: date = date.today()
    medication: list[Medication] = field(default_factory=list)
    examinations: list[ExaminationRequest] = field(default_factory=list)

    @classmethod
    def create_view_from_intake(cls, intake):
        """ Create a view from an intake in the database """

        if not hasattr(app, "current_patient_view"):
            raise NoCurrentPatientError("No current patient found")

        intake_view = cls(patient=app.current_patient_view)
        app.current_patient_view.current_intake = intake_view
        return intake_view

    def create_intake_from_view(self):
        """ Create an intake from this view """

        patient_model = app.current_patient_view.patient
        return Intake(patient=patient_model,
                      date_intake=self.date_intake)

