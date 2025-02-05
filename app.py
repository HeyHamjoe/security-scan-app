from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Security Scan Web App!"})

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    target_url = data.get('url')

    if not target_url:
        return jsonify({"error": "Please provide a valid target URL"}), 400

    # Dummy response for now
    return jsonify({"message": f"Scan initiated for {target_url}!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)