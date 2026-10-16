import os
import io
import base64
import secrets
from datetime import date, datetime
from urllib.parse import quote

import qrcode
from flask import (
    Flask,
    request,
    render_template_string,
    url_for,
    abort,
)

app = Flask(__name__)

# =====================================================
# EVENT SETTINGS
# =====================================================

EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
DEFAULT_VENUE = "NIET Plot 19 Campus"

LOGO_FILENAME = "NIET New Engineering Color Logo.jpg"

# Demo tickets are stored in memory.
# Restarting the server clears these tickets.
tickets = {}


# =====================================================
# COMMON CSS
# =====================================================

STYLE = """
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 18px;
    background: #eef2f8;
    font-family: Arial, Helvetica, sans-serif;
    color: #18365f;
}

.pass {
    width: 100%;
    max-width: 1500px;
    margin: 10px auto;
    background: #f5f8ff;
    border: 4px solid #d4ad54;
    border-radius: 25px;
    overflow: hidden;
    box-shadow: 0 8px 25px #00012;
}

/* HEADER */

.header {
    position: relative;
    display: grid;
    grid-template-columns: 330px minmax(0, 1fr) 210px;
    gap: 28px;
    align-items: center;
    padding: 24px 35px 35px;
    color: white;
    background: linear-gradient(
        110deg,
        #218b89 0%,
        #287e9e 48%,
        #3268ad 100%
    );
    border-top: 7px solid #e8c75a;
}

/* Colourful dots under the header */

.header::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 13px;

    background-image:
        radial-gradient(circle, #f2d45d 5px, transparent 5.5px),
        radial-gradient(circle, #9bb8f2 5px, transparent 5.5px),
        radial-gradient(circle, #64c5bd 5px, transparent 5.5px);

    background-size: 60px 13px;
    background-position: 0 0, 30px 0, 15px 0;
    background-repeat: repeat-x;
}

/* LOGO */

.logo-box {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 115px;
    padding: 10px;
    background: white;
    border-radius: 15px;
    color: #18365f;
    font-weight: bold;
    text-align: center;
}

.logo {
    display: block;
    width: 100%;
    height: 105px;
    object-fit: contain;
}

/* TITLE */

.event-title {
    min-width: 0;
}

.small-title {
    margin-bottom: 7px;
    font-size: 17px;
    font-weight: bold;
}

.event-title h1 {
    margin: 0;
    font-size: clamp(26px, 3vw, 43px);
    font-weight: 800;
    overflow-wrap: anywhere;
}

.event-title p {
    margin: 9px 0 0;
    font-size: 21px;
    font-weight: bold;
}

.entry-label {
    padding: 15px 12px;
    border: 3px solid #8eafe3;
    border-radius: 40px;
    text-align: center;
    font-weight: bold;
    font-size: 18px;
}

/* MAIN PASS CONTENT */

.pass-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 3px 365px;
    column-gap: 28px;
    padding: 30px;
}

.left-panel {
    min-width: 0;
}

.participant-label {
    margin: 5px 0 18px;
    color: #234f91;
    font-size: 19px;
    font-weight: bold;
}

.name {
    margin: 0 0 30px;
    color: #18365f;
    font-size: clamp(30px, 4vw, 55px);
    font-weight: 800;
    overflow-wrap: anywhere;
}

/* DATE AND VENUE */

.event-info {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 0;
    margin-bottom: 28px;
}

.event-date,
.venue {
    min-width: 0;
    min-height: 145px;
    padding: 24px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
}

.event-date {
    border-radius: 22px;
}

.venue {
    border-radius: 22px;
}

.info-label {
    display: block;
    margin-bottom: 22px;
    font-size: 15px;
    font-weight: bold;
}

.info-value {
    font-size: clamp(18px, 2vw, 25px);
    font-weight: bold;
    overflow-wrap: anywhere;
}

/* STUDENT DETAILS */

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 15px;
}

.item {
    min-width: 0;
    min-height: 140px;
    padding: 20px;
    background: #eaf1ff;
    border: 2px solid #d7c28c;
    border-top: 8px solid #e8c75a;
    border-radius: 14px;
    overflow-wrap: anywhere;
}

.item small {
    display: block;
    margin-bottom: 20px;
    color: #526680;
    font-size: 14px;
    font-weight: bold;
}

.item strong {
    color: #18365f;
    font-size: 19px;
}

/* DOTTED SEPARATOR */

.separator {
    position: relative;
    align-self: stretch;
    width: 3px;
    margin: -30px 0;
    background: repeating-linear-gradient(
        to bottom,
        #d4ad54 0,
        #d4ad54 9px,
        transparent 9px,
        transparent 20px
    );
}

.circle {
    position: absolute;
    left: 50%;
    width: 42px;
    height: 42px;
    border: 3px solid #d4ad54;
    border-radius: 50%;
    background: #f5f8ff;
    transform: translateX(-50%);
}

.circle.top {
    top: 0;
}

.circle.bottom {
    bottom: 0;
}

/* QR AREA */

.qr-panel {
    min-width: 0;
    padding-left: 0;
    text-align: center;
}

.pill {
    display: inline-block;
    min-width: 165px;
    padding: 13px 25px;
    margin: 5px 0 22px;
    border-radius: 35px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    font-weight: bold;
    font-size: 17px;
}

.qr-panel h2 {
    margin: 5px 0 25px;
    color: #234f91;
    font-size: 23px;
}

.qr-box {
    padding: 24px;
    background: #eaf1ff;
    border-radius: 25px;
}

.qr-image {
    display: block;
    width: 100%;
    max-width: 300px;
    height: auto;
    margin: auto;
    padding: 8px;
    background: white;
}

.ticket-number {
    margin-top: 17px;
    color: #234f91;
    font-size: 16px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.hint {
    margin: 22px 0 0;
    color: #687b95;
    font-size: 16px;
    line-height: 1.6;
}

.preview-note {
    margin-top: 16px;
    padding: 12px;
    border-radius: 10px;
    background: #fff3d7;
    color: #765b20;
    font-size: 12px;
    font-weight: bold;
    line-height: 1.5;
}

/* FORM */

.form-panel {
    width: 100%;
    max-width: 600px;
    margin: 25px auto;
    padding: 28px;
    background: white;
    border: 3px solid #d4ad54;
    border-radius: 20px;
    box-shadow: 0 8px 25px #00012;
}

.form-logo {
    display: block;
    width: 230px;
    max-width: 100%;
    height: 100px;
    margin: auto;
    object-fit: contain;
}

.form-panel h1 {
    color: #234f91;
    text-align: center;
    font-size: 27px;
}

.form-panel > p {
    text-align: center;
}

label {
    display: block;
    margin-top: 16px;
    font-weight: bold;
}

input,
select {
    width: 100%;
    padding: 13px;
    margin-top: 7px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 16px;
    background: white;
}

button,
.button {
    display: block;
    width: 100%;
    padding: 15px;
    margin-top: 20px;
    border: 0;
    border-radius: 10px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    text-decoration: none;
    cursor: pointer;
}

/* QR VERIFICATION PAGE */

.verify-card {
    width: 100%;
    max-width: 520px;
    margin: 25px auto;
    padding: 28px;
    border-top: 10px solid #3268ad;
    border-radius: 25px;
    background: white;
    box-shadow: 0 8px 30px #00012;
    text-align: center;
}

.verify-logo {
    display: block;
    width: 280px;
    max-width: 100%;
    height: 110px;
    margin: 0 auto 15px;
    object-fit: contain;
}

.status-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 115px;
    height: 115px;
    margin: 20px auto;
    border-radius: 50%;
    background: #3268ad;
    color: white;
    font-size: 65px;
    font-weight: bold;
}

.verify-card h1 {
    color: #281b1b;
    font-size: 32px;
}

.verify-message {
    color: #493e3e;
    font-size: 17px;
    line-height: 1.5;
}

.verify-name {
    margin: 28px 0 22px;
    color: #18365f;
    font-size: 29px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.verify-details {
    padding: 15px 20px;
    border: 2px solid #dce4ee;
    border-radius: 17px;
    background: #f8fafc;
    text-align: left;
}

.verify-row {
    padding: 15px 0;
    border-bottom: 1px solid #dce4ee;
    overflow-wrap: anywhere;
}

.verify-row:last-child {
    border-bottom: none;
}

.verify-row small {
    display: block;
    margin-bottom: 7px;
    color: #746a67;
    font-size: 13px;
    font-weight: bold;
}

.verify-row strong {
    font-size: 18px;
}

.verify-note {
    margin-top: 22px;
    padding: 17px;
    border-radius: 13px;
    background: #fff3d7;
    color: #765b20;
    font-size: 15px;
    line-height: 1.6;
}

@media (max-width: 850px) {
    body {
        padding: 8px;
    }

    .header {
        grid-template-columns: 1fr;
        gap: 15px;
        padding: 20px 18px 30px;
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
        width: 100%;
        max-width: 220px;
        margin: auto;
    }

    .pass-body {
        grid-template-columns: 1fr;
        gap: 30px;
        padding: 20px;
    }

    .separator {
        display: none;
    }

    .details {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .qr-panel {
        padding-top: 25px;
        border-top: 3px dashed #d4ad54;
    }

    .qr-box {
        max-width: 360px;
        margin: auto;
    }
}

@media (max-width: 450px) {
    .details,
    .event-info {
        grid-template-columns: 1fr;
    }

    .name {
        font-size: 29px;
    }

    .item {
        min-height: 100px;
    }

    .verify-card {
        padding: 20px;
    }
}

/* PRINT: LANDSCAPE PASS */

@media print {
    @page {
        size: A4 landscape;
        margin: 5mm;
    }

    body {
        padding: 0;
        background: white;
    }

    .pass {
        width: 100%;
        max-width: none;
        margin: 0;
        border-width: 2px;
        box-shadow: none;
        border-radius: 15px;
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }

    .header {
        grid-template-columns: 230px minmax(0, 1fr) 155px;
        gap: 16px;
        padding: 14px 18px 25px;
    }

    .logo-box {
        min-height: 85px;
    }

    .logo {
        height: 75px;
    }

    .event-title h1 {
        font-size: 28px;
    }

    .event-title p {
        font-size: 16px;
    }

    .pass-body {
        grid-template-columns: minmax(0, 1fr) 3px 250px;
        gap: 18px;
        padding: 20px;
    }

    .name {
        font-size: 34px;
        margin-bottom: 20px;
    }

    .event-date,
    .venue {
        min-height: 95px;
        padding: 13px;
    }

    .info-label {
        margin-bottom: 10px;
    }

    .info-value {
        font-size: 17px;
    }

    .item {
        min-height: 95px;
        padding: 10px;
    }

    .item small {
        margin-bottom: 12px;
    }

    .item strong {
        font-size: 14px;
    }

    .qr-box {
        padding: 10px;
    }

    .qr-image {
        max-width: 175px;
    }

    .pill {
        margin-bottom: 10px;
    }

    .qr-panel h2 {
        font-size: 17px;
        margin-bottom: 12px;
    }

    .hint {
        font-size: 12px;
        margin-top: 12px;
    }
}
"""


