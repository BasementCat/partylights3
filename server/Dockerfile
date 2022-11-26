FROM python:alpine

# WORKDIR /app

COPY requirements-build.txt /tmp/

# for deps, all in 1 run command, joined with &&
# runtime deps - `apk add <package...>`
# build deps - `apk add --no-cache --virtual .build-deps <package...>` - followed by `apk del .build-deps` after pip install

RUN apk add --no-cache --virtual .build-deps \
        # Build deps
        alpine-sdk \
        python3-dev \
    # May depend on build deps
    && pip install --no-cache-dir -r /tmp/requirements-build.txt \
    && apk del .build-deps

COPY requirements-py.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-py.txt