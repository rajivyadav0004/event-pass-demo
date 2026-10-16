
import os
import io
import base64
import secrets
from datetime import date
from flask import Flask, request, render_template_string, url_for
import qrcode

app = Flask(__name__)

EVENT_NAME = "SILVERNOVA 2026"
EVENT_SUBTITLE = "GARBA & DJ NIGHT"
DEFAULT_VENUE = "NIET Plot 19 Campus"
LOGO_FILENAME = "NIET New Engineering Color Logo.jpg"

# Demo storage: restart hone par records clear ho jayenge.
tickets = {}

CSS = """
* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 16px;
    background: #eef1f6;
    font-family: Arial, Helvetica, sans-serif;
    color: #18365f;
}

.pass {
    max-width: 1500px;
    width: 100%;
    margin: 10px auto;
    background: #f5f8ff;
    border: 4px solid #d4ad54;
    border-radius: 24px;
    overflow: hidden;
}

.header {
    position: relative;
    display: grid;
    grid-template-columns: 300px minmax(0, 1fr) 200px;
    align-items: center;
    gap: 25px;
    padding: 22px 30px 34px;
    color: white;
    background: linear-gradient(110deg, #218b89, #3268ad);
    border-top: 7px solid #e8c75a;
}

.header::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 13px;
    background-image:
        radial-gradient(circle, #f2d45d 5px, transparent 5.5px),
        radial-gradient(circle, #9bb8f2 5px, transparent 5.5px);
    background-size: 30px 13px;
    background-position: 0 0, 15px 0;
    background-repeat: repeat-x;
}

.logo-box {
    min-height: 110px;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 14px;
    color: #18365f;
    font-weight: bold;
    text-align: center;
}

.logo {
    display: block;
    width: 100%;
    height: 100px;
    object-fit: contain;
}

.small-title { font-size: 16px; font-weight: bold; }

.event-title h1 {
    margin: 8px 0;
    font-size: clamp(25px, 3vw, 42px);
    overflow-wrap: anywhere;
}

.event-title p { margin: 0; font-size: 20px; font-weight: bold; }

.entry {
    padding: 14px 10px;
    border: 3px solid #8eafe3;
    border-radius: 40px;
    text-align: center;
    font-weight: bold;
}

.pass-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 3px 350px;
    gap: 25px;
    padding: 30px;
}

.left { min-width: 0; }

.participant {
    margin: 5px 0 18px;
    color: #234f91;
    font-size: 18px;
    font-weight: bold;
}

.name {
    margin-bottom: 28px;
    font-size: clamp(30px, 4vw, 52px);
    font-weight: 800;
    overflow-wrap: anywhere;
}

.event-info {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    margin-bottom: 25px;
}

.info-box {
    min-width: 0;
    min-height: 135px;
    padding: 22px;
    color: white;
    background: linear-gradient(110deg, #168b87, #3268ad);
    border-radius: 20px;
}

.info-label {
    display: block;
    margin-bottom: 20px;
    font-size: 14px;
    font-weight: bold;
}

.info-value { font-size: 21px; font-weight: bold; overflow-wrap: anywhere; }

.details {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.detail {
    min-width: 0;
    min-height: 120px;
    padding: 17px;
    background: #eaf1ff;
    border: 2px solid #d7c28c;
    border-top: 7px solid #e8c65c;
    border-radius: 12px;
    overflow-wrap: anywhere;
}

.detail small {
    display: block;
    margin-bottom: 17px;
    color: #526680;
    font-size: 13px;
    font-weight: bold;
}

.detail strong { font-size: 17px; }

.separator {
    position: relative;
    align-self: stretch;
    width: 3px;
    margin: -30px 0;
    background: repeating-linear-gradient(
        to bottom, #d4ad54 0 9px, transparent 9px 20px
    );
}

.circle {
    position: absolute;
    left: 50%;
    width: 40px;
    height: 40px;
    border: 3px solid #d4ad54;
    border-radius: 50%;
    background: #f5f8ff;
    transform: translateX(-50%);
}
.circle.top { top: 0; }
.circle.bottom { bottom: 0; }

.qr-panel { min-width: 0; text-align: center; }

.pill {
    display: inline-block;
    margin: 5px 0 20px;
    padding: 12px 35px;
    border-radius: 30px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
    font-weight: bold;
}

.qr-panel h2 { margin: 5px 0 20px; font-size: 22px; }

.qr-box {
    padding: 20px;
    background: #eaf1ff;
    border-radius: 22px;
}

.qr-image {
    display: block;
    width: 100%;
    max-width: 270px;
    height: auto;
    padding: 7px;
    margin: auto;
    background: white;
}

.ticket-number {
    margin-top: 15px;
    font-weight: bold;
    font-size: 14px;
    overflow-wrap: anywhere;
}

.hint { margin-top: 20px; color: #687b95; line-height: 1.5; }

.sample-note {
    margin-top: 16px;
    padding: 11px;
    border-radius: 9px;
    background: #fff3d7;
    color: #765b20;
    font-size: 12px;
    line-height: 1.5;
    font-weight: bold;
}

.form-card, .verify-card {
    width: 100%;
    max-width: 520px;
    margin: 25px auto;
    padding: 26px;
    background: white;
    border-radius: 24px;
    box-shadow: 0 8px 30px #0001;
}

.form-card { border-top: 9px solid #218b89; }
.form-card h1 { text-align: center; font-size: 26px; }

label {
    display: block;
    margin-top: 15px;
    font-weight: bold;
}

input, select {
    width: 100%;
    margin-top: 6px;
    padding: 12px;
    border: 1px solid #ccd5e0;
    border-radius: 8px;
    font-size: 16px;
    background: white;
}

.button {
    display: block;
    width: 100%;
    margin-top: 20px;
    padding: 15px;
    border: 0;
    border-radius: 10px;
    background: linear-gradient(110deg, #168b87, #3268ad);
    color: white;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.verify-card {
    max-width: 520px;
    padding: 28px;
    border-top: 10px solid #218b89;
    text-align: center;
}

.verify-logo {
    display: block;
    width: 270px;
    max-width: 100%;
    height: 100px;
    margin: 0 auto 15px;
    object-fit: contain;
}

.status-icon {
    display: flex;
    width: 110px;
    height: 110px;
    align-items: center;
    justify-content: center;
    margin: 20px auto;
    border-radius: 50%;
    background: #3268ad;
    color: white;
    font-size: 60px;
    font-weight: bold;
}

.verify-card h1 { color: #281b1b; font-size: 30px; }

.verify-message { font-size: 16px; line-height: 1.5; }

.verify-name {
    margin: 25px 0 20px;
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
.verify-row:last-child { border-bottom: 0; }

.verify-row small {
    display: block;
    margin-bottom: 7px;
    color: #746a67;
    font-size: 13px;
    font-weight: bold;
}

.verify-row strong { font-size: 18px; }

@media (max-width: 850px) {
    body { padding: 8px; }

    .header {
        grid-template-columns: 1fr;
        gap: 14px;
        padding: 18px 16px 28px;
        text-align: center;
    }

    .logo-box { max-width: 320px; width: 100%; margin: auto; }
    .event-title h1 { font-size: 29px; }
    .event-title p { font-size: 18px; }
    .entry { max-width: 220px; margin: auto; width: 100%; }

    .pass-body {
        grid-template-columns: 1fr;
        gap: 28px;
        padding: 18px;
    }

    .separator { display: none; }
    .event-info, .details { grid-template-columns: 1fr; }
    .qr-panel { border-top: 3px dashed #d4ad54; padding-top: 22px; }
    .qr-box { max-width: 340px; margin: auto; }
}

@media print {
    @page { size: A4 landscape; margin: 5mm; }
    body { padding: 0; background: white; }
    .pass { margin: 0; box-shadow: none; border-width: 2px; }
    .header {
        grid-template-columns: 210px minmax(0, 1fr) 145px;
        gap: 15px;
        padding: 12px 16px 24px;
    }
    .logo { height: 70px; }
    .logo-box { min-height: 80px; }
    .event-title h1 { font-size: 27px; }
    .event-title p { font-size: 15px; }
    .pass-body {
        grid-template-columns: minmax(0, 1fr) 3px 235px;
        gap: 16px;
        padding: 18px;
    }
    .name { font-size: 31px; margin-bottom: 18px; }
    .info-box { min-height: 90px; padding: 12px; }
    .info-label { margin-bottom: 10px; }
    .info-value { font-size: 16px; }
    .detail { min-height: 85px; padding: 9px; }
    .detail small { margin-bottom: 10px; }
    .detail strong { font-size: 13px; }
    .qr-box { padding: 9px; }
    .qr-image { max-width: 165px; }
}
"""


