# Learning from research

A lock issuer and a downstream resource enforce different contracts. A unique
lock-key token helps compare ownership of that key; it does not supply ordered
generation admission at a different resource. A numeric high-water check also
does not authenticate a higher token or detect same-number generation reuse.

Checking lease validity before sending leaves a pause/delay interval before
resource arrival. This lab chooses array arrival order and avoids inventing a
clock/expiry model. Repeated token acceptance is an explicit convention, not
proof of exactly-once effects or persistent ownership.

Unknown assumptions should not become trusted transitions. Entire-input
validation must precede incomplete reports so late malformed data cannot hide
behind an unknown prefix. Independent prefix maxima make a useful small oracle;
finite agreement remains model evidence, not a distributed protocol proof.

The local draft confused assumptions with verified issuance. Keeping raw and
reviewed versions separate preserves that mistake and its correction.

Implementation lesson: logical text endings are not proof of physical CLI bytes.
Windows stream translation caused initial LF-versus-CRLF failures; configure
delivery and assert actual subprocess bytes. The independent oracle/complete
goldens detected behavior without deriving expectations from production.

Report-width evidence separates a genuine128-request shape (30,552bytes) from
an impossible combination of independently longest fields (31,695bytes). The
latter is an upper-width argument, not a natural overflow or RSS/time proof.
Four single-defect mutants were assertion-detected without extra errors; finite
test agreement still cannot authenticate an issuer or prove real atomicity.
