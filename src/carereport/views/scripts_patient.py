#    Copyright 2024/2025 Menno Hölscher
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
import sys
from PyQt6.QtWidgets import (QApplication, QDialog, QListWidget,
                             QTreeWidget, QLabel, QWidget,
                             QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QPushButton, 
                             QLineEdit, QTextEdit, QListWidgetItem,
                             QTreeWidgetItem)
from .patientdialog  import Ui_inputPatient
from .patient_views import PatientView


class PatientChanges(QDialog, Ui_inputPatient):
    """ This class handles creating and changing patient data

    It exchanges the data with 5he model through the patient view.
    """
    def __init__(self, patient_view):

        super().__init__()

        self.setupUi(self)


# Code for testing purposes
app = QApplication([])
main_window = PatientChanges(PatientView())
main_window.show()
sys.exit(app.exec())
