# Local verification — October5,2026

Windows/Python3.13.7/Bandit1.9.4. Approved stages1–4 under coordinator05:45
record in ../.private/coordination/2026-10-05/SUCCESSORS.md. No new repository.

| Check | Actual result/evidence |
|---|---|
| Pre-code contract/oracle freeze | SCHEMA/cases/support bytes and SHA256 in research/contract-freeze.json;20 full reports/8 errors, before application modules |
| Retained upstream snapshots | All14 lengths/hashes matched research manifest; one mutable historical issue |
| Normal/optimized/restored tests | 27 each, exit0; docs/verification/final/normal.log, optimized.log, restored.log |
| Independent complete arithmetic traces | 1,456 prefix-max traces; no production oracle calls |
| CLI |28 hand records +12 closed stdout/stderr/both combinations +2 fixed-error checks =42 children per normal/O suite; new harness propagates -O |
| Four isolated mutants |16/17/19/11 assertion failures,0 other errors; copies restored/originals unchanged; final/*/mutant.log |
| Bandit application/scripts |0 findings/errors,4 narrow harness annotations; final/bandit.stdout/stderr |
| Unsuppressed control |Exactly B404/B603 and two synthetic numeric B105;0 application findings/errors; bandit-control.json |
| Genuine128-request stress |14,591 input bytes;30,552 report bytes; final/max-input.json and max-report.json |
| Independent width envelope |31,695 bytes, unreachable combined maxima; scripts/report_bound.py; cap262,144 |
| Source/oracle receipt |final/results.json; source lengths/SHA256 and unchanged three frozen oracle records |

Initial verification results/logs are preserved under docs/verification/initial:
all tests passed, but Bandit caught two numeric-token false positives. They were
reviewed and annotated; final scan passed. Initial development's two Windows
newline failures were corrected in production delivery, without changing frozen
expectations. Complete deterministic data is synthetic; no hostile payloads,
Ruby/pickle restoration, upstream source/service execution or blocked retry
verifier was performed. Reports do not certify legitimate issuance or safety.

Reusable verifier: `python scripts/verify.py --output FRESH_DIRECTORY` performs
fixed local commands, complete logs, hash checks, isolated assertion mutants,
restoration and stress/width measurements; it requires installed Bandit and
never installs or sends network requests. Use a fresh output path. Raw separate
stdout/stderr files avoid treating combined scanner logging as pure JSON.

Source review is recorded in REVIEW.md. AST/hygiene/current-receipt checks are
recorded in docs/verification/closeout.json after documentation. Hygiene is a
limited credential-pattern check, not a comprehensive secret-scanner guarantee.
No project history exists; parent/unrelated repositories were not scanned/edited.

NOT RUN: other Python versions/OS, real leases/services/issuer/resource storage,
distributed failure injection, exhaustive fuzzing, process RSS/time containment,
hosted CI/CodeQL/protections/security eligibility, external advisory/secret audit,
configured types/lint (no such project checks). Manual hostile-input review
remains; no new dependency install/publication/merge/deployment or spending.
