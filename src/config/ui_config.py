"""UI configuration presets."""

import customtkinter as ctk

# App theme
APP_APPEARANCE = {
    "appearance_mode": "dark",
    "color_theme": "dark-blue",
    "geometry": "1920x1080",
    "app_icon": "../../assets/images/ddt(invert).ico",
}

# UI logos and elements
UI_COMPONENTS = {
    "joy_faceboss_logo": "../../assets/images/FACEBOSS_20Invert2-removebg-preview.png",
    "faceboss_ddt_logo": "../../assets/images/datadownloadtool-ai-brush-removebg-90tmmxb5.png",
    "ddt_icon": "../../assets/images/ddt.ico",
    "home_btn": "../../assets/images/home.png",
}

COMPONENT_DIMENSIONS = {
    "button": {
        "height": 40,
        "width": 75,
    },
    "label": {},
    "image": {
        "height": 150,
        "width": 600,
    },
    "entry": {"width": 150},
}

UI_PADDING = {
    "small": 5,
    "medium": 10,
    "large": 20,
}

UI_FONTS = {
    "status": 20,
    "label_size": 25,
    "checkbox_size": 15,
}

UI_COLORS = {
    "add": "#28a745",
    "add_hover": "#218838",
    "remove": "#dc3545",
    "remove_hover": "#c82333",
    "clear": "#b00020",
    "clear_hover": "#8e0018",
    "delete_database": "#b00020",
    "delete_database_hover": "#8e0018",
    "primary": "#0d6efd",
    "primary_hover": "#0b5ed7",
    "white": "#FFFFFF",
    "black": "#000000",
    "charcoal": "#36454F",
    "charcoal_hover": "#2a353d",
    "checkbox": "#0eeb1d",
    "checkbox_hover": "#11a81b",
    "status": "#EEEEEE",
}
