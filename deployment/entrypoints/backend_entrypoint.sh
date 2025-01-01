#!/bin/bash
# $APP_PORT comes from docker-compose backend environment
# $VIRTUAL_ENV is uploaded by dockerfile into docker envs
set -e
source $VIRTUAL_ENV/bin/activate
cd /backend/api


#gunicorn app:app \
#--workers 4 \
#--worker-class=gevent --worker-connections=1000 \
#--bind 0.0.0.0:$APP_PORT --log-level 'debug'


gunicorn app:app \
--workers 5 \
--worker-class uvicorn.workers.UvicornWorker \
--bind 0.0.0.0:$APP_PORT --log-level 'debug'

#--worker-class=gevent --worker-connections=1000
#gunicorn --worker-class=gevent --worker-connections=1000 --workers=3 main:app


# gunicorn app:app \
#--logger-class "logging.gunicorn_patch.CustomLogger" \
# --workers 1 \
# --worker-class uvicorn.workers.UvicornWorker \
# --bind 0.0.0.0:"$APP_PORT" --log-level 'debug'
