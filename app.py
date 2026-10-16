from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
from datetime import datetime

app = Flask(__name__)

# Demo ticket storage
tickets = {}

# Event configuration
EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
EVENT_DATE = "15 Oct 2026"

# Logo file: static/niet-logo.jpg
LOGO_PATH = "niet-logo.jpg"

MAROON = "#701329"
ORANGE = "#e87516"
CREAM = "#fff9e9"
GOLD = "#d6b75b"


# =====================================================
# EVENT PASS PAGE
# =====================================================

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
    background: #eef1f6;
    font-family: Arial, Helvetica, sans-serif;
    color: #35111b;
}

.pass {
    width: 100%;
    max-width: 1200px;
    margin: 15px auto;
    background: {{ cream }};
    border: 4px solid {{ gold }};
    border-radius: 22px;
    overflow: hidden;
}

/* HEADER */

.header {
    position: relative;
    display: grid;
    grid-template-columns: 270px minmax(0, 1fr) 175px;
    align-items: center;
    gap: 25px;
    padding: 22px 28px;
    background: {{ maroon }};
    color: #ffe7a0;
    border-top: 7px solid #e8a02d;
    border-bottom: 7px solid #e8a02d;
}

/* Colourful decorative strip */

.header::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: -7px;
    height: 7px;
    background: repeating-linear-gradient(
        90deg,
        #e8a02d 0px,
        #e8a02d 10px,
        #fff0c2 10px,
        #fff0c2 17px,
        #a83c78 17px,
        #a83c78 24px,
        #fff0c2 24px,
        #fff0c2 31px
    );
}

/* NIET LOGO */

