FROM jupyter/scipy-notebook:latest
LABEL authors="robinkirchner"

EXPOSE 8888

COPY entrypoint.sh /home/backend/analysis/entrypoint.sh
COPY requirements.txt /home/backend/analysis/requirements.txt

WORKDIR /home/backend/analysis

RUN pip install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]
