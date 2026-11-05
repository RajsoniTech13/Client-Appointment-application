from datetime import date, datetime
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import sqlite3


HOST = "127.0.0.1"
PORT = 8000
DATABASE = "appointments.db"
SERVICES = ("Consultation", "Follow-up", "Project review", "Other")


def connect_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    with connect_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                service TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Scheduled',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS one_scheduled_appointment_per_slot
            ON appointments (appointment_date, appointment_time)
            WHERE status = 'Scheduled'
        """)


def page(content, title="Client appointments", notice="", notice_kind="success"):
    message = f'<div class="notice {notice_kind}" role="status">{escape(notice)}</div>' if notice else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Appointly</title>
  <style>
    :root {{ color-scheme: light; --ink:#202b39; --muted:#718096; --line:#e5eaf0; --blue:#3559e0; --bg:#f5f7fb; }}
    * {{ box-sizing:border-box }} body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif }}
    header {{ height:72px; background:#fff; border-bottom:1px solid var(--line); display:flex; align-items:center; padding:0 max(24px,calc((100% - 1120px)/2)); gap:12px }}
    .logo {{ width:34px;height:34px;border-radius:10px;background:var(--blue);color:white;display:grid;place-items:center;font-weight:800 }} header strong {{ font-size:17px }} header span {{ color:var(--muted);font-size:13px;margin-left:auto }}
    main {{ max-width:1120px;margin:38px auto;padding:0 24px }} .intro {{ margin-bottom:25px }} h1 {{ font-size:29px;line-height:1.2;margin:0 0 7px;letter-spacing:-.6px }} .intro p {{ margin:0;color:var(--muted) }}
    .layout {{ display:grid;grid-template-columns:minmax(300px, .82fr) minmax(440px,1.4fr);gap:22px;align-items:start }} .card {{ background:white;border:1px solid var(--line);border-radius:14px;padding:24px;box-shadow:0 5px 18px #26344a08 }}
    h2 {{ font-size:18px;margin:0 0 18px }} label {{ display:block;font-size:13px;font-weight:650;margin:14px 0 6px }} input,select,textarea {{ width:100%;border:1px solid #d9e0e9;border-radius:8px;padding:11px 12px;font:inherit;color:var(--ink);background:#fff;outline:none }} input:focus,select:focus,textarea:focus {{ border-color:var(--blue);box-shadow:0 0 0 3px #3559e01a }} textarea {{ min-height:80px;resize:vertical }} .row {{ display:grid;grid-template-columns:1fr 1fr;gap:12px }}
    button {{ border:0;border-radius:8px;padding:11px 15px;font:inherit;font-weight:650;cursor:pointer }} .primary {{ background:var(--blue);color:white;width:100%;margin-top:19px }} .primary:hover {{ background:#284bd0 }} .cancel {{ padding:7px 10px;background:#fff1f0;color:#bd3d35;font-size:12px }} .cancel:hover {{ background:#ffe5e2 }}
    .table-wrap {{ overflow:auto }} table {{ border-collapse:collapse;width:100%;min-width:510px }} th {{ text-align:left;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em;padding:0 10px 12px }} td {{ padding:13px 10px;border-top:1px solid var(--line);vertical-align:middle;font-size:13px }} .client {{ font-weight:650;font-size:14px }} .sub {{ display:block;color:var(--muted);font-size:12px }} .pill {{ display:inline-block;background:#edf7f1;color:#28804b;border-radius:20px;padding:4px 9px;font-size:11px;font-weight:700 }} .pill.cancelled {{ background:#f1f2f5;color:#737b88 }}
    .empty {{ padding:34px 14px;text-align:center;color:var(--muted);border:1px dashed var(--line);border-radius:10px }} .notice {{ padding:12px 15px;margin:0 0 20px;border-radius:9px;font-size:14px }} .success {{ background:#eaf7ef;color:#236d41 }} .error {{ background:#fff0ee;color:#a8322a }} .small {{ color:var(--muted);font-size:12px;margin:12px 0 0 }}
    @media(max-width:850px) {{ .layout {{ grid-template-columns:1fr }} main {{ margin:26px auto }} }} @media(max-width:520px) {{ .card {{ padding:18px }} .row {{ grid-template-columns:1fr;gap:0 }} header span {{ display:none }} h1 {{ font-size:25px }} }}
  </style>
</head>
<body>
  <header><div class="logo">A</div><strong>Appointly</strong><span>Client scheduling</span></header>
  <main><div class="intro"><h1>Appointments</h1><p>Book and manage your client meetings in one place.</p></div>{message}{content}</main>
</body>
</html>"""


