import sqlite3
from datetime import datetime

import pytest

import app
from validate_appointment_slots import validate_appointment_slot


FIXED_NOW = datetime(2030, 1, 1, 12, 0)


@pytest.mark.parametrize(
    ("date_value", "time_value", "expected_error"),
    [
        pytest.param("2030-01-01", "12:01", None, id="available-future-slot"),
        pytest.param(
            "2030-01-01",
            "12:00",
            "Choose a date and time in the future.",
            id="boundary-equal-to-now",
        ),
        pytest.param(
            "2030-01-01",
            "11:59",
            "Choose a date and time in the future.",
            id="past-slot",
        ),
        pytest.param(
            "2030-02-30", "12:01", "Enter a valid date and time.", id="invalid-date"
        ),
    ],
)
def test_appointment_slot_validation(date_value, time_value, expected_error):
    assert validate_appointment_slot(date_value, time_value, FIXED_NOW) == expected_error


def test_booked_slot_rejects_second_scheduled_appointment(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "DATABASE", str(tmp_path / "appointments.db"))
    app.initialize_db()

    appointment = (
        "Jamie Morgan",
        "jamie@example.com",
        "555-0100",
        "Consultation",
        "2030-01-02",
        "09:30",
        "",
    )
    with app.connect_db() as connection:
        connection.execute(
            """INSERT INTO appointments
            (client_name, email, phone, service, appointment_date, appointment_time, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            appointment,
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """INSERT INTO appointments
                (client_name, email, phone, service, appointment_date, appointment_time, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("Taylor Lee", "taylor@example.com", "555-0101", *appointment[3:]),
            )
