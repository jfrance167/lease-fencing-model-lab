# Security model

This synthetic model accepts untrusted bytes/native values. It does not acquire
leases, issue tokens, authenticate holders or execute resource operations.
Adversary-controlled higher/equal tokens are arithmetic data. No output decision
authorizes a real action; all real assurances remain unverified.

Trust boundaries: raw width/depth/byte preflight; exact native tree admission;
full schema and unique-ID validation; pure scalar high-water comparisons;
detached renderer tree; regular file read and checked output. Unknown basis is
validated completely before null results. Custom object/type/key hooks and
container aliases/cycles are rejected by identity-first checks. Duplicate JSON
keys, surrogates, floats/nonfinite values and trailing data are invalid.

Fixed caps bound modeled work, not allocations made by native callers, hard RSS,
CPU duration, process isolation, simultaneous mutation or hostile filesystems.
JSON array/key counts are postallocation. File descriptors are checked, but
open/read races can still block or substitute evidence. Use stable local files.
Reports/errors escape or omit supplied text; no credential/path is reflected.
Best-effort diagnostics can be lost if stderr fails; delivered bytes are not
transactional. Exit0 includes incomplete, so inspect state/assurances.

No live testing, consensus/durability/mutual exclusion proof, clock simulation,
retry verifier execution, hostile samples, private data, dependency downloads,
network service, repository publication or hosted assurance is included.
Manual review is required before considering hostile evidence use. Finite tests,
static scanning and an implementing-agent review do not prove absence of bugs.

For a suspected defect, retain a minimal inert synthetic input, interpreter/OS,
expected contract and bounded observed outcome in local project records. Keep
credentials/private targets out of portfolio fixtures and external reports.