def render_dashboard(notice="", notice_kind="success", values=None):
    values = values or {}
    def val(key):
        return escape(values.get(key, ""), quote=True)

    options = "".join(
        f'<option value="{escape(service, quote=True)}" {"selected" if values.get("service") == service else ""}>{escape(service)}</option>'
        for service in SERVICES
    )
    form = f"""<section class="card"><h2>Request an appointment</h2>
      <form method="post" action="/appointments">
        <label for="client_name">Client name *</label><input id="client_name" name="client_name" maxlength="100" required value="{val('client_name')}" placeholder="e.g. Jamie Morgan">
        <label for="email">Email address *</label><input id="email" type="email" name="email" maxlength="254" required value="{val('email')}" placeholder="you@example.com">
        <label for="phone">Phone</label><input id="phone" name="phone" maxlength="40" value="{val('phone')}" placeholder="+1 555 0100" required>
        <label for="service">Appointment type *</label><select id="service" name="service" required><option value="">Choose a service</option>{options}</select>
        <div class="row"><div><label for="appointment_date">Date *</label><input id="appointment_date" type="date" name="appointment_date" min="{date.today().isoformat()}" required value="{val('appointment_date')}"></div><div><label for="appointment_time">Time *</label><input id="appointment_time" type="time" name="appointment_time" required value="{val('appointment_time')}"></div></div>
        <label for="notes">Notes <span style="font-weight:400;color:#718096">(optional)</span></label><textarea id="notes" name="notes" maxlength="500" placeholder="Anything to prepare for the meeting?">{val('notes')}</textarea>
        <button class="primary" type="submit">Book appointment</button><p class="small">All times use your local time. A time can only be booked once.</p>
      </form></section>"""
    with connect_db() as connection:
        rows = connection.execute("SELECT * FROM appointments ORDER BY appointment_date, appointment_time, id").fetchall()
    if rows:
        body = "".join(
            f"""<tr><td><span class="client">{escape(row['client_name'])}</span><span class="sub">{escape(row['email'])}{' · ' + escape(row['phone']) if row['phone'] else ''}</span></td>
            <td>{escape(row['service'])}</td><td>{escape(datetime.strptime(row['appointment_date'], '%Y-%m-%d').strftime('%b'))} {int(row['appointment_date'][8:])}, {escape(row['appointment_date'][:4])}<span class="sub">{escape(datetime.strptime(row['appointment_time'], '%H:%M').strftime('%I:%M %p').lstrip('0'))}</span></td>
            <td><span class="pill{' cancelled' if row['status'] == 'Cancelled' else ''}">{escape(row['status'])}</span></td><td>{f'<form method="post" action="/appointments/{row["id"]}/cancel"><button class="cancel" type="submit">Cancel</button></form>' if row['status'] == 'Scheduled' else ''}</td></tr>"""
            for row in rows
        )
        appointment_list = f'<div class="table-wrap"><table><thead><tr><th>Client</th><th>Type</th><th>Date &amp; time</th><th>Status</th><th></th></tr></thead><tbody>{body}</tbody></table></div>'
    else:
        appointment_list = '<div class="empty">No appointments yet.<br>New bookings will appear here.</div>'
    listing = f'<section class="card"><h2>Client schedule <span style="float:right;color:#718096;font-size:13px;font-weight:500">{len(rows)} total</span></h2>{appointment_list}</section>'
    return page(f'<div class="layout">{form}{listing}</div>', notice=notice, notice_kind=notice_kind)


class AppointmentHandler(BaseHTTPRequestHandler):
    def send_html(self, html, status=200):
        data = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def redirect(self):
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path != "/":
            self.send_html(page("<div class='empty'>That page could not be found.</div>", "Not found"), 404)
            return
        self.send_html(render_dashboard())

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith("/appointments/") and path.endswith("/cancel"):
            try:
                appointment_id = int(path.split("/")[2])
            except (ValueError, IndexError):
                self.send_html(render_dashboard("Invalid appointment.", "error"), 400)
                return
            with connect_db() as connection:
                connection.execute("UPDATE appointments SET status='Cancelled' WHERE id=? AND status='Scheduled'", (appointment_id,))
            self.redirect()
            return
        if path != "/appointments":
            self.send_html(page("<div class='empty'>That page could not be found.</div>", "Not found"), 404)
            return

        length = min(int(self.headers.get("Content-Length", "0")), 10000)
        posted = parse_qs(self.rfile.read(length).decode("utf-8", "replace"), keep_blank_values=True)
        values = {key: posted.get(key, [""])[0].strip() for key in ("client_name", "email", "phone", "service", "appointment_date", "appointment_time", "notes")}
        error = None
        if not values["client_name"] or not values["email"] or not values["service"] or not values["appointment_date"] or not values["appointment_time"]:
            error = "Please complete all required fields."
        elif len(values["email"]) > 254 or "@" not in values["email"]:
            error = "Enter a valid email address."
        elif values["service"] not in SERVICES:
            error = "Choose one of the listed appointment types."
        elif len(values["client_name"]) > 100 or len(values["phone"]) > 40 or len(values["notes"]) > 500:
            error = "One or more fields are too long."
        else:
            try:
                appointment_at = datetime.strptime(values["appointment_date"] + " " + values["appointment_time"], "%Y-%m-%d %H:%M")
                if appointment_at <= datetime.now():
                    error = "Choose a date and time in the future."
            except ValueError:
                error = "Enter a valid date and time."
        if error:
            self.send_html(render_dashboard(error, "error", values), 400)
            return

        try:
            with connect_db() as connection:
                connection.execute("""INSERT INTO appointments
                    (client_name,email,phone,service,appointment_date,appointment_time,notes)
                    VALUES (?,?,?,?,?,?,?)""", tuple(values[key] for key in ("client_name", "email", "phone", "service", "appointment_date", "appointment_time", "notes")))
        except sqlite3.IntegrityError:
            self.send_html(render_dashboard("That date and time is already booked. Please choose another slot.", "error", values), 409)
            return
        self.redirect()

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    initialize_db()
    print(f"Appointment app running at http://{HOST}:{PORT}")
    try:
        HTTPServer((HOST, PORT), AppointmentHandler).serve_forever()
    except KeyboardInterrupt:
        print("\nAppointment app stopped.")
