
import os
import io
import base64
import secrets
from datetime import date

import qrcode
from flask import (
    Flask,
    request,
    render_template_string,
    url_for,
    abort,
)

app = Flask(__name__)

EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
DEFAULT_VENUE = "NIET Plot 19 Campus"
LOGO_FILENAME = "NIET New Engineering Color Logo.jpg"

# Demo records are stored in memory.
# Restarting the server clears the records.
tickets = {}

CSS = """
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 16px;
    background: #eef1f6;
    font-family: Arial, Helvetica, sans-serif;
    color: #18365f;
}

.pass {
    width: 100%;
    max-width: 1500px;
    margin: 10px auto;
    background: #fff9e9;
    border: 4px solid #d6b75b;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 8px 28px #0001;
}

.header {
    position: relative;
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr) 175px;
    gap: 24px;
    align-items: center;
    padding: 22px 28px 34px;
    color: #ffe7a0;
    background: #701329;
    border-top: 7px solid #e8a02d;
}

.header::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 13px;
    background-image:
        radial-gradient(circle, #e8a02d 5px, transparent 5.5px),
        radial-gradient(circle, #fff0c2 5px, transparent 5.5px),
        radial-gradient(circle, #c94b91 5px, transparent 5.5px);
    background-size: 45px 13px;
    background-position: 0 0, 15px 0, 30px 0;
    background-repeat: repeat-x;
}

.logo-box {
    min-height: 105px;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 13px;
}

.logo {
    display: block;
    width: 100%;
    height: 95px;
    object-fit: contain;
}

.event-title {
    min-width: 0;
}

.small-title {
    margin-bottom: 6px;
    font-size: 15px;
    font-weight: bold;
}

.event-title h1 {
    margin: 0;
    font-size: clamp(25px, 3vw, 40px);
    overflow-wrap: anywhere;
}

.event-title p {
    margin: 8px 0 0;
    font-size: 19px;
    font-weight: bold;
}

.entry-label {
    padding: 12px 10px;
    border: 2px solid #d99aab;
    border-radius: 30px;
    text-align: center;
    font-weight: bold;
}

.pass-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 3px 320px;
    gap: 25px;
    padding: 28px;
}

.left-panel {
    min-width: 0;
}

.participant-label {
    margin: 5px 0 18px;
    font-size: 16px;
    font-weight: bold;
}

.name {
    margin: 0 0 26px;
    color: #701329;
    font-size: clamp(28px, 4vw, 48px);
    font-weight: 800;
    overflow-wrap: anywhere;
}

.event-info {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}

.event-date,
.venue {
    min-width: 0;
    min-height: 120px;
    padding: 20px;
    border-radius: 18px;
    color: white;
    overflow-wrap: anywhere;
}

.event-date {
    background: #701329;
}

.venue {
    background: #ed7915;
}

.info-label {
    display: block;
    margin-bottom: 18px;
    font-size: 13px;
    font-weight: bold;
}

.info-value {
    font-size: 21px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.item {
    min-width: 0;
    min-height: 112px;
    padding: 16px;
    border: 2px solid #e1cf9a;
    border-top: 7px solid #e8c65c;
    border-radius: 12px;
    overflow-wrap: anywhere;
}

.item small {
    display: block;
    margin-bottom: 14px;
    color: #786b5e;
    font-size: 12px;
    font-weight: bold;
}

.item strong {
    color: #38131c;
    font-size: 17px;
}

/* Vertical dotted divider */

.separator {
    position: relative;
    align-self: stretch;
    width: 3px;
    margin: -28px 0;
    background: repeating-linear-gradient(
        to bottom,
        #d8b968 0 9px,
        transparent 9px 20px
    );
}

.circle {
    position: absolute;
    left: 50%;
    width: 40px;
    height: 40px;
    border: 3px solid #d8b968;
    border-radius: 50%;
    background: #fff9e9;
    transform: translateX(-50%);
}

.circle.top {
    top: 0;
}

.circle.bottom {
    bottom: 0;
}

/* QR section */

.qr-panel {
    min-width: 0;
    padding-left: 22px;
    border-left: 0;
    text-align: center;
}

.pill {
    display: inline-block;
    margin: 5px 0 18px;
    padding: 12px 32px;
    border-radius: 30px;
    color: white;
    background: #701329;
    font-weight: bold;
}

.qr-panel h2 {
    margin: 5px 0 18px;
    font-size: 20px;
}

.qr-box {
    width: 100%;
    padding: 17px;
    background: #fff1d0;
    border-radius: 20px;
}

.qr-image {
    display: block;
    width: 100%;
    max-width: 250px;
    height: auto;
    margin: auto;
    background: white;
}

.ticket-number {
    margin-top: 14px;
    font-size: 13px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.hint {
    margin-top: 18px;
    color: #71665f;
    line-height: 1.5;
}

.sample-note {
    margin-top: 16px;
    padding: 10px;
    border-radius: 9px;
    background: #fff3d7;
    color: #765b20;
    font-size: 12px;
    font-weight: bold;
    line-height: 1.5;
}

/* Registration and verification cards */

.form-card,
.verify-card {
    width: 100%;
    max-width: 520px;
    margin: 22px auto;
    padding: 26px;
    background: white;
    border-radius: 24px;
    box-shadow: 0 8px 30px #0001;
}

.form-card {
    border-top: 9px solid #701329;
}

.form-logo,
.verify-logo {
    display: block;
    width: 260px;
    max-width: 100%;
    height: 100px;
    margin: 0 auto 18px;
    object-fit: contain;
}

.form-card h1 {
    text-align: center;
    color: #701329;
}

.form-card > p {
    text-align: center;
}

label {
    display: block;
    margin-top: 14px;
    font-weight: bold;
}

input,
select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccc;
    border-radius: 7px;
    font-size: 16px;
    background: white;
}

.button {
    display: block;
    width: 100%;
    padding: 15px;
    margin-top: 20px;
    background: linear-gradient(110deg, #701329, #a83d57);
    color: white;
    text-align: center;
    text-decoration: none;
    border: 0;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

/* QR verification page */

.verify-card {
    max-width: 510px;
    padding: 28px;
    border-top: 10px solid #21834a;
    text-align: center;
}

.status-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 112px;
    height: 112px;
    margin: 20px auto;
    border-radius: 50%;
    background: #21834a;
    color: white;
    font-size: 64px;
    font-weight: bold;
}

.status-icon.invalid {
    background: #a52a3a;
}

.verify-card h1 {
    margin: 8px 0 14px;
    color: #281b1b;
    font-size: 31px;
}

.verify-message {
    color: #493e3e;
    font-size: 17px;
    line-height: 1.5;
}

.verify-name {
    margin: 26px 0 20px;
    color: #18365f;
    font-size: 29px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.verify-details {
    padding: 14px 20px;
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
    margin-top: 20px;
    padding: 15px;
    border-radius: 12px;
    background: #fff3d7;
    color: #765b20;
    font-size: 13px;
    line-height: 1.5;
}

/* Mobile layout */

@media (max-width: 850px) {
    body {
        padding: 8px;
    }

    .header {
        grid-template-columns: 1fr;
        gap: 14px;
        padding: 17px 16px 28px;
        text-align: center;
    }

    .logo-box {
        width: 100%;
        max-width: 320px;
        margin: auto;
    }

    .event-title h1 {
        font-size: 28px;
    }

    .event-title p {
        font-size: 17px;
    }

    .entry-label {
        width: 100%;
        max-width: 220px;
        margin: auto;
    }

    .pass-body {
        grid-template-columns: 1fr;
        gap: 25px;
        padding: 18px;
    }

    .separator {
        display: none;
    }

    .event-info,
    .details {
        grid-template-columns: 1fr;
    }

    .qr-panel {
        padding: 22px 0 0;
        border-top: 3px dashed #d8c48c;
    }

    .qr-box {
        max-width: 330px;
        margin: auto;
    }
}

/* Print layout */

@media print {
    @page {
        size: A4 landscape;
        margin: 6mm;
    }

    body {
        padding: 0;
        background: white;
    }

    .pass {
        max-width: none;
        margin: 0;
        box-shadow: none;
        border-width: 2px;
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }

    .header {
        grid-template-columns: 190px minmax(0, 1fr) 140px;
        gap: 14px;
        padding: 12px 16px 23px;
    }

    .logo {
        height: 70px;
    }

    .logo-box {
        min-height: 78px;
    }

    .event-title h1 {
        font-size: 25px;
    }

    .event-title p {
        font-size: 15px;
    }

    .pass-body {
        grid-template-columns: minmax(0, 1fr) 3px 220px;
        gap: 15px;
        padding: 17px;
    }

    .name {
        font-size: 30px;
        margin-bottom: 17px;
    }

    .event-date,
    .venue {
        min-height: 85px;
        padding: 12px;
    }

    .info-label {
        margin-bottom: 10px;
    }

    .info-value {
        font-size: 16px;
    }

    .item {
        min-height: 80px;
        padding: 9px;
    }

    .item small {
        margin-bottom: 8px;
    }

    .item strong {
        font-size: 13px;
    }

    .qr-box {
        padding: 8px;
    }

    .qr-image {
        max-width: 160px;
    }

    .no-print {
        display: none !important;
    }
}
"""

