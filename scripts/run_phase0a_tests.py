#!/usr/bin/env python3
"""在離線安全邊界內執行 Phase 0A 契約。"""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run() -> int:
    blocked = []

    def deny_external_io(event, _args):
        if event.startswith("socket.") or event in {
            "subprocess.Popen", "os.system", "os.exec", "os.spawn", "os.posix_spawn",
        }:
            blocked.append(event)
            raise PermissionError(f"Phase 0A offline boundary blocked {event}")

    sys.addaudithook(deny_external_io)
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_phase0*.py")
    if not suite.countTestCases():
        print("FAIL: no Phase 0A contract tests discovered", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Phase 0A network/process attempts blocked by audit hook: {len(blocked)}")
    if blocked:
        print(f"FAIL: unexpected I/O events: {', '.join(sorted(set(blocked)))}")
    return int(not result.wasSuccessful() or bool(blocked))


if __name__ == "__main__":
    raise SystemExit(run())
