
from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
from datetime import date

app = Flask(__name__)
tickets = {}

LOGO = "NIET New Engineering Color Logo.jpg"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NIET SILVERNOVA 2026 - Entry Pass</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, sans-serif;
    color: #64152a;
}

.pass {
    width: 100%;
    max-width: 1200px;
    margin: 20px auto;
    background: #fff9e9;
    border: 4px solid #d6b75b;
    border-radius: 22px;
    overflow: hidden;
    box-shadow: 0 12px 35px #0001;
}

.header {
    background: #701329;
    color: #ffe7a0;
    padding: 20px 28px;
    border-bottom: 7px solid #e8a02d;
    display: flex;
    align-items: center;
    gap: 28px;
}

.logo-box {
    flex: 0 0 250px;
    background: white;
    border-radius: 12px;
    padding: 8px;
    text-align: center;
}

.logo {
    display: block;
    width: 100%;
    max-height: 110px;
    object-fit: contain;
}

.event-title {
    flex: 1;
}

.event-title .small-title {
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 5px;
}

.event-title h1 {
    font-size: 32px;
    margin: 0;
    font-weight: 800;
}

.event-title p {
    margin: 8px 0 0;
    font-size: 19px;
    font-weight: bold;
}

.entry-label {
    border: 2px solid #d99aab;
    border-radius: 30px;
    padding: 13px 22px;
    font-weight: bold;
    white-space: nowrap;
}

.dots {
    height: 14px;
    background: repeating-linear-gradient(
        90deg,
        #701329 0 12px,
        #e8a02d 12px 20px,
        #fff9e9 20px 28px,
        #c94b91 28px 36px
    );
}

.pass-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 30px;
    padding: 28px;
}

.participant-label {
    font-size: 17px;
    font-weight: bold;
    margin-bottom: 18px;
}

.name {
    font-size: clamp(28px, 4vw, 48px);
    font-weight: 800;
    color: #701329;
    overflow-wrap: anywhere;
    margin-bottom: 28px;
}

.event-info {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}

.event-date, .venue {
    padding: 20px;
    border-radius: 20px;
    color: white;
    min-height: 120px;
}

