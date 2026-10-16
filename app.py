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

# Logo ko static folder mein rakhein.
LOGO_FILENAME = "NIET New Engineering Color Logo.jpg"

# Demo records memory mein store hote hain.
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
    background: #f5f8ff;
    border: 4px solid #d4ad54;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 8px 28px #0001;
}

/* Header */
.header {
    position: relative;
    display: grid;
    grid-template-columns: 230px minmax(0, 1fr) 160px;
    gap: 25px;
    align-items: center;
    padding: 22px 25px 34px;
    color: white;
    background: linear-gradient(110deg, #218b89, #3268ad);
    border-top: 7px solid #e8c75a;
}

/* Header ke neeche colourful dotted line */
.header::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 13px;
    background-image:
        radial-gradient(circle, #f2d45d 4px, transparent 4.5px),
        radial-gradient(circle, #9bb8f2 4px, transparent 4.5px),
        radial-gradient(circle, #64c5bd 4px, transparent 4.5px);
    background-size: 40px 13px;
    background-position: 0 0, 13px 0, 26px 0;
    background-repeat: repeat-x;
}

.logo-box {
    min-height: 85px;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 12px;
    color: #18365f;
    font-weight: bold;
    text-align: center;
}

.logo {
    display: block;
    width: 100%;
    height: 75px;
    object-fit: contain;
}

.small-title {
    font-size: 14px;
    font-weight: bold;
}

.event-title h1 {
    margin: 7px 0;
    font-size: clamp(24px, 3vw, 38px);
    overflow-wrap: anywhere;
}

.event-title p {
    margin: 0;
    font-size: 17px;
    font-weight: bold;
}

.entry {
    padding: 12px 8px;
    border: 3px solid #8eafe3;
    border-radius: 40px;
    text-align: center;
    font-size: 14px;
    font-weight: bold;
}

/* Pass ka main layout */
.pass-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 3px 300px;
    gap: 25px;
    padding: 28px;
}

.left {
    min-width: 0;
}

.participant {
    margin: 5px 0 15px;
    color: #234f91;
    font-size: 16px;
    font-weight: bold;
}

.name {
    margin-bottom: 22px;
    font-size: clamp(28px, 4vw, 46px);
    font-weight: 800;
    overflow-wrap: anywhere;
}

.event-info {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 0;
    margin-bottom: 22px;
}

.info-box {
    min-width: 0;
    min-height: 105px;
    padding: 18px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    border-radius: 18px;
    overflow-wrap: anywhere;
}

.info-label {
    display: block;
    margin-bottom: 16px;
    font-size: 12px;
    font-weight: bold;
}

.info-value {
    font-size: 18px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.detail {
    min-width: 0;
    min-height: 100px;
    padding: 14px;
    background: #eaf1ff;
    border: 2px solid #d7c28c;
    border-top: 7px solid #e8c75a;
    border-radius: 12px;
    overflow-wrap: anywhere;
}

.detail small {
    display: block;
    margin-bottom: 14px;
    color: #526680;
    font-size: 12px;
    font-weight: bold;
}

.detail strong {
    font-size: 15px;
}

/* Golden dotted vertical divider */
.separator {
    position: relative;
    align-self: stretch;
    width: 3px;
    margin: -28px 0;
    background: repeating-linear-gradient(
        to bottom,
        #d4ad54 0 8px,
        transparent 8px 18px
    );
}

.circle {
    position: absolute;
    left: 50%;
    width: 30px;
    height: 30px;
    border: 2px solid #d4ad54;
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

/* QR panel */
.qr-panel {
    min-width: 0;
    text-align: center;
}

.pill {
    display: inline-block;
    padding: 10px 24px;
    margin: 4px 0 18px;
    border-radius: 35px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    font-weight: bold;
    font-size: 14px;
}

.qr-panel h2 {
    margin: 5px 0 20px;
    color: #234f91;
    font-size: 19px;
}

.qr-box {
    padding: 18px;
    background: #eaf1ff;
    border-radius: 22px;
}

.qr-image {
    display: block;
    width: 100%;
    max-width: 250px;
    height: auto;
    margin: auto;
    padding: 7px;
    background: white;
}

.ticket-number {
    margin-top: 12px;
    color: #234f91;
    font-size: 14px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.hint {
    margin: 18px 0 0;
    color: #687b95;
    font-size: 14px;
    line-height: 1.6;
}

.sample-label {
    margin-top: 14px;
    color: #765b20;
    font-size: 11px;
    font-weight: bold;
}

/* Registration form and verification page */
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
    border-top: 8px solid #21834a;
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
    color: #234f91;
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
    padding: 14px;
    margin-top: 18px;
    border: 0;
    border-radius: 10px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
    font-size: 15px;
    font-weight: bold;
    text-align: center;
    text-decoration: none;
    cursor: pointer;
}

.verify-card {
    max-width: 510px;
    border-top: 9px solid #21834a;
    text-align: center;
}

.status-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100px;
    height: 100px;
    margin: 20px auto;
    border-radius: 50%;
    background: #21834a;
    color: white;
    font-size: 60px;
    font-weight: bold;
}

.status-icon.invalid {
    background: #a52a3a;
}

.verify-card h1 {
    margin: 8px 0 14px;
    color: #281b1b;
    font-size: 30px;
}

.verify-message {
    color: #493e3e;
    font-size: 16px;
    line-height: 1.5;
}

.verify-name {
    margin: 24px 0 18px;
    color: #18365f;
    font-size: 26px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.verify-details {
    padding: 12px 18px;
    border: 2px solid #dce4ee;
    border-radius: 16px;
    background: #f8fafc;
    text-align: left;
}

.verify-row {
    padding: 13px 0;
    border-bottom: 1px solid #dce4ee;
    overflow-wrap: anywhere;
}

.verify-row:last-child {
    border-bottom: none;
}

.verify-row small {
    display: block;
    margin-bottom: 6px;
    color: #746a67;
    font-size: 12px;
    font-weight: bold;
}

.verify-row strong {
    font-size: 17px;
}

.verify-note {
    margin-top: 18px;
    padding: 13px;
    border-radius: 12px;
    background: #e5f5e9;
    color: #27633b;
    font-size: 13px;
    line-height: 1.5;
}

/* Mobile view */
@media (max-width: 850px) {
    body {
        padding: 8px;
    }

    .header {
        grid-template-columns: 1fr;
        gap: 14px;
        padding: 16px 15px 28px;
        text-align: center;
    }

    .logo-box {
        width: 100%;
        max-width: 300px;
        margin: auto;
    }

    .event-title h1 {
        font-size: 27px;
    }

    .event-title p {
        font-size: 16px;
    }

    .entry {
        width: 100%;
        max-width: 200px;
        margin: auto;
    }

    .pass-body {
        grid-template-columns: 1fr;
        gap: 22px;
        padding: 17px;
    }

    .separator {
        display: none;
    }

    .event-info,
    .details {
        grid-template-columns: 1fr;
        gap: 10px;
    }

    .qr-panel {
        padding-top: 20px;
        border-top: 3px dashed #d4ad54;
    }

    .qr-box {
        max-width: 350px;
        margin: auto;
    }
}

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
        grid-template-columns: 180px minmax(0, 1fr) 130px;
        gap: 14px;
        padding: 10px 14px 23px;
    }

    .logo {
        height: 65px;
    }

    .logo-box {
        min-height: 72px;
    }

    .pass-body {
        grid-template-columns: minmax(0, 1fr) 3px 220px;
        gap: 15px;
        padding: 16px;
    }

    .name {
        font-size: 30px;
        margin-bottom: 16px;
    }

    .info-box {
        min-height: 75px;
        padding: 10px;
    }

    .info-label {
        margin-bottom: 8px;
    }

    .info-value {
        font-size: 15px;
    }

    .detail {
        min-height: 70px;
        padding: 8px;
    }

    .detail small {
        margin-bottom: 7px;
    }

    .detail strong {
        font-size: 12px;
    }

    .qr-box {
        padding: 8px;
    }

    .qr-image {
        max-width: 155px;
    }
}
"""


FORM_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SilverNova 2026 - Sample Pass</title>
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
    <p class="sample-label">SAMPLE PASS — NOT AN OFFICIAL EVENT TICKET</p>

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

        <button class="button" type="submit">Generate Sample Pass</button>
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
    <title>SilverNova 2026 - Sample Pass</title>
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

        <div class="entry">SAMPLE PASS</div>
    </header>

    <main class="pass-body">
        <section class="left">
            <div class="participant">SAMPLE PARTICIPANT PASS</div>
            <div class="name">{{ ticket.name }}</div>

            <div class="event-info">
                <div class="info-box">
                    <span class="info-label">EVENT DATE</span>
                    <div class="info-value">
                        {{ ticket.event_date_display }}
                    </div>
                </div>

                <div class="info-box">
                    <span class="info-label">VENUE</span>
                    <div class="info-value">{{ ticket.venue }}</div>
                </div>
            </div>

            <div class="details">
                <div class="detail">
                    <small>COURSE</small>
                    <strong>{{ ticket.course }}</strong>
                </div>
                <div class="detail">
                    <small>BRANCH</small>
                    <strong>{{ ticket.branch }}</strong>
                </div>
                <div class="detail">
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
                     alt="Sample QR code">

                <div class="ticket-number">{{ ticket.id }}</div>
            </div>

            <p class="hint">
                Scan this QR code at the NIET entry gate
            </p>
            <p class="sample-label">SAMPLE RECORD</p>
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
    <title>QR Record - SilverNova 2026</title>
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
            This QR code matches a saved sample record for the
            SilverNova Garba &amp; DJ Night event.
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
                <strong style="color:#701329">{{ ticket.id }}</strong>
            </div>
        </div>

        <div class="verify-note">
            This is a sample record, not official ticket verification.
            Event entry must be confirmed by the authorised organiser.
        </div>

        <a class="button"
           href="{{ url_for('show_pass', ticket_id=ticket.id) }}">
            View sample e-pass
        </a>

    {% else %}
        <div class="status-icon invalid">×</div>
        <h1>Record Not Found</h1>
        <p class="verify-message">
            No matching sample record was found.
        </p>
        <a class="button" href="{{ url_for('home') }}">
            Back to registration
        </a>
    {% endif %}
</div>
</body>
</html>
"""


def logo_info():
    """Static folder mein logo file check karta hai."""
    path = os.path.join(app.static_folder or "static", LOGO_FILENAME)

    if os.path.isfile(path):
        return True, url_for("static", filename=LOGO_FILENAME)

    return False, ""


def render_page(template, **context):
    """Common variables ke saath HTML page render karta hai."""
    exists, logo_url = logo_info()

    context.update({
        "css": CSS,
        "logo_exists": exists,
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

    fields = {
        "name": request.form.get("name", "").strip(),
        "event_date": request.form.get("event_date", "").strip(),
        "venue": request.form.get("venue", "").strip(),
        "course": request.form.get("course", "").strip(),
        "branch": request.form.get("branch", "").strip(),
        "year": request.form.get("year", "").strip(),
    }

    if not all(fields.values()):
        return "Please complete every field.", 400

    try:
        parsed_date = date.fromisoformat(fields["event_date"])
    except ValueError:
        return "Please enter a valid event date.", 400

    # Unique sample ticket number.
    ticket_id = "NIET-SAMPLE-" + secrets.token_hex(5).upper()

    ticket = {
        **fields,
        "id": ticket_id,
        "event_date_display": parsed_date.strftime("%d %b %Y"),
    }

    tickets[ticket_id] = ticket

    # QR mein isi app ka verification URL store hota hai.
    verification_url = url_for(
        "verify",
        ticket_id=ticket_id,
        _external=True,
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
    ticket = tickets.get(ticket_id)

    if not ticket:
        abort(404, description="Sample pass not found.")

    return render_page(PASS_HTML, ticket=ticket)


@app.get("/verify/<ticket_id>")
def verify(ticket_id):
    ticket = tickets.get(ticket_id)

    if ticket is None:
        return render_page(VERIFY_HTML, ticket=None), 404

    return render_page(VERIFY_HTML, ticket=ticket), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        debug=False,
    )
