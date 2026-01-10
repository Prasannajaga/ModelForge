# Global Colors
DARK_BG = "#121212"
PANEL_BG = "#1e1e1e"
ACCENT_BLUE = "#3b82f6"
ACCENT_BLUE_HOVER = "#2563eb"
TEXT_COLOR = "#e0e0e0"
TEXT_SECONDARY = "#a0a0a0"
BORDER_COLOR = "#333333"
INPUT_BG = "#2a2a2a"

# Application-wide Styles
MAIN_WINDOW_STYLE = f"""
    background-color: {DARK_BG};
    color: {TEXT_COLOR};
"""

SIDEBAR_STYLE = f"""
    background-color: {PANEL_BG};
    color: {TEXT_COLOR};
    border-right: 1px solid {BORDER_COLOR};
"""

HEADER_LABEL_STYLE = f"""
    font-size: 18px; 
    font-weight: bold; 
    background-color: {PANEL_BG};
    color: {TEXT_COLOR};
    padding: 10px;
    border-bottom: 1px solid {BORDER_COLOR};
"""

SIDEBAR_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: transparent;
        border: none;
        text-align: left;
        padding: 12px 20px;
        color: {TEXT_SECONDARY};
        font-size: 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #2d2d2d;
        color: white;
        border-left: 3px solid {ACCENT_BLUE};
    }}
    QPushButton:checked {{
        background-color: #2d2d2d;
        color: white;
        border-left: 3px solid {ACCENT_BLUE};
    }}
"""

CONTENT_AREA_STYLE = f"""
    background-color: {DARK_BG};
"""

# Optimize View Styles
VIEW_LABEL_STYLE = f"""
    font-size: 24px;
    color: {TEXT_COLOR};
    font-weight: bold;
"""

OPTIMIZE_VIEW_STYLE = f"""
    background-color: {DARK_BG};
"""

CARD_STYLE = f"""
    QFrame {{
        background-color: {PANEL_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 6px;
    }}
    QLabel {{
        color: {TEXT_COLOR};
        border: none;
    }}
"""

GROUP_TITLE_STYLE = f"""
    font-size: 14px;
    font-weight: bold;
    color: {TEXT_COLOR};
    margin-bottom: 8px;
    background-color: transparent;
    border: none;
"""

INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {INPUT_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        color: {TEXT_COLOR};
        padding: 8px;
        selection-background-color: {ACCENT_BLUE};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {ACCENT_BLUE};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
"""

BUTTON_PRIMARY_STYLE = f"""
    QPushButton {{
        background-color: {ACCENT_BLUE};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 16px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_BLUE_HOVER};
    }}
    QPushButton:pressed {{
        background-color: #1d4ed8;
    }}
"""

UPLOAD_WIDGET_STYLE = f"""
    QFrame {{
        background-color: {INPUT_BG};
        border: 1px dashed {BORDER_COLOR};
        border-radius: 6px;
    }}
    QFrame:hover {{
        border: 1px dashed {ACCENT_BLUE};
        background-color: #2d2d2d;
    }}
    QLabel {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
    }}
"""

TAB_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PANEL_BG};
        color: {TEXT_SECONDARY};
        border: none;
        padding: 12px;
        font-weight: bold;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QPushButton:checked {{
        background-color: {BORDER_COLOR}; /* Slightly lighter for active tab look if needed, or just keep seamless */
        color: {ACCENT_BLUE};
        border-bottom: 2px solid {ACCENT_BLUE};
    }}
    QPushButton:hover {{
        color: {ACCENT_BLUE};
    }}
"""

CHECKBOX_STYLE = f"""
    QCheckBox {{
        color: {TEXT_COLOR};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        background-color: {INPUT_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {ACCENT_BLUE};
    }}
    QCheckBox::indicator:checked {{
        background-color: {ACCENT_BLUE};
        border: 1px solid {ACCENT_BLUE};
        image: url(none); /* We don't have an image, relying on color */
    }}
"""
