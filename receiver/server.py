import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "testreport.json"


class ReportHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/report":
            self.send_error(404, "Endpoint not found")
            return

        token = os.environ.get("REPORT_TOKEN")
        authorization = self.headers.get("Authorization", "")
        if not token or authorization != "Bearer " + token:
            self.send_error(401, "Unauthorized")
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 2_000_000:
                self.send_error(400, "Invalid report size")
                return

            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                self.send_error(400, "Invalid JSON report")
                return

            REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
            temp_file = REPORT_FILE.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
            temp_file.replace(REPORT_FILE)

            print(f"Report saved: {REPORT_FILE}")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"saved"}')
        except (ValueError, json.JSONDecodeError):
            self.send_error(400, "Invalid JSON")
        except OSError as error:
            print(f"Could not save report: {error}")
            self.send_error(500, "Could not save report")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), ReportHandler)
    print("Report Receiver running at http://127.0.0.1:8000")
    print("Waiting for GitHub Actions reports...")
    server.serve_forever()
