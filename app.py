<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pass Preview Details</title><style>{{ style }}</style></head><body>
<div class="verify-card">
{% if logo_exists %}<img class="verify-logo" src="{{ url_for('static', filename=logo_filename) }}" alt="NIET logo">
{% else %}<h2>NIET Greater Noida</h2>{% endif %}
<div class="status-icon">i</div>
<h1>Pass Preview</h1>
<p class="verify-message">This QR code displays the information stored in the demo application.</p>
{% if ticket %}
<div class="verify-name">{{ ticket.name }}</div>
<div class="verify-details">
<div class="verify-row"><small>COURSE</small><strong>{{ ticket.course }}</strong></div>
<div class="verify-row"><small>BRANCH</small><strong>{{ ticket.branch }}</strong></div>
<div class="verify-row"><small>YEAR OF STUDY</small><strong>{{ ticket.year }}</strong></div>
<div class="verify-row"><small>EVENT DATE</small><strong>{{ ticket.event_date }}</strong></div>
<div class="verify-row"><small>VENUE</small><strong>{{ ticket.venue }}</strong></div>
<div class="verify-row"><small>TICKET NUMBER</small><strong>{{ ticket.id }}</strong></div>
</div>
<div class="notice">PREVIEW ONLY — NOT VALID FOR ENTRY. This page does not verify an official ticket.</div>
<a class="button" href="{{ url_for('home') }}">Create Another Preview</a>
{% else %}
<div class="notice">This preview ticket was not found. Generate a new preview from the homepage.</div>
<a class="button" href="{{ url_for('home') }}">Back to Registration</a>
{% endif %}
</div></body></html>
"""


def logo_available():
    return os.path.isfile(
        os.path.join(app.static_folder or "static", LOGO_FILENAME)
    )


def base_public_url():
    return os.environ.get("RENDER_EXTERNAL_URL", "").strip().rstrip("/") or request.url_root.rstrip("/")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(
            FORM_HTML, style=STYLE, event_name=EVENT_NAME,
            subtitle=EVENT_SUBTITLE, venue=DEFAULT_VENUE,
            logo_exists=logo_available(), logo_filename=LOGO_FILENAME,
        )

    name = request.form.get("name", "").strip()
    raw_date = request.form.get("event_date", "").strip()
    venue = request.form.get("venue", "").strip()
    course = request.form.get("course", "").strip()
    branch = request.form.get("branch", "").strip()
    year = request.form.get("year", "").strip()

    if not all([name, raw_date, venue, course, branch, year]):
        return "Please complete all fields.", 400

    try:
        parsed_date = date.fromisoformat(raw_date)
    except ValueError:
        return "Invalid event date.", 400

    ticket_id = "NIET-" + secrets.token_hex(5).upper()
    ticket = {
        "id": ticket_id,
        "name": name,
        "event_date": parsed_date.strftime("%d %b %Y"),
        "venue": venue,
        "course": course,
        "branch": branch,
        "year": year,
    }

    # The QR points to the public verification page.
    verify_url = base_public_url() + url_for("verify", ticket_id=ticket_id)
    qr_image = qrcode.make(verify_url)
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    ticket["qr"] = base64.b64encode(buffer.getvalue()).decode("ascii")
    tickets[ticket_id] = ticket

    return render_template_string(
        PASS_HTML, style=STYLE, ticket=ticket, event_name=EVENT_NAME,
        subtitle=EVENT_SUBTITLE, logo_exists=logo_available(),
        logo_filename=LOGO_FILENAME,
    )


@app.get("/verify/<ticket_id>")
def verify(ticket_id):
    ticket = tickets.get(ticket_id)
    status = 200 if ticket else 404
    return render_template_string(
        VERIFY_HTML, style=STYLE, ticket=ticket,
        logo_exists=logo_available(), logo_filename=LOGO_FILENAME,
    ), status


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)

