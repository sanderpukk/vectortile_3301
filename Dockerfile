FROM ghcr.io/osgeo/gdal:ubuntu-full-latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY src/ /app/src/
COPY config/ /app/config/
COPY viewer/ /app/viewer/

ENV PYTHONPATH=/app/src

ENTRYPOINT ["python3", "-m", "vt_pipeline"]
