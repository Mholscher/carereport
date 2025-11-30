from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtCore import QEvent


class DescriptionWidget(QPlainTextEdit):

    def focusEvent(self, event):
        """ The focus out event sets the view to the value of the field """

        if event.type() == QEvent.Type.FocusAboutToChange:
            if self.save_to_view is not None:
                print("Going to save:", self.toPlainText())
                self.save_to_view()
        super().focusOutEvent(event)
