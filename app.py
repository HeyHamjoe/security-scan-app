from flask import Flask, jsonify, request, send_file, render_template, redirect, url_for
from zapv2 import ZAPv2
import time
import os
from datetime import datetime

app = Flask(__name__)

# OWASP ZAP configuration
ZAP_API_KEY = "mysecureapikey"
ZAP_API_URL = 'http://localhost:8080'
REPORT_PATH = "/app/reports"

# Initialize the ZAP client with the API key
zap = ZAPv2(apikey=ZAP_API_KEY, proxies={'http': ZAP_API_URL})

# Ensure the reports directory exists
os.makedirs(REPORT_PATH, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/zap-scan')
def zap_scan_form():
    return render_template('zap_scan.html')

@app.route('/scan', methods=['POST'])
def run_scan():
    # Get the target URL from the form
    target_url = request.form.get('url')

    if not target_url:
        return jsonify({"error": "Please provide a valid target URL"}), 400

    # Start ZAP spidering the target
    print(f"Starting spider for: {target_url}")
    zap.spider.scan(target_url)

    # Wait for the spider to complete
    while int(zap.spider.status()) < 100:
        print(f"Spider progress: {zap.spider.status()}%")
        time.sleep(1)

    print("Spider completed. Starting active scan.")
    scan_id = zap.ascan.scan(target_url)

    # Wait for the active scan to complete
    while int(zap.ascan.status(scan_id)) < 100:
        print(f"Scan progress: {zap.ascan.status(scan_id)}%")
        time.sleep(2)

    print("Scan completed. Generating report.")

    # Generate the report filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"{REPORT_PATH}/zap_report_{timestamp}.html"

    # Generate and save the HTML report
    with open(report_file, "w") as f:
        f.write(zap.core.htmlreport())

    print(f"Report saved as {report_file}")

    return redirect(url_for('list_reports'))

@app.route('/reports', methods=['GET'])
def list_reports():
    # List all HTML reports in the reports directory
    reports = [
        report for report in os.listdir(REPORT_PATH) if report.endswith(".html")
    ]
    reports.sort(reverse=True)  # Sort by most recent first
    return render_template('report_list.html', reports=reports)

@app.route('/reports/view/<filename>', methods=['GET'])
def view_report(filename):
    report_file = os.path.join(REPORT_PATH, filename)
    if os.path.exists(report_file):
        return send_file(report_file, mimetype='text/html')
    else:
        return jsonify({"error": "Report not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)