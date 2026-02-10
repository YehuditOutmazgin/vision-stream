"""
Tailwind-inspired styling for VisionStream application.
"""

# Color palette
COLORS = {
    "background": "#f8fafc",
    "foreground": "#0f172a",
    "card": "#ffffff",
    "muted_foreground": "#64748b",
    "border": "#e2e8f0",
    "input": "#ffffff",
    "primary": "#3b82f6",
    "primary_foreground": "#ffffff",
    "muted": "#f1f5f9",
}

# Main stylesheet
MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QWidget {{
    background-color: {COLORS['background']};
    color: {COLORS['foreground']};
}}

QLineEdit {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    color: {COLORS['foreground']};
    padding: 8px 12px;
    font-size: 14px;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

QLineEdit::placeholder {{
    color: {COLORS['muted_foreground']};
}}

QPushButton {{
    background-color: {COLORS['card']};
    color: {COLORS['foreground']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {COLORS['muted']};
}}

QPushButton:pressed {{
    background-color: {COLORS['border']};
}}

QPushButton:disabled {{
    opacity: 0.5;
    color: {COLORS['muted_foreground']};
}}

QPushButton#play_btn {{
    background-color: {COLORS['primary']};
    color: {COLORS['primary_foreground']};
    border: none;
}}

QPushButton#play_btn:hover {{
    background-color: #2563eb;
}}

QPushButton#play_btn:pressed {{
    background-color: #1d4ed8;
}}

QLabel {{
    color: {COLORS['foreground']};
}}

QLabel#title {{
    font-size: 36px;
    font-weight: bold;
    color: {COLORS['foreground']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

QLabel#description {{
    color: {COLORS['muted_foreground']};
    font-size: 15px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
}}

QLabel#status {{
    color: {COLORS['muted_foreground']};
    font-size: 12px;
}}

QFrame {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
}}

QMessageBox {{
    background-color: {COLORS['background']};
}}

QMessageBox QLabel {{
    color: {COLORS['foreground']};
    background-color: transparent;
    border: none;
    padding: 0px;
}}

QMessageBox QTextEdit {{
    color: {COLORS['foreground']};
    background-color: transparent;
    border: none;
    padding: 0px;
}}

QMessageBox QPushButton {{
    min-width: 60px;
    background-color: {COLORS['card']};
    color: {COLORS['foreground']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 16px;
}}

QMessageBox QPushButton:hover {{
    background-color: {COLORS['muted']};
}}
"""
