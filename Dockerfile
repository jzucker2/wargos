# https://fastapi.tiangolo.com/deployment/docker/
# TODO: update and pin python version
FROM python:3.12-alpine

# TODO: Is this the best workdir?
WORKDIR /code

# TODO: need to go over requirements
COPY ./requirements.txt /code/requirements.txt

# This looks good
RUN pip install --no-cache-dir -r /code/requirements.txt

# This looks good
COPY ./app /code/app

# TODO: make port configurable and maybe get behind gunicorn
CMD ["fastapi", "run", "app/main.py", "--port", "9395"]
