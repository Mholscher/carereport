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

from datetime import datetime
import getpass 
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from configparser import ConfigParser
from sqlalchemy import (String, DateTime)
from sqlalchemy.orm import sessionmaker, mapped_column
from PyQt6.QtWidgets import QApplication


config = ConfigParser()
success = config.read('localcarereport.cfg')
if success:
    dburi = config['DATABASE']['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(dburi, isolation_level="READ UNCOMMITTED")
    Session = sessionmaker(bind=engine)
    session = Session()
else:
    raise FileNotFoundError('Configuration file not loaded!')


class Base(DeclarativeBase):
    """ Add mutation fields to each table """

    user = mapped_column(String(25), default=getpass.getuser, 
                               onupdate=getpass.getuser)
    updated_at = mapped_column(DateTime, default=datetime.now, 
                               onupdate=datetime.now)


app = QApplication([])


def validate_field_existance(instance, key, field, raise_on_empty):
    """ Validate a field has a value in it, not none or empty string """

    if field is None or field == "":
        raise raise_on_empty(f"{key} cannot be empty")
    return field


from carereport.models.patient import Patient, Intake
from carereport.models.medical import (Medication, ExaminationRequest,
                                       ExaminationResult, DietHeader,
                                       DietLines, Diagnose)
import carereport.views.scripts_patient
