FROM python:3.13.3-slim

WORKDIR /app

ENV TZ=Europe/Berlin

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod 0644 crontab && crontab crontab
RUN chmod 0755 entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
