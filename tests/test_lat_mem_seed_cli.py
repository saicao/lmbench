"""Check environment-driven CLI behavior: python3 tests/test_lat_mem_seed_cli.py PATH."""
import os
import re
import subprocess
import sys

binary = sys.argv[1]
# CLI checks only; these values skip timing calibration, not used in performance runs.
base_env = dict(os.environ, ENOUGH='100000', TIMING_O='0', LOOP_O='0')
base_env.pop('LMBENCH_SEED', None)
tail = ['-N', '1', '-s', '32768', '-e', '32768', '1', '64']
for seed, options in [(None, ['-t']), ('0', ['-t']), ('2327', ['-t']),
                      ('4294967295', ['-t']), ('2327', ['-t', '-P', '2']),
                      ('2327', [])]:
    env = dict(base_env)
    if seed is not None:
        env['LMBENCH_SEED'] = seed
    result = subprocess.run([binary, *options, *tail], capture_output=True, text=True, env=env, timeout=60)
    assert result.returncode == 0 and 'Invalid LMBENCH_SEED' not in result.stderr, result.stderr
    point = re.search(r'^0\.03125\s+(\d+(?:\.\d+)?)', result.stderr, re.M)
    assert point and float(point[1]) > 0, result.stderr
for option in ['-S', '--seed']:
    result = subprocess.run([binary, '-t', option, '2327', *tail], capture_output=True, text=True, env=base_env, timeout=5)
    assert result.returncode != 0, result.stderr
print('PASS: env seed unset/zero/max/2327, inherited -P 2, stride mode, no seed CLI options')
