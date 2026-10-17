import re
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from evaluator import evaluate, format_result

OPERATORS = ("+", "-", "*", "/")
OPERATOR_CHARS = "".join(OPERATORS)

BUTTON_ROWS = [
    ["7", "8", "9", "Del", "AC"],
    ["4", "5", "6", "*", "/"],
    ["1", "2", "3", "+", "-"],
    ["0", ".", "10^x", "Ans", "="],
]

DISPLAY_STYLE = """
    font-size: 24px;
    background-color: white;
    color: black;
    border-radius: 5px;
    padding: 0 8px;
"""

BUTTON_STYLE = """
    QPushButton {
        font-size: 16px;
        color: black;
        background-color: #9cb7e6;
        border: 2px solid #eba434;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #b9cdf0;
    }
    QPushButton:pressed {
        background-color: #7f9fd6;
    }
"""


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.last_answer = ""
        self.reset_display = False  # True while the display shows a result
        self.error = False  # True while the display shows "Error"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Calculator")
        self.resize(360, 340)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(60)
        self.display.setStyleSheet(DISPLAY_STYLE)

        grid_layout = QGridLayout()
        for row, labels in enumerate(BUTTON_ROWS):
            for col, text in enumerate(labels):
                button = QPushButton(text)
                button.setFixedHeight(55)
                button.setStyleSheet(BUTTON_STYLE)
                button.clicked.connect(
                    lambda checked, t=text: self.on_button_click(t)
                )
                grid_layout.addWidget(button, row, col)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.display)
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def on_button_click(self, text):
        if text == "AC":
            self.clear()
        elif text == "Del":
            self.delete_last()
        elif text == "Ans":
            self.insert_answer()
        elif text == "=":
            self.calculate()
        elif text == "10^x":
            self.insert_power_of_ten()
        elif text == ".":
            self.insert_dot()
        elif text in OPERATORS:
            self.insert_operator(text)
        else:
            self.insert_digit(text)

    def clear(self):
        self.display.clear()
        self.reset_display = False
        self.error = False

    def _begin_input(self, continue_result=False):
        """Prepare the display before new input is added.

        An error is always wiped. A previous result is wiped too, unless the
        input is an operator that continues the calculation from it.
        """
        if self.error:
            self.clear()
        elif self.reset_display:
            if not continue_result:
                self.display.clear()
            self.reset_display = False

    def delete_last(self):
        if self.error:
            self.clear()
            return
        text = self.display.text()
        self.reset_display = False
        # "**" is one operator, so remove both characters together.
        self.display.setText(text[:-2] if text.endswith("**") else text[:-1])

    def insert_digit(self, digit):
        self._begin_input()
        self.display.setText(self.display.text() + digit)

    def insert_dot(self):
        self._begin_input()
        text = self.display.text()
        current_number = re.split(r"[+\-*/]", text)[-1]
        if "." in current_number:
            return
        if not current_number:
            text += "0"
        self.display.setText(text + ".")

    def insert_operator(self, op):
        self._begin_input(continue_result=True)
        text = self.display.text()
        if not text:
            if op == "-":  # a leading minus is a sign
                self.display.setText("-")
            return
        if text[-1] in OPERATORS:
            if op == "-" and text[-1] in ("*", "/"):
                self.display.setText(text + op)  # e.g. 5*-3
                return
            text = text.rstrip(OPERATOR_CHARS)  # replace the old operator
            if not text:  # only a lone sign was typed
                return
        self.display.setText(text + op)

    def insert_answer(self):
        if not self.last_answer:
            return
        self._begin_input()
        text = self.display.text()
        if text and (text[-1].isdigit() or text[-1] == "."):
            return  # would glue the answer onto the number being typed
        self.display.setText(text + self.last_answer)

    def insert_power_of_ten(self):
        self._begin_input()
        text = self.display.text()
        if text and text[-1] not in OPERATORS:
            return  # 10** needs an operator (or nothing) in front of it
        self.display.setText(text + "10**")

    def calculate(self):
        text = self.display.text()
        if self.error or not text:
            return
        try:
            result = format_result(evaluate(text))
        except (ValueError, ArithmeticError):
            self.display.setText("Error")
            self.error = True
            self.reset_display = False
            return
        self.display.setText(result)
        self.last_answer = result
        self.reset_display = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())
