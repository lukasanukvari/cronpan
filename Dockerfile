FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron bash dos2unix coreutils && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install flask && pip install . --no-build-isolation

COPY test/crontab /tmp/testcrontab
RUN dos2unix /tmp/testcrontab && echo "" >> /tmp/testcrontab && crontab /tmp/testcrontab

# Seed sample logs for analytics_pipeline
RUN mkdir -p /root/.cronlogs/analytics_pipeline
COPY test/sample_logs/analytics_pipeline/ /root/.cronlogs/analytics_pipeline/

# Startup script: launch cron + cronpan together
RUN echo '#!/bin/bash\nservice cron start\ncronpan' > /start.sh && chmod +x /start.sh

EXPOSE 7878
CMD ["/start.sh"]
