#!/usr/bin/env bash
docker exec -it $(docker ps --filter name=honeymessages -aq) python3 manage.py collectstatic --noinput
