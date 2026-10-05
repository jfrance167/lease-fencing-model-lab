# Lease-fencing research — October 5, 2026

Research-stage record: at that milestone no project application code or
candidate execution occurred. Coordinator subsequently approved PLAN stages1–4
at05:45; current implementation evidence is in STATE/VERIFICATION, separate
from these source observations. Candidate code has never been executed here.

## Reuse and discovery

Targeted workspace/vault searches for fencing tokens, stale owners, lease
expiry and generation found the owned retry plan/research note, but no dedicated
fencing lab in the searches performed. This is not an exhaustive absence claim.
Read retry-idempotency-lab/PLAN.md and vault `02 Research/Retry Idempotency
Plan.md`: atomic-model effects and replay/response semantics defer distributed
leases; they do not supply an issuer or resource enforcement. Its blocked
verification remains blocked and is not retried. Bounded-queue STATE and vault
project note were read: FIFO/waiting-slot accounting is separate from stale
generation admission. Reviewed owned MIT input/CLI patterns are potential reuse
after approval, without editing or importing the completed sibling lab.

Connected GitHub repository search `fencing token lock` succeeded, returning
ubgo/lock, FelixSeptem/mortise, pivovarit/fencepost and flintlk/lock. Search hits
were discovery leads, not verified quality findings or adopted code. The
primary-linked etcd/redis mechanisms offered stronger fit for source comparison.
Pinned public source was obtained through read-only GitHub CLI calls when
needed. Fourteen retained inert text snapshots have path/revision/length/hash
records in research/snapshot-manifest.json; the historical issue is explicitly
mutable. No untrusted source was imported, installed, built or run.

## Primary semantic sources

