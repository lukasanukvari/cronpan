#!/usr/bin/env python3
"""A job that prints lots of long lines to test log rendering."""
import sys

lines = [
    'Initializing data pipeline for environment: production-us-east-1',
    'Loading configuration from /etc/app/config.yaml — found 142 keys across 12 sections',
    'Connecting to database host=db.internal.example.com port=5432 dbname=analytics user=etl_service',
    'Connection established. Server version: PostgreSQL 15.3 on x86_64-pc-linux-gnu',
    'Fetching records from table=events WHERE created_at >= NOW() - INTERVAL 24 HOURS',
    'Query returned 48,291 rows in 1.23s — estimated memory usage: 94.7 MB',
    'Starting transformation pipeline: normalize → deduplicate → enrich → validate',
    'Step 1/4 normalize: applied 7 normalization rules to 48,291 records, 312 records failed validation and were skipped',
    'Step 2/4 deduplicate: found 1,847 duplicate event_ids, keeping most recent by updated_at timestamp',
    'Step 3/4 enrich: joined with user_profiles table on user_id — 46,132 matches (98.3% hit rate)',
    'Step 4/4 validate: schema validation passed for 46,044 records, 88 records dropped due to missing required fields: [session_id, geo_country]',
    'Writing 46,044 records to output bucket=s3://analytics-prod/events/2026/03/11/ prefix=batch_20260311_143501',
    'Upload progress: 10% (4,604 records) — throughput: 2,301 records/sec',
    'Upload progress: 25% (11,511 records) — throughput: 2,287 records/sec',
    'Upload progress: 50% (23,022 records) — throughput: 2,295 records/sec',
    'Upload progress: 75% (34,533 records) — throughput: 2,301 records/sec',
    'Upload progress: 100% (46,044 records) — throughput: 2,298 records/sec',
    'Upload complete. Total bytes written: 187,432,019 (178.7 MB). Duration: 20.03s',
    'Updating job_runs table: INSERT INTO job_runs (job_name, started_at, finished_at, records_processed, status)',
    'Sending completion notification to monitoring.internal.example.com/api/v2/events',
    'Response: 200 OK {"event_id":"evt_9f3a2b1c","received":true,"alert_triggered":false}',
    'Cleaning up temp files in /tmp/etl_scratch/batch_20260311_143501/ — removed 14 files (23.1 MB)',
    'Pipeline complete. Summary: input=48291 skipped=312 dupes=1847 enriched=46132 invalid=88 written=46044',
    'Total wall time: 31.7s — next scheduled run: 2026-03-11 15:00:00 UTC',
]

for line in lines:
    print(line, flush=True)

print('Done.', flush=True)
sys.exit(0)
