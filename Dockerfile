FROM python:3.12-slim

ENV HOST=0.0.0.0 \
    PORT=8000 \
    DATABASE=/data/appointments.db \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --system --create-home appuser \
    && mkdir /data \
    && chown appuser:appuser /data

COPY --chown=appuser:appuser app.py validate_appointment_slots.py ./

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
