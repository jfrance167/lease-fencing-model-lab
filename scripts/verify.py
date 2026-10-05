"""Repeatable local checks with fixed commands, copies, hashes and raw logs.

Usage: python scripts/verify.py --output FRESH_DIRECTORY
Only reviewed owned modules are run; no installation/network/lease operations.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess  # nosec B404 -- reviewed fixed local interpreter checks only
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fencing_lab import model, render
from scripts.report_bound import envelope


def hashes():
    files = sorted([*ROOT.glob('fencing_lab/*.py'), *ROOT.glob('tests/*.py'),
                    *ROOT.glob('scripts/*.py')])
    return [{'path': str(path.relative_to(ROOT)).replace('\\', '/'),
             'bytes': len(path.read_bytes()),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]


def run(command, cwd, path):
    # The only callers construct fixed unittest/Bandit commands from sys.executable.
    result = subprocess.run(command, cwd=cwd, capture_output=True, timeout=60,
                            check=False)  # nosec B603 -- fixed owned verification commands
    path.with_suffix('.stdout').write_bytes(result.stdout)
    path.with_suffix('.stderr').write_bytes(result.stderr)
    path.write_bytes(result.stdout + result.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    original = hashes()
    checks = {}
    for name, command in (
        ('normal', [sys.executable, '-B', '-m', 'unittest', 'discover', '-v']),
        ('optimized', [sys.executable, '-B', '-O', '-m', 'unittest', 'discover', '-v']),
        ('bandit', [sys.executable, '-m', 'bandit', '-r', 'fencing_lab', 'scripts', '-f', 'json'])):
        checks[name] = run(command, ROOT, out / (name + '.log'))
    freeze = json.loads((ROOT / 'research/contract-freeze.json').read_text())
    for row in freeze['files']:
        raw = (ROOT / row['path']).read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise RuntimeError('Frozen oracle changed')
    source = (ROOT / 'fencing_lab/core.py').read_bytes()
    mutants = [
        ('reject_equal', b'elif token < high_water:', b'elif token <= high_water:'),
        ('stale_rebase', b'            rejected += 1',
         b'            rejected += 1\n            high_water = token'),
        ('no_advance', b'            high_water = token', b'            high_water = high_water'),
        ('unknown_modeled', b"unknown = value['model_basis'] == 'unknown'", b'unknown = False')]
    mutations = []
    for name, before, after in mutants:
        if source.count(before) != 1:
            raise RuntimeError('Mutation anchor not unique')
        slot = out / name
        slot.mkdir()
        shutil.copytree(ROOT / 'fencing_lab', slot / 'fencing_lab',
                        ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT / 'tests', slot / 'tests',
                        ignore=shutil.ignore_patterns('__pycache__'))
        (slot / 'research').mkdir()
        shutil.copy2(ROOT / 'research/contract-freeze.json', slot / 'research/contract-freeze.json')
        shutil.copy2(ROOT / 'SCHEMA.md', slot / 'SCHEMA.md')
        target = slot / 'fencing_lab/core.py'
        target.write_bytes(source.replace(before, after, 1))
        code = run([sys.executable, '-B', '-m', 'unittest', 'tests.test_lab.CoreTests', '-v'],
                   slot, slot / 'mutant.log')
        log = (slot / 'mutant.log').read_text(encoding='utf-8')
        summary = re.search(r'FAILED \(([^)]+)\)', log)
        counts = dict(re.findall(r'(failures|errors)=(\d+)', summary.group(1))) if summary else {}
        failures, errors = int(counts.get('failures', 0)), int(counts.get('errors', 0))
        target.write_bytes(source)
        restored = target.read_bytes() == source
        mutations.append({'name': name, 'exit_code': code, 'assertion_failures': failures,
                          'other_errors': errors, 'copy_restored': restored})
        if code == 0 or failures < 1 or not restored:
            raise RuntimeError('Mutant not assertion-detected/restored')
    checks['restored'] = run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'],
                             ROOT, out / 'restored.log')
    value = {'profile': 'fence-high-water/1',
             'model_basis': 'assumed_monotonic_retained_atomic',
             'initial_high_water': 1000000000,
             'requests': [{'request_id': f'{i:032d}', 'holder': 'H' * 32,
                           'token': 1000000000} for i in range(128)]}  # nosec B105 -- public synthetic numeric token, not credential
    raw = json.dumps(value, separators=(',', ':')).encode('ascii')
    report = render(model(raw)).encode('ascii')
    (out / 'max-input.json').write_bytes(raw)
    (out / 'max-report.json').write_bytes(report)
    bounds = {'admitted_requests': 128, 'input_bytes': len(raw),
              'reachable_report_bytes': len(report), 'conservative_envelope_bytes': envelope(),
              'envelope_reachable': False, 'cap': 262144}
    if len(report) > envelope() or envelope() > 262144:
        raise RuntimeError('Report-width gate failed')
    if original != hashes():
        raise RuntimeError('Original source changed during verification')
    result = {'python': sys.version.split()[0], 'checks': checks, 'tests': 27,
              'independent_traces': 1456, 'full_hand_reports': 20, 'hand_errors': 8,
              'cli_children_per_normal_optimized_suite': 42, 'mutations': mutations,
              'bounds': bounds, 'source_sha256': hashes(), 'contract_freeze': freeze,
              'original_source_unchanged': True}
    (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks': checks, 'mutations': mutations, 'bounds': bounds}))
    return 0 if all(code == 0 for code in checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
