from flask import Flask, request, render_template_string, abort
import secrets
import qrcode
import io
import base64

app = Flask(__name__)

# Demo only: temporary in-memory ticket storage
tickets = {}

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Event Pass Demo</title>
<style>
body {
    margin: 0;
    background: #fff7e6;
    font-family: Arial, sans-serif;
    color: #651126;
}
header {
    background: #70132b;
    color: #ffe2a0;
    padding: 22px;
    text-align: center;
}
.card {
    max-width: 850px;
    margin: 25px auto;
    padding: 22px;
    background: #fffaf0;
    border: 3px solid #d7b65b;
    border-radius: 18px;
}
input, select, button {
    box-sizing: border-box;
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    font-size: 16px;
}
button {
    background: #70132b;
    color: white;
    border: 0;
    border-radius: 8px;
}
.pass {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}
.qr { text-align: center; overflow-wrap: anywhere; }
img { max-width: 100%; }
@media(max-width:600px) {
    .pass { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<header>
    <h2>EVENT PASS DEMO</h2>
    <p>Registration & QR Verification</p>
</header>

<div class="card">
{% if ticket %}
    <div class="pass">
        <div>
            <p>REGISTERED PARTICIPANT</p>
            <h1>{{ ticket.name }}</h1>
            <h3>Event Date: {{ ticket.date }}</h3>
            <h3>Venue: {{ ticket.venue }}</h3>
            <p><b>Course:</b> {{ ticket.course }}</p>
            <p><b>Branch:</b> {{ ticket.branch }}</p>
            <p><b>Year:</b> {{ ticket.year }}</p>
            <p><b>Ticket ID:</b> {{ token }}</p>
            <button onclick="window.print()">Print / Save PDF</button>
        </div>
        <div class="qr">
            <h3>QR VERIFICATION</h3>
            <img src="data:image/png;base64,{{ qr }}">
            <p>Scan to verify this demo ticket.</p>
            <a href="{{ verify_url }}">Open verification page</a>
        </div>
    </div>
{% else %}
    <h2>Student Registration</h2>
    <form method="post">
        <input name="name" placeholder="Student name" required>
        <input name="course" placeholder="Course" required>
        <input name="branch" placeholder="Branch" required>
        <select name="year" required>
            <option value="">Select year</option>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>
        <input name="date" type="date" required>
        <input name="venue" placeholder="Event venue" required>
        <button type="submit">Generate Demo Pass</button>
    </form>
{% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        token = secrets.token_urlsafe(24)
        tickets[token] = {
            "name": request.form["name"].strip(),
            "course": request.form["course"].strip(),
            "branch": request.form["branch"].strip(),
            "year": request.form["year"],
            "date": request.form["date"],
            "venue": request.form["venue"].strip()
        }
        return render_template_string(
            PAGE, ticket=tickets[token], token=token,
            qr=make_qr(request.host_url + "ticket-verify/" + token),
            verify_url=request.host_url + "ticket-verify/" + token
        )
    return render_template_string(PAGE, ticket=None)

def make_qr(url):
    image = qrcode.make(url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

@app.route("/ticket-verify/<token>")
def verify(token):
    ticket = tickets.get(token)
    if not ticket:
        return "<h2>Ticket not found or expired</h2>", 404
    return render_template_string(
        PAGE, ticket=ticket, token=token,
        qr=make_qr(request.url),
        verify_url=request.url
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