# =====================================================
# HTML: REGISTRATION FORM
# =====================================================

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova 2026 - Pass Preview</title>
<style>{{ style }}</style>
</head>
<body>

<div class="form-panel">

    {% if logo_exists %}
    <img class="form-logo"
         src="{{ url_for('static', filename=logo_filename) }}"
         alt="NIET logo">
    {% else %}
    <h2 style="text-align:center">NIET Greater Noida</h2>
    {% endif %}

    <h1>{{ event_name }}</h1>
    <p><strong>{{ subtitle }}</strong></p>

    <div class="preview-note">
        DEMONSTRATION ONLY — NOT VALID FOR ENTRY
    </div>

    <form method="POST" action="{{ url_for('home') }}">

        <label for="name">Full Name</label>
        <input id="name" name="name"
               maxlength="100" required>

        <label for="event_date">Event Date</label>
        <input id="event_date" type="date"
               name="event_date"
               value="2026-10-16" required>

        <label for="venue">Venue</label>
        <input id="venue" name="venue"
               value="{{ venue }}"
               maxlength="150" required>

        <label for="course">Course</label>
        <select id="course" name="course" required>
            <option value="B. Tech">B. Tech</option>
            <option value="M.Tech">M.Tech</option>
            <option value="MBA">MBA</option>
            <option value="B.Pharm">B.Pharm</option>
        </select>

        <label for="branch">Branch</label>
        <input id="branch" name="branch"
               placeholder="e.g. Biotechnology"
               maxlength="100" required>

        <label for="year">Year of Study</label>
        <select id="year" name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button type="submit">Generate Pass Preview</button>
    </form>
