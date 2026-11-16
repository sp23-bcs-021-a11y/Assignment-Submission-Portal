# Assignment Submission Portal

**COMSATS University Islamabad – Attock Campus**  
**DevOps Lab Mid | CSC418 – DevOps for Cloud Computing**  
**Instructor:** Mr. Babar Shazad | **Student:** Muhammad Sadiq | **Reg#:** SP23-BCS-021

---

## Project Overview

A Flask-based portal where students submit their name, registration number, assignment title, and a submission URL. Valid entries are saved to SQLite and displayed in reverse order. Every push to GitHub triggers an automated CI pipeline that runs three test cases, builds a JSON report, and delivers it to a local HTTP receiver on your machine.

---

## Repository Structure

```
Assignment-Submission-Portal/
├── app.py                        # Flask application
├── requirements.txt              # Python dependencies
├── submissions.db                # SQLite database (auto-created)
├── testreport.json               # Latest report (auto-generated)
├── templates/
│   └── index.html                # Submission form + list
├── static/
│   └── style.css                 # Stylesheet
├── tests/
│   └── test_app.py               # Automated test cases (pytest)
├── scripts/
│   └── run_tests_and_report.py   # Runs tests, builds & sends JSON report
├── receiver/
│   └── server.py                 # Local HTTP receiver – saves testreport.json
├── docs/
│   └── index.html                # Static GitHub Pages demo
└── .github/
    └── workflows/
        └── ci.yml                # GitHub Actions CI + deploy pipeline
```

---

## Prerequisites

