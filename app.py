from flask import Flask, jsonify, request, send_file, render_template, redirect, url_for
from zapv2 import ZAPv2
import time
import os

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

    # Generate the HTML report
    report_file = f"{REPORT_PATH}/zap_report.html"
    with open(report_file, "w") as f:
        f.write(zap.core.htmlreport())

    return redirect(url_for('serve_report'))

# Serve the generated HTML report
@app.route('/report', methods=['GET'])
def serve_report():
    report_file = f"{REPORT_PATH}/zap_report.html"
    if os.path.exists(report_file):
        return send_file(report_file, mimetype='text/html')
    else:
        return jsonify({"error": "Report not found. Run a scan first."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)