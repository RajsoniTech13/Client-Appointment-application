# Client Appointment Application

A small Python web app for booking and managing client appointments. It uses only the Python standard library and stores appointments in a local SQLite database.

## Run

From this folder, start the app with:

```sh
python3 app.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Press `Ctrl+C` in the terminal to stop the server. The app creates `appointments.db` in this folder when it starts.

## Features

- Book an appointment with client contact details, service, date, time, and optional notes.
- Reject past appointments and prevent duplicate date-and-time bookings.
- View scheduled and cancelled appointments, and cancel a scheduled booking.
- Keep data between runs in SQLite.

This is intended for local use. It does not include accounts, access controls, or remote hosting configuration.
