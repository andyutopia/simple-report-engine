import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OPTIONS_PATH = os.path.join(TEMPLATE_DIR, "options.json")
FONT_DIR = os.path.join(BASE_DIR, "fonts")
TRAYS_DIR = os.path.join(BASE_DIR, "trays")

# Ensure trays directory exists
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(FONT_DIR, exist_ok=True)
os.makedirs(TRAYS_DIR, exist_ok=True)