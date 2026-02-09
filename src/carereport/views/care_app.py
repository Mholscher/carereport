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

from PyQt6.QtCore import (QLocale, pyqtSignal)
from PyQt6.QtWidgets import QMainWindow, QWidget
from carereport import app
from .mainwindow import Ui_MainWindow
from .formhandle import Ui_Form
# from .patient_views import PatientView


class CentralForm(QWidget, Ui_Form):
    """ This is the formhandler to fill the central widget of the main window

    It shows the identification data of the "current patient" at the top of
    the window. Any data for this patient can de shown in the multi tabular
    widget below it. Think of medical data as examinations, but also data for
    the day to day care, such as any diets the patient follows.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.diet_tab = None


class CareAppWindow(QMainWindow, Ui_MainWindow):
    """ This is the class which creates the mainwindow for the application. """

    newCurrentPatient = pyqtSignal()

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.main_form = CentralForm()
        self.setCentralWidget(self.main_form)
        self.actionAfsluiten.triggered.connect(self.close)
        self.show()
        self.statusbar.showMessage("Carereport klaar")

    def set_new_current_patient(self, new_patient_view):
        """ Set a new patient as current including side effects.

        Side effects like replacing data in the tab widget tabs that are
        depending on the patient. In practice it will be (fast) all of
        the tabs in the widget.

        Side effects will be done by emitting the newCurrentPatient signal.
        """

        app.current_patient_view = new_patient_view
        self.on_current_patient_change()
        self.newCurrentPatient.emit()

    def on_current_patient_change(self):
        """ Set all fields/attributes in the main window

        This does not entail changes to e.g. the tabwidget with the patient
        detail data, like diet medication etc. This is the responsibility
        of the individual tab pages
        """

        self.main_form.patientnameedit.setText(app.current_patient_view.surname
                                               + ', ' +
                                               app.current_patient_view.initials)
        born = app.current_patient_view.birthdate
        loc = QLocale()
        self.main_form.birthdateedit.setText(loc.toString(born,
                                             loc.FormatType.ShortFormat))
        if self.main_form.diet_tab:
            pass
        else:
            from .scripts_diet import DietListWidget
            self.main_form.diet_tab = DietListWidget(app.current_patient_view)


mainwindow = CareAppWindow()
