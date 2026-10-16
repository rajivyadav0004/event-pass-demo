from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
from datetime import datetime

app = Flask(__name__)

# Demo storage
tickets = {}

# Event configuration
EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
EVENT_DATE = "15 Oct 2026"

LOGO_PATH = "NIET New Engineering Color Logo.jpg"


# ==================================================
# LANDSCAPE EVENT PASS
# ==================================================

PASS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Event Pass Demo</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, sans-serif;
    color: #701329;
}

.pass {
    width: 100%;
    max-width: 1200px;
    margin: 15px auto;
    background: #fff9e9;
    border: 4px solid #d6b75b;
    border-radius: 22px;
    overflow: hidden;
    position: relative;
}

.demo-label {
    text-align: center;
    padding: 6px;
    background: #fff0c2;
    color: #701329;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}

.header {
    display: grid;
    grid-template-columns: 270px 1fr 175px;
    align-items: center;
    gap: 25px;
    padding: 22px 28px;
    background: #701329;
    color: #ffe7a0;
    border-bottom: 7px solid #e8a02d;
}

.logo-box {
    background: white;
    border-radius: 14px;
    padding: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100px;
}

.logo-box img {
    width: 100%;
    max-width: 245px;
    height: 90px;
    object-fit: contain;
}

.event-title {
    font-weight: normal;
}

.event-title .present {
    font-size: 16px;
    margin-bottom: 8px;
}

.event-title h1 {
    font-size: 34px;
    font-weight: normal;
    margin: 0 0 8px;
}

.event-title p {
    font-size: 20px;
    font-weight: normal;
    margin: 0;
}

.entry-label {
    text-align: center;
    border: 2px solid #e7b8c4;
    border-radius: 40px;
    padding: 14px 10px;
    font-size: 17px;
    font-weight: normal;
}

.pass-content {
    display: grid;
    grid-template-columns: 1fr 290px;
    gap: 28px;
    padding: 28px;
}

.left-section {
    padding-right: 25px;
    border-right: 2px dashed #d6b75b;
}

.admit {
    font-size: 17px;
    margin-bottom: 18px;
    font-weight: normal;
}

.name {
    font-size: 38px;
    font-weight: bold;
    overflow-wrap: anywhere;
    margin-bottom: 25px;
}

.event-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 22px;
}

.date-box,
.event-box {
    padding: 22px;
    border-radius: 18px;
    color: white;
    background: #701329;
    min-height: 115px;
}

.event-box {
    background: #e87516;
}

.field-label {
    font-size: 12px;
    margin-bottom: 12px;
    color: inherit;
    opacity: 0.85;
}