FORM_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SilverNova Pass Preview</title>
<style>{{ css }}</style>
</head>
<body>
<div class="form-card">
    {% if logo_exists %}
    <img class="verify-logo" src="{{ logo_url }}" alt="NIET logo">
    {% else %}
    <h2 style="text-align:center">NIET Greater Noida</h2>
    {% endif %}

    <h1>{{ event_name }}</h1>
    <p style="text-align:center">{{ subtitle }}</p>

    <div class="sample-note">
        SAMPLE PREVIEW — NOT VALID FOR EVENT ENTRY
    </div>

    <form method="post">
        <label for="name">Full Name</label>
        <input id="name" name="name" maxlength="100" required>

        <label for="event_date">Event Date</label>
        <input id="event_date" name="event_date" type="date"
               value="2026-10-16" required>

        <label for="venue">Venue</label>
        <input id="venue" name="venue"
               value="{{ venue }}" maxlength="150" required>

        <label for="course">Course</label>
        <select id="course" name="course" required>
            <option>B. Tech</option>
            <option>M.Tech</option>
            <option>MBA</option>
            <option>B.Pharm</option>
        </select>

        <label for="branch">Branch</label>
        <input id="branch" name="branch" maxlength="100" required>

        <label for="year">Year of Study</label>
        <select id="year" name="year" required>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
        </select>

        <button class="button" type="submit">Generate Pass Preview</button>
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

        <div class="entry">ENTRY PASS</div>
    </header>

    <main class="pass-body">
        <section class="left">
            <div class="participant">ADMIT ONE - REGISTERED PARTICIPANT</div>
            <div class="name">{{ ticket.name }}</div>

            <div class="event-info">
                <div class="info-box">
                    <span class="info-label">EVENT DATE</span>
                    <div class="info-value">{{ ticket.event_date }}</div>
                </div>
                <div class="info-box">
                    <span class="info-label">VENUE</span>
                    <div class="info-value">{{ ticket.venue }}</div>
                </div>
            </div>

            <div class="details">
                <div class="detail">
                    <small>COURSE</small><strong>{{ ticket.course }}</strong>
                </div>
                <div class="detail">
                    <small>BRANCH</small><strong>{{ ticket.branch }}</strong>
                </div>
                <div class="detail">
                    <small>YEAR OF STUDY</small><strong>{{ ticket.year }}</strong>
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
                     alt="Pass preview QR code">
                <div class="ticket-number">{{ ticket.id }}</div>
            </div>

            <p class="hint">Scan this QR code at the NIET entry gate</p>

            <div class="sample-note">
                SAMPLE PREVIEW — NOT VALID FOR EVENT ENTRY
            </div>
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

    <div class="status-icon">i</div>
    <h1>Pass Preview</h1>

    <p class="verify-message">
        This QR code displays the participant details saved
        in the demonstration application.
    </p>

    {% if ticket %}
    <div class="verify-name">{{ ticket.name }}</div>

    <div class="verify-details">
        <div class="verify-row">
            <small>COURSE</small><strong>{{ ticket.course }}</strong>
        </div>
        <div class="verify-row">
            <small>BRANCH</small><strong>{{ ticket.branch }}</strong>
        </div>
        <div class="verify-row">
            <small>YEAR OF STUDY</small><strong>{{ ticket.year }}</strong>
        </div>
        <div class="verify-row">
            <small>EVENT</small><strong>{{ ticket.event_date }}</strong>
        </div>
        <div class="verify-row">
            <small>VENUE</small><strong>{{ ticket.venue }}</strong>
        </div>
        <div class="verify-row">
            <small>TICKET NUMBER</small><strong>{{ ticket.id }}</strong>
        </div>
    </div>

    <div class="sample-note">
        SAMPLE PREVIEW — NOT VALID FOR EVENT ENTRY.
        This page does not verify an official ticket.
    </div>

    <a class="button" href="{{ url_for('show_pass', ticket_id=ticket.id) }}">
        View e-pass
    </a>
    {% else %}
    <div class="sample-note">
        This preview record was not found. Generate a new preview.
    </div>
    <a class="button" href="{{ url_for('home') }}">Back to registration</a>
    {% endif %}
