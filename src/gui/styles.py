"""
Modern, clean styling for VisionStream application.
Light theme with bright colors and professional design.
"""

# Color palette - Modern Light Theme
COLORS = {
    "background": "#f5f7fa",
    "foreground": "#1a1f36",
    "card": "#ffffff",
    "muted_foreground": "#6b7280",
    "border": "#e5e7eb",
    "input": "#ffffff",
    "primary": "#6366f1",
    "primary_hover": "#4f46e5",
    "primary_active": "#4338ca",
    "primary_foreground": "#ffffff",
    "muted": "#f3f4f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "secondary": "#8b5cf6",
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
    border-radius: 8px;
    color: {COLORS['foreground']};
    padding: 10px 14px;
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
    background-color: #fafbff;
}}

QLineEdit::placeholder {{
    color: {COLORS['muted_foreground']};
}}

QPushButton {{
    background-color: {COLORS['card']};
    color: {COLORS['foreground']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

QPushButton:hover {{
    background-color: {COLORS['muted']};
    border: 1px solid #d1d5db;
}}

QPushButton:pressed {{
    background-color: #e5e7eb;
}}

QPushButton:disabled {{
    opacity: 0.5;
    color: {COLORS['muted_foreground']};
}}

QPushButton#play_btn {{
    background-color: {COLORS['primary']};
    color: {COLORS['primary_foreground']};
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 24px;
}}

QPushButton#play_btn:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton#play_btn:pressed {{
    background-color: {COLORS['primary_active']};
}}

QLabel {{
    color: {COLORS['foreground']};
}}

QLabel#title {{
    font-size: 28px;
    font-weight: 700;
    color: {COLORS['foreground']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

QLabel#description {{
    color: {COLORS['muted_foreground']};
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.5;
}}

QLabel#status {{
    color: {COLORS['muted_foreground']};
    font-size: 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

QFrame {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
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
    border-radius: 8px;
    padding: 8px 18px;
}}

QMessageBox QPushButton:hover {{
    background-color: {COLORS['muted']};
}}
"""
