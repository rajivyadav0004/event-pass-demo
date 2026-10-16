from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
from datetime import datetime

app = Flask(__name__)

# Demo ticket storage
tickets = {}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Event Pass Demo</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #eee9dc;
    font-family: Arial, sans-serif;
    color: #64152a;
}

.form-box {
    max-width: 650px;
    margin: 15px auto 30px;
    padding: 22px;
    background: white;
    border-radius: 12px;
}

.form-box h2 {
    margin-top: 0;
}

label {
    display: block;
    font-weight: bold;
    margin-top: 13px;
}

input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 16px;
}

button {
    width: 100%;
    margin-top: 18px;
    padding: 14px;
    background: #70152c;
    color: white;
    border: none;
    border-radius: 7px;
    font-size: 16px;
    cursor: pointer;
}

.pass {
    width: 100%;
    max-width: 1100px;
    margin: auto;
    overflow: hidden;
    background: #fff9e9;
    border: 4px solid #d6b75b;
    border-radius: 20px;
    position: relative;
}

.header {
    min-height: 145px;
    padding: 24px;
    background: #701329;
    color: #ffe7a0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    border-bottom: 7px solid #e8a02d;
}

.header h1 {
    margin: 8px 0;
    font-size: clamp(22px, 3vw, 36px);
}

.header p {
    margin: 5px 0;
    font-size: 18px;
}

.badge {
    border: 2px solid #e8b5bf;
    border-radius: 30px;
    padding: 12px 18px;
    white-space: nowrap;
    font-weight: bold;
}

.demo-banner {
    text-align: center;
    color: #8b1d32;
    background: #ffedbd;
    font-weight: bold;
    padding: 9px;
    letter-spacing: 1px;
}

.content {
    display: grid;
    grid-template-columns: 2fr 1fr;
}

.details {
    padding: 28px;
    border-right: 3px dashed #d7c27e;
}

.eyebrow {
    font-size: 16px;
    font-weight: bold;
}

.student-name {
    font-size: clamp(27px, 4vw, 43px);
    font-weight: bold;
    margin: 20px 0 25px;
    overflow-wrap: anywhere;
}

.event-row {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 10px;
    margin-bottom: 22px;
}

.event-card {
    padding: 17px;
    border-radius: 16px;
    color: #fff2ce;
    background: #701329;
    min-width: 0;
}

.event-card.venue {
    background: #e87516;
}

.small-label {
    font-size: 12px;
    font-weight: bold;
    opacity: .9;
}

.event-value {
    margin-top: 12px;
    font-size: 17px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
}

.info-card {
    border: 2px solid #e0cb83;
    border-top: 6px solid #e7c75c;
    border-radius: 8px 8px 15px 15px;
    padding: 14px 10px;
    min-height: 100px;
    overflow-wrap: anywhere;
}

.info-card span {
    display: block;
    font-size: 12px;
    color: #806d53;
    font-weight: bold;
    margin-bottom: 14px;
}

.info-card strong {
    font-size: 15px;
}

.ticket-id {
    margin-top: 20px;
    font-size: 12px;
    overflow-wrap: anywhere;
}

.qr-section {
    padding: 25px 18px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}

.qr-pill {
    background: #701329;
    color: white;
    padding: 10px 25px;
    border-radius: 30px;
    font-weight: bold;
}

.qr-section h3 {
    font-size: 18px;
    margin: 25px 0 15px;
}

.qr-image {
    width: 100%;
    max-width: 255px;
    height: auto;
    padding: 10px;
    background: white;
}

.qr-id {
    font-size: 12px;
    font-weight: bold;
    margin-top: 12px;
    overflow-wrap: anywhere;
}

.qr-note {
    margin-top: 20px;
    color: #806d53;
    font-size: 13px;
    line-height: 1.5;
}

.watermark {
    position: absolute;
    left: 50%;
    top: 60%;
    transform: translate(-50%, -50%) rotate(-25deg);
    color: rgba(120, 30, 45, .07);
    font-size: clamp(35px, 7vw, 75px);
    font-weight: bold;
    pointer-events: none;
    white-space: nowrap;
}

.print-button {
    display: block;
    max-width: 1100px;
    width: 100%;
    margin: 15px auto;
    background: #701329;
    color: white;
    border: 0;
    border-radius: 8px;
    padding: 15px;
    font-size: 16px;
    cursor: pointer;
}

.verify-box {
    max-width: 650px;
    margin: 30px auto;
    background: white;
    padding: 22px;
    border-radius: 12px;
    text-align: center;
}

@media (max-width: 600px) {
    body {
        padding: 8px;
    }

    .header {
        padding: 16px;
        min-height: 110px;
    }

    .header p {
        font-size: 13px;
    }

    .badge {
        font-size: 11px;
        padding: 8px;
    }

    .content {
        grid-template-columns: 1fr;
    }

    .details {
        padding: 17px;
        border-right: 0;
        border-bottom: 3px dashed #d7c27e;
    }

    .qr-section {
        padding: 20px;
    }

    .info-grid {
        gap: 6px;
    }

    .info-card {
        padding: 10px 6px;
    }

    .info-card span {
        font-size: 10px;
    }

    .info-card strong {
        font-size: 12px;
    }

    .event-row {
        grid-template-columns: 1fr 1fr;
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
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }

    .form-box,
    .print-button,
    .verify-box {
        display: none !important;
    }

    .pass {
        max-width: none;
        width: 100%;
        border-radius: 12px;
        break-inside: avoid;
    }

    .header {
        min-height: 120px;
    }

    .details {
        padding: 20px;
    }

    .qr-image {
        max-width: 210px;
    }
}
</style>
</head>

