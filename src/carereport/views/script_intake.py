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
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from carereport import (Medication, ExaminationRequest)
from .patient_views import PatientView


@dataclass
class NewIntake():
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

    patient: Optional[PatientView] = None
    date_intake: date = date.today()
    medication: list[Medication] = field(default_factory=list)
    examinations: list[ExaminationRequest] = field(default_factory=list)


@dataclass
class ExistingIntake():
    """ Data for an existing intake for a patient.

    The data is the same as for a new intake, the patient and date of intake
    have no option to be empty or a default. Any data in the lists in the
    class is new data.
    """

    patient: PatientView
    date_intake: date
    medication: list[Medication] = field(default_factory=list)
    examinations: list[ExaminationRequest] = field(default_factory=list)
