#!/bin/bash
LOGDIR="$1"
JOB_NAME="$2"
LOGFILE="${LOGDIR}/$(date '+%Y%m%d').log"
START=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOGDIR"

echo "▶ [$START] START: $JOB_NAME" >> "$LOGFILE"

while IFS= read -r line; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line" >> "$LOGFILE"
done

END=$(date '+%Y-%m-%d %H:%M:%S')
EXIT_CODE="${PIPESTATUS[0]}"

echo "■ [$END] END: $JOB_NAME | EXIT:$EXIT_CODE" >> "$LOGFILE"
