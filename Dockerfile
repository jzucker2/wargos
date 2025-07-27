# https://fastapi.tiangolo.com/deployment/docker/
ARG PYTHON_VERSION=3.12-alpine
FROM python:${PYTHON_VERSION} AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN set -x \
    && apk update  \
    && apk add --no-cache  \
      gcc \
      python3-dev \
      musl-dev \
      linux-headers

# TODO: Is this the best workdir?
WORKDIR /code

# TODO: need to go over requirements
COPY ./requirements.txt /code/requirements.txt

# This looks good
RUN pip wheel --no-deps --wheel-dir /code/wheels -r /code/requirements.txt

FROM python:${PYTHON_VERSION} AS runner

RUN set -x \
    && apk update  \
    && apk add --no-cache  \
      curl

COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .

RUN pip install --no-cache --no-deps /wheels/*

WORKDIR /code

# This looks good
COPY ./app /code/app

# Set default environment variables for Gunicorn
ENV PORT=9395
ENV WORKERS=4
ENV WORKER_CLASS=uvicorn.workers.UvicornWorker
ENV TIMEOUT=120
ENV KEEPALIVE=2
ENV MAX_REQUESTS=1000
ENV MAX_REQUESTS_JITTER=50

# Expose the port on which the application will run
EXPOSE ${PORT}

HEALTHCHECK --interval=5s --timeout=5s --retries=3 \
    CMD curl -f http://0.0.0.0:${PORT}/healthz || exit 1

# Use Gunicorn with Uvicorn workers
CMD ["sh", "-c", "gunicorn app.main:app --bind 0.0.0.0:${PORT} --workers ${WORKERS} --worker-class ${WORKER_CLASS} --timeout ${TIMEOUT} --keep-alive ${KEEPALIVE} --max-requests ${MAX_REQUESTS} --max-requests-jitter ${MAX_REQUESTS_JITTER}"]