FORM_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova 2026 - Pass Preview</title>
<style>{{ css }}</style>
</head>
<body>
<div class="form-card">
    {% if logo_exists %}
    <img class="form-logo" src="{{ logo_url }}" alt="NIET logo">
    {% else %}
    <h2 style="text-align:center">NIET Greater Noida</h2>
    {% endif %}

    <h1>{{ event_name }}</h1>
    <p><strong>{{ subtitle }}</strong></p>

    <div class="sample-note">
        SAMPLE PREVIEW — NOT VALID FOR EVENT ENTRY
    </div>

    <form method="post">
        <label for="name">Full Name</label>
        <input id="name" name="name" maxlength="100" required>

        <label for="event_date">Event Date</label>
        <input id="event_date" type="date" name="event_date"
               value="2026-10-16" required>

        <label for="venue">Venue</label>
        <input id="venue" name="venue" value="{{ venue }}"
               maxlength="150" required>

        <label for="course">Course</label>
        <select id="course" name="course" required>
            <option>B. Tech</option>
            <option>M.Tech</option>
            <option>MBA</option>
            <option>B.Pharm</option>
        </select>

        <label for="branch">Branch</label>
        <input id="branch" name="branch" maxlength="100"
               placeholder="e.g. Biotechnology" required>

        <label for="year">Year of Study</label>
        <select id="year" name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button class="button" type="submit">
            Generate Pass Preview
        </button>
    </form>
