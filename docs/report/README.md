# LaTeX project report

The PDF is a review copy of the implemented Smart Maintenance Monitor, with measured results and clearly stated boundaries. The editable source is `smart_maintenance_report.tex`; original evidence images used by the report are in `figures/`.

Build from this folder using a standard LaTeX installation with TikZ, listings, hyperref, booktabs, tabularx, lmodern and microtype:

```sh
latexmk -pdf smart_maintenance_report.tex
```

Alternatively, use `tectonic smart_maintenance_report.tex`. The supplied PDF was compiled using Tectonic 0.17.0 on the Mac. The first build downloads TeX resources; a full TeX installation can compile locally without those first-run downloads. This report build is separate from the Ubuntu ML application environment.

Read `reports/submission_acceptance.md`, `reports/finishing_checks.md` and their linked JSON/log records in the main project for exact verification identities. The document describes the verified implementation rather than all features of the initial blueprint. The actual narrated demonstration video and final submission access remain separate handoff tasks.
