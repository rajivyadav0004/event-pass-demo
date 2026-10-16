from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
import os
from datetime import datetime

app = Flask(__name__)

# =========================================================
# CONFIGURATION
# =========================================================

tickets = {}

EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
EVENT_DATE = "16 Oct 2026"
VENUE = "NIET Plot 19 Campus"

# Put the real NIET logo image in the static/ folder.
# These alternatives let the app find it even if its extension differs.
LOGO_CANDIDATES = (
    "niet-logo.png", "niet-logo.jpg", "niet-logo.jpeg", "niet-logo.webp",
    "NIET-logo.png", "NIET-logo.jpg", "logo.png", "logo.jpg"
)

def find_logo_filename():
    for filename in LOGO_CANDIDATES:
        filepath = os.path.join(app.static_folder or "static", filename)
        if os.path.isfile(filepath):
            return filename
    return None

LOGO_PATH = find_logo_filename()

# Theme
TEAL = "#168B87"
BLUE = "#3268AD"
NAVY = "#18365F"
GOLD = "#D4AD54"
BACKGROUND = "#EAF0F8"
CREAM = "#F5F8FF"


# =========================================================
# EVENT PASS TEMPLATE
# =========================================================

PASS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>SilverNova 2026 - Event Pass</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eaf0f8;
    font-family: Arial, Helvetica, sans-serif;
    color: #18365f;
}

.pass {
    width: 100%;
    max-width: 1200px;
    margin: 15px auto;
    background: #f5f8ff;
    border: 4px solid #d4ad54;
    border-radius: 25px;
    overflow: hidden;
}

/* HEADER */

.header {
    position: relative;
    display: grid;
    grid-template-columns: 270px minmax(0, 1fr) 190px;
    align-items: center;
    gap: 25px;
    padding: 22px 28px 32px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    border-top: 7px solid #e8c75a;
    color: white;
}
