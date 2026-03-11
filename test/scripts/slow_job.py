#!/usr/bin/env python3
"""A slow job that takes 15 seconds — used to test the 'running now' indicator."""
import sys
import time

def log(msg):
    print(msg, flush=True)
    sys.stdout.flush()

log("slow_job: starting...")
for i in range(1, 16):
    log(f"slow_job: step {i}/15")
    time.sleep(1)
log("slow_job: done.")
