# cronpan

A cron job monitor for humans. See your jobs, their logs, and toggle them on/off — no daemon, no database, no config files. Your crontab is the source of truth.

---

## Install

```bash
pipx install cronpan
```

Or with pip:

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
cronpan 9000
cronpan --port 9000
```

---

## Keep it running (Linux / VM)

To run cronpan as a background service that starts on boot:

```bash
cronpan --install-service
```

This writes a systemd unit file to `/tmp/cronpan.service` and prints the exact commands to install it:

```
sudo cp /tmp/cronpan.service /etc/systemd/system/cronpan.service
sudo systemctl daemon-reload
sudo systemctl enable cronpan
sudo systemctl start cronpan
```

> The `sudo` commands require root because writing to `/etc/systemd/system/` is a privileged operation. cronpan itself runs as your regular user — no root needed at runtime.

To stop and remove the service:

```bash
sudo systemctl stop cronpan
sudo systemctl disable cronpan
sudo rm /etc/systemd/system/cronpan.service
```

---

## Logging

cronpan can capture output from your cron jobs into daily log files at `~/.cronlogs/`.

Click **enable logging** on any job in the UI. It wraps the command with a logger script that timestamps each line of output.

Log files are organized as:
```
~/.cronlogs/
  job_name/
    20260310.log
    20260311.log
```

---

## Crontab conventions

cronpan reads and writes your real crontab. It uses comments to store display names:

```
#[DESCRIPTION] My Job Name
* * * * * /path/to/script.py
```

Disabled jobs are prefixed:
```
#[DISABLED] * * * * * /path/to/script.py
```

Deleted jobs are kept but hidden:
```
#[DELETED] * * * * * /path/to/script.py
```

---

## Docker (for testing)

```bash
docker build -t cronpan .
docker run -p 7878:7878 cronpan
```