</div>

</body>
</html>
"""


# =====================================================
# HTML: EVENT PASS
# =====================================================

PASS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova 2026 - Event Pass Preview</title>
<style>{{ style }}</style>
</head>
<body>

<div class="pass">

    <header class="header">

        <div class="logo-box">
            {% if logo_exists %}
            <img class="logo"
                 src="{{ url_for('static', filename=logo_filename) }}"
                 alt="NIET logo">
            {% else %}
            NIET Greater Noida
            {% endif %}
        </div>

        <div class="event-title">
            <div class="small-title">NIET PRESENTS</div>
            <h1>{{ event_name }}</h1>
            <p>{{ subtitle }}</p>
        </div>

        <div class="entry-label">ENTRY PASS</div>

    </header>

    <main class="pass-body">

        <section class="left-panel">

            <div class="participant-label">
                ADMIT ONE - REGISTERED PARTICIPANT
            </div>

            <div class="name">{{ ticket.name }}</div>

            <div class="event-info">

                <div class="event-date">
                    <span class="info-label">EVENT DATE</span>
                    <div class="info-value">
                        {{ ticket.event_date }}
                    </div>
                </div>

                <div class="venue">
                    <span class="info-label">VENUE</span>
                    <div class="info-value">
                        {{ ticket.venue }}
                    </div>
                </div>

            </div>

            <div class="details">

                <div class="item">
                    <small>COURSE</small>
                    <strong>{{ ticket.course }}</strong>
                </div>

                <div class="item">
                    <small>BRANCH</small>
                    <strong>{{ ticket.branch }}</strong>
                </div>

                <div class="item">
                    <small>YEAR OF STUDY</small>
                    <strong>{{ ticket.year }}</strong>
                </div>

            </div>

        </section>

        <div class="separator" aria-hidden="true">
            <span class="circle top"></span>
            <span class="circle bottom"></span>
        </div>

        <aside class="qr-panel">

            <div class="pill">E-PASS</div>

            <h2>GATE VERIFICATION</h2>

            <div class="qr-box">

                <img class="qr-image"
                     src="data:image/png;base64,{{ ticket.qr }}"
                     alt="QR code for pass preview">

                <div class="ticket-number">
                    {{ ticket.id }}
                </div>

            </div>

            <p class="hint">
                Scan this QR code at the NIET entry gate
            </p>

            <div class="preview-note">
                UNOFFICIAL PREVIEW — NOT VALID FOR ENTRY
            </div>

            <button class="button" onclick="window.print()">
                Print / Save PDF
            </button>

        </aside>

    </main>

</div>

</body>
</html>
"""


