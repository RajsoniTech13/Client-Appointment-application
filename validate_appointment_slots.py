"""Checks the appointment date/time validation used by the web app."""

from datetime import datetime


def validate_appointment_slot(date_value, time_value, now=None):
    """Return an error message for an invalid or past slot, otherwise None."""
    try:
        appointment_at = datetime.strptime(
            f"{date_value} {time_value}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return "Enter a valid date and time."

    if appointment_at <= (now or datetime.now()):
        return "Choose a date and time in the future."
    return None


def main():
    fixed_now = datetime(2030, 1, 1, 12, 0)
    cases = (
        ("2030-01-01", "12:01", None),
        ("2030-01-01", "12:00", "Choose a date and time in the future."),
        ("2029-12-31", "11:59", "Choose a date and time in the future."),
        ("2030-02-30", "12:01", "Enter a valid date and time."),
        ("2030-01-01", "25:00", "Enter a valid date and time."),
    )

    for date_value, time_value, expected in cases:
        actual = validate_appointment_slot(date_value, time_value, fixed_now)
        if actual != expected:
            raise AssertionError(
                f"{date_value} {time_value}: expected {expected!r}, got {actual!r}"
            )

    print(f"Appointment slot validation passed ({len(cases)} cases).")


if __name__ == "__main__":
    main()


