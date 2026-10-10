#!/usr/bin/env python3
"""Verify that preparation preserves scene/resource bytes and script identities."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def verify(source, prepared):
    report = json.loads((prepared / 'WEB_PORT_PREPARATION.json').read_text())
    changed = set(report['changed']) | set(report['overlayFiles']) | {'ProjectSettings/ProjectVersion.txt'}
    removed = report['removed']
    removed_guids = set()
    failures = []
    unchanged = 0
    for old in source.rglob('*'):
        if not old.is_file():
            continue
        rel = old.relative_to(source).as_posix()
        new = prepared / rel
        expected_removed = any(rel == x or rel == x + '.meta' or rel.startswith(x + '/') for x in removed)
        if expected_removed:
            if old.suffix == '.meta':
                match = re.search(r'^guid: (\w+)', old.read_text(), re.M)
                if match:
                    removed_guids.add(match[1])
            # The unused folder's .meta can remain; it has no script identity.
            continue
        if not new.is_file():
            failures.append('Unexpected missing file: ' + rel)
        elif rel not in changed:
            if hashlib.sha256(old.read_bytes()).digest() != hashlib.sha256(new.read_bytes()).digest():
                failures.append('Unexpected modified file: ' + rel)
            else:
                unchanged += 1
    for path in (prepared / 'Assets').rglob('*'):
        if path.suffix in ('.unity', '.prefab', '.asset', '.mat', '.controller'):
            refs = set(re.findall(r'guid: (\w+)', path.read_text(errors='replace')))
            if refs & removed_guids:
                failures.append('Reference to removed asset: ' + str(path.relative_to(prepared)))
    result = {'passed': not failures, 'unchangedInputFiles': unchanged,
              'removedAssetGuidsChecked': len(removed_guids), 'failures': failures,
              'unityEditorRun': False, 'webglBuild': False}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.source, args.prepared)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