# =====================================================
# HTML: QR SCAN VERIFICATION PAGE
# =====================================================

VERIFY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pass Preview Details</title>
<style>{{ style }}</style>
</head>
<body>

<div class="verify-card">

    {% if logo_exists %}
    <img class="verify-logo"
         src="{{ url_for('static', filename=logo_filename) }}"
         alt="NIET logo">
    {% else %}
    <h2>NIET Greater Noida</h2>
    {% endif %}

    <div class="status-icon">i</div>

    <h1>Pass Preview</h1>

    <p class="verify-message">
        This QR code displays the information stored
        in the demonstration application.
    </p>

    {% if ticket %}

    <div class="verify-name">{{ ticket.name }}</div>

    <div class="verify-details">

        <div class="verify-row">
            <small>COURSE</small>
            <strong>{{ ticket.course }}</strong>
        </div>

        <div class="verify-row">
            <small>BRANCH</small>
            <strong>{{ ticket.branch }}</strong>
        </div>

        <div class="verify-row">
            <small>YEAR OF STUDY</small>
            <strong>{{ ticket.year }}</strong>
        </div>

        <div class="verify-row">
            <small>EVENT DATE</small>
            <strong>{{ ticket.event_date }}</strong>
        </div>

        <div class="verify-row">
            <small>VENUE</small>
            <strong>{{ ticket.venue }}</strong>
        </div>

        <div class="verify-row">
            <small>TICKET NUMBER</small>
            <strong style="color:#234f91">
                {{ ticket.id }}
            </strong>
        </div>

    </div>

    <div class="verify-note">
        UNOFFICIAL PREVIEW — NOT VALID FOR ENTRY.
        This page does not confirm official ticket
        validity or authorise entry to an event.
    </div>

    <a class="button" href="{{ url_for('home') }}">
        Create Another Preview
    </a>

    {% else %}

    <div class="verify-note">
        This preview ticket could not be found.
        Generate a new preview from the registration page.
    </div>

    {% endif %}

