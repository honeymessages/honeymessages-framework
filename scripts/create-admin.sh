#!/usr/bin/env bash
docker exec -it $(docker ps --filter name=honeymessages-docker -aq) python3 manage.py createsuperuser
