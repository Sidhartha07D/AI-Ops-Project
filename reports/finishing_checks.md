# Finishing checks before final review

These are observed measurements, separate from the original phase reports. AI disclosure remains deferred and is not drafted here.

## Completed

- Current test plan now names eight DVC stages, all 13 collected unit tests, and primary VM-only CI. Deleted screenshot 26 is not claimed as outage evidence.
- All seven service containers were stopped/removed using Compose and recreated successfully. Post-restart smoke passed predictions, invalid input, feedback, pipeline validation and UI. DVC remained synchronized; the user drift timer was active. See `service_restart_check.json`.
- Fresh source checkout and DVC workspace/cache restore passed at source `60168ec0d2a507a206abb61102f4cbe79326293a`. Both active and candidate model digests matched; the restored active model loaded and returned the expected demonstration score. Exact commands are in `current_restore_check.json`. This reused the existing Python environment and local artifact store, not a newly installed environment.
- Two-minute paced API probe at source `60168ec0d2a507a206abb61102f4cbe79326293a`: 240 requests, 240 successful, 0 errors, duration 120.003 seconds; p50 81.77 ms, p95 102.46 ms, p99 120.87 ms. All responses matched the active model within 1e-6. Exact data: `sustained_load.json`. Two clients were paced to at most two total requests per second. This is not saturation capacity, a guaranteed SLA or a model-accuracy evaluation.

## Still pending

- Genuine model-outage/recovery browser captures and concise local-check screenshot. Ubuntu is locked/display inactive; no new browser screenshot has been claimed.
- Actual full VM shutdown/start check. The completed service restart must not be described as an operating-system reboot.
- Instructor access and final submission format, then final package/manifest and student viva rehearsal.
- Fresh environment installation and standalone offline image distribution have not been demonstrated; retain that limitation unless explicitly tested.
