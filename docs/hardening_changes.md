# Submission corrections and observed limits

The submission-hardening branch adds the local workflow recommended after course review. It does not implement the entire original blueprint.

Implemented: source hash validation as a dependency gate; eight-stage DVC lifecycle; clean-source candidate provenance; versioned parameters and declared environment snapshot; validation-only evaluation/importance and candidate packaging; VM-only CI with actual counts/logs; critical Python lint/format checks; isolated test observation files; locked-test repeat guard; direct model/API parity and short load probe; controlled storage/feedback errors; real artifact/metric review; guarded release switching with automatic recovery; packaged API module; full pipeline summaries/tool links; user Help; broader monitoring and scheduled drift freshness; HLD diagram, actual OpenAPI export and manual corrections.

Verification includes a genuine successful promotion/rollback plus a deliberately injected post-start failure with automatic restoration. These are separate from unit mocks and history assertions. The candidate matches the champion's validation result; no improvement or new locked-test result is claimed.

During implementation, test discovery initially imported its own runner. A proper main guard fixed collection; later counts come from the corrected runner. The first full local CI attempt also found new DVC outputs missing from the backup remote; the workflow now pushes immutable objects to the configured local remote before its integration sync check. Both issues were detected by checks, fixed and rerun. Historical screenshot 26 was mislabelled and is excluded from browser outage proof.

Still limited: fresh environment installation, full offline image distribution, zero-downtime releases, production authentication/TLS, fresh industrial labels, an exhaustive browser/load/security suite, and full blueprint extras. The existing environment's declared versions are verified; this is not the same as claiming a freshly rebuilt environment. The requirements matrix and scope decisions retain these distinctions. AI disclosure remains deferred.
