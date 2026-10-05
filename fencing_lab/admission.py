"""Fixed bounded input gates adapted from Jake's owned queue lab (MIT)."""

import json

MAX_BYTES = 65536
MAX_DEPTH = 8
MAX_ARRAY = 128
MAX_KEYS = 512
MAX_NODES = 4096
MAX_STRING = 128
MAX_STRING_SPELLING = 1536
MAX_NUMBER = 16
MAX_OUTPUT = 262144
CODES = frozenset({'invalid_input', 'unsupported_profile', 'limit_exceeded',
                   'input_error', 'output_error'})


class LabError(Exception):
    """Content-free closed error codes; input text never enters diagnostics."""

    def __init__(self, code):
        self.code = code if type(code) is str and code in CODES else 'invalid_input'
        super().__init__(self.code)


def lexical_gate(raw):
    if type(raw) is not bytes:
        raise LabError('invalid_input')
    if len(raw) > MAX_BYTES:
        raise LabError('limit_exceeded')
    inside = escaped = False
    depth = width = number_width = 0
    for byte in raw:
        if inside:
            if byte == 34 and not escaped:
                inside = False
                continue
            width += 1
            if width > MAX_STRING_SPELLING:
                raise LabError('limit_exceeded')
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            continue
        if byte in b'0123456789eE+-.':
            number_width += 1
            if number_width > MAX_NUMBER:
                raise LabError('limit_exceeded')
        else:
            number_width = 0
        if byte == 34:
            inside, escaped, width = True, False, 0
        elif byte in (91, 123):
            depth += 1
            if depth > MAX_DEPTH:
                raise LabError('limit_exceeded')
        elif byte in (93, 125):
            depth -= 1
            if depth < 0:
                raise LabError('invalid_input')
    if inside or depth != 0:
        raise LabError('invalid_input')


def _string(value):
    if len(value) > MAX_STRING:
        raise LabError('limit_exceeded')
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise LabError('invalid_input')


def _tree(value, key_limit):
    # Exact types are checked before comparisons, conversion or iteration.
    pending = [(value, 0)]
    seen = set()
    nodes = keys = 0
    while pending:
        node, depth = pending.pop()
        nodes += 1
        if nodes > MAX_NODES:
            raise LabError('limit_exceeded')
        kind = type(node)
        if kind is dict or kind is list:
            if id(node) in seen:
                raise LabError('invalid_input')
            seen.add(id(node))
            depth += 1
            if depth > MAX_DEPTH:
                raise LabError('limit_exceeded')
            if kind is dict:
                keys += len(node)
                if keys > key_limit:
                    raise LabError('limit_exceeded')
                for key in node:
                    if type(key) is not str:
                        raise LabError('invalid_input')
                    _string(key)
                children = list(node.values())
            else:
                if len(node) > MAX_ARRAY:
                    raise LabError('limit_exceeded')
                children = node
            pending.extend((child, depth) for child in reversed(children))
        elif kind is str:
            _string(node)
        elif kind is int:
            if node.bit_length() > 54 or len(str(node)) > MAX_NUMBER:
                raise LabError('limit_exceeded')
        elif kind is bool or node is None:
            pass
        else:
            raise LabError('invalid_input')


def check_tree(value):
    """Admit an exact builtin, bounded, nonaliased input tree."""
    _tree(value, MAX_KEYS)


def check_report_tree(value):
    """Renderer trees permit the 128 rows' keys, with fixed separate ceiling."""
    _tree(value, 2048)


def _integer(text):
    if len(text) > MAX_NUMBER:
        raise LabError('limit_exceeded')
    return int(text)


def _no_number(_text):
    raise LabError('invalid_input')


def parse(raw):
    """Bound widths/depth before JSON allocation; counts remain postallocation."""
    lexical_gate(raw)
    total_keys = 0

    def pairs(items):
        nonlocal total_keys
        total_keys += len(items)
        if total_keys > MAX_KEYS:
            raise LabError('limit_exceeded')
        result = {}
        for key, value in items:
            if key in result:
                raise LabError('invalid_input')
            result[key] = value
        return result

    failed = False
    try:
        value = json.loads(raw.decode('utf-8'), parse_int=_integer,
                           parse_float=_no_number, parse_constant=_no_number,
                           object_pairs_hook=pairs)
    except (ValueError, UnicodeError, RecursionError):
        failed = True
    if failed:
        # Raise outside the handler: don't retain JSONDecodeError's source doc.
        raise LabError('invalid_input')
    check_tree(value)
    return value
