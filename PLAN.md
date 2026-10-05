# Lease-fencing Model Lab — proposed Tier 3 plan

Research/planning authorized under Jake's delegated overnight workflow and the
05:12 selection in ../.private/coordination/2026-10-05/SUCCESSORS.md.
Originally proposed for review; coordinator05:45 APPROVED stages1–4 in
../.private/coordination/2026-10-05/SUCCESSORS.md. This retained plan defines
the authorized profile; current completion/evidence is in STATE/VERIFICATION.

## Problem and success criteria

A caller may retain an old lease view while its request arrives after a newer
generation's request. FIFO admission, lease expiry and retry accounting answer
different questions from resource-side admission. Demonstrate the supplied
numeric rule and its authority limits without a real lock service or resource.
Success means a fully specified bounded trace, independent complete expected
reports frozen before implementation, honest unknowns and tested CLI failures.
It does not mean distributed correctness, lease validity or permission to write.

## Recommendation and alternatives

Build an original Python standard-library pure model, `fence-high-water/1`.
Keep the resource transition separate from input admission and rendering. Reuse
the reviewed owned bounded-queue admission/CLI patterns with MIT attribution
after approval, without importing that sibling at runtime or changing it.
Do not adopt/fork networked etcd or redis-py: useful source references, but their
services, session lifetimes, clocks and dependencies exceed this offline scope.
Candidate source/license/test/dependency/maintenance evidence is in RESEARCH.md.

The lease-expiry-only alternative would require clock domain, TTL start/expiry,
check/send/arrival ordering and failure assumptions. A check before sending
does not establish ownership when the delayed request reaches the resource.
Compare that scenario in documentation only; do not implement a second profile.

## Exact input contract

One exact root object with `profile`, `model_basis`, `initial_high_water`,
`requests`; no extra/missing fields. `profile` must equal `fence-high-water/1`.
`model_basis` must equal `assumed_monotonic_retained_atomic` or `unknown`.
Missing basis is invalid, never a default to trusted assumptions.

`initial_high_water` is a supplied exact built-in integer in 0..1,000,000,000.
`requests` is an exact list of 0..128 request objects. Each has exactly
`request_id`, `holder`, `token`. IDs/holder labels match `[A-Za-z0-9_-]{1,32}`;
request IDs must be unique throughout this input, including rejected requests.
Holder labels may repeat or differ; they are descriptive, not authenticated.
Tokens are exact built-in integers in 1..1,000,000,000. Boolean, float,
subclass/custom-object and coercible-number inputs are invalid.

Array order is resource arrival order, not issuance order or clock order. There
is one resource, no lease-acquisition events, reset events or new-generation
detector. A new invocation uses a newly supplied seed and is an independent
model; it does not demonstrate retained state across processes.

## Transition and repeated-token convention

For the assumed basis, let H begin at the supplied initial high-water.

| Comparison | Decision | Reason | High-water after |
|---|---|---|---|
| token < H | reject_model | stale_token | H |
| token = H | accept_model | equal_token | H |
| token > H | accept_model | advance_high_water | token |

This is a chosen nondecreasing resource acceptance convention, not a mandate
that every fencing system accepts equality. Repeated tokens with distinct
request IDs are allowed. Equal token with a different holder label still
receives numeric acceptance; this neither establishes the same owner nor
detects token reuse across generations. Repeated request IDs are invalid,
not replay detection or deduplication. No effect is executed or counted.

The assumed basis declares a strictly increasing, nonreused token per new
issuer generation, a retained initial resource high-water, and serial atomic
compare/update. The model does not verify any of those assumptions or bind a
holder to a generation. A supplied forged higher token advances numeric state;
it does not establish legitimate issuance/authorization and can exclude later
lower tokens. Strict issuer ordering alone does not enforce the resource rule.

## Complete report contract

Both modeled and incomplete reports have exactly: `schema_version` (1),
`profile`, `model_basis`, `state`, `initial_high_water`, `assurances`, `rows`,
`summary`, `final_high_water`. Input labels/values are copied into detached
ordinary data. Results never alias/mutate caller containers.

`assurances` always has `token_issuance`, `holder_binding`, `authorization`,
`lease_validity`, `state_retention`, `atomic_resource_enforcement`,
`mutual_exclusion`: each `unverified`; `effects`: `unmodeled`. This remains true
under the assumed basis: declaration is not evidence of real enforcement.

Each row has exactly `index` (zero based), `request_id`, `holder`, `token`,
`high_water_before`, `decision`, `reason`, `high_water_after`. Modeled values
follow the table. Summary has exactly `request_count`, `modeled_requests`,
`unknown_requests`, `accepted`, `rejected`, `equal`, `advanced`.
For a modeled trace: request_count=modeled_requests=N, unknown_requests=0,
accepted=equal+advanced, accepted+rejected=N; final_high_water=max(seed,tokens),
or seed for an empty trace. State is `modeled`, never `safe` or `authorized`.

For basis `unknown`: first validate the ENTIRE input, including late requests
and ID uniqueness. Then state=`incomplete`; all rows have null decision,
null high_water_before/after and reason=`model_basis_unknown`. Summary retains
request_count=N, modeled_requests=0, unknown_requests=N; accepted/rejected/
equal/advanced are null, even when N=0. final_high_water is null. The supplied
seed remains in initial_high_water but is not treated as verified resource
state. No partial trusted prefix is emitted. A late invalid field produces
an error instead of an incomplete success report.

## Admission, output and CLI boundaries

