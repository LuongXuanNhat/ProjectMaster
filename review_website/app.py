import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MASTER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSORED_DIR = os.path.join(MASTER_DIR, "Censored")

if not os.path.exists(CENSORED_DIR):
    os.makedirs(CENSORED_DIR)

TARGET_SAVE_FILE = os.path.join(CENSORED_DIR, "data_traning_offical.json")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/api/report_data', methods=['GET'])
def get_report_data():
    filename = "labeled_results_all_v5.json"
    filepath = os.path.join(MASTER_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": f"File not found: {filename}"}), 404
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        stats = {}
        for item in data:
            labels = item.get("labels", [])
            for label in labels:
                name = label.get("name")
                value = label.get("value")
                
                if name not in stats:
                    stats[name] = {"0.0": 0, "0.5": 0, "1.0": 0, "total": 0}
                
                val_str = str(value)
                if val_str in stats[name]:
                    stats[name][val_str] += 1
                stats[name]["total"] += 1
                
        # Tính tỷ lệ
        report_result = []
        for name, item_stats in stats.items():
            total = item_stats["total"]
            if total > 0:
                report_result.append({
                    "criteria": name,
                    "0.0_count": item_stats["0.0"],
                    "0.0_percent": round((item_stats["0.0"] / total) * 100, 2),
                    "0.5_count": item_stats["0.5"],
                    "0.5_percent": round((item_stats["0.5"] / total) * 100, 2),
                    "1.0_count": item_stats["1.0"],
                    "1.0_percent": round((item_stats["1.0"] / total) * 100, 2),
                    "total": total
                })
                
        return jsonify({"success": True, "data": report_result, "total_items": len(data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    files = []
    for f in os.listdir(MASTER_DIR):
        if f.endswith('.json'):
            files.append(f)
    return jsonify({"files": files})

@app.route('/api/data', methods=['GET'])
def get_data():
    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "No file specified"}), 400
    
    filepath = os.path.join(MASTER_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": f"File not found: {filename}"}), 404
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_data():
    item = request.json
    if not item:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        if os.path.exists(TARGET_SAVE_FILE):
            with open(TARGET_SAVE_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    existing_data = []
                else:
                    existing_data = json.loads(content)
        else:
            existing_data = []
    except Exception as e:
        print("Error reading target file:", e)
        existing_data = []
        
    existing_data.append(item)
    
    try:
        with open(TARGET_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
