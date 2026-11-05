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


# This Dockerfile builds a small Python container for an appointment app:

# 
# - `RUN ...` — creates a system user named `appuser`, creates `/data`, and gives that user ownership of the data directory.
# - `COPY --chown=...` — copies the two Python files into `/app` and makes `appuser` their owner. The validation script is copied but not run by this Dockerfile.
# - `USER appuser` — runs the app as the non-root user, which is safer.
# - `EXPOSE 8000` — documents that the container listens on port 8000; it does not publish the port by itself.
# - `CMD ["python", "app.py"]` — starts the app when the container runs.

# To make the app reachable from your machine, you’d typically start it with a port mapping such as `-p 8000:8000`.