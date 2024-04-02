#!/usr/bin/env bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build --force-recreate
docker exec -it $(docker ps --filter name=honeymessages -aq) python3 manage.py migrate
docker exec -it $(docker ps --filter name=honeymessages -aq) python3 manage.py collectstatic --noinput
