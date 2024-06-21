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

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker

config = ConfigParser()
success = config.read('localcarereport.cfg')
if success:
    dburi = config['DATABASE']['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(dburi, isolation_level="READ UNCOMMITTED")
    Session = sessionmaker(bind=engine)
    session=Session()
else:
    raise FileNotFoundError('Configuration file not found!')

class Base(DeclarativeBase):

    pass

from carereport.models.patient import Patient
from carereport.models.medical import Medication
