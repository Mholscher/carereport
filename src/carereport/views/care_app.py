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
""" This module holds the application part of carereport. It imports the actual
QApplication, it is set up in the package.
Here we create and set up the main window of the application and fill it
with the actions the user can take."""

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QMainWindow, QWidget
from .mainwindow import Ui_MainWindow
from .formhandle import Ui_Form
from carereport import app


class CentralForm(QWidget, Ui_Form):
    """ This is the formhandler to fill the central widget of the main window

    It shows the identification data of the "current patient" at the top of
    the window. Any data for this patient can de shown in the multi tabular
    widget blow it. Think of medical data as examinations, but also data for
    the day to day care, such as any diets the patient follows.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        # if app.current_patient_view:
        #     patient_view = app.current_patient_view
        #     self.patientnameedit.setText(patient_view.surname,
        #                                  ',',
        #                                  patient_view.initials)
        #     self.birthdateedit.setText(QDate(patient_view.birthdate.year,
        #                                patient_view.birthdate.month,
        #                                patient_view.birthdate.day))


class CareAppWindow(QMainWindow, Ui_MainWindow):
    """ This is the class which creates the mainwindow for the application. """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.setCentralWidget(CentralForm())
        self.actionAfsluiten.triggered.connect(self.close)
        # self.actionNieuw.triggered.connect(FindCreateChangePatient)
        self.show()
        self.statusbar.showMessage("Carereport klaar")


careapp_mainwindow = CareAppWindow()
from .scripts_patient import NewIntake
careapp_mainwindow.new_intake = NewIntake()
careapp_mainwindow.actionNieuw.triggered.connect(
    careapp_mainwindow.new_intake.ask_user)
