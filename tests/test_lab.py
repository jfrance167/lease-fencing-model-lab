"""Frozen full reports, independent arithmetic and untrusted-input boundaries."""

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fencing_lab import LabError, model, render
from fencing_lab.admission import check_tree, lexical_gate, parse, MAX_BYTES
from fencing_lab.__main__ import emit, main, read_input
from tests.support import finite_traces

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'tests/cases.json').read_text(encoding='utf-8'))


def supplied(seed=0, tokens=(), basis='assumed_monotonic_retained_atomic'):
    return {'profile': 'fence-high-water/1', 'model_basis': basis,
            'initial_high_water': seed,
            'requests': [{'request_id': f'r{i}', 'holder': 'holder', 'token': t}
                         for i, t in enumerate(tokens)]}


def encoded(value):
    return json.dumps(value, separators=(',', ':')).encode('utf-8')


class CoreTests(unittest.TestCase):
    def test_frozen_complete_reports_and_errors(self):
        for case in CASES:
            for value in (case['input'], encoded(case['input'])):
                with self.subTest(case=case['name'], bytes=type(value) is bytes):
                    if 'expected' in case:
                        self.assertEqual(model(value), case['expected'])
                        self.assertEqual(json.loads(render(model(value))), case['expected'])
                    else:
                        with self.assertRaises(LabError) as caught:
                            model(value)
                        self.assertEqual({'error': caught.exception.code}, case['expected_error'])

    def test_independent_prefix_max_complete_traces(self):
        total = 0
        for seed, tokens, comparisons in finite_traces():
            value = supplied(seed, tokens)
            relations = [relation for _, relation, _ in comparisons]
            rows = [{'index': i, **value['requests'][i], 'high_water_before': before,
                     'decision': 'reject_model' if relation < 0 else 'accept_model',
                     'reason': {-1: 'stale_token', 0: 'equal_token', 1: 'advance_high_water'}[relation],
                     'high_water_after': after}
                    for i, (before, relation, after) in enumerate(comparisons)]
            expected = {'schema_version': 1, 'profile': 'fence-high-water/1',
                        'model_basis': value['model_basis'], 'state': 'modeled',
                        'initial_high_water': seed,
                        'assurances': CASES[0]['expected']['assurances'], 'rows': rows,
                        'summary': {'request_count': len(tokens), 'modeled_requests': len(tokens),
                                    'unknown_requests': 0, 'accepted': sum(r >= 0 for r in relations),
                                    'rejected': relations.count(-1), 'equal': relations.count(0),
                                    'advanced': relations.count(1)},
                        'final_high_water': max([seed, *tokens])}
            self.assertEqual(model(value), expected)
            total += 1
        self.assertEqual(total, 1456)

    def test_unknown_states_even_empty(self):
        for tokens in ([], [1], [4, 2, 4]):
            report = model(supplied(3, tokens, 'unknown'))
            self.assertEqual(report['state'], 'incomplete')
            self.assertIsNone(report['final_high_water'])
            for field in ('accepted', 'rejected', 'equal', 'advanced'):
                self.assertIsNone(report['summary'][field])
            for row in report['rows']:
                for field in ('decision', 'high_water_before', 'high_water_after'):
                    self.assertIsNone(row[field])

    def test_holder_invariance_and_numeric_authority_limits(self):
        value = supplied(8, [8, 99, 8])
        before = model(value)
        for row in value['requests']:
            row['holder'] = 'different'
        after = model(value)
        for report in (before, after):
            for row in report['rows']:
                del row['holder']
        self.assertEqual(before, after)
        self.assertEqual(after['assurances']['authorization'], 'unverified')
        self.assertEqual(after['assurances']['effects'], 'unmodeled')

    def test_inputs_unchanged_results_detached_and_deterministic(self):
        value = supplied(2, [3, 2, 3])
        original = copy.deepcopy(value)
        one = model(value)
        self.assertEqual(value, original)
        self.assertEqual(one, model(value))
        one['rows'][0]['token'] = 100
        one['assurances']['authorization'] = 'changed'
        self.assertEqual(value, original)
        self.assertEqual(model(value)['rows'][0]['token'], 3)

    def test_whole_unknown_schema_validated(self):
        value = supplied(0, [1, 2], 'unknown')
        value['requests'][-1]['extra'] = []
        with self.assertRaises(LabError):
            model(value)

    def test_max_shape_reachable(self):
        value = supplied(1000000000, [1000000000] * 128)
        for i, row in enumerate(value['requests']):
            row['request_id'] = f'{i:032d}'
            row['holder'] = 'H' * 32
        report = model(value)
        self.assertEqual(report['summary']['equal'], 128)
        self.assertEqual(report['final_high_water'], 1000000000)
        self.assertLess(len(render(report)), 262144)

    def test_original_contract_hashes(self):
        freeze = json.loads((ROOT / 'research/contract-freeze.json').read_text())
        for row in freeze['files']:
            data = (ROOT / row['path']).read_bytes()
            self.assertEqual(len(data), row['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(), row['sha256'])


class AdmissionTests(unittest.TestCase):
    def test_duplicate_keys_and_bad_json(self):
        for raw in (b'{"x":1,"x":2}', b'{}{}', b'"unterminated', b'\xff',
                    b'[}', b'NaN', b'Infinity', b'1.0', b'1e2'):
            with self.subTest(raw=raw), self.assertRaises(LabError):
                parse(raw)

    def test_bounded_number_conversion_before_large_integer(self):
        for raw in (b'1' * 17, b'1e' + b'9' * 17):
            with self.assertRaises(LabError) as caught:
                parse(raw)
            self.assertEqual(caught.exception.code, 'limit_exceeded')
        with self.assertRaises(LabError):
            model(supplied(0, [10 ** 10000]))

    def test_depth_encoded_and_native_boundary(self):
        for count in (8, 9):
            raw = b'[' * count + b'0' + b']' * count
            tree = 0
            for _ in range(count):
                tree = [tree]
            if count == 8:
                self.assertEqual(parse(raw), tree)
                check_tree(tree)
            else:
                with self.assertRaises(LabError):
                    parse(raw)
                with self.assertRaises(LabError):
                    check_tree(tree)

    def test_string_decoded_and_lexical_budgets(self):
        self.assertEqual(parse(encoded('\U0001f600' * 128)), '\U0001f600' * 128)
        for value in ('x' * 129, '\U0001f600' * 129):
            with self.assertRaises(LabError):
                parse(encoded(value))
        with self.assertRaises(LabError):
            parse(b'"\\ud800"')
        with self.assertRaises(LabError):
            check_tree('\ud800')

    def test_array_and_total_key_caps(self):
        check_tree([0] * 128)
        with self.assertRaises(LabError):
            check_tree([0] * 129)
        check_tree({str(i): 0 for i in range(512)})
        with self.assertRaises(LabError):
            check_tree({str(i): 0 for i in range(513)})

    def test_raw_cap_and_node_budget(self):
        raw = encoded(supplied())
        self.assertEqual(model(raw + b' ' * (MAX_BYTES - len(raw)))['state'], 'modeled')
        with self.assertRaises(LabError):
            parse(raw + b' ' * (MAX_BYTES + 1 - len(raw)))
        with self.assertRaises(LabError):
            check_tree([[0] * 128 for _ in range(33)])

    def test_native_alias_and_cycle_rejection(self):
        shared = {'request_id': 'x', 'holder': 'a', 'token': 1}
        value = supplied()
        value['requests'] = [shared, shared]
        with self.assertRaises(LabError):
            model(value)
        cycle = []
        cycle.append(cycle)
        with self.assertRaises(LabError):
            check_tree(cycle)

    def test_no_native_class_hooks(self):
        calls = []
        class Meta(type):
            def __eq__(cls, other):
                calls.append('type equality')
                raise AssertionError('must not compare custom types')
        class Custom(metaclass=Meta):
            def __iter__(self):
                calls.append('iteration')
                raise AssertionError('must not iterate')
        for value in (Custom(), [Custom()], {'x': Custom()}):
            with self.assertRaises(LabError):
                model(value)
        self.assertEqual(calls, [])

    def test_key_and_bytes_subclasses_no_hooks(self):
        calls = []
        class Key(str):
            def __eq__(self, other):
                calls.append('key equality')
                return super().__eq__(other)
            __hash__ = str.__hash__
        class Data(bytes):
            def __len__(self):
                calls.append('length')
                raise AssertionError('must not read subclass')
        value = {Key('profile'): 'fence-high-water/1'}
        calls.clear()
        for candidate in (value, Data(b'{}')):
            with self.assertRaises(LabError):
                model(candidate)
        self.assertEqual(calls, [])

    def test_numeric_domain_and_missing_extra_fields(self):
        for token in (False, 1.0, None, -1, 0, 1000000001):
            with self.assertRaises(LabError):
                model(supplied(0, [token]))
        for seed in (True, -1, 1000000001):
            with self.assertRaises(LabError):
                model(supplied(seed))
        value = supplied(); value['model_basis'] = 'unexpected'
        with self.assertRaises(LabError):
            model(value)

    def test_error_codes_do_not_retain_input_exception(self):
        try:
            parse(b'{"private_marker":')
        except LabError as error:
            self.assertIsNone(error.__context__)
            self.assertEqual(str(error), 'invalid_input')


class CliTests(unittest.TestCase):
    def invoke(self, args, closed=()):
        command = [sys.executable]
        if sys.flags.optimize:
            command.append('-O')
        command.extend(['-m', 'fencing_lab', *args])
        with subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as process:
            for name in closed:
                getattr(process, name).close()
                setattr(process, name, None)
            try:
                output, error = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill(); process.communicate()
                self.fail('CLI timeout')
        return process.returncode, output, error

    def test_all_frozen_reports_and_errors_real_cli(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / 'sample.json'
            for case in CASES:
                path.write_bytes(encoded(case['input']))
                code, output, error = self.invoke([str(path)])
                if 'expected' in case:
                    self.assertEqual((code, error), (0, b''))
                    self.assertEqual(output, encoded(case['expected']) + b'\n')
                else:
                    self.assertEqual((code, output), (2, b''))
                    self.assertEqual(error, encoded(case['expected_error']) + b'\n')

    def test_actual_closed_stream_matrix(self):
        cases = [('report', ['examples/delayed.json'], 'stdout'),
                 ('error', ['missing-evidence.json'], 'stderr'),
                 ('help', ['--help'], 'stdout'),
                 ('usage', ['--unknown'], 'stderr')]
        for name, args, used in cases:
            for closed in (('stdout',), ('stderr',), ('stdout', 'stderr')):
                with self.subTest(case=name, closed=closed):
                    code, output, error = self.invoke(args, closed)
                    self.assertEqual(code, 2 if used in closed or name in ('error', 'usage') else 0)
                    for captured in (output, error):
                        if captured is not None:
                            self.assertNotIn(b'Traceback', captured)
                            self.assertNotIn(b'Exception ignored', captured)

    def test_write_count_exact_types_and_flush_failures(self):
        for count in (True, 2.0, None, 0, 1, 3):
            sink = Mock(); sink.write.return_value = count
            with self.assertRaises(LabError):
                emit('xy', sink)
        sink = Mock(); sink.write.return_value = 2
        emit('xy', sink)
        sink.flush.assert_called_once()
        for failure in (BrokenPipeError(), ValueError('closed')):
            for operation in ('write', 'flush'):
                sink = Mock(); sink.write.return_value = 2
                getattr(sink, operation).side_effect = failure
                with self.assertRaises(LabError):
                    emit('xy', sink)

    def test_failed_sinks_report_error_help_usage_seams(self):
        for args in (['ignored'], ['--help'], ['--unknown']):
            out = Mock(); out.write.return_value = None
            err = Mock(); err.write.side_effect = BrokenPipeError()
            with patch('fencing_lab.__main__.read_input', return_value=encoded(supplied())):
                with patch('sys.stdout', out), patch('sys.stderr', err):
                    self.assertEqual(main(args), 2)

    def test_missing_sinks_seam(self):
        with patch('sys.stdout', None), patch('sys.stderr', None):
            with patch('fencing_lab.__main__.read_input', return_value=encoded(supplied())):
                self.assertEqual(main(['ignored']), 2)

    def test_read_file_growth_and_descriptor_changes(self):
        class Stream(io.BytesIO):
            def fileno(self):
                return 7
        for mode, data in ((stat.S_IFDIR, b'{}'), (stat.S_IFREG, b'x' * (MAX_BYTES + 1))):
            path = Mock(spec=Path)
            path.stat.return_value = SimpleNamespace(st_mode=stat.S_IFREG)
            path.open.return_value = Stream(data)
            with patch('fencing_lab.__main__.os.fstat',
                       return_value=SimpleNamespace(st_mode=mode, st_size=2)):
                with self.assertRaises(LabError):
                    read_input(path)

    def test_no_reflected_argument_or_path(self):
        code, output, error = self.invoke(['--private-marker'])
        self.assertEqual((code, output, error), (2, b'', b'{"error":"invalid_input"}\n'))
        code, output, error = self.invoke(['absent-private-marker'])
        self.assertEqual((code, output, error), (2, b'', b'{"error":"input_error"}\n'))

    def test_output_boundary_seam_not_natural_overflow(self):
        report = model(supplied(0, [1]))
        size = len(render(report))
        with patch('fencing_lab.core.MAX_OUTPUT', size):
            self.assertEqual(len(render(report)), size)
        with patch('fencing_lab.core.MAX_OUTPUT', size - 1), self.assertRaises(LabError):
            render(report)


if __name__ == '__main__':
    unittest.main()
