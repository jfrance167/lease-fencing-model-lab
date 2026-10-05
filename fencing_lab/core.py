"""Supplied arrival-ordered numeric model; no lease, identity or real effects."""

import json

from .admission import LabError, MAX_OUTPUT, check_tree, check_report_tree, parse

PROFILE = 'fence-high-water/1'
BASIS = 'assumed_monotonic_retained_atomic'
ASSURANCE_NAMES = ('token_issuance', 'holder_binding', 'authorization',
                   'lease_validity', 'state_retention',
                   'atomic_resource_enforcement', 'mutual_exclusion')


def _keys(value, names):
    if type(value) is not dict or set(value) != set(names):
        raise LabError('invalid_input')


def _integer(value, minimum):
    if type(value) is not int or not minimum <= value <= 1000000000:
        raise LabError('invalid_input')


def _identifier(value):
    if type(value) is not str or not 1 <= len(value) <= 32:
        raise LabError('invalid_input')
    if any(char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
           for char in value):
        raise LabError('invalid_input')


def validate(value):
    """Validate all requests before evaluation, including unknown-basis traces."""
    check_tree(value)
    _keys(value, ('profile', 'model_basis', 'initial_high_water', 'requests'))
    if type(value['profile']) is not str:
        raise LabError('invalid_input')
    if value['profile'] != PROFILE:
        raise LabError('unsupported_profile')
    if type(value['model_basis']) is not str or value['model_basis'] not in (BASIS, 'unknown'):
        raise LabError('invalid_input')
    _integer(value['initial_high_water'], 0)
    if type(value['requests']) is not list:
        raise LabError('invalid_input')
    ids = set()
    for request in value['requests']:
        _keys(request, ('request_id', 'holder', 'token'))
        _identifier(request['request_id'])
        _identifier(request['holder'])
        _integer(request['token'], 1)
        if request['request_id'] in ids:
            raise LabError('invalid_input')
        ids.add(request['request_id'])


def model(value):
    """Return a detached complete report from bytes or an exact builtin tree."""
    if type(value) is bytes:
        value = parse(value)
    validate(value)
    unknown = value['model_basis'] == 'unknown'
    high_water = value['initial_high_water']
    rows = []
    accepted = rejected = equal = advanced = 0
    for index, request in enumerate(value['requests']):
        before = high_water
        token = request['token']
        if unknown:
            decision, reason = None, 'model_basis_unknown'
        elif token < high_water:
            decision, reason = 'reject_model', 'stale_token'
            rejected += 1
        elif token == high_water:
            decision, reason = 'accept_model', 'equal_token'
            accepted += 1
            equal += 1
        else:
            decision, reason = 'accept_model', 'advance_high_water'
            high_water = token
            accepted += 1
            advanced += 1
        rows.append({'index': index, 'request_id': request['request_id'],
                     'holder': request['holder'], 'token': token,
                     'high_water_before': None if unknown else before,
                     'decision': decision, 'reason': reason,
                     'high_water_after': None if unknown else high_water})
    count = len(rows)
    summary = {'request_count': count, 'modeled_requests': 0 if unknown else count,
               'unknown_requests': count if unknown else 0,
               'accepted': None if unknown else accepted,
               'rejected': None if unknown else rejected,
               'equal': None if unknown else equal,
               'advanced': None if unknown else advanced}
    assurances = {name: 'unverified' for name in ASSURANCE_NAMES}
    assurances['effects'] = 'unmodeled'
    return {'schema_version': 1, 'profile': PROFILE, 'model_basis': value['model_basis'],
            'state': 'incomplete' if unknown else 'modeled',
            'initial_high_water': value['initial_high_water'], 'assurances': assurances,
            'rows': rows, 'summary': summary,
            'final_high_water': None if unknown else high_water}


def render(report):
    """Return bounded compact ASCII JSON + LF; reject before delivering bytes."""
    check_report_tree(report)
    encoder = json.JSONEncoder(ensure_ascii=True, allow_nan=False, separators=(',', ':'))
    parts = []
    size = 1
    for chunk in encoder.iterencode(report):
        size += len(chunk)
        if size > MAX_OUTPUT:
            raise LabError('output_error')
        parts.append(chunk)
    return ''.join(parts) + '\n'