.field-value {
    font-size: 20px;
    overflow-wrap: anywhere;
}

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.item {
    padding: 16px;
    min-height: 100px;
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

.right-section {
    text-align: center;
    padding: 0 4px;
}

.epass {
    display: inline-block;
    background: #701329;
    color: white;
    border-radius: 25px;
    padding: 12px 35px;
    margin-bottom: 18px;
    font-size: 15px;
}

.right-section h2 {
    font-size: 19px;
    font-weight: normal;
    margin: 8px 0 20px;
}

.qr-box {
    padding: 18px;
    border-radius: 15px;
    background: #fff0cf;
}

.qr-box img {
    display: block;
    width: 100%;
    max-width: 230px;
    margin: auto;
    background: white;
}

.ticket-number {
    font-size: 14px;
    font-weight: bold;
    margin-top: 14px;
    overflow-wrap: anywhere;
}

.scan-text {
    margin: 18px 0;
    color: #786b5e;
    font-size: 13px;
    line-height: 1.5;
}

.btn {
    display: block;
    width: 100%;
    padding: 13px;
    margin-top: 12px;
    background: #701329;
    color: white;
    border-radius: 7px;
    text-decoration: none;
    font-size: 14px;
}

button {
    display: block;
    width: calc(100% - 56px);
    margin: 0 28px 25px;
    padding: 14px;
    border: none;
    border-radius: 8px;
    background: #701329;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

@media (max-width: 760px) {
    .header {
        grid-template-columns: 1fr;
        text-align: center;
        gap: 15px;
    }

    .logo-box {
        max-width: 300px;
        width: 100%;
        margin: auto;
    }

    .event-title h1 {
        font-size: 28px;
    }

    .pass-content {
        grid-template-columns: 1fr;
    }

    .left-section {
        border-right: none;
        border-bottom: 2px dashed #d6b75b;
        padding-right: 0;
        padding-bottom: 25px;
    }

    .details {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .right-section {
        max-width: 320px;
        width: 100%;
        margin: auto;
    }
}

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
        border-radius: 12px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    .pass-content {
        grid-template-columns: 1fr 250px;
        gap: 18px;
        padding: 20px;
    }

    .header {
        grid-template-columns: 230px 1fr 150px;
        padding: 16px 20px;
        gap: 18px;
    }

    .logo-box img {
        height: 75px;
    }

    .event-title h1 {
        font-size: 28px;
    }

    .name {
        font-size: 30px;
    }

    .item {
        padding: 12px;
        min-height: 80px;
    }

    button,
    .btn {
        display: none;
    }
}
</style>
</head>

<body>

<div class="pass">

    <div class="demo-label">
        DEMO PASS — NOT VALID FOR ENTRY
    </div>

    <div class="header">

        <div class="logo-box">
            <img
                src="{{ url_for('static', filename=logo) }}"
                alt="NIET logo">
        </div>

        <div class="event-title">
            <div class="present">NIET PRESENTS</div>
            <h1>{{ event_name }}</h1>
            <p>{{ event_subtitle }}</p>
        </div>

        <div class="entry-label">
            ENTRY PASS
        </div>

    </div>

    <div class="pass-content">

        <div class="left-section">

            <div class="admit">
                ADMIT ONE - REGISTERED PARTICIPANT
            </div>

            <div class="name">{{ ticket.name }}</div>

            <div class="event-info">

                <div class="date-box">
                    <div class="field-label">EVENT DATE</div>
                    <div class="field-value">
                        {{ ticket.event_date }}
                    </div>
                </div>

                <div class="event-box">
                    <div class="field-label">EVENT</div>
                    <div class="field-value">
                        {{ event_name }}
                    </div>
                </div>

            </div>

            <div class="details">

                <div class="item">
                    <div class="field-label">COURSE</div>
                    <div class="field-value">{{ ticket.course }}</div>
                </div>

                <div class="item">
                    <div class="field-label">BRANCH</div>
                    <div class="field-value">{{ ticket.branch }}</div>
                </div>

                <div class="item">
                    <div class="field-label">YEAR OF STUDY</div>
                    <div class="field-value">{{ ticket.year }}</div>
                </div>

            </div>

        </div>

        <div class="right-section">

            <div class="epass">E-PASS</div>

            <h2>GATE VERIFICATION</h2>

            <div class="qr-box">

                <img
                    src="data:image/png;base64,{{ ticket.qr }}"
                    alt="Demo QR code">

                <div class="ticket-number">
                    {{ ticket.id }}
                </div>

            </div>

            <div class="scan-text">
                Scan this QR code to view demo registration details.
            </div>

            <a class="btn"
               href="{{ url_for('verify', ticket_id=ticket.id) }}">
                Open verification page
            </a>

        </div>

    </div>

    <button onclick="window.print()">
        Print / Save PDF
    </button>

</div>

</body>
</html>
"""


# ==================================================
# QR SCANNER VERIFICATION PAGE
# ==================================================

VERIFY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Demo Ticket Verification</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, sans-serif;
    color: #35111b;
}

.card {
    max-width: 650px;
    margin: 20px auto;
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
    width: 100%;
    max-width: 380px;
    height: 115px;
    object-fit: contain;
}

.demo-label {
    text-align: center;
    padding: 8px;
    background: #fff0c2;
    color: #701329;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    margin-bottom: 22px;
}

.name {
    text-align: center;
    font-size: 30px;
    color: #172f43;
    margin: 15px 0 25px;
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
    color: #746a67;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 8px;
}

.value {
    font-size: 20px;
    font-weight: bold;
}

.ticket-number {
    color: #701329;
    letter-spacing: 1px;
}

.back {
    display: block;
    padding: 15px;
    margin-top: 25px;
    background: #f3e8d8;
    color: #35111b;
    border-radius: 10px;
    text-align: center;
    text-decoration: none;
    font-weight: bold;
}

@media (min-width: 700px) {
    .details {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
}

@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    body {
        background: white;
    }

    .card {
        max-width: none;
        box-shadow: none;
    }

    .back {
        display: none;
    }
}
</style>
</head>

<body>

<div class="card">

    <div class="logo">
        <img
            src="{{ url_for('static', filename=logo) }}"
            alt="NIET logo">
    </div>

    <div class="demo-label">
        DEMO VERIFICATION — NOT AN OFFICIAL ENTRY CONFIRMATION
    </div>

    {% if ticket %}

        <h2 class="name">{{ ticket.name }}</h2>

        <div class="details">

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

        </div>

    {% else %}

        <h2 class="name">Ticket not found</h2>

        <p>
            This demo ticket could not be found.
            Please generate a new demo pass.
        </p>

    {% endif %}

    <a class="back" href="{{ url_for('home') }}">
        Back to registration
    </a>

</div>

</body>
</html>
"""


# ==================================================
# REGISTRATION FORM
# ==================================================

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Event Pass Registration Demo</title>

<style>
body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, sans-serif;
    color: #35111b;
}

.form-box {
    max-width: 550px;
    margin: 20px auto;
    padding: 25px;
    background: white;
    border-radius: 16px;
}

.logo {
    display: block;
    width: 100%;
    max-width: 320px;
    height: 100px;
    object-fit: contain;
    margin: auto;
}

.demo-label {
    text-align: center;
    font-size: 12px;
    font-weight: bold;
    color: #701329;
    margin: 12px 0;
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
}

button {
    width: 100%;
    padding: 14px;
    margin-top: 20px;
    background: #701329;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
}
</style>

</head>

<body>

<div class="form-box">

    <img class="logo"
         src="{{ url_for('static', filename=logo) }}"
         alt="NIET logo">

    <div class="demo-label">
        EVENT PASS DEMO
    </div>

    <h2>Registration Form</h2>

    <form method="POST">

        <label>Full Name</label>
        <input name="name" maxlength="100" required>

        <label>Event Date</label>
        <input type="date" name="event_date"
               value="2026-10-15" required>

        <label>Course</label>
        <select name="course" required>
            <option value="B.Tech">B.Tech</option>
            <option value="MBA">MBA</option>
            <option value="M.Tech">M.Tech</option>
            <option value="B.Pharm">B.Pharm</option>
        </select>

        <label>Branch</label>
        <input name="branch"
               placeholder="e.g. Biotechnology"
               maxlength="100" required>

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


# ==================================================
# HOME ROUTE
# ==================================================

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
            formatted_date = datetime.strptime(
                raw_date, "%Y-%m-%d"
            ).strftime("%d %b %Y")
        except ValueError:
            return "Invalid event date.", 400

        # Demo ticket number
        ticket_id = "NIET-" + secrets.token_hex(6).upper()

        ticket = {
            "id": ticket_id,
            "name": name,
            "event_date": formatted_date,
            "course": course,
            "branch": branch,
            "year": year,
        }

        # Generate QR containing verification URL
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
            event_subtitle=EVENT_SUBTITLE
        )

    return render_template_string(
        FORM_HTML,
        logo=LOGO_PATH
    )


# ==================================================
# QR VERIFICATION ROUTE
# ==================================================

@app.route("/verify/<ticket_id>")
def verify(ticket_id):

    ticket = tickets.get(ticket_id)

    return render_template_string(
        VERIFY_HTML,
        ticket=ticket,
        logo=LOGO_PATH,
        event_name=EVENT_NAME
    )


# ==================================================
# RUN APP
# ==================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
