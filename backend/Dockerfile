FROM pandas/pandas:alpine

# set work directory
WORKDIR /usr/src/backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
