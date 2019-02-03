#!/bin/bash

if [ "$1" = "api_server" ]; then

  if [ "$TEST" = "1" ]; then
    echo "Run unit test"
    python -m pytest  test/ -vv
    exit 0
  fi

  gunicorn --reload "rest.app:get_app()"
  sleep infinity
fi

exec "$@"