<body>

{% if show_form %}
<div class="form-box">
    <h2>Event Pass Generator</h2>
    <p>DEMO TEMPLATE — NOT VALID FOR EVENT ENTRY</p>

    <form method="POST">
        <label>Student Name</label>
        <input name="student_name" required maxlength="100"
               placeholder="Enter student name">

        <label>Course</label>
        <input name="course" required maxlength="60"
               placeholder="e.g. B.Tech">

        <label>Branch</label>
        <input name="branch" required maxlength="80"
               placeholder="e.g. Biotechnology">

        <label>Year of Study</label>
        <select name="year" required>
            <option value="">Select year</option>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <label>Event Date</label>
        <input type="date" name="event_date" required>

        <label>Venue</label>
        <input name="venue" required maxlength="150"
               value="NIET Plot 19 Campus">

        <button type="submit">Generate Demo Pass</button>
    </form>
</div>
{% endif %}

{% if ticket %}
<div class="pass">

    <div class="header">
        <div>
            <div style="font-weight:bold;font-size:13px;">
                EVENT ORGANIZER
            </div>
            <h1>EVENT PASS DEMO</h1>
            <p>Student Event • Entry Pass Preview</p>
        </div>
        <div class="badge">DEMO PASS</div>
    </div>

    <div class="demo-banner">
        SAMPLE ONLY — NOT VALID FOR ENTRY
    </div>

    <div class="content">

        <div class="details">
            <div class="eyebrow">REGISTERED PARTICIPANT</div>

            <div class="student-name">
                {{ ticket.student_name }}
            </div>

            <div class="event-row">
                <div class="event-card">
                    <div class="small-label">EVENT DATE</div>
                    <div class="event-value">
                        {{ ticket.event_date }}
                    </div>
                </div>

                <div class="event-card venue">
                    <div class="small-label">VENUE</div>
                    <div class="event-value">
                        {{ ticket.venue }}
                    </div>
                </div>
            </div>

            <div class="info-grid">
                <div class="info-card">
                    <span>COURSE</span>
                    <strong>{{ ticket.course }}</strong>
                </div>

                <div class="info-card">
                    <span>BRANCH</span>
                    <strong>{{ ticket.branch }}</strong>
                </div>

                <div class="info-card">
                    <span>YEAR OF STUDY</span>
                    <strong>{{ ticket.year }}</strong>
                </div>
            </div>

            <div class="ticket-id">
                <strong>DEMO TICKET ID:</strong><br>
                {{ ticket.ticket_id }}
            </div>
        </div>

        <div class="qr-section">
            <div class="qr-pill">E-PASS DEMO</div>

            <h3>QR VERIFICATION</h3>

            <img class="qr-image"
                 src="data:image/png;base64,{{ ticket.qr_image }}"
                 alt="Demo ticket QR code">

            <div class="qr-id">{{ ticket.ticket_id }}</div>

            <div class="qr-note">
                Scan to open the demo verification page.<br>
                This does not authorize event entry.
            </div>

            <p>
                <a href="{{ url_for('verify', ticket_id=ticket.ticket_id) }}">
                    Open verification page
                </a>
            </p>
        </div>
    </div>

    <div class="watermark">DEMO</div>
</div>

<button class="print-button" onclick="window.print()">
    Print / Save PDF
</button>
{% endif %}

{% if verification %}
<div class="verify-box">
    <h2>DEMO QR VERIFICATION</h2>
    <p><strong>Status:</strong> {{ verification.status }}</p>

    {% if verification.ticket %}
        <p><strong>Name:</strong>
           {{ verification.ticket.student_name }}</p>
        <p><strong>Course:</strong>
           {{ verification.ticket.course }}</p>
        <p><strong>Branch:</strong>
           {{ verification.ticket.branch }}</p>
        <p><strong>Year:</strong>
           {{ verification.ticket.year }}</p>
        <p><strong>Event Date:</strong>
           {{ verification.ticket.event_date }}</p>
        <p><strong>Venue:</strong>
           {{ verification.ticket.venue }}</p>
    {% endif %}

    <p>This is a demonstration, not an official entry authorization.</p>
    <a href="{{ url_for('home') }}">Create another demo pass</a>
</div>
{% endif %}

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        course = request.form.get("course", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()
        event_date = request.form.get("event_date", "").strip()
        venue = request.form.get("venue", "").strip()

        if not all([
            student_name, course, branch,
            year, event_date, venue
        ]):
            return "Please fill in all fields.", 400

        ticket_id = secrets.token_urlsafe(12)

        ticket = {
            "student_name": student_name,
            "course": course,
            "branch": branch,
            "year": year,
            "event_date": event_date,
            "venue": venue,
            "ticket_id": ticket_id,
        }

        tickets[ticket_id] = ticket

        verify_url = url_for(
            "verify",
            ticket_id=ticket_id,
            _external=True
        )

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4
        )
        qr.add_data(verify_url)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        qr_image = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        ticket["qr_image"] = qr_image

        return render_template_string(
            HTML,
            show_form=False,
            ticket=ticket,
            verification=None
        )

    return render_template_string(
        HTML,
        show_form=True,
        ticket=None,
        verification=None
    )


@app.route("/verify/<ticket_id>")
def verify(ticket_id):
    ticket = tickets.get(ticket_id)

    if ticket:
        status = "DEMO RECORD FOUND"
    else:
        status = "DEMO RECORD NOT FOUND"

    return render_template_string(
        HTML,
        show_form=False,
        ticket=None,
        verification={
            "status": status,
            "ticket": ticket
        }
    )


if __name__ == "__main__":
    app.run(debug=False)
