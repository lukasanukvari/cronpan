"""
Crontab read/write/parse logic for cronpan.
No database. Crontab is the source of truth.
"""

import os
import re
import subprocess
from pathlib import Path


CRONLOGS_DIR = Path.home() / '.cronlogs'
LOGGER_SCRIPT = CRONLOGS_DIR / 'logger.sh'

# logger.sh lives as a real file alongside this module
_LOGGER_SH_SOURCE = Path(__file__).parent / 'logger.sh'


def ensure_logger():
    """Copy logger.sh from package into ~/.cronlogs/ if not present."""
    CRONLOGS_DIR.mkdir(exist_ok=True)
    if not LOGGER_SCRIPT.exists():
        content = _LOGGER_SH_SOURCE.read_text()
        LOGGER_SCRIPT.write_text(content)
        LOGGER_SCRIPT.chmod(0o755)


def read_raw_crontab() -> list[str]:
    """Return raw crontab lines."""
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def write_raw_crontab(lines: list[str]):
    """Write lines back to crontab."""
    content = '\n'.join(lines) + '\n'
    proc = subprocess.run(['crontab', '-'], input=content, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f'Failed to write crontab: {proc.stderr}')


def is_cron_line(line: str) -> bool:
    """Check if a line is a cron entry (active or disabled/deleted)."""
    stripped = line.strip()
    for prefix in ('#[DISABLED] ', '#[DELETED] '):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break
    if re.match(r'^(@reboot|@yearly|@annually|@monthly|@weekly|@daily|@hourly)', stripped):
        return True
    if re.match(r'^(\*|[\d,\-*/]+)\s+(\*|[\d,\-*/]+)\s+(\*|[\d,\-*/]+)\s+(\*|[\d,\-*/]+)\s+(\*|[\d,\-*/]+)\s+\S', stripped):
        return True
    return False


def extract_log_path(command: str):
    """
    Extract log dir (our logger) or log file (user's own) from command.
    Returns (log_path, job_name, is_dir).
    """
    m = re.search(r'\|\s*\S*logger\.sh\s+(\S+)\s+"([^"]*)"', command)
    if m:
        return m.group(1).replace('~', str(Path.home())), m.group(2), True
    m = re.search(r'>>\s*(\S+\.log)', command)
    if m:
        return m.group(1).replace('~', str(Path.home())), None, False
    return None, None, False


def strip_our_logging(command: str) -> str:
    """Remove our logger.sh pipe from a command to show the clean user command."""
    command = re.sub(r'\s*2>&1\s*\|\s*\S*logger\.sh\s+\S+\s+"[^"]*"', '', command)
    return command.strip()


def is_complex(command: str) -> bool:
    """Detect shell constructs we can't safely wrap."""
    clean = strip_our_logging(command)
    if re.search(r'\|(?!\s*\S*logger\.sh)', clean):
        return True
    if '&&' in clean or '||' in clean:
        return True
    if clean.strip().startswith('{'):
        return True
    return False


def has_other_redirection(command: str) -> bool:
    """Check if command has >> redirection that isn't our logger."""
    clean = strip_our_logging(command)
    return '>>' in clean or ('>' in clean and '2>&1' not in clean and '>>' not in clean)


def parse_schedule_command(line: str):
    """Split a cron line into (schedule_str, command_str)."""
    line = line.strip()
    m = re.match(r'^(@\w+)\s+(.*)', line)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r'^((?:\S+\s+){5})(.*)', line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return line, ''


