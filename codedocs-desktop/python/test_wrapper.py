"""Tests for the JSON stdio wrapper."""

import json
import os
import subprocess
import sys
import unittest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_WRAPPER = os.path.join(_THIS_DIR, "wrapper.py")


def _run_wrapper(msg, timeout=120):
    """Send a JSON message to wrapper.py via stdin and return parsed output lines."""
    env = os.environ.copy()
    env["PYTHONPATH"] = _REPO_ROOT + os.pathsep + env.get("PYTHONPATH", "")

    proc = subprocess.run(
        [sys.executable, _WRAPPER],
        input=json.dumps(msg) + "\n",
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )

    lines = []
    for raw in proc.stdout.strip().splitlines():
        if raw.strip():
            lines.append(json.loads(raw))
    return lines, proc.returncode


class TestWrapper(unittest.TestCase):

    def test_scan_produces_progress_and_result(self):
        """Scan this repo — expect progress events followed by a result."""
        lines, rc = _run_wrapper({"command": "scan", "path": _REPO_ROOT})
        self.assertEqual(rc, 0, f"Wrapper exited with code {rc}")
        self.assertTrue(len(lines) >= 2, "Expected at least progress + result lines")

        progress_lines = [l for l in lines if l["type"] == "progress"]
        result_lines = [l for l in lines if l["type"] == "result"]

        self.assertTrue(len(progress_lines) > 0, "No progress events received")
        self.assertEqual(len(result_lines), 1, "Expected exactly one result event")

        # Progress events have step/total/label
        for p in progress_lines:
            self.assertIn("step", p)
            self.assertIn("total", p)
            self.assertIn("label", p)
            self.assertIsInstance(p["step"], int)
            self.assertIsInstance(p["total"], int)

        # Result contains expected file keys
        result = result_lines[0]
        self.assertIn("files", result)
        files = result["files"]
        for key in ("scan-report", "sales-datasheet", "technical-spec", "decision-brief"):
            self.assertIn(key, files, f"Missing file key: {key}")
            self.assertIsInstance(files[key], str)
            self.assertTrue(len(files[key]) > 0, f"Empty HTML for {key}")

    def test_scan_with_target(self):
        """Scan with target='react-node' — migration-plan must appear in result."""
        lines, rc = _run_wrapper({
            "command": "scan",
            "path": _REPO_ROOT,
            "options": {"target": "react-node"},
        })
        self.assertEqual(rc, 0, f"Wrapper exited with code {rc}")

        result_lines = [l for l in lines if l["type"] == "result"]
        self.assertEqual(len(result_lines), 1)

        files = result_lines[0]["files"]
        self.assertIn("migration-plan", files, "migration-plan missing when target is set")
        self.assertTrue(len(files["migration-plan"]) > 0, "Empty migration-plan HTML")

    def test_invalid_path(self):
        """Non-existent path should produce an error event."""
        lines, rc = _run_wrapper({"command": "scan", "path": "/nonexistent/path/abc123"})
        self.assertNotEqual(rc, 0, "Expected non-zero exit code for invalid path")
        self.assertTrue(len(lines) >= 1, "Expected at least one output line")

        error_lines = [l for l in lines if l["type"] == "error"]
        self.assertEqual(len(error_lines), 1, "Expected exactly one error event")
        self.assertIn("message", error_lines[0])
        self.assertTrue(len(error_lines[0]["message"]) > 0)


if __name__ == "__main__":
    unittest.main()
