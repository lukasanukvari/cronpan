"""
cronpan Flask server.
"""

import re
import sys
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory

from cronpan.crontab import (
    add_logging,
    clear_logs,
    delete_job,
    disable_job,
    enable_job,
    get_running_procs,
    is_job_running,
    list_log_dates,
    parse_crontab,
    read_logs,
    remove_logging,
    rename_job,
    strip_our_logging,
)


STATIC_DIR = Path(__file__).parent / 'static'
app = Flask(__name__, static_folder=str(STATIC_DIR))


@app.route('/')
def root():
    return redirect('/home')


@app.route('/home')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(STATIC_DIR, path)


@app.route('/api/jobs')
def api_jobs():
    try:
        jobs = parse_crontab()
        for job in jobs:
            job['running'] = is_job_running(job['raw_command']) if job['status'] == 'active' else False
        return jsonify({'ok': True, 'jobs': jobs})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/enable', methods=['POST'])
def api_enable(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        enable_job(job['line_index'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/disable', methods=['POST'])
def api_disable(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        disable_job(job['line_index'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/delete', methods=['POST'])
def api_delete(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        delete_job(job['line_index'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/add-logging', methods=['POST'])
def api_add_logging(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        add_logging(job['line_index'], job['name'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/remove-logging', methods=['POST'])
def api_remove_logging(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        remove_logging(job['line_index'])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/logs')
def api_logs(job_id):
    try:
        date = request.args.get('date')
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        if not job['log_path']:
            return jsonify({'ok': False, 'error': 'No log file configured for this job.'})
        content, error = read_logs(job['log_path'], date=date)
        if error:
            return jsonify({'ok': False, 'error': error})
        return jsonify({'ok': True, 'logs': content, 'log_path': job['log_path']})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/log-dates')
def api_log_dates(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        dates = list_log_dates(job['log_path']) if job.get('log_is_dir') and job.get('log_path') else []
        return jsonify({'ok': True, 'dates': dates})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/rename', methods=['POST'])
def api_rename(job_id):
    try:
        data = request.get_json()
        new_name = (data.get('name') or '').strip()
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        rename_job(job['line_index'], new_name)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/jobs/<int:job_id>/clear-logs', methods=['POST'])
def api_clear_logs(job_id):
    try:
        jobs = parse_crontab()
        job = next((j for j in jobs if j['id'] == job_id), None)
        if not job:
            return jsonify({'ok': False, 'error': 'Job not found'}), 404
        if not job.get('log_path'):
            return jsonify({'ok': False, 'error': 'No log path configured for this job.'})
        count = clear_logs(job['log_path'])
        return jsonify({'ok': True, 'deleted': count})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/debug/ps')
def api_debug_ps():
    """Debug: show raw process list and running detection for each job."""
    procs = get_running_procs()
    jobs = parse_crontab()
    job_debug = []
    for job in jobs:
        rc = job.get('raw_command', '')
        clean = strip_our_logging(rc).strip()
        tokens = re.findall(r'(/[^\s|&;>]+)', clean)
        tokens = [t for t in tokens if '.' in t.split('/')[-1] or t.count('/') > 2]
        matches = [p for p in procs for t in tokens if t in p]
        job_debug.append({'name': job['name'], 'tokens': tokens, 'matches': matches[:3]})
    return jsonify({'ok': True, 'proc_count': len(procs), 'sample_procs': procs[:20], 'jobs': job_debug})


def run(port=7878, debug=False):
    print(f'\n  🌱 cronpan running at http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=debug)
