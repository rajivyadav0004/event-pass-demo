
        <div class="verify-name">{{ verification.ticket.student_name }}</div>

        <div class="verify-details">
            <div class="verify-row">
                <span>COURSE</span>
                <strong>{{ verification.ticket.course }}</strong>
            </div>
            <div class="verify-row">
                <span>BRANCH</span>
                <strong>{{ verification.ticket.branch }}</strong>
            </div>
            <div class="verify-row">
                <span>YEAR OF STUDY</span>
                <strong>{{ verification.ticket.year }}</strong>
            </div>
            <div class="verify-row">
                <span>EVENT DATE</span>
                <strong>{{ verification.ticket.event_date_display }}</strong>
            </div>
            <div class="verify-row">
                <span>VENUE</span>
                <strong>{{ verification.ticket.venue }}</strong>
            </div>
            <div class="verify-row">
                <span>DEMO TICKET NUMBER</span>
                <strong class="verify-ticket-number">{{ verification.ticket.ticket_id }}</strong>
            </div>
        </div>

        <a class="verify-button" href="{{ url_for('home') }}">Create another demo pass</a>
    {% else %}
        <div class="status-icon">×</div>
        <h1>Ticket Not Found</h1>
        <p class="verify-subtitle">This QR code does not match a demo ticket stored by this running app.</p>
        <a class="verify-button" href="{{ url_for('home') }}">Back to demo generator</a>
    {% endif %}

    <div class="demo-warning">
        DEMO ONLY — NOT AN OFFICIAL NIET PASS OR AUTHORIZATION FOR EVENT ENTRY.
    </div>
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
            "event_date_display": datetime.strptime(
                event_date, "%Y-%m-%d"
            ).strftime("%d %b %Y"),
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

    if not ticket:
        verification = {
            "status": "TICKET NOT FOUND",
            "ticket": None,
            "is_valid": False
        }
    else:
        try:
            event_day = datetime.strptime(
                ticket["event_date"], "%Y-%m-%d"
            ).date()
            today = datetime.now().date()
            is_valid = event_day >= today
        except (ValueError, TypeError, KeyError):
            is_valid = False

        verification = {
            "status": "DEMO TICKET VALID" if is_valid else "TICKET EXPIRED",
            "ticket": ticket,
            "is_valid": is_valid
        }

    return render_template_string(
        HTML,
        show_form=False,
        ticket=None,
        verification=verification
    )

