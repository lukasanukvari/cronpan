# cronpan

Cron job monitor for humans — no daemon, no docker, no database, just your crontab.

---

## Install

```bash
pip install cronpan
```

---

## Run

```bash
cronpan
```

Opens at `http://localhost:7878`. On a headless machine (VM, server) it won't try to open a browser — just visit the URL from your own machine at `http://your-server-ip:7878`.

Change the port:

```bash
cronpan --port 9000
```

---

## What you can do

- View all your cron jobs in one place
- Enable / disable jobs without editing the crontab manually
- Rename jobs with a display name
- Enable built-in logging — captures output to daily log files at `~/.cronlogs/`
- Set a custom log file path for jobs that already write their own logs
- View system jobs from `/etc/cron.d/` (read-only)

---

## Logging

### Built-in logging

Click **enable logging** on any job. cronpan wraps the command with a logger script that timestamps every line of output and writes daily log files:

```
~/.cronlogs/
  job_name/
    20260310.log
    20260311.log
```

### Custom log file

If your script already writes its own log file, click **set log file** and enter the full path. cronpan will read it as-is and show it in the UI. The path is stored as a comment in your crontab:

```
* * * * * /path/to/script.py #[LOGPATH] /var/log/myjob.log
```

---

## Keep it running (Linux / VM)

To run cronpan as a background service that starts on boot:

```bash
cronpan --install-service
```

This writes a systemd unit file to `/tmp/cronpan.service` and prints the exact commands to install it:

```bash
sudo cp /tmp/cronpan.service /etc/systemd/system/cronpan.service
sudo systemctl daemon-reload
sudo systemctl enable cronpan
sudo systemctl start cronpan
```

> cronpan runs as your regular user — no root needed at runtime.

To stop and remove the service:

```bash
sudo systemctl stop cronpan
sudo systemctl disable cronpan
sudo rm /etc/systemd/system/cronpan.service
```

---

## Crontab conventions

cronpan reads and writes your real crontab. It uses comments to store metadata:

```
#[DESCRIPTION] My Job Name
* * * * * /path/to/script.py
```

```
#[DISABLED] * * * * * /path/to/script.py
```

```
#[DELETED] * * * * * /path/to/script.py
```

```
* * * * * /path/to/script.py #[LOGPATH] /var/log/myjob.log
```

---

## Docker (for testing)

```bash
docker build -t cronpan .

docker run -p 7878:7878 cronpan
```
