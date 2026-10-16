
from flask import Flask, request, render_template_string, url_for
import qrcode
import io
import base64
import secrets
from datetime import datetime, date

app = Flask(__name__)
tickets = {}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NIET Event Pass</title>
<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 20px;
    background: #eef1f6;
    font-family: Arial, sans-serif;
    color: #35111b;
}
.form-box {
    max-width: 600px;
    margin: 20px auto;
    padding: 24px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 30px #0001;
}
label { display: block; margin-top: 14px; font-weight: bold; }
input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccc;
    border-radius: 7px;
    font-size: 16px;
}
button, .btn {
    display: block;
    width: 100%;
    padding: 14px;
    margin-top: 20px;
    background: #701329;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    text-align: center;
    text-decoration: none;
    cursor: pointer;
}
.pass {
    max-width: 900px;
    margin: 20px auto;
    overflow: hidden;
    background: #fff9e9;
    border: 4px solid #d6b75b;
    border-radius: 20px;
}
.header {
    padding: 28px 24px;
    background: #701329;
    color: #ffe7a0;
    text-align: center;
    border-bottom: 7px solid #e8a02d;
}
.header h1 { margin: 0 0 10px; font-size: 30px; }
.content { padding: 28px; }
.name { font-size: 32px; font-weight: bold; margin: 15px 0 24px; }
.details {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}
.item {
    padding: 16px;
    border: 1px solid #e0c878;
    border-radius: 10px;
    overflow-wrap: anywhere;
}
.item small { display: block; color: #786b5e; font-weight: bold; margin-bottom: 8px; }
.qr { text-align: center; padding: 20px 0; }
.qr img { width: 230px; max-width: 100%; }
.status { text-align: center; font-size: 26px; font-weight: bold; }
.muted { color: #71665f; text-align: center; }
@media (max-width: 480px) {
    body { padding: 10px; }
    .content { padding: 18px; }
    .details { grid-template-columns: 1fr; }
    .name { font-size: 26px; }
}
</style>
</head>
<body>
{% if ticket %}
<div class="pass">
    <div class="header">
        <h1>NIET EVENT PASS</h1>
        <div>REGISTERED PARTICIPANT</div>
    </div>
    <div class="content">
        <div class="name">{{ ticket.name }}</div>
        <div class="details">
            <div class="item"><small>EVENT DATE</small>{{ ticket.event_date }}</div>
            <div class="item"><small>VENUE</small>{{ ticket.venue }}</div>
            <div class="item"><small>COURSE</small>{{ ticket.course }}</div>
            <div class="item"><small>BRANCH</small>{{ ticket.branch }}</div>
            <div class="item"><small>YEAR OF STUDY</small>{{ ticket.year }}</div>
            <div class="item"><small>TICKET ID</small>{{ ticket.id }}</div>
        </div>
        <div class="qr">
            <h3>QR VERIFICATION</h3>
            <img src="data:image/png;base64,{{ ticket.qr }}" alt="Ticket verification QR code">
            <p class="muted">Scan this QR code to verify this ticket.</p>
            <a class="btn" href="{{ url_for('verify', ticket_id=ticket.id) }}">Open verification page</a>
        </div>
        <button onclick="window.print()">Print / Save PDF</button>
    </div>
</div>
{% else %}
<div class="form-box">
    <h2>NIET Event Pass Registration</h2>
    <form method="POST" action="{{ url_for('home') }}">
        <label>Full Name</label>
        <input name="name" required maxlength="100">

        <label>Event Date</label>
        <input type="date" name="event_date" required>

        <label>Venue</label>
        <input name="venue" value="NIET Plot 19 Campus" required maxlength="150">

        <label>Course</label>
        <select name="course" required>
            <option value="BTech">B.Tech</option>
            <option value="MBA">MBA</option>
            <option value="MTech">M.Tech</option>
            <option value="BPharm">B.Pharm</option>
        </select>

        <label>Branch</label>
        <input name="branch" placeholder="e.g. Biotechnology" required maxlength="100">

        <label>Year of Study</label>
        <select name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button type="submit">Generate Event Pass</button>
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
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ticket Verification</title>
<style>
body { margin:0; padding:20px; background:#eef1f6; font-family:Arial,sans-serif; }
.card { max-width:480px; margin:30px auto; padding:28px; background:white;
        border-radius:22px; border-top:10px solid #701329; text-align:center; }
.logo { font-size:24px; font-weight:bold; color:#701329; }
.status { font-size:30px; font-weight:bold; margin:24px 0 10px; }
.ok { color:#16834a; } .bad { color:#b42335; }
.row { text-align:left; padding:14px; margin-top:10px; background:#f5f7fa;
       border-radius:10px; overflow-wrap:anywhere; }
small { display:block; color:#746a67; font-weight:bold; margin-bottom:6px; }
</style>
</head>
<body>
<div class="card">
    <div class="logo">NIET Greater Noida</div>
    {% if ticket and valid %}
        <div class="status ok">✓ Valid Ticket</div>
        <p>This ticket is registered in the demo system.</p>
        <h2>{{ ticket.name }}</h2>
        <div class="row"><small>COURSE</small>{{ ticket.course }}</div>
        <div class="row"><small>BRANCH</small>{{ ticket.branch }}</div>
        <div class="row"><small>YEAR OF STUDY</small>{{ ticket.year }}</div>
        <div class="row"><small>EVENT DATE</small>{{ ticket.event_date }}</div>
        <div class="row"><small>TICKET ID</small>{{ ticket.id }}</div>
    {% else %}
        <div class="status bad">✕ Invalid Ticket</div>
        <p>This ticket ID was not found in the current demo session.</p>
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

        ticket_id = secrets.token_urlsafe(12)

        verification_url = url_for(
            "verify", ticket_id=ticket_id, _external=True
        )

        qr = qrcode.make(verification_url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        tickets[ticket_id] = {
            "id": ticket_id,
            "name": name,
            "event_date": event_date,
            "venue": venue,
            "course": course,
            "branch": branch,
            "year": year,
            "qr": qr_base64,
        }

        return render_template_string(HTML, ticket=tickets[ticket_id])

    return render_template_string(HTML, ticket=None)


@app.route("/verify/<ticket_id>")
def verify(ticket_id):
    ticket = tickets.get(ticket_id)
    return render_template_string(
        VERIFY_HTML,
        ticket=ticket,
        valid=ticket is not None
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