</div>

</body>
</html>
"""


# =====================================================
# HELPERS
# =====================================================

def logo_available():
    logo_path = os.path.join(
        app.static_folder or "static",
        LOGO_FILENAME
    )
    return os.path.isfile(logo_path)


def public_base_url():
    """
    Use Render's public service URL when deployed.
    Locally, fall back to the current request host.
    """
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()

    if render_url:
        return render_url.rstrip("/")

    return request.url_root.rstrip("/")


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


# =====================================================
# HOMEPAGE AND REGISTRATION
# =====================================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "GET":
        return render_template_string(
            FORM_HTML,
            style=STYLE,
            event_name=EVENT_NAME,
            subtitle=EVENT_SUBTITLE,
            venue=DEFAULT_VENUE,
            logo_exists=logo_available(),
            logo_filename=LOGO_FILENAME,
        )

    name = request.form.get("name", "").strip()
    event_date = request.form.get("event_date", "").strip()
    venue = request.form.get("venue", "").strip()
    course = request.form.get("course", "").strip()
    branch = request.form.get("branch", "").strip()
    year = request.form.get("year", "").strip()

    if not all([
        name,
        event_date,
        venue,
        course,
        branch,
        year,
    ]):
        return "Please complete all fields.", 400

    try:
        parsed_date = date.fromisoformat(event_date)
        formatted_date = parsed_date.strftime("%d %b %Y")
    except ValueError:
        return "Invalid event date.", 400

    # Ticket number starts with NIET-
    suffix = secrets.token_hex(5).upper()
    ticket_id = "NIET-" + suffix

    ticket = {
        "id": ticket_id,
        "name": name,
        "event_date": formatted_date,
        "venue": venue,
        "course": course,
        "branch": branch,
        "year": year,
    }

    # Build the public QR verification URL
    verify_path = url_for("verify", ticket_id=ticket_id)
    verify_url = public_base_url() + verify_path

    # Generate QR code
    qr_image = qrcode.make(verify_url)
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")

    ticket["qr"] = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    tickets[ticket_id] = ticket

    return render_template_string(
        PASS_HTML,
        style=STYLE,
        ticket=ticket,
        event_name=EVENT_NAME,
        subtitle=EVENT_SUBTITLE,
        logo_exists=logo_available(),
        logo_filename=LOGO_FILENAME,
    )


# =====================================================
# QR VERIFICATION ROUTE
# =====================================================

@app.route("/verify/<ticket_id>")
def verify(ticket_id):

    ticket = tickets.get(ticket_id)

    if ticket is None:
        return render_template_string(
            VERIFY_HTML,
            style=STYLE,
            ticket=None,
            logo_exists=logo_available(),
            logo_filename=LOGO_FILENAME,
        ), 404

    return render_template_string(
        VERIFY_HTML,
        style=STYLE,
        ticket=ticket,
        logo_exists=logo_available(),
        logo_filename=LOGO_FILENAME,
    )


# =====================================================
# START APPLICATION
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
