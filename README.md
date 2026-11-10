# Assignment Submission Portal

A Flask portal for submitting assignment details and a submission URL. Valid
submissions are stored in SQLite and displayed in reverse submission order.

## Run locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

## Run tests and create a report

```powershell
python -m pytest -v
```

To generate `testreport.json` and send it to the local receiver:

```powershell
$env:REPORT_TOKEN = "choose-a-local-token"
$env:REPORT_RECEIVER_URL = "http://127.0.0.1:8000"
python scripts/run_tests_and_report.py
```

## Start the local receiver

```powershell
$env:REPORT_TOKEN = "choose-a-local-token"
python receiver/server.py
```

The receiver saves the latest report as `reports/testreport.json`. For a
GitHub-hosted runner, expose port 8000 through a tunnel or relay and store its
URL as the `REPORT_RECEIVER_URL` GitHub Actions secret. Store the same token
as `REPORT_TOKEN`. Keep both the receiver and tunnel running. Reports are sent
for passing and failing runs, and failed tests still fail the test job.

## GitHub Pages

The `main` branch deploys the static demonstration in `docs/` only after the
test job passes. The Pages URL is shown in the workflow environment after the
first successful deployment.