.event-date { background: #701329; }
.venue { background: #ed7915; }

.info-label {
    display: block;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 18px;
    opacity: .9;
}

.info-value {
    font-size: 22px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.item {
    padding: 17px;
    border: 2px solid #e1cf9a;
    border-top: 7px solid #e8c65c;
    border-radius: 12px;
    min-width: 0;
    overflow-wrap: anywhere;
}

.item small {
    display: block;
    font-size: 12px;
    font-weight: bold;
    color: #786b5e;
    margin-bottom: 15px;
}

.item strong {
    font-size: 18px;
    color: #38131c;
}

.qr-panel {
    border-left: 3px dashed #d8c48c;
    padding-left: 25px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.pill {
    background: #701329;
    color: white;
    border-radius: 30px;
    padding: 12px 35px;
    font-weight: bold;
    margin-bottom: 18px;
}

.qr-panel h2 {
    font-size: 21px;
    margin: 5px 0 20px;
}

.qr-box {
    background: #fff1d0;
    padding: 18px;
    border-radius: 20px;
    width: 100%;
}

.qr-box img {
    display: block;
    width: 100%;
    max-width: 250px;
    margin: auto;
    background: white;
}

.ticket-number {
    font-size: 13px;
    font-weight: bold;
    overflow-wrap: anywhere;
    margin-top: 14px;
}

.hint {
    color: #71665f;
    line-height: 1.5;
    margin-top: 20px;
}

.btn {
    display: block;
    width: 100%;
    padding: 14px;
    margin-top: 14px;
    background: #701329;
    color: white;
    text-align: center;
    text-decoration: none;
    border: 0;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    font-size: 15px;
}

.form-box {
    max-width: 650px;
    margin: 25px auto;
    padding: 25px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 30px #0001;
}

.form-logo {
    width: 190px;
    max-width: 100%;
    display: block;
    margin: 0 auto 18px;
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

@media (max-width: 760px) {
    body { padding: 8px; }

    .header {
        padding: 16px;
        flex-wrap: wrap;
        gap: 14px;
    }

    .logo-box {
        flex-basis: 150px;
    }

    .logo { max-height: 75px; }

    .event-title { min-width: 150px; }

    .event-title h1 { font-size: 23px; }
    .event-title p { font-size: 14px; }
    .event-title .small-title { font-size: 12px; }
    .entry-label { padding: 9px 14px; font-size: 12px; }

    .pass-body {
        grid-template-columns: 1fr;
        padding: 18px;
        gap: 24px;
    }

    .name { margin-bottom: 20px; }

    .event-info { grid-template-columns: 1fr; }

    .event-date, .venue { min-height: auto; }

    .details { grid-template-columns: repeat(2, minmax(0, 1fr)); }

    .qr-panel {
        border-left: 0;
        border-top: 3px dashed #d8c48c;
        padding: 24px 0 0;
    }

    .qr-box { max-width: 330px; }
}

@media print {
    @page { size: A4 landscape; margin: 7mm; }

    body { padding: 0; background: white; }

    .pass {
        max-width: none;
        width: 100%;
        margin: 0;
        box-shadow: none;
        border-width: 2px;
        border-radius: 10px;
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }

    .header { padding: 12px 18px; gap: 18px; }
    .logo-box { flex-basis: 190px; }
    .logo { max-height: 75px; }
    .event-title h1 { font-size: 25px; }
    .event-title p { font-size: 15px; }

    .pass-body {
        grid-template-columns: minmax(0, 1fr) 235px;
        gap: 16px;
        padding: 18px;
    }

    .name { font-size: 32px; margin-bottom: 18px; }
    .event-date, .venue { padding: 13px; min-height: 85px; }
    .info-value { font-size: 17px; }
    .item { padding: 10px; }
    .item strong { font-size: 14px; }
    .qr-panel { border-left: 2px dashed #d8c48c; border-top: 0; padding: 0 0 0 16px; }
    .qr-box { padding: 10px; }
    .qr-box img { max-width: 175px; }
    .btn, .no-print { display: none !important; }
}
</style>
</head>
<body>

{% if ticket %}
<div class="pass">
    <div class="header">
        <div class="logo-box">
            <img class="logo"
                 src="{{ url_for('static', filename='NIET New Engineering Color Logo.jpg') }}"
                 alt="NIET Greater Noida Logo">
        </div>

        <div class="event-title">
            <div class="small-title">NIET PRESENTS</div>
            <h1>SILVERNOVA 2026</h1>
            <p>GARBA &amp; DJ NIGHT</p>
        </div>

        <div class="entry-label">ENTRY PASS</div>
    </div>

    <div class="dots"></div>

    <div class="pass-body">
        <div class="left-panel">
            <div class="participant-label">
                ADMIT ONE - REGISTERED PARTICIPANT
            </div>

            <div class="name">{{ ticket.name }}</div>

            <div class="event-info">
                <div class="event-date">
                    <span class="info-label">EVENT DATE</span>
                    <div class="info-value">{{ ticket.event_date }}</div>
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
        </div>

        <div class="qr-panel">
            <div class="pill">E-PASS</div>
            <h2>GATE VERIFICATION</h2>

            <div class="qr-box">
                <img src="data:image/png;base64,{{ ticket.qr }}"
                     alt="QR verification code">

                <div class="ticket-number">{{ ticket.id }}</div>
            </div>

            <p class="hint">Scan this QR code to check ticket status.</p>

            <a class="btn" href="{{ url_for('verify', ticket_id=ticket.id) }}">
                Open verification page
            </a>

            <button class="btn no-print" onclick="window.print()">
                Print / Save PDF
            </button>
        </div>
    </div>
</div>

{% else %}
<div class="form-box">
    <img class="form-logo"
         src="{{ url_for('static', filename='NIET New Engineering Color Logo.jpg') }}"
         alt="NIET Logo">

    <h2>NIET Event Pass Registration</h2>

    <form method="POST" action="{{ url_for('home') }}">
        <label>Full Name</label>
        <input name="name" required maxlength="100">

        <label>Event Date</label>
        <input type="date" name="event_date" required>

        <label>Venue</label>
        <input name="venue" value="NIET Plot 19 Campus"
               required maxlength="150">

        <label>Course</label>
        <select name="course" required>
            <option value="BTech">B.Tech</option>
            <option value="MBA">MBA</option>
            <option value="MTech">M.Tech</option>
            <option value="BPharm">B.Pharm</option>
        </select>

        <label>Branch</label>
        <input name="branch" placeholder="e.g. Biotechnology"
               required maxlength="100">

        <label>Year of Study</label>
        <select name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button class="btn" type="submit">Generate Event Pass</button>
    </form>
</div>
{% endif %}

</body>
</html>
"""

VERIFY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NIET Ticket Verification</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 22px;
    background: #eef1f6;
    font-family: Arial, sans-serif;
    color: #281b1b;
}

.card {
    max-width: 510px;
    margin: 20px auto;
    padding: 28px;
    background: white;
    border-radius: 25px;
    border-top: 12px solid #701329;
    box-shadow: 0 12px 35px #0001;
    text-align: center;
}

.logo {
    width: 260px;
    max-width: 100%;
    height: auto;
    object-fit: contain;
    margin: 5px auto 20px;
}

.status {
    font-size: 35px;
    font-weight: 800;
    margin: 22px 0 12px;
}

.ok { color: #16834a; }
.bad { color: #701329; }

.message {
    font-size: 17px;
    line-height: 1.5;
}

.person {
    font-size: 30px;
    color: #172d42;
    overflow-wrap: anywhere;
    margin: 28px 0 20px;
}

.row {
    text-align: left;
    padding: 16px;
    margin-top: 10px;
    background: #f5f7fa;
    border: 1px solid #dce3eb;
    border-radius: 13px;
    overflow-wrap: anywhere;
}

.row small {
    display: block;
    color: #746a67;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 8px;
}

.row strong { font-size: 18px; }

.btn {
    display: block;
    width: 100%;
    padding: 17px;
    margin-top: 24px;
    background: #f1e8dc;
    color: #281b1b;
    border-radius: 12px;
    text-decoration: none;
    font-size: 18px;
    font-weight: bold;
}

@media print {
    @page { size: A4 portrait; margin: 10mm; }
    body { padding: 0; background: white; }
    .card { box-shadow: none; }
    .btn { display: none; }
}
</style>
</head>

<body>
<div class="card">

    <img class="logo"
         src="{{ url_for('static', filename='NIET New Engineering Color Logo.jpg') }}"
         alt="NIET Greater Noida Logo">

    {% if ticket and expired %}
        <div style="font-size:100px; color:#701329; font-weight:bold;">
            ×
        </div>

        <div class="status bad">Ticket expired</div>

        <p class="message">
            This ticket expired on <strong>{{ ticket.event_date }}</strong>.
        </p>

    {% elif ticket and valid %}
        <div class="status ok">✓ Valid Ticket</div>
        <p class="message">This ticket is registered in the demo system.</p>

    {% else %}
        <div class="status bad">✕ Invalid Ticket</div>
        <p class="message">
            This ticket was not found. It may be invalid or unavailable.
        </p>
    {% endif %}

    {% if ticket %}
        <h1 class="person">{{ ticket.name }}</h1>

        <div class="row">
            <small>COURSE</small>
            <strong>{{ ticket.course }}</strong>
        </div>

        <div class="row">
            <small>BRANCH</small>
            <strong>{{ ticket.branch }}</strong>
        </div>

        <div class="row">
            <small>YEAR OF STUDY</small>
            <strong>{{ ticket.year }}</strong>
        </div>

        <div class="row">
            <small>EVENT DATE</small>
            <strong>{{ ticket.event_date }}</strong>
        </div>

        <div class="row">
            <small>VENUE</small>
            <strong>{{ ticket.venue }}</strong>
        </div>

        <div class="row">
            <small>TICKET NUMBER</small>
            <strong style="color:#701329">{{ ticket.id }}</strong>
        </div>

        <a class="btn" href="{{ url_for('home') }}">Back to registration</a>
    {% endif %}

</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        event_date = request.form.get("event_date", "").strip()
        venue = request.form.get("venue", "").strip()
        course = request.form.get("course", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()

        if not all([name, event_date, venue, course, branch, year]):
            return "Please complete all fields.", 400

        try:
            date.fromisoformat(event_date)
        except ValueError:
            return "Please enter a valid event date.", 400

        ticket_id = secrets.token_urlsafe(12)

        tickets[ticket_id] = {
            "id": ticket_id,
            "name": name,
            "event_date": event_date,
            "venue": venue,
            "course": course,
            "branch": branch,
            "year": year,
        }

        verification_url = url_for(
            "verify", ticket_id=ticket_id, _external=True
        )

        qr = qrcode.make(verification_url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")

        tickets[ticket_id]["qr"] = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return render_template_string(
            HTML, ticket=tickets[ticket_id]
        )

    return render_template_string(HTML, ticket=None)


@app.route("/verify/<ticket_id>")
def verify(ticket_id):
    ticket = tickets.get(ticket_id)

    if not ticket:
        return render_template_string(
            VERIFY_HTML,
            ticket=None,
            valid=False,
            expired=False
        ), 404

    try:
        event_day = date.fromisoformat(ticket["event_date"])
    except (ValueError, TypeError):
        event_day = date.min

    expired = event_day < date.today()
    valid = not expired

    return render_template_string(
        VERIFY_HTML,
        ticket=ticket,
        valid=valid,
        expired=expired
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