[Kleppmann's analysis (2016)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
describes a delayed older lease holder whose write arrives after a newer token.
Resource-side comparison against retained higher tokens prevents that numeric
regression; a random unique token alone lacks ordering. This is a selected
failure scenario and design explanation, not universal consensus or a current
vulnerability verdict. The article links a counterargument; the lab does not
settle every distributed-lock algorithm debate.

[Redis's official locking guidance](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
explicitly discusses fencing and retention of a valid lock, and cautions about
TTL clock assumptions. It supports separating expiry checks from downstream
enforcement. No Redis algorithm safety/insecurity verdict follows from this
bounded research; no Redis installation, cluster or failure experiment ran.

[etcd v3.6 concurrency API](https://etcd.io/docs/v3.6/dev-guide/api_concurrency_reference_v3/)
describes a returned ownership key guarding etcd transactions and lease-related
key lifetime, with repeated acquisition under the same lease treated specially.
That guards operations participating in the etcd comparison; it does not
automatically enforce fencing in an external resource. Released v3.6 docs and
the pinned current main source below are distinct revisions.

All three pages were opened/read during the retained research session; sources
are evidence. Firecrawl was not used because optional current free eligibility
was not established. No new fetch/inference was required for recovery.

## Actual candidate inspection

### etcd-io/etcd

Pinned main revision `91703b3d47f3208f9095f77f765c27cc1510ce9a`.
Observed nonarchived, default main, pushed October 4, 2026 at 13:23:33Z;
that pinned commit date matches. Recent activity is maintenance evidence, not
proof of safety, reviewed releases or availability.

Read [mutex.go](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/client/v3/concurrency/mutex.go):
transaction creates a lease-attached key or reuses an existing session key;
oldest creation revision determines ownership. Lock waits for predecessor
deletion then rechecks its key; IsOwner constructs a creation-revision compare.
Read [session.go](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/client/v3/concurrency/session.go):
grant/keepalive and a goroutine establish real service-dependent lifetimes.
These mechanisms do not supply an offline external-resource transition.

Read actual [example tests](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/client/v3/concurrency/example_mutex_test.go)
and [integration waiter test](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/tests/integration/v3lock_grpc_test.go).
The latter creates a one-node cluster, grants two leases and verifies increasing
revisions after unlock/waiter progress with timing controls. Tests were read,
not executed; they are not proof of this proposed model or external fencing.

Actual [go.mod](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/client/v3/go.mod)
requires Go 1.27/toolchain 1.27.1 and monorepo API/client replacements alongside
grpc/protobuf/zap/prometheus and other direct/transitive modules. This is main,
not a claimed released v3.6 dependency contract. None is necessary for a pure
numeric Python trace; no installation/artifact/advisory audit was performed.

Read actual [Apache-2.0 LICENSE](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/LICENSE),
including redistribution terms: source adoption would require license/notices,
modified-file notices and applicable NOTICE treatment. No source copying or
derivative distribution proposed; reference links retained.
Read actual [CodeQL workflow](https://github.com/etcd-io/etcd/blob/91703b3d47f3208f9095f77f765c27cc1510ce9a/.github/workflows/codeql-analysis.yml):
push/PR/schedule and immutable action refs are present. Its top read-all and
job permission/checkout choices are not copied into this lab. Hosted results,
all test CI, protections and security alerts were not assessed.

### redis/redis-py

Pinned master revision `cdf81483ce0645e67b4033fe4313ba467737dcbf`.
Observed nonarchived, default master, pushed October 5, 2026 at 07:00:22Z;
pinned commit dated October 4, 06:46:15Z. Branch activity differs from pinned
commit date; neither establishes security quality.

Read actual [redis/lock.py](https://github.com/redis/redis-py/blob/cdf81483ce0645e67b4033fe4313ba467737dcbf/redis/lock.py):
default UUID1-based bytes token, SET NX PX acquisition, clock/sleep waiting and
Lua compare-token release/extend/reacquire protect operations on a lock key.
That unique token is not a monotonic generation fence at an external resource.
Release preserves local token until successful remote release and clears only
the expected token. No service behavior or failure isolation tested here.

Read selected actual [tests/test_lock.py](https://github.com/redis/redis-py/blob/cdf81483ce0645e67b4033fe4313ba467737dcbf/tests/test_lock.py):
competing acquisition/release, TTL/PTTL, mismatched token rejection and
connection-error token preservation have tests. Selected tests were read, not
run; the entire async implementation was not reviewed.

Read actual [pyproject](https://github.com/redis/redis-py/blob/cdf81483ce0645e67b4033fe4313ba467737dcbf/pyproject.toml):
Python>=3.10, Hatchling build, conditional async-timeout dependency below Python
3.11.3, optional hiredis/xxhash/crypto/requests/JWT/pybreaker/telemetry extras.
No redis dependency is proposed; no wheel/transitive artifact/advisory audit.
Actual [MIT LICENSE](https://github.com/redis/redis-py/blob/cdf81483ce0645e67b4033fe4313ba467737dcbf/LICENSE)
requires retention of copyright/permission for copied substantial portions;
none copied. README support/source and selected actual
[integration CI](https://github.com/redis/redis-py/blob/cdf81483ce0645e67b4033fe4313ba467737dcbf/.github/workflows/integration.yaml)
were inspected: Docker/Redis/parser/event-loop/Python matrices and audit jobs
exist; some action refs are mutable and audit exclusions explicit. Exclusions
were not copied or independently validated as false positives; no current
vulnerability finding or passed hosted run is inferred. Composite actions/all
workflow bodies were not exhaustively audited.

Actual [issue 3847](https://github.com/redis/redis-py/issues/3847) was read and
retained as a mutable snapshot: a closed historical report (created November
16, 2025, updated January 9, 2026) describes cancellation during asynchronous
release after premature local token clearing. It illustrates the difference
between local state and a remote operation, not a reproduced current defect.
The proposed lab excludes async/service/cancellation execution entirely.

## Fit, security and licensing conclusion

Build the original resource high-water trace; do not adopt or fork either
network client. Standard library meets the specified bounded offline behavior;
this recommendation follows fit/inspectability, not an assertion that fewer
dependencies always imply safety. Original future code will use MIT; owned
gate reuse requires attribution, upstream research citations do not imply
borrowed code. No Scorecard, complete advisory audit, upstream test execution,
all issues/CI, hosted protections or hostile-runtime tests were performed.

One local Ollama prose request completed in 5,510 ms, 99 output tokens. Raw
draft is preserved separately; it incorrectly called the seed an array,
claimed issuer checks and inferred null decisions from lack of infrastructure.
Corrected facts: seed scalar, array arrival order, issuer assumptions unverified,
unknown basis causes nulls after full validation; an assumed offline basis
allows numeric model decisions without real infrastructure. No remote worker,
paid fallback, downloaded model or Laya invocation. Contract/security reasoning
stays with Codex. See .drafts/comparison-reviewed.md and DECISIONS.md.

At the research milestone, the next gate was coordinator PLAN review before
application code/oracles/scripts/tests. That gate subsequently passed at05:45.
The research integrity check remains snapshot evidence, not implementation or
distributed-safety verification; current owned-model checks are recorded separately.
