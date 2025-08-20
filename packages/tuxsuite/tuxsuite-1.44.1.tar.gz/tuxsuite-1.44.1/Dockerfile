FROM python:3.9-slim

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl jq media-types mailcap \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

COPY dist/*.whl /

# hadolint ignore=DL3013
RUN pip --no-cache-dir install /*.whl

CMD ["tuxsuite", "--help"]
