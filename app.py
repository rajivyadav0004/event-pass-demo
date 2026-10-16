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

# Logo must exist inside the static folder.
LOGO_PATH = "niet-logo.jpg"

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

.header::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 10px;

    background: repeating-linear-gradient(
        90deg,
        #f2d45d 0px,
        #f2d45d 10px,
        #9cb8f0 10px,
        #9cb8f0 20px,
        #65c5bd 20px,
        #65c5bd 30px
    );
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

/* CONTENT */

.pass-content {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 28px;
    padding: 28px;
}

.left-section {
    position: relative;
    min-width: 0;
    padding-right: 25px;
    border-right: none;
}

/* GOLDEN DOTTED SEPARATOR WITH CIRCLES */

.left-section::after {
    content: "";
    position: absolute;
    top: -28px;
    bottom: -28px;
    right: -14px;
    width: 3px;

    background: repeating-linear-gradient(
        to bottom,
        #d4ad54 0px,
        #d4ad54 9px,
        transparent 9px,
        transparent 19px
    );
}

.left-section::before {
    content: "";
    position: absolute;
    z-index: 2;
    top: -34px;
    right: -23px;

    width: 20px;
    height: 20px;
    border: 3px solid #d4ad54;
    border-radius: 50%;
    background: #f5f8ff;

    box-shadow: 0 calc(100% + 0px) 0 -3px #f5f8ff;
}

/* Separator end circle */

.pass-content {
    position: relative;
}