def parse_crontab() -> list[dict]:
    """
    Parse crontab into a list of job dicts.
    Each job:
      id, name, schedule, command, raw_command, status,
      log_path, log_accessible, is_complex, has_other_redirect,
      line_index (of the cron line in raw lines)
    """
    ensure_logger()
    raw = read_raw_crontab()
    jobs = []
    job_id = 0
    i = 0

    while i < len(raw):
        line = raw[i]

        if not is_cron_line(line):
            i += 1
            continue

        stripped = line.strip()
        status = 'active'
        actual_line = stripped

        if stripped.startswith('#[DELETED] '):
            status = 'deleted'
            actual_line = stripped[len('#[DELETED] '):]
        elif stripped.startswith('#[DISABLED] '):
            status = 'disabled'
            actual_line = stripped[len('#[DISABLED] '):]

        # Look for #[DESCRIPTION] comment immediately above (skip blank lines)
        name = None
        j = i - 1
        while j >= 0 and raw[j].strip() == '':
            j -= 1
        if j >= 0:
            desc_m = re.match(r'#\[DESCRIPTION\]\s+(.*)', raw[j].strip())
            legacy_m = re.match(r'#\[(.+)\]$', raw[j].strip()) if not desc_m else None
            if desc_m:
                name = desc_m.group(1).strip()
            elif legacy_m and legacy_m.group(1) not in ('DISABLED', 'DELETED'):
                name = legacy_m.group(1)

        schedule, command = parse_schedule_command(actual_line)
        display_command = strip_our_logging(command)

        if not name:
            name = display_command

        log_path, _, log_is_dir = extract_log_path(command)
        log_accessible = False
        log_inaccessible_reason = None
        has_logging = False
        log_our_file = False

        if log_path:
            has_logging = True
            p = Path(log_path)
            log_our_file = str(CRONLOGS_DIR) in str(p)
            if log_is_dir:
                if p.exists() and any(p.glob('*.log')):
                    log_accessible = True
                else:
                    log_inaccessible_reason = 'Job has not run yet since logging was enabled.'
            else:
                if p.exists() and os.access(p, os.R_OK):
                    log_accessible = True
                elif not p.exists():
                    log_inaccessible_reason = f'Log file not found: {log_path}'
                else:
                    log_inaccessible_reason = f'No read permission: {log_path}'

        complex_job = is_complex(command)
        other_redirect = has_other_redirection(command)

        jobs.append({
            'id': job_id,
            'name': name,
            'schedule': schedule,
            'command': display_command,
            'raw_command': command,
            'status': status,
            'line_index': i,
            'log_path': log_path,
            'log_accessible': log_accessible,
            'log_inaccessible_reason': log_inaccessible_reason,
            'has_logging': has_logging,
            'log_our_file': log_our_file,
            'log_is_dir': log_is_dir,
            'is_complex': complex_job,
            'has_other_redirect': other_redirect,
        })

        job_id += 1
        i += 1

    return jobs


def enable_job(line_index: int):
    raw = read_raw_crontab()
    line = raw[line_index].strip()
    if line.startswith('#[DISABLED] '):
        raw[line_index] = line[len('#[DISABLED] '):]
    write_raw_crontab(raw)


def disable_job(line_index: int):
    raw = read_raw_crontab()
    line = raw[line_index].strip()
    if not line.startswith('#[DISABLED] ') and not line.startswith('#[DELETED] '):
        raw[line_index] = '#[DISABLED] ' + line
    write_raw_crontab(raw)


def delete_job(line_index: int):
    raw = read_raw_crontab()
    line = raw[line_index].strip()
    for prefix in ('#[DISABLED] ', '#[DELETED] '):
        if line.startswith(prefix):
            line = line[len(prefix):]
    raw[line_index] = '#[DELETED] ' + line
    write_raw_crontab(raw)


def add_logging(line_index: int, job_name: str):
    """Add our logger.sh pipe to a cron line."""
    ensure_logger()
    raw = read_raw_crontab()
    line = raw[line_index].strip()

    prefix = ''
    for p in ('#[DISABLED] ', '#[DELETED] '):
        if line.startswith(p):
            prefix = p
            line = line[len(p):]
            break

    schedule, command = parse_schedule_command(line)
    safe_name = job_name.replace('"', "'")
    log_dirname = re.sub(r'[^\w\-]', '_', job_name.lower())[:40]
    log_path = str(CRONLOGS_DIR / log_dirname)
    new_command = f'{command} 2>&1 | {LOGGER_SCRIPT} {log_path} "{safe_name}"'
    new_line = f'{schedule} {new_command}'
    raw[line_index] = prefix + new_line
    write_raw_crontab(raw)


def remove_logging(line_index: int):
    """Remove our logger.sh from a cron line."""
    raw = read_raw_crontab()
    line = raw[line_index].strip()

    prefix = ''
    for p in ('#[DISABLED] ', '#[DELETED] '):
        if line.startswith(p):
            prefix = p
            line = line[len(p):]
            break

    schedule, command = parse_schedule_command(line)
    clean_command = strip_our_logging(command)
    raw[line_index] = prefix + f'{schedule} {clean_command}'
    write_raw_crontab(raw)


