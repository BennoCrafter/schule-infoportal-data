# schule-infoportal-data

A self-hosted Docker container that fetches substitutions and news from schule-infoportal-api
once a day (22:00, via cron) and stores them in a local SQLite database.

Run with `docker compose up -d`.

To trigger an update manually (e.g. for testing): `python main.py`.
To change the schedule, edit the cron expression in the `crontab` file.
