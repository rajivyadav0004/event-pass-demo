
import os
import io
import base64
import secrets
from datetime import datetime

import qrcode
from flask import Flask, request, render_template_string, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
VENUE = "NIET Plot 19 Campus"

tickets = {}

LOGO_CANDIDATES = [
    "niet-logo.png",
    "niet-logo.jpg",
    "niet-logo.jpeg",
    "niet-logo.webp",
    "NIET-logo.png",
    "NIET-logo.jpg",
    "logo.png",
    "logo.jpg",
]


def find_logo():
    static_dir = app.static_folder or "static"

    for filename in LOGO_CANDIDATES:
        path = os.path.join(static_dir, filename)
        if os.path.isfile(path):
            return filename

    return None


LOGO = find_logo()

STYLE = """
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 20px;
    background: #eaf0f8;
    font-family: Arial, sans-serif;
    color: #18365f;
}

.form-panel, .pass-panel, .verify-panel {
    max-width: 1050px;
    margin: 20px auto;
    padding: 25px;
    background: white;
    border: 3px solid #d4ad54;
    border-radius: 20px;
}

.form-panel, .verify-panel {
    max-width: 520px;
}

.logo {
    display: block;
    max-width: 280px;
    width: 100%;
    height: 90px;
    object-fit: contain;
    margin: auto;
}

h1, h2 { text-align: center; }

label {
    display: block;
    margin-top: 15px;
    font-weight: bold;
}

input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    border: 1px solid #ccd5e0;
    border-radius: 8px;
    background: white;
}

button {
    width: 100%;
    padding: 14px;
    margin-top: 22px;
    border: 0;
    border-radius: 8px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    font-weight: bold;
    cursor: pointer;
}

.header {
    display: grid;
    grid-template-columns: 200px 1fr 140px;
    gap: 20px;
    align-items: center;
    padding: 20px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    border-top: 7px solid #e8c75a;
}

.logo-box {
    padding: 10px;
    background: white;
    border-radius: 12px;
    text-align: center;
    color: #18365f;
    font-weight: bold;
}

.header h1 { font-size: 30px; }
.header p { text-align: center; font-weight: bold; }

.entry {
    padding: 12px;
    border: 2px solid #9dbde8;
    border-radius: 25px;
    text-align: center;
    font-weight: bold;
}

.content {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 3px 260px;
    gap: 18px;
    padding-top: 28px;
}

.separator {
    position: relative;
    background: repeating-linear-gradient(
        to bottom,
        #d4ad54 0 9px,
        transparent 9px 19px
    );
}

.circle {
    position: absolute;
    left: 50%;
    width: 20px;
    height: 20px;
    border: 3px solid #d4ad54;
    border-radius: 50%;
    background: white;
    transform: translateX(-50%);
}

.circle.top { top: -10px; }
.circle.bottom { bottom: -10px; }

.name {
    font-size: 32px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.info, .details {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin: 20px 0;
}

.info-box {
    padding: 18px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    border-radius: 14px;
}

.details { grid-template-columns: repeat(3, minmax(0, 1fr)); }

.detail {
    padding: 14px;
    background: #edf3ff;
    border: 2px solid #d4ad54;
    border-radius: 10px;
    overflow-wrap: anywhere;
}

.label {
    margin-bottom: 8px;
    color: #687b95;
    font-size: 12px;
    font-weight: bold;
}

.value { font-weight: bold; overflow-wrap: anywhere; }

.right { text-align: center; min-width: 0; }

.qr {
    width: 100%;
    max-width: 220px;
    padding: 8px;
    background: white;
}

.ticket-id {
    margin-top: 12px;
    font-size: 12px;
    font-weight: bold;
    overflow-wrap: anywhere;
}

.notice {
    margin-top: 18px;
    padding: 12px;
    background: #fff3d7;
    color: #765b20;
    border-radius: 8px;
    font-size: 12px;
    line-height: 1.5;
    text-align: center;
}

@media (max-width: 760px) {
    body { padding: 8px; }

    .header, .content {
        grid-template-columns: 1fr;
    }

    .header { text-align: center; }
    .header h1 { font-size: 25px; }
    .separator { display: none; }
    .details, .info { grid-template-columns: 1fr; }
    .right { max-width: 300px; margin: auto; }
    .name { font-size: 26px; }
}
"""

FORM_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova Registration</title>
<style>{{ style }}</style>
</head>
<body>
<div class="form-panel">
    <div class="logo-box">
        {% if logo %}
        <img class="logo" src="{{ url_for('static', filename=logo) }}" alt="NIET logo">
        {% else %}
        NIET Greater Noida
        {% endif %}
    </div>

    <h1>{{ event_name }}</h1>
    <p style="text-align:center"><b>{{ subtitle }}</b></p>

    <div class="notice">
        Unofficial preview only. This pass is not valid for entry.
    </div>

    <form method="POST" action="{{ url_for('home') }}">
        <label for="name">Full Name</label>
        <input id="name" name="name" maxlength="100" required>

        <label for="event_date">Event Date</label>
        <input id="event_date" name="event_date"
               type="date" value="2026-10-16" required>

        <label for="course">Course</label>
        <select id="course" name="course" required>
            <option>B.Tech</option>
            <option>M.Tech</option>
            <option>MBA</option>
            <option>B.Pharm</option>
        </select>

        <label for="branch">Branch</label>
        <input id="branch" name="branch"
               placeholder="e.g. Biotechnology" maxlength="100" required>

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