</div>
</body>
</html>
"""

PASS_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova 2026 - Event Pass Preview</title>
<style>{{ css }}</style>
</head>
<body>
<div class="pass">
    <header class="header">
        <div class="logo-box">
            {% if logo_exists %}
            <img class="logo" src="{{ logo_url }}" alt="NIET logo">
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
                        {{ ticket.event_date_display }}
                    </div>
                </div>

                <div class="venue">
                    <span class="info-label">VENUE</span>
                    <div class="info-value">{{ ticket.venue }}</div>
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

                <div class="ticket-number">{{ ticket.id }}</div>
            </div>

            <p class="hint">
                Scan this QR code to view the saved pass details.
            </p>

            <div class="sample-note">
                SAMPLE PREVIEW — NOT VALID FOR EVENT ENTRY
            </div>

            <button class="button no-print" onclick="window.print()">
                Print / Save PDF
            </button>
        </aside>
    </main>
</div>
</body>
</html>
"""

VERIFY_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pass Preview Details</title>
<style>{{ css }}</style>
</head>
<body>
<div class="verify-card">
    {% if logo_exists %}
    <img class="verify-logo" src="{{ logo_url }}" alt="NIET logo">
    {% else %}
    <h2>NIET Greater Noida</h2>
    {% endif %}

    {% if ticket %}
        <div class="status-icon">✓</div>
        <h1>Ticket Found</h1>

        <p class="verify-message">
            The QR code matches a record in this demonstration app.
        </p>

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
                <small>EVENT</small>
                <strong>{{ ticket.event_date_display }}</strong>
            </div>

            <div class="verify-row">
                <small>TICKET NUMBER</small>
                <strong style="color:#701329">
                    {{ ticket.id }}
                </strong>
            </div>
        </div>

        <div class="verify-note">
            SAMPLE PREVIEW — NOT VALID FOR EVENT ENTRY.
            This page does not confirm official ticket validity.
        </div>

        <a class="button"
           href="{{ url_for('show_pass', ticket_id=ticket.id) }}">
            View e-pass
        </a>

    {% else %}
        <div class="status-icon invalid">×</div>
        <h1>Ticket Not Found</h1>

        <p class="verify-message">
            No matching record was found in this demonstration app.
        </p>

        <a class="button" href="{{ url_for('home') }}">
            Back to registration
        </a>
    {% endif %}
