# https://fastapi.tiangolo.com/deployment/docker/
# TODO: update and pin python version
FROM python:3.12-slim AS builder

#RUN apt-get update && \
#    apt-get upgrade -y && \
#    apt-get install -y gcc
RUN apt-get update -y && apt-get install -y \
        gcc \
    && apt-get clean

# TODO: Is this the best workdir?
WORKDIR /code

# TODO: need to go over requirements
COPY ./requirements.txt /code/requirements.txt

# This looks good
RUN pip wheel --no-deps --wheel-dir /code/wheels -r /code/requirements.txt

FROM python:3.12-slim AS runner

COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .

RUN pip install --no-cache /wheels/*

#ENV PATH=/root/.local/bin:$PATH

WORKDIR /code
#COPY --from=builder /code /code

# This looks good
COPY ./app /code/app

# Expose the port on which the application will run
EXPOSE 9395

ENV PATH=/root/.local/bin:$PATH

# TODO: make port configurable and maybe get behind gunicorn
CMD ["fastapi", "run", "app/main.py", "--port", "9395"]
