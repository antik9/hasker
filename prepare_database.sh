#!/usr/bin/env bash

docker run -d --name prepare_database \
    -v hasker_pg_data:/var/lib/postgresql/data \
    -v $(pwd)/create_admin.sh:/tmp/create_admin.sh \
    postgres:9.6

sleep 5
docker exec prepare_database bash -c 'bash /tmp/create_admin.sh'

docker stop prepare_database