.separator-end {
    position: absolute;
    z-index: 3;
    left: calc(100% - 314px);
    bottom: 10px;

    width: 20px;
    height: 20px;
    border: 3px solid #d4ad54;
    border-radius: 50%;
    background: #f5f8ff;
    transform: translateX(-50%);
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

/* MOBILE */

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

    .left-section {
        padding-right: 0;
        padding-bottom: 25px;
        border-bottom: 3px dashed #d4ad54;
    }

    .left-section::after,
    .left-section::before,
    .separator-end {
        display: none;
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
                src="{{ url_for('static', filename=logo) }}"
                alt="NIET Greater Noida logo"
                onerror="
                    this.style.display='none';
                    this.nextElementSibling.style.display='block';
                ">

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

        <div class="separator-end"></div>

        <aside class="right-section">

            <div class="epass">E-PASS</div>

            <h2>NIET ENTRY GATE</h2>

            <div class="qr-box">

                <img
                    src="data:image/png;base64,{{ ticket.qr }}"
                    alt="QR code for demo ticket">

                <div class="ticket-number">
                    {{ ticket.id }}
                </div>

            </div>

            <div class="scan-text">
                Scan this QR code at the NIET entry gate.
            </div>

        </aside>

    </main>

</div>

</body>
</html>
"""


# =========================================================
# QR VERIFICATION PAGE
# =========================================================

VERIFY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>NIET Entry Gate - Ticket Lookup</title>

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

.card {
    width: 100%;
    max-width: 480px;
    margin: 25px auto;
    padding: 28px;
    background: white;
    border-radius: 24px;
    border-top: 8px solid #21844d;
    box-shadow: 0 8px 30px #0001;
}

.logo {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 110px;
    margin-bottom: 15px;
}

.logo img {
    display: block;
    width: 100%;
    max-width: 340px;
    height: 110px;
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
    background: #21844d;
    color: white;
    font-size: 70px;
    font-weight: bold;
}

h1 {
    margin: 20px 0 10px;
    color: #18365f;
    text-align: center;
    font-size: 30px;
}

.subtitle {
    margin: 0 0 25px;
    color: #526680;
    text-align: center;
    font-size: 16px;
    line-height: 1.5;
}

.name {
    margin: 25px 0;
    color: #234f91;
    text-align: center;
    font-size: 29px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.details {
    padding: 15px 22px;
    background: #f8fafc;
    border: 2px solid #dce4ee;
    border-radius: 18px;
}

.row {
    padding: 16px 0;
    border-bottom: 1px solid #dce4ee;
    overflow-wrap: anywhere;
}

.row:last-child {
    border-bottom: none;
}

.label {
    display: block;
    margin-bottom: 7px;
    color: #786b65;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

.value {
    color: #30231f;
    font-size: 19px;
    font-weight: bold;
}

.ticket-number {
    color: #a12c45;
    overflow-wrap: anywhere;
}

.notice {
    margin-top: 22px;
    padding: 15px;
    background: #fff3d7;
    color: #765b20;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.6;
    text-align: center;
}

@media (max-width: 420px) {
    body {
        padding: 10px;
    }

    .card {
        padding: 20px;
    }

    h1 {
        font-size: 26px;
    }

    .name {
        font-size: 25px;
    }
}
</style>

</head>

<body>

<div class="card">

    <div class="logo">

        <img
            src="{{ url_for('static', filename=logo) }}"
            alt="NIET Greater Noida logo"
            onerror="this.style.display='none';">

    </div>

    <div class="status-icon">✓</div>

    <h1>NIET ENTRY GATE</h1>

    {% if ticket %}

        <p class="subtitle">
            Ticket information
        </p>

        <h2 class="name">
            {{ ticket.name }}
        </h2>

        <div class="details">

            <div class="row">
                <span class="label">COURSE</span>
                <div class="value">
                    {{ ticket.course }}
                </div>
            </div>

            <div class="row">
                <span class="label">BRANCH</span>
                <div class="value">
                    {{ ticket.branch }}
                </div>
            </div>

            <div class="row">
                <span class="label">YEAR OF STUDY</span>
                <div class="value">
                    {{ ticket.year }}
                </div>
            </div>

            <div class="row">
                <span class="label">VENUE</span>
                <div class="value">
                    {{ venue }}
                </div>
            </div>

            <div class="row">
                <span class="label">EVENT DATE</span>
                <div class="value">
                    {{ ticket.event_date }}
                </div>
            </div>

            <div class="row">
                <span class="label">TICKET NUMBER</span>
                <div class="value ticket-number">
                    {{ ticket.id }}
                </div>
            </div>

        </div>

        <div class="notice">
            This page displays information from the
            demonstration application. Official ticket
            validity must be confirmed by the event organiser.
        </div>

    {% else %}

        <p class="subtitle">
            Ticket not found. This ticket may not exist
            in the current application session.
        </p>

    {% endif %}

</div>

</body>
</html>
"""


# =========================================================
# REGISTRATION FORM
# =========================================================

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>SilverNova 2026 Registration</title>

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

.form-box {
    max-width: 550px;
    margin: 20px auto;
    padding: 25px;
    background: white;
    border-radius: 18px;
    border-top: 8px solid #21844d;
    box-shadow: 0 8px 30px #0001;
}

.logo {
    display: block;
    width: 100%;
    max-width: 320px;
    height: 110px;
    object-fit: contain;
    margin: auto;
}

h2 {
    color: #234f91;
    text-align: center;
}

.subtitle {
    text-align: center;
}

label {
    display: block;
    margin-top: 15px;
    font-weight: bold;
}

input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 16px;
    background: white;
}

button {
    width: 100%;
    padding: 15px;
    margin-top: 22px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
    border: none;
    border-radius: 9px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.notice {
    margin-top: 18px;
    padding: 12px;
    background: #fff3d7;
    color: #765b20;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.5;
}
</style>

</head>

<body>

<div class="form-box">

    <img
        class="logo"
        src="{{ url_for('static', filename=logo) }}"
        alt="NIET Greater Noida logo">

    <h2>{{ event_name }}</h2>

    <p class="subtitle">{{ event_subtitle }}</p>

    <div class="notice">
        Demonstration registration. Official admission
        requires confirmation from the event organiser.
    </div>

    <form method="POST" action="{{ url_for('home') }}">

        <label for="name">Full Name</label>
        <input
            id="name"
            name="name"
            maxlength="100"
            autocomplete="name"
            required>

        <label for="event_date">Event Date</label>
        <input
            id="event_date"
            type="date"
            name="event_date"
            value="2026-10-16"
            required>

        <label for="course">Course</label>
        <select id="course" name="course" required>
            <option value="B.Tech">B.Tech</option>
            <option value="MBA">MBA</option>
            <option value="M.Tech">M.Tech</option>
            <option value="B.Pharm">B.Pharm</option>
        </select>

        <label for="branch">Branch</label>
        <input
            id="branch"
            name="branch"
            placeholder="e.g. Biotechnology"
            maxlength="100"
            required>

        <label for="year">Year of Study</label>
        <select id="year" name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button type="submit">
            Generate Pass Preview
        </button>

    </form>

</div>

</body>
</html>
"""


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        raw_date = request.form.get("event_date", "").strip()
        course = request.form.get("course", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()

        if not all([name, raw_date, course, branch, year]):
            return "Please complete all fields.", 400

        try:
            parsed_date = datetime.strptime(
                raw_date, "%Y-%m-%d"
            )
            formatted_date = parsed_date.strftime("%d %b %Y")

        except ValueError:
            return "Invalid event date.", 400

        ticket_id = "DEMO-" + secrets.token_hex(6).upper()

        ticket = {
            "id": ticket_id,
            "name": name,
            "event_date": formatted_date,
            "course": course,
            "branch": branch,
            "year": year,
        }

        verification_url = url_for(
            "verify",
            ticket_id=ticket_id,
            _external=True
        )

        qr = qrcode.make(verification_url)

        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")

        ticket["qr"] = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        tickets[ticket_id] = ticket

        return render_template_string(
            PASS_HTML,
            ticket=ticket,
            logo=LOGO_PATH,
            event_name=EVENT_NAME,
            event_subtitle=EVENT_SUBTITLE,
            venue=VENUE,
        )

    return render_template_string(
        FORM_HTML,
        logo=LOGO_PATH,
        event_name=EVENT_NAME,
        event_subtitle=EVENT_SUBTITLE,
    )


# =========================================================
# QR VERIFICATION ROUTE
# =========================================================

@app.route("/verify/<ticket_id>")
def verify(ticket_id):

    ticket = tickets.get(ticket_id)

    return render_template_string(
        VERIFY_HTML,
        ticket=ticket,
        logo=LOGO_PATH,
        venue=VENUE,
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
