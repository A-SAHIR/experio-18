# Pulling ubuntu image with a specific tag from the docker hub.
FROM ubuntu:18.04

# Adding maintainer name (Optional).
MAINTAINER Brahim Lamnaouar

WORKDIR /cron

# Updating the packages and installing cron and vim editor if you later want to edit your script from inside your container.
RUN apt-get update \
    && apt-get install cron vim python3-pip python3-dev libpq-dev -y

RUN pip3 install python-dotenv requests psycopg2-binary python-dateutil==2.8.2

# Crontab file copied to cron.d directory.
COPY ./cron/container_cronjob /etc/cron.d/container_cronjob

# Script file copied into container.
COPY ./cron/entrypoint.sh /cron/entrypoint.sh

# Giving executable permission to script file.
RUN chmod +x /cron/entrypoint.sh

COPY ./cron/scripts /cron
COPY ./cron/cron.env /cron/.env

# Running commands for the startup of a container.
CMD ["/bin/bash", "-c", "/cron/entrypoint.sh && chmod 644 /etc/cron.d/container_cronjob && cron && tail -f /var/log/cron.log"]
