"""Inert local JSON CLI. Checked I/O adapted from Jake's queue lab (MIT)."""

import argparse
import json
import os
from pathlib import Path
import stat
import sys

from .admission import LabError, MAX_BYTES
from .core import model, render


def emit(output, stream):
    """Require an exact count and flush; delivered bytes cannot be rolled back."""
    failed = False
    try:
        written = stream.write(output)
        if type(written) is not int or written != len(output):
            raise LabError('output_error')
        stream.flush()
    except (OSError, ValueError, AttributeError):
        failed = True
    if failed:
        raise LabError('output_error')


class Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise LabError('invalid_input')

    def _print_message(self, message, file=None):
        if message:
            emit(message, file if file is not None else sys.stdout)


def read_input(path):
    """Stable regular-file read; not isolation against replacement/mount races."""
    if not stat.S_ISREG(path.stat().st_mode):
        raise LabError('input_error')
    with path.open('rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise LabError('input_error')
        if info.st_size > MAX_BYTES:
            raise LabError('limit_exceeded')
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise LabError('limit_exceeded')
    return raw


def main(argv=None):
    """Exit0 modeled/incomplete, exit2 error. Help retains argparse exit0."""
    try:
        parser = Parser(prog='fencing-lab', description='Model supplied numeric resource fencing')
        parser.add_argument('file', type=Path)
        args = parser.parse_args(argv)
        emit(render(model(read_input(args.file))), sys.stdout)
        return 0
    except LabError as error:
        code = error.code
    except OSError:
        code = 'input_error'
    try:
        emit(json.dumps({'error': code}, separators=(',', ':')) + '\n', sys.stderr)
    except LabError:
        pass
    return 2


if __name__ == '__main__':
    try:
        # Physical CLI bytes follow the frozen ASCII/LF contract on Windows too.
        for name in ('stdout', 'stderr'):
            stream = getattr(sys, name)
            if stream is not None:
                stream.reconfigure(encoding='ascii', errors='strict', newline='\n')
        status = main()
    except SystemExit as error:
        status = error.code
    except (OSError, ValueError):
        status = 2
    for name in ('stdout', 'stderr'):
        stream = getattr(sys, name)
        if stream is None:
            continue
        try:
            stream.flush()
        except (OSError, ValueError):
            setattr(sys, name, None)
            status = 2
    raise SystemExit(status)