- Python 3.10 or later
- pip
- Git
- (For tunnel) [ngrok](https://ngrok.com) or any public tunnel client

---

## 1 — Run the Application Locally

```powershell
# Clone the repository
git clone https://github.com/<your-username>/Assignment-Submission-Portal.git
cd Assignment-Submission-Portal

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

Open **http://127.0.0.1:5000** in your browser.  
Fill in all four fields and click **Submit**. Valid submissions appear in the table below the form. Missing fields or an invalid URL shows an error message without saving.

---

## 2 — Run the Automated Tests

### Quick test run (verbose output)

```powershell
# Make sure the virtual environment is active
.\venv\Scripts\Activate.ps1

python -m pytest -v
```

### Three required test cases

| Test | What it checks | Expected result |
|------|---------------|-----------------|
| `test_valid_submission` | Complete details + valid URL | Saved, appears in list |
| `test_missing_registration_number` | Empty registration number | Rejected with validation message |
| `test_invalid_submission_url` | URL without scheme (e.g. `invalid-url`) | Rejected, nothing saved |

A failing test causes the pytest process to exit with a non-zero code, which fails the CI stage.

### Generate the JSON report locally (without receiver)

```powershell
.\venv\Scripts\Activate.ps1
python scripts/run_tests_and_report.py
```

`testreport.json` is written to the project root. `REPORT_RECEIVER_URL` is not required for local generation.

---

## 3 — Start the Local Report Receiver

The receiver is a lightweight HTTP server that listens for POST requests from GitHub Actions and saves the report as `reports/testreport.json`.

### Step 1 – Choose a secret token

Pick any string, for example `mysecrettoken123`. You will use the same value in both the receiver and in the GitHub Actions secrets.

### Step 2 – Start the receiver

```powershell
$env:REPORT_TOKEN = "mysecrettoken123"
python receiver/server.py
```

Output:
```
Report Receiver running at http://127.0.0.1:8000
Waiting for GitHub Actions reports...
```

Leave this terminal open during demonstrations.

### Step 3 – Expose port 8000 with a tunnel (required for GitHub-hosted runners)

GitHub Actions runners cannot reach `127.0.0.1` on your machine. Use a tunnel:

```powershell
# In a second terminal (keep the receiver running in the first)
ngrok http 8000
```

ngrok prints a public URL like `https://abc123.ngrok-free.app`. Copy it.

### Step 4 – Add GitHub Actions secrets

Go to your repository → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|-------------|-------|
| `REPORT_RECEIVER_URL` | The ngrok URL, e.g. `https://abc123.ngrok-free.app` |
| `REPORT_TOKEN` | The same token you set in Step 2 |

### Step 5 – Push any change

The CI pipeline runs automatically, sends the report to your receiver, and saves it to `reports/testreport.json`.

---

## 4 — Run Tests Locally AND Send to Receiver (combined)

```powershell
.\venv\Scripts\Activate.ps1
$env:REPORT_TOKEN      = "mysecrettoken123"
$env:REPORT_RECEIVER_URL = "http://127.0.0.1:8000"   # or your ngrok URL
python scripts/run_tests_and_report.py
```

---

## 5 — CI Pipeline Summary

File: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

```
On every push (any branch) or pull request to main:
  job: test
    1. Checkout code
    2. Set up Python 3.12
    3. pip install -r requirements.txt
    4. python scripts/run_tests_and_report.py
       └─ Runs pytest, builds JSON report, POSTs it to REPORT_RECEIVER_URL
       └─ Exits non-zero on test failure → job fails

On push to main (only when test job passes):
  job: deploy
    → Publishes docs/ to GitHub Pages
```

**Reports are sent for both passing and failing runs.** The test job exit code reflects the actual test outcome—a failed test causes the CI stage to fail.

---

## 6 — JSON Report Format

`reports/testreport.json` example:

```json
{
    "repository": "sadiq/Assignment-Submission-Portal",
    "branch": "main",
    "commit_sha": "a1b2c3d4...",
    "pipeline_run_id": "123456789",
    "execution_timestamp": "2026-10-26T10:00:00+00:00",
    "tests": [
        {
            "name": "tests/test_app.py::test_valid_submission",
            "result": "passed",
            "failure_message": null
        },
        {
            "name": "tests/test_app.py::test_missing_registration_number",
            "result": "passed",
            "failure_message": null
        },
        {
            "name": "tests/test_app.py::test_invalid_submission_url",
            "result": "passed",
            "failure_message": null
        }
    ],
    "total": 3,
    "passed": 3,
    "failed": 0,
    "overall_status": "passed"
}
```

---

## 7 — Demonstrate the Full Workflow

### Passing run

1. Receiver and tunnel are running.
2. Push any valid change to GitHub.
3. Watch **Actions** tab → test job turns green.
4. Confirm `reports/testreport.json` updated with `"overall_status": "passed"`.

### Failing run (introduce a defect)

Temporarily break a test, for example edit `app.py` and change:

```python
flash("All fields are required.", "error")
```
to:
```python
flash("BROKEN MESSAGE", "error")
```

Push the change. The `test_missing_registration_number` test fails → CI stage fails → report shows `"overall_status": "failed"`.

### Recovery run

Revert the defect and push again. All tests pass. Report updates to `"overall_status": "passed"`.

---

## 8 — GitHub Pages (Bonus)

The `deploy` job in `ci.yml` publishes `docs/index.html` to GitHub Pages **only when the test job passes on `main`**. A failing run leaves the previously published version untouched.

**Enable Pages once:**  
Repository → **Settings → Pages → Source → GitHub Actions**

The deployed URL will be:  
`https://<your-username>.github.io/Assignment-Submission-Portal/`

---

## 9 — Email Report (Bonus)

Add the following secrets to GitHub Actions:

| Secret | Description |
|--------|-------------|
| `EMAIL_SENDER` | Sending Gmail address |
| `EMAIL_PASSWORD` | Gmail App Password (not your login password) |
| `EMAIL_RECIPIENT` | Address to receive the report |

Extend `scripts/run_tests_and_report.py` to call `smtplib` after `send_report()`, attaching `testreport.json` and including commit SHA and test counts in the body.

---

## Quick-Reference Command Sheet

| Task | Command |
|------|---------|
| Activate venv | `.\venv\Scripts\Activate.ps1` |
| Install deps | `pip install -r requirements.txt` |
| Run app | `python app.py` → http://127.0.0.1:5000 |
| Run tests only | `python -m pytest -v` |
| Run tests + report | `python scripts/run_tests_and_report.py` |
| Start receiver | `$env:REPORT_TOKEN="token"; python receiver/server.py` |
| Expose via tunnel | `ngrok http 8000` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: flask` | Activate venv first: `.\venv\Scripts\Activate.ps1` |
| Receiver returns 401 | `REPORT_TOKEN` on receiver and in GitHub secrets must match exactly |
| Report not received | Check ngrok is running and `REPORT_RECEIVER_URL` secret is updated |
| GitHub Pages not deploying | Go to Settings → Pages and set Source to **GitHub Actions** |
| `submissions.db` permission error | Delete it and restart — it auto-recreates |
