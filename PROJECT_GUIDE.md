# Assignment Submission Portal - Complete Guide

## 1. Project ka purpose

Yeh project students ke assignments submit karne ke liye banaya gaya hai.
Student apna:

- naam
- registration number
- assignment title
- submission URL

enter karta hai. Valid form submit hone par data SQLite database mein save hota
hai aur neeche submission list mein display hota hai.

Project mein automated tests, GitHub Actions CI, local JSON report receiver,
aur GitHub Pages static demo bhi included hain.

## 2. Important files aur unka kaam

| File/folder | Purpose |
|---|---|
| `app.py` | Flask backend. Form validation, SQLite saving, aur saved submissions display karta hai. |
| `templates/index.html` | Main portal ka form aur submissions table. |
| `static/style.css` | Portal ka design/layout. |
| `submissions.db` | Local SQLite database jahan submissions save hoti hain. |
| `tests/test_app.py` | 3 automated tests. |
| `requirements.txt` | Flask aur pytest dependencies. |
| `.github/workflows/ci.yml` | Har push par GitHub Actions test aur Pages deployment chalata hai. |
| `scripts/run_tests_and_report.py` | Pytest run karta hai, results JSON mein convert karta hai, aur receiver ko bhejta hai. |
| `receiver/server.py` | Local HTTP server jo JSON report receive karke save karta hai. |
| `reports/testreport.json` | Latest received test report. |
| `docs/index.html` | GitHub Pages par deployed static demo. |
| `README.md` | Short setup instructions. |

## 3. Application kaise run karein

PowerShell mein:

```powershell
cd C:\Users\sadiq\Assignment-Submission-Portal
.\venv\Scripts\Activate.ps1
python app.py
```

Browser mein open karein:

```text
http://127.0.0.1:5000
```

Valid test ke liye:

- Student name: `Ali Ahmed`
- Registration number: `SP23-BCS-001`
- Assignment title: `Cloud Computing`
- Submission URL: `https://github.com`

Submit karne ke baad success message aur submission list mein record nazar
aayega.

## 4. Validation kaise verify karein

### Missing registration number

Registration number blank chhor kar submit karein.

Expected:

- `All fields are required.` message
- submission database mein save nahi hogi

### Invalid URL

URL mein `invalid-url` enter karein.

Expected:

- `Invalid submission URL` message
- submission save nahi hogi

## 5. Automated tests

```powershell
cd C:\Users\sadiq\Assignment-Submission-Portal
.\venv\Scripts\Activate.ps1
python -m pytest -v
```

Expected result:

```text
3 passed
```

Teen tests:

1. Complete details aur valid URL: submission save hoti hai.
2. Missing registration number: submission reject hoti hai.
3. Invalid URL: submission reject hoti hai.

## 6. Local report receiver

Receiver ko alag terminal mein start karein:

```powershell
cd C:\Users\sadiq\Assignment-Submission-Portal
.\venv\Scripts\Activate.ps1
$env:REPORT_TOKEN="test-token"
python receiver\server.py
```

Is terminal ko running rehne dein.

Doosre terminal mein:

```powershell
cd C:\Users\sadiq\Assignment-Submission-Portal
.\venv\Scripts\Activate.ps1
$env:REPORT_TOKEN="test-token"
$env:REPORT_RECEIVER_URL="http://127.0.0.1:8000"
python scripts\run_tests_and_report.py
```

Expected output:

```text
3 passed
Report sent to http://127.0.0.1:8000
```

Report yahan save hoti hai:

```text
reports\testreport.json
```

Report mein repository, branch, commit SHA, pipeline ID, timestamp, har test ka
result, total/passed/failed counts, aur overall status hota hai.

## 7. GitHub Actions CI kaise kaam karti hai

File:

```text
.github\workflows\ci.yml
```

Jab bhi `main` ya kisi branch par push hota hai:

1. GitHub code checkout karta hai.
2. Python 3.12 install hota hai.
3. `requirements.txt` install hota hai.
4. `scripts/run_tests_and_report.py` tests chalata hai.
5. Test report receiver ko bheji jati hai.
6. Agar koi test fail ho, test job fail hoti hai.
7. Sirf successful `main` test ke baad Pages deploy hota hai.

GitHub Actions check karne ke liye:

1. Repository open karein.
2. `Actions` tab click karein.
3. Latest `Python CI` run open karein.
4. `test` green hona chahiye.
5. `deploy` green hona chahiye.

## 8. Passing, failing, corrected demonstration

### Passing run

```powershell
python scripts\run_tests_and_report.py
```

Expected:

```text
3 passed
```

### Failing run

Temporary defect ke liye `app.py` mein URL validation ki line temporarily change
karein, phir:

```powershell
python scripts\run_tests_and_report.py
```

Expected:

```text
1 failed, 2 passed
```

Report mein expected values:

```json
{
  "passed": 2,
  "failed": 1,
  "overall_status": "failed"
}
```

### Corrected run

Temporary defect ko undo karein aur dobara run karein:

```powershell
python scripts\run_tests_and_report.py
```

Expected:

```text
3 passed
```

## 9. GitHub par push karke verify karna

```powershell
git add .
git commit -m "Update assignment portal"
git push origin main
```

Push ke baad GitHub Actions automatically run hogi.

## 10. GitHub Pages

Static demo URL:

<https://sp23-bcs-021-a11y.github.io/Assignment-Submission-Portal/>

Pages demo browser mein fields validate karta hai. Actual data save karne ke
liye Flask application (`python app.py`) use karni hai, kyunki GitHub Pages
server-side Python backend run nahi karta.

## 11. Final verification checklist

- [ ] `python app.py` se portal open hota hai.
- [ ] Valid submission save aur display hoti hai.
- [ ] Missing registration number reject hota hai.
- [ ] Invalid URL reject hota hai.
- [ ] `python -m pytest -v` par 3 tests pass hote hain.
- [ ] Receiver running hota hai.
- [ ] `reports/testreport.json` update hoti hai.
- [ ] GitHub Actions ka `test` job green hota hai.
- [ ] Failing test par `test` job red hoti hai.
- [ ] Fixed code par `test` job dobara green hoti hai.
- [ ] Successful `main` push ke baad `deploy` job green hoti hai.
- [ ] GitHub Pages URL open hota hai.
