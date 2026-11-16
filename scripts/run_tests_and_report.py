"""Run pytest, build a machine-readable report, and send it to the receiver."""

import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent


def build_report(xml_path: Path, exit_code: int) -> dict:
    root = ElementTree.parse(xml_path).getroot()
    tests = []
    for case in root.iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        problem = failure if failure is not None else error
        tests.append({
            "name": f"{case.get('classname', '')}::{case.get('name', '')}",
            "result": "failed" if problem is not None else "passed",
            "failure_message": (
                (problem.get("message", "") + "\n" + (problem.text or "")).strip()
                if problem is not None else None
            ),
        })

    failed = sum(test["result"] == "failed" for test in tests)
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "total": len(tests),
        "passed": len(tests) - failed,
        "failed": failed,
        "overall_status": "passed" if exit_code == 0 else "failed",
    }


def send_report(report: dict) -> None:
    receiver_url = os.environ.get("REPORT_RECEIVER_URL")
    if not receiver_url:
        print("REPORT_RECEIVER_URL is not set; report was generated locally.")
        return

    request = urllib.request.Request(
        receiver_url.rstrip("/") + "/report",
        data=json.dumps(report).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + os.environ.get("REPORT_TOKEN", ""),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"receiver returned HTTP {response.status}")
    print(f"Report sent to {receiver_url}")


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary_directory:
        xml_path = Path(temporary_directory) / "junit.xml"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", f"--junitxml={xml_path}"],
            cwd=ROOT,
            check=False,
        )
        report = build_report(xml_path, result.returncode)
        (ROOT / "testreport.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        send_report(report)
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
