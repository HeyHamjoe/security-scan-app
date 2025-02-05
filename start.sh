#!/bin/bash

# Set the ZAP API key
ZAP_API_KEY="mysecureapikey"

# Find the zap.sh script dynamically
ZAP_SH=$(find /opt/zap -name zap.sh | head -n 1)

if [ -z "$ZAP_SH" ]; then
    echo "Error: Unable to find zap.sh in /opt/zap."
    exit 1
fi

# Start OWASP ZAP in daemon mode (headless)
echo "Starting OWASP ZAP..."
$ZAP_SH -daemon -port 8080 -host 0.0.0.0 -config api.key=$ZAP_API_KEY &

# Wait for ZAP to be fully initialized
echo "Waiting for ZAP to start..."
while ! curl -s http://localhost:8080; do
    sleep 1
done

echo "ZAP started successfully."

# Start the Flask app
echo "Starting Flask app..."
python app.py