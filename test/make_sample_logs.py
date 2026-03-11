from pathlib import Path

log_dir = Path('/tmp/cronpan/test/sample_logs/analytics_pipeline')
log_dir.mkdir(parents=True, exist_ok=True)

day1 = '20260310'
day2 = '20260311'

lines_day1 = [
    '▶ [2026-03-10 08:50:01] START: Analytics Pipeline',
    '[2026-03-10 08:50:01] Initializing data pipeline for environment: production-us-east-1',
    '[2026-03-10 08:50:01] Loading configuration from /etc/app/config.yaml — found 142 keys across 12 sections',
    '[2026-03-10 08:50:02] Connecting to database host=db.internal.example.com port=5432 dbname=analytics user=etl_service',
    '[2026-03-10 08:50:02] Connection established. Server version: PostgreSQL 15.3 on x86_64-pc-linux-gnu',
    '[2026-03-10 08:50:02] Fetching records from table=events WHERE created_at >= NOW() - INTERVAL 24 HOURS',
    '[2026-03-10 08:50:03] Query returned 48,291 rows in 1.23s — estimated memory usage: 94.7 MB',
    '[2026-03-10 08:50:03] Starting transformation pipeline: normalize → deduplicate → enrich → validate',
    '[2026-03-10 08:50:04] Step 1/4 normalize: applied 7 normalization rules to 48,291 records, 312 records failed validation and were skipped',
    '[2026-03-10 08:50:05] Step 2/4 deduplicate: found 1,847 duplicate event_ids, keeping most recent by updated_at timestamp',
    '[2026-03-10 08:50:06] Step 3/4 enrich: joined with user_profiles table on user_id — 46,132 matches (98.3% hit rate)',
    '[2026-03-10 08:50:07] Step 4/4 validate: schema validation passed for 46,044 records, 88 records dropped due to missing required fields',
    '[2026-03-10 08:50:08] Writing 46,044 records to s3://analytics-prod/events/2026/03/10/',
    '[2026-03-10 08:50:09] Upload progress: 25% (11,511 records) — throughput: 2,287 records/sec',
    '[2026-03-10 08:50:11] Upload progress: 50% (23,022 records) — throughput: 2,295 records/sec',
    '[2026-03-10 08:50:13] Upload progress: 75% (34,533 records) — throughput: 2,301 records/sec',
    '[2026-03-10 08:50:15] Upload progress: 100% (46,044 records) — throughput: 2,298 records/sec',
    '[2026-03-10 08:50:15] Upload complete. Total bytes written: 187,432,019 (178.7 MB). Duration: 20.03s',
    '[2026-03-10 08:50:16] Pipeline complete. Summary: input=48291 skipped=312 dupes=1847 written=46044',
    '■ [2026-03-10 08:50:16] END: Analytics Pipeline | EXIT:0',
]

lines_day2 = [
    '▶ [2026-03-11 08:50:01] START: Analytics Pipeline',
    '[2026-03-11 08:50:01] Initializing data pipeline for environment: production-us-east-1',
    '[2026-03-11 08:50:01] Loading configuration from /etc/app/config.yaml — found 142 keys across 12 sections',
    '[2026-03-11 08:50:02] Connecting to database host=db.internal.example.com port=5432 dbname=analytics user=etl_service',
    '[2026-03-11 08:50:02] Connection established. Server version: PostgreSQL 15.3 on x86_64-pc-linux-gnu',
    '[2026-03-11 08:50:02] Fetching records from table=events WHERE created_at >= NOW() - INTERVAL 24 HOURS',
    '[2026-03-11 08:50:03] Query returned 51,847 rows in 1.41s — estimated memory usage: 101.2 MB',
    '[2026-03-11 08:50:03] Starting transformation pipeline: normalize → deduplicate → enrich → validate',
    '[2026-03-11 08:50:04] Step 1/4 normalize: applied 7 normalization rules to 51,847 records, 401 records failed validation and were skipped',
    '[2026-03-11 08:50:05] Step 2/4 deduplicate: found 2,103 duplicate event_ids, keeping most recent by updated_at timestamp',
    '[2026-03-11 08:50:06] Step 3/4 enrich: joined with user_profiles table on user_id — 49,218 matches (97.9% hit rate)',
    '[2026-03-11 08:50:07] Step 4/4 validate: schema validation passed for 49,101 records, 117 records dropped due to missing required fields',
    '[2026-03-11 08:50:08] Writing 49,101 records to s3://analytics-prod/events/2026/03/11/',
    '[2026-03-11 08:50:09] Upload progress: 25% — throughput: 2,301 records/sec',
    '[2026-03-11 08:50:11] Upload progress: 50% — throughput: 2,288 records/sec',
    '[2026-03-11 08:50:13] Upload progress: 75% — throughput: 2,294 records/sec',
    '[2026-03-11 08:50:15] Upload progress: 100% (49,101 records) — throughput: 2,296 records/sec',
    '[2026-03-11 08:50:15] Upload complete. Total bytes written: 200,147,832 (190.9 MB). Duration: 21.11s',
    '[2026-03-11 08:50:16] ERROR: Failed to update job_runs table — connection timeout after 30s',
    '[2026-03-11 08:50:16] Retrying database write... attempt 2/3',
    '[2026-03-11 08:50:17] Retrying database write... attempt 3/3',
    '[2026-03-11 08:50:17] All retries exhausted. Continuing without audit log entry.',
    '[2026-03-11 08:50:17] Pipeline complete with warnings. input=51847 skipped=401 dupes=2103 written=49101',
    '■ [2026-03-11 08:50:17] END: Analytics Pipeline | EXIT:1',
]

(log_dir / f'{day1}.log').write_text('\n'.join(lines_day1) + '\n')
(log_dir / f'{day2}.log').write_text('\n'.join(lines_day2) + '\n')
print('Sample logs written.')