.logo-box {
    width: 100%;
    min-height: 100px;
    padding: 12px;
    background: white;
    border-radius: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.logo-box img {
    display: block;
    width: 100%;
    max-width: 245px;
    height: 90px;
    object-fit: contain;
}

/* EVENT TITLE */

.event-title {
    min-width: 0;
    font-weight: normal;
}

.present {
    margin-bottom: 8px;
    font-size: 16px;
    font-weight: normal;
    color: #ffe7a0;
}

.event-title h1 {
    margin: 0 0 8px;
    font-size: 34px;
    font-weight: normal;
    color: #ffffff;
}

.event-title p {
    margin: 0;
    font-size: 20px;
    font-weight: normal;
    color: #ffe7a0;
}

.entry-label {
    padding: 14px 10px;
    border: 2px solid #e7b8c4;
    border-radius: 40px;
    text-align: center;
    color: white;
    font-size: 17px;
    font-weight: normal;
}

/* MAIN CONTENT */

.pass-content {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 290px;
    gap: 28px;
    padding: 28px;
}

.left-section {
    min-width: 0;
    padding-right: 25px;
    border-right: 2px dashed {{ gold }};
}

.admit {
    margin-bottom: 18px;
    font-size: 17px;
    font-weight: normal;
}

.name {
    margin-bottom: 25px;
    color: {{ maroon }};
    font-size: 38px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

/* EVENT DATE AND EVENT */

.event-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 22px;
}

.date-box,
.event-box {
    min-height: 115px;
    padding: 22px;
    border-radius: 18px;
    color: white;
}

.date-box {
    background: {{ maroon }};
}

.event-box {
    background: {{ orange }};
}

.field-label {
    margin-bottom: 12px;
    font-size: 12px;
    font-weight: normal;
    opacity: 0.9;
}

.field-value {
    font-size: 20px;
    font-weight: normal;
    overflow-wrap: anywhere;
}

/* COURSE, BRANCH, YEAR */

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.item {
    min-width: 0;
    min-height: 100px;
    padding: 16px;
    border: 2px solid #e0c878;
    border-top: 6px solid #e0c878;
    border-radius: 10px;
    overflow-wrap: anywhere;
}

.item .field-label {
    color: #786b5e;
}

.item .field-value {
    color: #35111b;
    font-size: 17px;
}

/* QR SECTION */

.right-section {
    min-width: 0;
    padding: 0 4px;
    text-align: center;
}

.epass {
    display: inline-block;
    margin-bottom: 18px;
    padding: 12px 35px;
    background: {{ maroon }};
    color: white;
    border-radius: 25px;
    font-size: 15px;
}

.right-section h2 {
    margin: 8px 0 20px;
    color: {{ maroon }};
    font-size: 19px;
    font-weight: normal;
}

.qr-box {
    padding: 18px;
    background: #fff0cf;
    border-radius: 15px;
}

.qr-box img {
    display: block;
    width: 100%;
    max-width: 230px;
    margin: auto;
    background: white;
}

.ticket-number {
    margin-top: 14px;
    color: {{ maroon }};
    font-size: 14px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.scan-text {
    margin: 18px 0;
    color: #786b5e;
    font-size: 13px;
    line-height: 1.5;
}

/* MOBILE RESPONSIVE */

@media (max-width: 760px) {
    body {
        padding: 10px;
    }

    .header {
        grid-template-columns: 1fr;
        gap: 15px;
        padding: 20px;
        text-align: center;
    }

    .logo-box {
        width: 100%;
        max-width: 300px;
        margin: auto;
    }

    .event-title h1 {
        font-size: 28px;
    }

    .event-title p {
        font-size: 18px;
    }

    .pass-content {
        grid-template-columns: 1fr;
        gap: 25px;
        padding: 18px;
    }

    .left-section {
        padding-right: 0;
        padding-bottom: 25px;
        border-right: none;
        border-bottom: 2px dashed {{ gold }};
    }

    .details {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .right-section {
        width: 100%;
        max-width: 320px;
        margin: auto;
    }

    .name {
        font-size: 30px;
    }
}

@media (max-width: 380px) {
    .event-info {
        grid-template-columns: 1fr;
    }

    .details {
        grid-template-columns: 1fr;
    }

    .event-title h1 {
        font-size: 24px;
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
                alt="NIET Greater Noida logo">
        </div>

        <div class="event-title">

            <div class="present">NIET PRESENTS</div>

            <h1>{{ event_name }}</h1>

            <p>{{ event_subtitle }}</p>

        </div>

        <div class="entry-label">
            ENTRY PASS
        </div>

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

                    <div class="field-label">
                        EVENT DATE
                    </div>

                    <div class="field-value">
                        {{ ticket.event_date }}
                    </div>

                </div>

                <div class="event-box">

                    <div class="field-label">
                        EVENT
                    </div>

                    <div class="field-value">
                        {{ event_name }}
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

        <aside class="right-section">

            <div class="epass">E-PASS</div>

            <h2>GATE VERIFICATION</h2>

            <div class="qr-box">

                <img
                    src="data:image/png;base64,{{ ticket.qr }}"
                    alt="Ticket QR code">

                <div class="ticket-number">
                    {{ ticket.id }}
                </div>

            </div>

            <div class="scan-text">
                Scan this QR code at the NIET entry gate
            </div>

        </aside>

    </main>

</div>

</body>
</html>
"""


# =====================================================
# QR VERIFICATION PAGE
# =====================================================

VERIFY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>SilverNova 2026 - Ticket Details</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, Helvetica, sans-serif;
    color: #35111b;
}

.card {
    max-width: 480px;
    margin: 25px auto;
    padding: 28px;
    background: white;
    border-radius: 22px;
    border-top: 10px solid #701329;
    box-shadow: 0 8px 30px #0001;
}

.logo {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
}

.logo img {
    display: block;
    width: 100%;
    max-width: 380px;
    height: 115px;
    object-fit: contain;
}

.name {
    margin: 20px 0 25px;
    color: #172f43;
    text-align: center;
    font-size: 30px;
    overflow-wrap: anywhere;
}

.row {
    padding: 15px;
    margin-top: 10px;
    background: #f5f7fa;
    border: 1px solid #dfe5eb;
    border-radius: 12px;
    overflow-wrap: anywhere;
}

.label {
    display: block;
    margin-bottom: 8px;
    color: #746a67;
    font-size: 13px;
    font-weight: bold;
}

.value {
    font-size: 19px;
    font-weight: bold;
}

.ticket-number {
    color: #701329;
    letter-spacing: 0.5px;
    overflow-wrap: anywhere;
}
</style>

</head>

<body>

<div class="card">

    <div class="logo">
        <img
            src="{{ url_for('static', filename=logo) }}"
            alt="NIET Greater Noida logo">
    </div>

    {% if ticket %}

        <h2 class="name">
            {{ ticket.name }}
        </h2>

        <div class="row">
            <span class="label">COURSE</span>
            <div class="value">{{ ticket.course }}</div>
        </div>

        <div class="row">
            <span class="label">BRANCH</span>
            <div class="value">{{ ticket.branch }}</div>
        </div>

        <div class="row">
            <span class="label">YEAR OF STUDY</span>
            <div class="value">{{ ticket.year }}</div>
        </div>

        <div class="row">
            <span class="label">EVENT</span>
            <div class="value">{{ event_name }}</div>
        </div>

        <div class="row">
            <span class="label">EVENT DATE</span>
            <div class="value">{{ ticket.event_date }}</div>
        </div>

        <div class="row">
            <span class="label">TICKET NUMBER</span>
            <div class="value ticket-number">
                {{ ticket.id }}
            </div>
        </div>

    {% else %}

        <h2 class="name">Ticket Not Found</h2>

        <p>
            This ticket is not available in the current
            demo application session.
        </p>

    {% endif %}

</div>

</body>
</html>
"""


# =====================================================
# REGISTRATION FORM
# =====================================================

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>SilverNova 2026 Registration</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, Helvetica, sans-serif;
    color: #35111b;
}

.form-box {
    max-width: 550px;
    margin: 20px auto;
    padding: 25px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 30px #0001;
    border-top: 8px solid #701329;
}

.logo {
    display: block;
    width: 100%;
    max-width: 320px;
    height: 100px;
    object-fit: contain;
    margin: auto;
}

h2 {
    text-align: center;
    color: #701329;
}

.subtitle {
    text-align: center;
    color: #786b5e;
}

label {
    display: block;
    margin-top: 14px;
    font-weight: bold;
}

input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccc;
    border-radius: 7px;
    font-size: 16px;
    background: white;
}

button {
    width: 100%;
    padding: 14px;
    margin-top: 22px;
    background: #701329;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
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

    <form method="POST" action="{{ url_for('home') }}">

        <label>Full Name</label>
        <input name="name" maxlength="100" required>

        <label>Event Date</label>
        <input
            type="date"
            name="event_date"
            value="2026-10-15"
            required>

        <label>Course</label>
        <select name="course" required>
            <option value="B.Tech">B.Tech</option>
            <option value="MBA">MBA</option>
            <option value="M.Tech">M.Tech</option>
            <option value="B.Pharm">B.Pharm</option>
        </select>

        <label>Branch</label>
        <input
            name="branch"
            placeholder="e.g. Biotechnology"
            maxlength="100"
            required>

        <label>Year of Study</label>
        <select name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button type="submit">
            Generate Demo Pass
        </button>

    </form>

</div>

</body>
</html>
"""


# =====================================================
# HOME ROUTE
# =====================================================

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

        # Generate a unique demo ticket number
        ticket_id = "NIET-" + secrets.token_hex(6).upper()

        ticket = {
            "id": ticket_id,
            "name": name,
            "event_date": formatted_date,
            "course": course,
            "branch": branch,
            "year": year,
        }

        # QR code points to the ticket verification page
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
            maroon=MAROON,
            orange=ORANGE,
            cream=CREAM,
            gold=GOLD,
        )

    return render_template_string(
        FORM_HTML,
        logo=LOGO_PATH,
        event_name=EVENT_NAME,
        event_subtitle=EVENT_SUBTITLE,
    )


# =====================================================
# QR VERIFICATION ROUTE
# =====================================================

@app.route("/verify/<ticket_id>")
def verify(ticket_id):

    ticket = tickets.get(ticket_id)

    return render_template_string(
        VERIFY_HTML,
        ticket=ticket,
        logo=LOGO_PATH,
        event_name=EVENT_NAME,
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