PASS_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova Pass Preview</title>
<style>{{ style }}</style>
</head>
<body>
<div class="pass-panel">
    <header class="header">
        <div class="logo-box">
            {% if logo %}
            <img class="logo" src="{{ url_for('static', filename=logo) }}" alt="NIET logo">
            {% else %}
            NIET Greater Noida
            {% endif %}
        </div>

        <div>
            <div style="text-align:center">NIET PRESENTS</div>
            <h1>{{ event_name }}</h1>
            <p>{{ subtitle }}</p>
        </div>

        <div class="entry">ENTRY PASS<br>PREVIEW</div>
    </header>

    <main class="content">
        <section>
            <p><b>REGISTERED PARTICIPANT — PREVIEW</b></p>
            <div class="name">{{ ticket.name }}</div>

            <div class="info">
                <div class="info-box">
                    <div class="label" style="color:white">EVENT DATE</div>
                    <div class="value">{{ ticket.event_date }}</div>
                </div>
                <div class="info-box">
                    <div class="label" style="color:white">VENUE</div>
                    <div class="value">{{ venue }}</div>
                </div>
            </div>

            <div class="details">
                <div class="detail">
                    <div class="label">COURSE</div>
                    <div class="value">{{ ticket.course }}</div>
                </div>
                <div class="detail">
                    <div class="label">BRANCH</div>
                    <div class="value">{{ ticket.branch }}</div>
                </div>
                <div class="detail">
                    <div class="label">YEAR</div>
                    <div class="value">{{ ticket.year }}</div>
                </div>
            </div>
        </section>

        <div class="separator">
            <span class="circle top"></span>
            <span class="circle bottom"></span>
        </div>

        <aside class="right">
            <h2>QR PASS DETAILS</h2>
            <img class="qr" src="data:image/png;base64,{{ ticket.qr }}" alt="QR code">
            <div class="ticket-id">{{ ticket.id }}</div>
            <p>Scan the QR code to view preview details.</p>
            <div class="notice">UNOFFICIAL PREVIEW — NOT VALID FOR ENTRY</div>
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
<style>{{ style }}</style>
</head>
<body>
<div class="verify-panel">
    <div class="logo-box">
        {% if logo %}
        <img class="logo" src="{{ url_for('static', filename=logo) }}" alt="NIET logo">
        {% else %}
        NIET Greater Noida
        {% endif %}
    </div>

    <h1>PASS PREVIEW DETAILS</h1>

    {% if ticket %}
    <h2>{{ ticket.name }}</h2>

    <div class="detail">
        <div class="label">COURSE</div>
        <div class="value">{{ ticket.course }}</div>
    </div>
    <div class="detail">
        <div class="label">BRANCH</div>
        <div class="value">{{ ticket.branch }}</div>
    </div>
    <div class="detail">
        <div class="label">YEAR</div>
        <div class="value">{{ ticket.year }}</div>
    </div>
    <div class="detail">
        <div class="label">EVENT DATE</div>
        <div class="value">{{ ticket.event_date }}</div>
    </div>
    <div class="detail">
        <div class="label">VENUE</div>
        <div class="value">{{ venue }}</div>
    </div>
    <div class="detail">
        <div class="label">TICKET NUMBER</div>
        <div class="value">{{ ticket.id }}</div>
    </div>

    <div class="notice">
        UNOFFICIAL PREVIEW — NOT VALID FOR ENTRY.
        Confirm ticket validity with the event organiser.
    </div>
    {% else %}
    <p>Ticket not found. Generate a new preview from the homepage.</p>
    {% endif %}
</div>
</body>
</html>
"""


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(
            FORM_HTML,
            style=STYLE,
            logo=LOGO,
            event_name=EVENT_NAME,
            subtitle=EVENT_SUBTITLE,
        )

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

    ticket_id = "NIET-PREVIEW-" + secrets.token_hex(6).upper()

    ticket = {
        "id": ticket_id,
        "name": name,
        "event_date": formatted_date,
        "course": course,
        "branch": branch,
        "year": year,
    }

    public_url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")

    if public_url:
        verify_url = public_url + url_for(
            "verify", ticket_id=ticket_id
        )
    else:
        verify_url = url_for(
            "verify", ticket_id=ticket_id, _external=True
        )

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
        logo=LOGO,
        event_name=EVENT_NAME,
        subtitle=EVENT_SUBTITLE,
        venue=VENUE,
    )


@app.get("/verify/<ticket_id>")
def verify(ticket_id):
    return render_template_string(
        VERIFY_HTML,
        style=STYLE,
        ticket=tickets.get(ticket_id),
        logo=LOGO,
        venue=VENUE,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