</div>
</body>
</html>
"""


def get_logo_info():
    """Check whether the logo image exists in the static folder."""
    path = os.path.join(
        app.static_folder or "static",
        LOGO_FILENAME
    )

    exists = os.path.isfile(path)

    if exists:
        logo_url = url_for("static", filename=LOGO_FILENAME)
    else:
        logo_url = ""

    return exists, logo_url


def render_page(template, **context):
    """Pass common template variables to each page."""
    logo_exists, logo_url = get_logo_info()

    context.update({
        "css": CSS,
        "logo_exists": logo_exists,
        "logo_url": logo_url,
        "event_name": EVENT_NAME,
        "subtitle": EVENT_SUBTITLE,
        "venue": DEFAULT_VENUE,
    })

    return render_template_string(template, **context)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_page(FORM_HTML)

    name = request.form.get("name", "").strip()
    raw_date = request.form.get("event_date", "").strip()
    venue = request.form.get("venue", "").strip()
    course = request.form.get("course", "").strip()
    branch = request.form.get("branch", "").strip()
    year = request.form.get("year", "").strip()

    if not all([name, raw_date, venue, course, branch, year]):
        return "Please complete every field.", 400

    try:
        parsed_date = date.fromisoformat(raw_date)
    except ValueError:
        return "Please enter a valid event date.", 400

    # Clearly marked sample ticket ID.
    ticket_id = "NIET-PREVIEW-" + secrets.token_hex(5).upper()

    ticket = {
        "id": ticket_id,
        "name": name,
        "event_date": raw_date,
        "event_date_display": parsed_date.strftime("%d %b %Y"),
        "venue": venue,
        "course": course,
        "branch": branch,
        "year": year,
    }

    tickets[ticket_id] = ticket

    # QR code opens the ticket verification route.
    verification_url = url_for(
        "verify",
        ticket_id=ticket_id,
        _external=True
    )

    qr_image = qrcode.make(verification_url)
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")

    ticket["qr"] = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return render_page(PASS_HTML, ticket=ticket)


@app.get("/pass/<ticket_id>")
def show_pass(ticket_id):
    """Display an existing sample pass."""
    ticket = tickets.get(ticket_id)

    if not ticket:
        abort(
            404,
            description="Preview ticket not found. Generate a new preview."
        )

    return render_page(PASS_HTML, ticket=ticket)


@app.route("/verify/<ticket_id>", methods=["GET"])
def verify(ticket_id):
    """
    QR verification route.

    The QR code contains a URL like:
    https://your-domain/verify/NIET-PREVIEW-XXXXXXXXXX
    """
    ticket = tickets.get(ticket_id)

    if ticket is None:
        return render_page(
            VERIFY_HTML,
            ticket=None
        ), 404

    return render_page(
        VERIFY_HTML,
        ticket=ticket
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
