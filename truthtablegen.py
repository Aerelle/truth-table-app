import sys
import itertools
from sympy import symbols, sympify, And, Or, Not, Implies, Equivalent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

A, B, C, D, E, F, G, H = symbols('A B C D E F G H')

def parse_expression(expression_text):
    try:
        return sympify(expression_text, locals={symbol.name: symbol for symbol in [A, B, C, D, E, F, G, H]})
    except Exception as e:
        print("Error parsing expression:", e)
        return None

def translate_to_symbolic(expression_text):
    return (expression_text.strip()
            .replace("∧", "&")
            .replace("∨", "|")
            .replace("¬", "~")
            .replace("→", ">>")
            .replace("↔", "<<"))

def get_main_operator(expression):
    if isinstance(expression, And): return "AND (∧)"
    elif isinstance(expression, Or): return "OR (∨)"
    elif isinstance(expression, Not): return "NOT (¬)"
    elif isinstance(expression, Implies): return "IMPLIES (→)"
    elif isinstance(expression, Equivalent): return "EQUIVALENT (↔)"
    return "None"

def generate_truth_table(expression, variables):
    combinations = list(itertools.product([True, False], repeat=len(variables)))
    return [[*combo, bool(expression.subs(dict(zip(variables, combo))))] for combo in combinations], [str(var) for var in variables] + ['Result']

class TruthTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logic Truth Table Generator")
        self.setGeometry(100, 100, 850, 700)
        self.setStyleSheet("background-color: #f5f5f5; color: #333333; font-family: 'Roboto', sans-serif;")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        instruction_label = QLabel("Enter an expression using A to H with up to 8 atomic sentences. You can use the logical symbols below.")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setFont(QFont("Roboto", 11))
        instruction_label.setStyleSheet("color: #555555;")
        layout.addWidget(instruction_label)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter logical expression (e.g., A ∧ B → ¬C)")
        self.input_field.setFont(QFont("Roboto", 12))
        self.input_field.setStyleSheet("padding: 8px; border: 1px solid #cccccc; border-radius: 4px;")
        layout.addWidget(self.input_field)

        symbol_layout = QHBoxLayout()
        symbols = {"∧": "AND", "∨": "OR", "¬": "NOT", "→": "IMPLIES", "↔": "EQUIVALENT"}
        for symbol, name in symbols.items():
            button = QPushButton(symbol, self)
            button.setToolTip(f"Insert {name}")
            button.setFont(QFont("Roboto", 12))
            button.setStyleSheet("padding: 8px; background-color: #3498db; color: white; border: none; border-radius: 4px;")
            button.clicked.connect(lambda _, s=symbol: self.insert_symbol(s))
            symbol_layout.addWidget(button)
        layout.addLayout(symbol_layout)

        self.generate_button = QPushButton("Generate Truth Table", self)
        self.generate_button.setFont(QFont("Roboto", 12, QFont.Bold))
        self.generate_button.setStyleSheet("padding: 10px; background-color: #2ecc71; color: white; border: none; border-radius: 4px;")
        self.generate_button.clicked.connect(self.generate_table)
        layout.addWidget(self.generate_button)

        self.operator_label = QLabel()
        self.operator_label.setFont(QFont("Roboto", 12))
        self.operator_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.operator_label)

        self.table_display = QTableWidget()
        self.table_display.setFont(QFont("Roboto", 10))
        self.table_display.setStyleSheet("border: 1px solid #cccccc;")
        layout.addWidget(self.table_display)

        main_widget.setLayout(layout)

    def insert_symbol(self, symbol):
        cursor_position = self.input_field.cursorPosition()
        new_text = self.input_field.text()[:cursor_position] + symbol + self.input_field.text()[cursor_position:]
        self.input_field.setText(new_text)
        self.input_field.setCursorPosition(cursor_position + len(symbol))

    def generate_table(self):
        expression_text = translate_to_symbolic(self.input_field.text().strip())
        expression = parse_expression(expression_text)
        
        if not expression:
            print(f"Parsing failed for expression: {expression_text}. Check your input syntax.")
            return

        main_operator = get_main_operator(expression)
        self.operator_label.setText(f"Main Logical Operator: {main_operator}")

        variables = sorted(expression.free_symbols, key=lambda s: s.name)
        table_data, headers = generate_truth_table(expression, variables)

        display_expression = (expression_text.replace("&", "∧")
                                              .replace("|", "∨")
                                              .replace("~", "¬")
                                              .replace(">>", "→")
                                              .replace("<<", "↔"))
        headers[-1] = display_expression

        self.table_display.setColumnCount(len(headers))
        self.table_display.setRowCount(len(table_data))
        self.table_display.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(table_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_display.setItem(row_idx, col_idx, item)

app = QApplication(sys.argv)
window = TruthTableApp()
window.show()
sys.exit(app.exec_())