def read_logs(log_path: str, date: str = None, lines: int = 500):
    """Read last N lines from a dated log dir or a plain log file."""
    from datetime import date as dt_mod

    p = Path(log_path.replace('~', str(Path.home())))
    if p.is_dir() or (not p.exists() and not log_path.endswith('.log')):
        if not p.exists():
            return None, 'Job has not run yet since logging was enabled.'
        target = date or dt_mod.today().strftime('%Y%m%d')
        path = p / f'{target}.log'
        if not path.exists():
            fmt = f'{target[:4]}-{target[4:6]}-{target[6:]}'
            return None, f'No logs for {fmt}.'
    else:
        path = p

    if not path.exists():
        return None, 'Log file does not exist yet.'
    if not os.access(path, os.R_OK):
        return None, 'Cannot read log file: permission denied.'

    try:
        content = path.read_text(errors='replace')
        all_lines = content.splitlines()
        if len(all_lines) > lines:
            all_lines = all_lines[-lines:]
        return '\n'.join(all_lines), None
    except Exception as e:
        return None, str(e)


def list_log_dates(log_path: str) -> list:
    """Return sorted list of available YYYYMMDD dates for a dir-based log path."""
    p = Path(log_path.replace('~', str(Path.home())))
    if not p.is_dir():
        return []
    dates = []
    for f in p.glob('*.log'):
        if re.match(r'^\d{8}$', f.stem):
            dates.append(f.stem)
    return sorted(dates, reverse=True)


def get_running_procs() -> list[str]:
    """Return full command strings of all running processes via /proc or ps fallback."""
    procs = []

    proc_path = Path('/proc')
    if proc_path.exists():
        for pid_dir in proc_path.iterdir():
            if not pid_dir.name.isdigit():
                continue
            try:
                cmdline = (pid_dir / 'cmdline').read_bytes()
                cmd = cmdline.replace(b'\x00', b' ').decode(errors='replace').strip()
                if cmd:
                    procs.append(cmd)
            except Exception:
                continue
        return procs

    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()[1:]
            return [' '.join(l.split()[10:]).strip() for l in lines if l.strip()]
    except Exception:
        pass

    return []


def is_job_running(raw_command: str) -> bool:
    """Check if a cron job is currently running by matching script paths in running processes."""
    if not raw_command:
        return False

    clean = strip_our_logging(raw_command).strip()
    tokens = re.findall(r'(/[^\s|&;>]+)', clean)
    tokens = [t for t in tokens if '.' in t.split('/')[-1] or t.count('/') > 2]

    if not tokens:
        first = clean.split()[0] if clean.split() else ''
        if len(first) > 5:
            tokens = [first]

    if not tokens:
        return False

    procs = get_running_procs()
    for proc in procs:
        for token in tokens:
            if token in proc:
                return True
    return False


def rename_job(line_index: int, new_name: str):
    """
    Update or insert #[DESCRIPTION] comment, and update logger name in the cron line.
    If new_name is empty, remove the description line so command is used as display name.
    """
    raw = read_raw_crontab()

    j = line_index - 1
    while j >= 0 and raw[j].strip() == '':
        j -= 1
    has_desc = j >= 0 and re.match(r'#\[(DESCRIPTION|[^\]]+)\]', raw[j].strip())

    if not new_name:
        if has_desc:
            raw.pop(j)
        write_raw_crontab(raw)
        return

    if has_desc:
        raw[j] = f'#[DESCRIPTION] {new_name}'
    else:
        raw.insert(line_index, f'#[DESCRIPTION] {new_name}')
        line_index += 1

    safe_name = new_name.replace('"', "'")
    cron_line = raw[line_index]
    cron_line = re.sub(
        r'(\|\s*\S*logger\.sh\s+\S+\s+)"[^"]*"',
        lambda m: m.group(1) + f'"{safe_name}"',
        cron_line,
    )
    raw[line_index] = cron_line
    write_raw_crontab(raw)


def clear_logs(log_path: str) -> int:
    """Delete all log files for a job. Returns number of files deleted."""
    p = Path(log_path.replace('~', str(Path.home())))
    count = 0
    if p.is_dir():
        for f in p.glob('*.log'):
            f.unlink()
            count += 1
    elif p.is_file():
        p.unlink()
        count = 1
    return count
