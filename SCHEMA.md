# Frozen fence-high-water/1 contract

PLAN.md exact input/report fields, transitions, assurances, nulls, numeric bounds
and CLI/error contract are authoritative; this pre-code file freezes them.
Profile fence-high-water/1; basis assumed_monotonic_retained_atomic or unknown.
Seed 0..1e9; token 1..1e9; request_id and holder ASCII [A-Za-z0-9_-]{1,32};
unique request IDs across all128-or-fewer requests; exact keys/types.
Equality numeric acceptance never identity; unknown validates all input first.

Raw65536 bytes; root container depth1, max8; array max128; total keys512;
visited values4096 excluding keys; decoded strings/keys max128 characters;
encoded string body max1536 bytes (128 supplementary Unicode escape pairs);
number spelling max16 characters. Surrogates/nonfinite/floats invalid. These
string budgets differ from the owned queue gate and are explicitly adapted.
Decoded keys/arrays/value counts are post-json-allocation checks; raw cap and
lexical width/depth gates precede decoding, not a hard RSS/time guarantee.
Native repeated container identity (alias/cycle) invalid; repeated scalars fine.

Precedence: structural/raw limits and primitive admission first, exact root keys
then profile (unsupported_profile), basis/seed/requests schema in fixed field
and array order; full schema before model. Duplicate keys invalid_input.
Over-wide numeric text limit_exceeded; forbidden numeric syntax invalid_input.
Invalid UTF8/trailing JSON invalid_input; raw type must be exact bytes.
Native ints >54 bits rejected limit_exceeded before str conversion, and spelling
>16 limit_exceeded; domain ints outside seed/token bounds invalid_input.

Report serialized compact ASCII JSON plus LF, maximum262144bytes. Keys exactly
as PLAN; row decisions accept_model/reject_model or null. Unknown row reason
model_basis_unknown and inferred states/counts/final null, even empty requests.
No report fields introduce positive real-system assurances.
Errors stderr compact {"error":"CODE"} plus LF, content-free. Codes
invalid_input/unsupported_profile/limit_exceeded/input_error/output_error.
Exit0 modeled/incomplete; exit2 error/output failure. Standard argparse help
ASCII is allowed; all invalid arguments yield fixed invalid_input. Exact int
write count, flush and shutdown checks apply to help/usage/errors/reports.

Before core: tests/cases.json and tests/support.py frozen with this file in
research/contract-freeze.json. Future correction must preserve old evidence,
explain a concrete oracle defect and never silently regenerate from production.
