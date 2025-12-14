# gui/themes.py

LIGHT_THEME = """
QWidget {
    background-color: #F5F7FA;
    font-family: Segoe UI, Arial;
    font-size: 13px;
    color: #2E2E2E;
}

QLabel {
    font-size: 14px;
    font-weight: 600;
}

QPushButton {
    background-color: #2F80ED;
    color: white;
    border-radius: 6px;
    padding: 8px 14px;
}

QPushButton:hover {
    background-color: #2563EB;
}

QTableWidget {
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #F0F2F5;
    padding: 8px;
    border: none;
    font-weight: 600;
}

QLineEdit, QComboBox {
    padding: 6px;
    border-radius: 6px;
    border: 1px solid #D0D0D0;
}
"""

DARK_THEME = """
QWidget {
    background-color: #121212;
    font-family: Segoe UI, Arial;
    font-size: 13px;
    color: #E0E0E0;
}

QLabel {
    font-size: 14px;
    font-weight: 600;
}

QPushButton {
    background-color: #3B82F6;
    color: white;
    border-radius: 6px;
    padding: 8px 14px;
}

QPushButton:hover {
    background-color: #2563EB;
}

QTableWidget {
    background-color: #1E1E1E;
    border: 1px solid #333;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #2A2A2A;
    padding: 8px;
    border: none;
    font-weight: 600;
}

QLineEdit, QComboBox {
    padding: 6px;
    border-radius: 6px;
    border: 1px solid #444;
    background-color: #1E1E1E;
    color: #E0E0E0;
}
"""