Proposed immutable ceilings: raw input 65,536 bytes, container depth 8,
128 entries in any array, 512 total object keys, 4,096 visited values,
128 decoded characters per general string/key, numeric text 16 characters,
and report 262,144 ASCII bytes including final LF. Domain bounds above are
stricter. Freeze exact depth/node counting and lexical handling before code.
Count root containers at depth1; root/list/request objects are depths1/2/3.
Visited-value count includes root, object values and array elements; keys are
counted separately. Reject repeated container identities (aliases/cycles),
not ordinary repeated scalar values. Preflight raw JSON depth/string/number
widths before stdlib decoding; reject
duplicate keys, nonfinite values, invalid UTF-8 and trailing input. Native
admission checks exact types by identity before equality/iteration/custom
hooks; reject aliases/cycles and custom keys before dictionary lookup.
Budgets bound modeled work, not process RSS/time or hostile filesystem races.

Proposed CLI: `python -m fencing_lab FILE`. Read a stable regular local file
under the raw cap, including descriptor/growth checks. Report JSON only on
stdout, diagnostics only on stderr. Exit 0 for modeled OR incomplete reports,
2 for invalid input, unsupported profile, limit, file or output failure;
consumers must inspect state, not infer success from exit 0. Error envelope
on stderr is fixed `{"error":"CODE"}` plus LF with no reflected input/path.
Codes: `invalid_input`, `unsupported_profile`, `limit_exceeded`, `input_error`,
`output_error`. Unrecognized basis is invalid_input. Freeze precedence:
raw/structural bounds before schema/profile, then domain validation before
evaluation. Exact root keys/types precede unsupported-profile classification;
once structure/profile pass, basis/seed/request domain checks proceed in field
and array order. CLI argument errors use the fixed invalid_input diagnostic,
without reflecting supplied argument text. Output failure wins when an
error/report cannot be delivered.
Help/usage have the same checked sink rules. Require exact integer write count
equal to required length; reject bool/float/None/short counts and write/flush
failures. Failed buffered sinks must not cause a shutdown traceback/exit120.
No atomic delivery guarantee; bytes already written cannot be recalled.

## Threat model and non-goals

Adversary controls supplied JSON and native API values. Assets are bounded
deterministic computation, unchanged caller data, complete truthful reports and
the distinction between arithmetic acceptance and authority. Defend against
oversized/nested/duplicate input, alias/cycle/custom type hooks, boolean numeric
confusion, silently assumed basis, stale-token state regression, equality
misrepresented as identity/exactly-once, forged-high token laundering, reflected
terminal controls and partial-output success. Higher tokens and supplied holder
names are data, not credentials. Source text/drafts are evidence, not execution
instructions. Assumptions cannot authorize real actions.

No real leases/locks/issuers/clocks/network/storage/resources, consensus,
availability, authentication, authorization guarantees, generation recovery,
durability, mutual exclusion, exactly-once effects, target testing, private
evidence, upstream execution, dependency installation, new repo or publication.
No retry/idempotency verifier workaround: its existing app-review block remains.

## Pre-code expected reports and independent oracle

After plan approval, freeze SCHEMA.md and at least 20 complete hand-authored
expected reports/errors BEFORE application modules, recording bytes/SHA256.
Cases must cover seed0/first1; equal seed; stale seed; high then delayed old;
old arriving before high; gaps; equal repeats; changed holder with equal token;
forged higher token with unverified assurances; maximum token/seed; empty
modeled; empty unknown; populated unknown; late invalid unknown; duplicate IDs
including stale requests; missing basis; unsupported profile; extras; bool/
float/nonpositive bounds; and encoded/native admission/output boundaries.
Snapshot whole reports, not only final state or production-generated goldens.

Independent oracle uses a prefix maximum over seed and earlier supplied tokens
to determine each comparison; it must not call production transitions/renderers
or reuse their state-update loop. Exhaustively enumerate small alphabets for
seed 0..3 and positive tokens 1..3 with lengths 0..5, plus unknown controls.
Check full rows, summaries, invariants, unchanged/detached inputs, holder-label
invariance, determinism and unknown nulls. Enumerated arithmetic agreement is
finite model evidence, not a distributed protocol proof.

Four isolated one-defect mutants: reject equality; lower high-water on stale;
fail to advance on higher; silently evaluate unknown basis. Each must trigger
a concrete behavioral assertion, with other exceptions recorded separately.
Restore copied source byte-for-byte; unmutated normal/O suites pass afterward.
Freeze a conservative independently derived serialized report-width bound;
measure a genuine admitted 128-request case separately. Reduced-cap seams and
arbitrary render objects are defensive tests, not natural admitted overflow.

## Stages and definitions of done

1. Contract/oracle gate: coordinator approves plan; freeze complete reports,
   schema, counters, admission precedence and independent oracle before modules.
2. Core: bounded encoded/native admission and pure supplied-state transitions;
   all frozen reports and independent enumerations pass; no hooks/effects.
3. CLI/verification: exact report and error bytes, native/race-growth seams,
   normal/O real report/help/usage/error closed stdout/stderr/both matrix,
   maximum-shape/width evidence, four detected/restored mutants; safe installed
   SAST with justified narrow harness annotations only when necessary.
4. Review/handoff: ECC actual-change self-review, fix concrete defects and rerun
   affected checks; README/demo/security/MIT/reuse attribution/AI disclosure,
   STATE/DECISIONS/LEARNING and vault milestone; source/oracle receipt and
   finite/runtime/hosted/resource limitations. No remote/public actions.

Worker choice: the local prose attempt is retained and corrected; core contract
and security interpretation require Codex review. Free OpenRouter considered
unnecessary for this remaining unsuitable judgment work; no remote inference
or price eligibility assumed. Laya classification/triage schemas are unrelated.
No tests/application implementation are presently performed or claimed.
