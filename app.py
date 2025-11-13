from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

STORAGE_FILE = 'updates.json'

def init_storage():
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'w') as f:
            json.dump({}, f)

init_storage()

@app.route('/')
def home ():
    return "Diun-Homepage tracker is running and active.", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("Error parsing JSON:", e)
        return jsonify({"error": str(e)}), 400
    
    with open(STORAGE_FILE, 'r') as f:
        updates = json.load(f)

    current_time = datetime.now().timestamp() * 1000
    one_hour_ms = 60 * 60 * 1000

    if updates:
        most_recent_timestamp = max(
            update.get('detected_at', 0) for update in updates.values()
        )

        if (current_time - most_recent_timestamp) > one_hour_ms:
            print("New scan cycle detected, clearing old updates")
            updates = {}

    image_key = data.get('image', 'unknown')

    updates[image_key] = {
        'image': data.get('image'),
        'status': data.get('status'),
        'provider': data.get('provider'),
        'digest': data.get('digest'),
        'created': data.get('created'),
        'platform': data.get('platform'),
        'hub_link': data.get('hub-link'),
        'hostname': data.get('hostname'),
        'metadata': data.get('metadata', {}),
        'detected_at': current_time
    }

    with open(STORAGE_FILE, 'w') as f:
        json.dump(updates, f, indent=2)

    return jsonify({"status": "success"}), 200

@app.route('/updates', methods=['GET'])
def get_updates():
    with open(STORAGE_FILE, 'r') as f:
        updates = json.load(f)

    return jsonify(updates)

@app.route('/updates/list', methods=['GET'])
def get_updates_list():
    with open(STORAGE_FILE, 'r') as f:
        updates = json.load(f)

    updates_list = []
    for image_key, image_data in updates.items():
        updates_list.append(image_data)

    updates_list.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
    return jsonify(updates_list)

@app.route('/updates/summary', methods=['GET'])
def get_updates_summary():
    with open(STORAGE_FILE, 'r') as f:
        updates = json.load(f)

    if not updates:
        return jsonify({
            "total": 0,
            "latest": "No updates available"
        })
    updates_list = list(updates.values())
    updates_list.sort(key=lambda x: x.get('detected_at', 0), reverse=True)

    most_recent = updates_list[0]

    return jsonify({
        "total": len(updates_list),
        "latest_image": most_recent.get('image', 'Unknown'),
        "latest_status": most_recent.get('status', 'Unknown'),
        "latest_timestamp": most_recent.get('detected_at', 0)
    })

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 5000))
    host = os.environ.get('APP_IP', '0.0.0.0')
    app.run(host=host, port=port, debug=False)