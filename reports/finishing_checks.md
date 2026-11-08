# Finishing checks before final review

These are observed measurements, separate from the original phase reports. AI disclosure remains deferred and is not drafted here.

## Completed

- Current test plan now names eight DVC stages, all 13 collected unit tests, and primary VM-only CI. Deleted screenshot 26 is not claimed as outage evidence.
- All seven service containers were stopped/removed using Compose and recreated successfully. Post-restart smoke passed predictions, invalid input, feedback, pipeline validation and UI. DVC remained synchronized; the user drift timer was active. See `service_restart_check.json`.
- Fresh source checkout and DVC workspace/cache restore passed at source `60168ec0d2a507a206abb61102f4cbe79326293a`. Both active and candidate model digests matched; the restored active model loaded and returned the expected demonstration score. Exact commands are in `current_restore_check.json`. This reused the existing Python environment and local artifact store, not a newly installed environment.
- Two-minute paced API probe at source `60168ec0d2a507a206abb61102f4cbe79326293a`: 240 requests, 240 successful, 0 errors, duration 120.003 seconds; p50 81.77 ms, p95 102.46 ms, p99 120.87 ms. All responses matched the active model within 1e-6. Exact data: `sustained_load.json`. Two clients were paced to at most two total requests per second. This is not saturation capacity, a guaranteed SLA or a model-accuracy evaluation.

- Genuine model-service outage and recovered inspection result were inspected and saved as captures 31/32; the model was immediately restored and integration smoke passed. Capture 33 displays the actual saved local verification records.

- Full Ubuntu reboot passed: the boot ID changed, both model digests and active policy were preserved, all services restarted, live integration passed, DVC stayed synchronized, the drift timer was active, and MLflow SQLite integrity was valid. See `vm_reboot_check.json`.

## Still pending

- Instructor access, user review of the LaTeX PDF report, the actual narrated 5–10 minute demonstration video, final package/manifest and student viva rehearsal. The video script targets 7–8 minutes; it is not a completed recording.
- Fresh environment installation and standalone offline image distribution have not been demonstrated; retain that limitation unless explicitly tested.
