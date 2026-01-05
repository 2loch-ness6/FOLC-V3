from flask import Flask, render_template, jsonify
import subprocess
import os

app = Flask(__name__)

# Configuration
STATUS_FILE = "/data/rayhunter/orbital_os.log"

def get_system_status():
    """
    Mock status for now. In production, this would parse logs 
    or check process status.
    """
    status = {
        "cpu_temp": "45°C",
        "memory_usage": "128MB / 512MB",
        "disk_usage": "45%",
        "wifi_mode": "Managed",
        "ip_address": "192.168.1.10" # Placeholder
    }
    return status

@app.route('/')
def index():
    return render_template('index.html', status=get_system_status())

@app.route('/api/status')
def api_status():
    return jsonify(get_system_status())

@app.route('/api/logs')
def api_logs():
    """
    Returns the last 50 lines of the system log.
    """
    try:
        if os.path.exists(STATUS_FILE):
            # Using tail to get last 50 lines
            result = subprocess.check_output(['tail', '-n', '50', STATUS_FILE], shell=False)
            return jsonify({"logs": result.decode('utf-8')})
        else:
            return jsonify({"logs": "Log file not found."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Running on 0.0.0.0 to be accessible externally
    debug = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.run(host='0.0.0.0', port=8080, debug=debug)
