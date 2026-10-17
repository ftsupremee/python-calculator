import sys

from PyQt6.QtWidgets import (
  QApplication,
  QGridLayout,
  QLineEdit,
  QPushButton,
  QVBoxLayout,
  QWidget,
)


class Calculator(QWidget):
  def __init__(self):
    super().__init__()
    self.last_answer = ""
    self.reset_display = (False)
    self.initUI()

  def initUI(self):
    self.setWindowTitle("Calculator Keypad")
    self.resize(300, 450)

    self.display = QLineEdit()
    self.display.setReadOnly(True)
    self.display.setFixedHeight(60)
    self.display.setStyleSheet(
        "font-size: 24px; background-color: white; color: black; border-radius:"
        " 5px;"
    )

    main_layout = QVBoxLayout()
    grid_layout = QGridLayout()

    main_layout.addWidget(self.display)

    buttons = [
        ("7", 0, 0),
        ("8", 1, 0),
        ("9", 2, 0),
        ("Del", 3, 0),
        ("AC", 4, 0),

        ("4", 0, 1),
        ("5", 1, 1),
        ("6", 2, 1),
        ("*", 3, 1),
        ("/", 4, 1),

        ("1", 0, 2),
        ("2", 1, 2),
        ("3", 2, 2),
        ("+", 3, 2),
        ("-", 4, 2),

        ("0", 0, 3),
        (".", 1, 3),
        ("10^x", 2, 3),
        ("Ans", 3, 3),
        ("=", 4, 3),
    ]  

    for text, col, row in buttons:
      button = QPushButton(text)
      button.setFixedHeight(55)
      button.setStyleSheet("""
      QPushButton{
        font-size: 16px;
        background-color: #9cb7e6;
        border-radius: 50%;
        border-color: #eba434;
        height: 55px;
        width:40px;
      }
      QPushButton:hover{
          box--shadow: inset 0 0 20px rgba(156, 183, 230, 0.6)
      }""")

      button.clicked.connect(lambda checked, t=text: self.on_button_click(t))
      grid_layout.addWidget(button, row, col)

    main_layout.addLayout(grid_layout)
    self.setLayout(main_layout)

  def on_button_click(self, text):
    current_text = self.display.text()

    if text == "AC":
      self.display.setText("")
    elif text == "Del":
      if not self.reset_display:
        self.display.setText(current_text[:-1])
    elif text == "Ans":
      if self.reset_display:
        self.display.setText(self.last_answer)
        self.reset_display = False
      else:
        self.display.setText(current_text + self.last_answer)
    elif text == "=":
      try:
        result = str(eval(current_text))
        self.display.setText(result)
        self.last_answer = result
        self.reset_display = True
      except Exception:
        self.display.setText("Error")
    elif text == "10^x":
      self.display.setText(f"{current_text} 10**")
    else:
      if self.reset_display:
        if text in "+-*/":
          self.display.setText(current_text + text)
        else: 
          self.display.setText(text)
        self.reset_display = False
      else:
        self.display.setText(current_text + text)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = Calculator()
  window.show()
  sys.exit(app.exec())