</div>
</body>
</html>
"""


def logo_exists():
    path = os.path.join(app.static_folder, LOGO_FILENAME)
    return os.path.isfile(path)


def logo_url():
    if logo_exists():
        return url_for("static", filename=LOGO_FILENAME)
    return ""


def render_page(template, **context):
    context.update({
        "css": CSS,
        "logo_exists": logo_exists(),
        "logo_url": logo_url(),
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
        event_date = date.fromisoformat(raw_date)
    except ValueError:
        return "Please enter a valid event date.", 400

    ticket_id = "NIET-" + secrets.token_hex(5).upper()

    ticket = {
        "id": ticket_id,
        "name": name,
        "event_date": event_date.strftime("%d %b %Y"),
        "venue": venue,
        "course": course,
        "branch": branch,
        "year": year,
    }

    tickets[ticket_id] = ticket

    # QR opens the public verification page.
    verify_url = (
        request.url_root.rstrip("/")
        + url_for("verify", ticket_id=ticket_id)
    )

    qr_image = qrcode.make(verify_url)
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")

    ticket["qr"] = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return render_page(PASS_HTML, ticket=ticket)


@app.get("/pass/<ticket_id>")
def show_pass(ticket_id):
    ticket = tickets.get(ticket_id)

    if ticket is None:
        return "Preview ticket not found. Please generate a new one.", 404

    return render_page(PASS_HTML, ticket=ticket)


@app.get("/verify/<ticket_id>")
def verify(ticket_id):
    ticket = tickets.get(ticket_id)
    status = 200 if ticket else 404

    return render_page(VERIFY_HTML, ticket=ticket), status


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
