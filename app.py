from flask import Flask, jsonify, request
from zapv2 import ZAPv2
import time

app = Flask(__name__)

# OWASP ZAP configuration
ZAP_API_KEY = "mysecureapikey"
ZAP_API_URL = 'http://localhost:8080'

# Initialize the ZAP client with the API key
zap = ZAPv2(apikey=ZAP_API_KEY, proxies={'http': ZAP_API_URL})


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Security Scan Web App!"})


@app.route('/scan', methods=['POST'])
def run_scan():
    data = request.json
    target_url = data.get('url')

    if not target_url:
        return jsonify({"error": "Please provide a valid target URL"}), 400

    # Start ZAP spidering the target
    print(f"Starting spider for: {target_url}")
    scan_id = zap.spider.scan(target_url)

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

    print("Scan completed. Retrieving alerts.")
    alerts = zap.core.alerts(baseurl=target_url)

    return jsonify({
        "message": f"Scan completed for {target_url}",
        "alerts": alerts
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)