"""Independent field-width envelope, not a reachable production trace."""

import json


def envelope():
    """Maximize each allowed field width independently; preserve proof limits."""
    row = {'index': 127, 'request_id': 'X' * 32, 'holder': 'H' * 32,
           'token': 1000000000, 'high_water_before': 1000000000,  # nosec B105 -- public numeric width ceiling, not credential
           'decision': 'reject_model', 'reason': 'model_basis_unknown',
           'high_water_after': 1000000000}
    report = {'schema_version': 1, 'profile': 'fence-high-water/1',
              'model_basis': 'assumed_monotonic_retained_atomic', 'state': 'incomplete',
              'initial_high_water': 1000000000,
              'assurances': {key: 'unverified' for key in
                             ('token_issuance', 'holder_binding', 'authorization',
                              'lease_validity', 'state_retention',
                              'atomic_resource_enforcement', 'mutual_exclusion')},
              'rows': [dict(row) for _ in range(128)],
              'summary': {key: 128 for key in ('request_count', 'modeled_requests',
                                             'unknown_requests', 'accepted', 'rejected',
                                             'equal', 'advanced')},
              'final_high_water': 1000000000}
    report['assurances']['effects'] = 'unmodeled'
    return len(json.dumps(report, ensure_ascii=True, separators=(',', ':')).encode('ascii')) + 1


if __name__ == '__main__':
    print(json.dumps({'conservative_bytes': envelope(), 'cap': 262144,
                      'reachable': False, 'basis': 'independently maximal field widths'}))
