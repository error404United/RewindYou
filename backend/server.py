from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
from getyttrans import save_transcript_to_json  

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directory to store extracted data
DATA_DIR = 'extracted_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/api/save-page-data', methods=['POST'])
def save_page_data():
    """
    Endpoint to receive and save webpage data from the Chrome extension
    """
    try:
        # Get the JSON data from the request
        page_data = request.get_json()
        
        if not page_data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create a filename based on timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize the title for use in filename
        title = page_data.get('title', 'untitled')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"{timestamp}_{safe_title}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Save the data to a JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved page data: {page_data.get('title', 'N/A')}")
        print(f"  URL: {page_data.get('url', 'N/A')}")
        print(f"  File: {filepath}")
        
        return jsonify({
            'success': True,
            'message': 'Page data saved successfully',
            'filename': filename,
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        print(f"✗ Error saving page data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@app.route('/api/save-youtube-transcript', methods=['POST'])
def save_youtube_transcript():
    try:
        data = request.get_json()
        youtube_url = data.get("url")

        if not youtube_url:
            return jsonify({
                "success": False,
                "error": "Missing YouTube URL"
            }), 400

        # Call existing transcript logic
        file_path = save_transcript_to_json(youtube_url)

        return jsonify({
            "success": True,
            "message": "YouTube transcript saved",
            "filename": os.path.basename(file_path)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/get-saved-pages', methods=['GET'])
def get_saved_pages():
    """
    Endpoint to retrieve list of all saved pages
    """
    try:
        files = os.listdir(DATA_DIR)
        json_files = [f for f in files if f.endswith('.json')]
        
        pages = []
        for filename in sorted(json_files, reverse=True):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pages.append({
                    'filename': filename,
                    'title': data.get('title', 'N/A'),
                    'url': data.get('url', 'N/A'),
                    'timestamp': data.get('timestamp', 'N/A'),
                    'wordCount': data.get('wordCount', 0)
                })
        
        return jsonify({
            'success': True,
            'count': len(pages),
            'pages': pages
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Backend is running'
    }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting RewindYou Backend Server")
    print("=" * 50)
    print(f"📁 Data directory: {os.path.abspath(DATA_DIR)}")
    print(f"🌐 API endpoint: http://localhost:5000/api/save-page-data")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
