#!/bin/bash
touch out/server.log
docker build -t honeymessages_ipython .
docker run -itd -p 8889:8888 \
  --mount type=bind,source="$(pwd)"/../../backend,target=/home/backend \
  --mount type=bind,source="$(pwd)"/../../.env,target=/home/.env \
  --mount type=bind,source="$(pwd)"/out/server.log,target=/home/server.log \
  --mount type=bind,source="$(pwd)"/out,target=/home/out \
  -e JUPYTER_TOKEN="honey" \
  --name honeymessages_ipython \
  honeymessages_ipython
