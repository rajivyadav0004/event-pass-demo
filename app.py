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

# Place the logo image inside the static/ folder.
LOGO_CANDIDATES = (
    "niet-logo.png",
    "niet-logo.jpg",
    "niet-logo.jpeg",
    "niet-logo.webp",
    "NIET-logo.png",
    "NIET-logo.jpg",
    "logo.png",
    "logo.jpg",
)


def find_logo_filename():
    for filename in LOGO_CANDIDATES:
        filepath = os.path.join(
            app.static_folder or "static",
            filename
        )

        if os.path.isfile(filepath):
            return filename

    return None


LOGO_PATH = find_logo_filename()

# Theme colours
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

/* Colourful dots on the header */

.header::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 10px;

    background-color: #3268ad;
    background-image:
        radial-gradient(circle, #f2d45d 4px, transparent 4.5px),
        radial-gradient(circle, #9cb8f0 4px, transparent 4.5px),
        radial-gradient(circle, #65c5bd 4px, transparent 4.5px);
    background-size: 60px 10px, 60px 10px, 60px 10px;
    background-position: 0 0, 20px 0, 40px 0;
    background-repeat: repeat-x;
}

/* LOGO */

.logo-box {
    width: 100%;
    min-height: 110px;
    padding: 12px;
    background: white;
    border-radius: 15px;

    display: flex;
    justify-content: center;
    align-items: center;
}

.logo-box img {
    display: block;
    width: 100%;
    max-width: 250px;
    height: 90px;
    object-fit: contain;
}

.logo-fallback {
    display: none;
    color: #18365f;
    font-weight: bold;
    text-align: center;
}

/* EVENT TITLE */

.event-title {
    min-width: 0;
}

.present {
    margin-bottom: 8px;
    font-size: 16px;
    font-weight: bold;
    color: white;
}

.event-title h1 {
    margin: 0 0 8px;
    color: white;
    font-size: 34px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.event-title p {
    margin: 0;
    color: white;
    font-size: 20px;
    font-weight: bold;
}

.entry-label {
    padding: 14px 10px;
    border: 3px solid #9dbde8;
    border-radius: 40px;
    color: white;
    text-align: center;
    font-size: 17px;
    font-weight: bold;
}

/* MAIN CONTENT */

.pass-content {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 3px 300px;
    column-gap: 14px;
    row-gap: 28px;
    padding: 28px;
}

.left-section {
    position: relative;
    min-width: 0;
    padding-right: 25px;
    border-right: none;
}

/* GOLDEN DOTTED LINE WITH CIRCLES */

.separator-line {
    position: relative;
    align-self: stretch;
    width: 3px;
    margin: -28px 0;

    background: repeating-linear-gradient(
        to bottom,
        #d4ad54 0px,
        #d4ad54 9px,
        transparent 9px,
        transparent 19px
    );
}

.separator-circle {
    position: absolute;
    left: 50%;
    width: 20px;
    height: 20px;
    border: 3px solid #d4ad54;
    border-radius: 50%;
    background: #f5f8ff;
    transform: translateX(-50%);
}

.separator-circle.top {
    top: -10px;
}

.separator-circle.bottom {
    bottom: -10px;
}

.admit {
    margin-bottom: 18px;
    color: #234f91;
    font-size: 17px;
    font-weight: bold;
}

.name {
    margin: 0 0 25px;
    color: #18365f;
    font-size: 40px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

/* DATE AND VENUE */

.event-info {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 12px;
    margin-bottom: 24px;
}

.date-box,
.venue-box {
    min-height: 125px;
    padding: 22px;
    border-radius: 20px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
}

.field-label {
    margin-bottom: 15px;
    font-size: 14px;
    font-weight: bold;
}

.field-value {
    font-size: 21px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

/* STUDENT DETAILS */

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.item {
    min-width: 0;
    min-height: 115px;
    padding: 16px;
    background: #edf3ff;
    border: 2px solid #d4ad54;
    border-top: 7px solid #e8c75a;
    border-radius: 12px;
    overflow-wrap: anywhere;
}

.item .field-label {
    color: #526680;
    font-size: 13px;
}

.item .field-value {
    color: #18365f;
    font-size: 19px;
    font-weight: bold;
}

/* QR SECTION */

.right-section {
    min-width: 0;
    padding: 0 4px;
    text-align: center;
}

.epass {
    display: inline-block;
    margin-bottom: 20px;
    padding: 13px 40px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
    border-radius: 30px;
    font-size: 17px;
    font-weight: bold;
}

.right-section h2 {
    margin: 8px 0 22px;
    color: #234f91;
    font-size: 21px;
    font-weight: bold;
}

.qr-box {
    padding: 20px;
    background: #eaf1ff;
    border-radius: 20px;
}

.qr-box img {
    display: block;
    width: 100%;
    max-width: 250px;
    margin: auto;
    padding: 8px;
    background: white;
}

.ticket-number {
    margin-top: 15px;
    color: #234f91;
    font-size: 14px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.scan-text {
    margin: 20px 0;
    color: #687b95;
    font-size: 14px;
    line-height: 1.6;
}

.preview-note {
    margin-top: 12px;
    padding: 10px;
    border-radius: 8px;
    background: #fff3d7;
    color: #765b20;
    font-size: 11px;
    line-height: 1.5;
    font-weight: bold;
}

/* MOBILE RESPONSIVE */

@media (max-width: 760px) {
    body {
        padding: 10px;
    }

    .header {
        grid-template-columns: 1fr;
        gap: 15px;
        padding: 20px 20px 30px;
        text-align: center;
    }

    .logo-box {
        width: 100%;
        max-width: 320px;
        margin: auto;
    }

    .event-title h1 {
        font-size: 29px;
    }

    .event-title p {
        font-size: 18px;
    }

    .entry-label {
        max-width: 220px;
        width: 100%;
        margin: auto;
    }

    .pass-content {
        grid-template-columns: 1fr;
        gap: 30px;
        padding: 18px;
    }

    .separator-line {
        display: none;
    }

    .left-section {
        padding-right: 0;
        padding-bottom: 25px;
        border-bottom: 3px dashed #d4ad54;
    }

    .name {
        font-size: 32px;
    }

    .right-section {
        width: 100%;
        max-width: 340px;
        margin: auto;
    }
}

@media (max-width: 420px) {
    .event-info,
    .details {
        grid-template-columns: 1fr;
    }

    .event-title h1 {
        font-size: 25px;
    }

    .name {
        font-size: 27px;
    }
}
</style>
</head>

<body>

<div class="pass">

    <header class="header">

        <div class="logo-box">

            <img
                src="{{ url_for('static', filename=logo) if logo else '' }}"
                alt="NIET Greater Noida logo"
                onerror="
                    this.style.display='none';
                    this.nextElementSibling.style.display='block';
                "
                {% if not logo %}style="display:none"{% endif %}>

            <div class="logo-fallback">
                NIET Greater Noida
            </div>

        </div>

        <div class="event-title">
            <div class="present">NIET PRESENTS</div>
            <h1>{{ event_name }}</h1>
            <p>{{ event_subtitle }}</p>
        </div>

        <div class="entry-label">ENTRY PASS</div>

    </header>

    <main class="pass-content">

        <section class="left-section">

            <div class="admit">
                ADMIT ONE - REGISTERED PARTICIPANT
            </div>

            <div class="name">
                {{ ticket.name }}
            </div>

            <div class="event-info">

                <div class="date-box">
                    <div class="field-label">EVENT DATE</div>
                    <div class="field-value">
                        {{ ticket.event_date }}
                    </div>
                </div>

                <div class="venue-box">
                    <div class="field-label">VENUE</div>
                    <div class="field-value">
                        {{ venue }}
                    </div>
                </div>

            </div>

            <div class="details">

                <div class="item">
                    <div class="field-label">COURSE</div>
                    <div class="field-value">
                        {{ ticket.course }}
                    </div>
                </div>

                <div class="item">
                    <div class="field-label">BRANCH</div>
                    <div class="field-value">
                        {{ ticket.branch }}
                    </div>
                </div>

                <div class="item">
                    <div class="field-label">YEAR OF STUDY</div>
                    <div class="field-value">
                        {{ ticket.year }}
                    </div>
                </div>

            </div>

        </section>

        <div class="separator-line" aria-hidden="true">
            <span class="separator-circle top"></span>
            <span class="separator-circle bottom"></span>
        </div>

        <aside class="right-section">

            <div class="epass">E-PASS</div>

            <h2>NIET ENTRY GATE</h2>

            <div class="qr-box">

                <img
                    src="data:image/png;base64,{{ ticket.qr }}"
                    alt="QR code for pass preview">

                <div class="ticket-number">
                    {{ ticket.id }}
                </div>

            </div>

            <div class="scan-text">
                Scan this QR code to view pass details.
            </div>

            <div class="preview-note">
                UNOFFICIAL PREVIEW — NOT VALID FOR ENTRY
            </div>

        </aside>

    </main>

</div>

</body>
</html>
"""
